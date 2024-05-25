import gzip
from datetime import timedelta
from pprint import pprint, pformat
import imp
import sys
import shutil
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
import re
import requests

# This is something I use to speed up development. It should always be False in production.
USE_CACHED_RESPONSES = False
SKIP_WRITING_HISTORY = False
USE_CANNED_TIMESTAMP = False
SET_CACHED_RESPONSES = False

BID_ASK_TOOLTIP = True
USE_WEIGHTED_AVERAGES = False

class FTXUniversalException(Exception):
    pass

def import_module(path, modname):
    fp, pathname, description = imp.find_module(modname, [path])
    return imp.load_module(modname, fp, pathname, description)

try:
    # TODO - use import_module()
    eboconfig = imp.load_source("eboconfig", "/python/eboconfig.py")
except:
    logging.error("Need a valid /python/eboconfig.py file. See /python/eboconfig.py.example for reference.")
    raise

# From Stack Overflow. Putting this here to assist in debugging. We can find better ways when we clean up.
def full_stack():
    import traceback, sys
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if exc is not None:  # i.e. an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if exc is not None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

def warning_email(headline, body):
    try:
        EMAIL_TO = ["maxim.lott@gmail.com"]
        EMAIL_FROM = "maxims.program@gmail.com" # TODO - probably set same as eboconfig.Email.smpt_username but think aobut it later
        EMAIL_SUBJECT = "Warning: " + headline
        EMAIL_SPACE = ", "
        def send_email():
            if eboconfig.Email.enabled:
                msg = MIMEText(body)
                msg['Subject'] = EMAIL_SUBJECT
                msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
                msg['From'] = EMAIL_FROM
                mail = smtplib.SMTP(eboconfig.Email.smtp_server, eboconfig.Email.smtp_port)
                mail.starttls()
                mail.login(eboconfig.Email.smtp_username, eboconfig.Email.smtp_password)
                mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
                mail.quit()
            else:
                print "Email not enabled, skipping warning report email"
            if eboconfig.LocalOutput.enabled:
                debug_warning_path = os.path.join(
                    eboconfig.LocalOutput.parent_path,
                    'warning_emails',
                    str(time.time()) + '.' + str(random.random()) + '.txt'
                )
                print "Writing warning email to local file: " + debug_warning_path
                debug_warning_dirname = os.path.dirname(debug_warning_path)
                if not os.path.exists(debug_warning_dirname): # TODO - python 3, just use exist_ok with makdirs
                    os.makedirs(debug_warning_dirname)
                with open(debug_warning_path, 'w') as f:
                    f.write(EMAIL_SUBJECT)
                    f.write('\n\n')
                    f.write(body)

        send_email()
    except Exception,e:
        print "!!! WARNING EMAIL NOT WORKING !!!"
        print str(e)
        pass

def missing_candidates_warning_email(NONEMPTY_USED_MARKETS, EMPTY_USED_MARKETS, finalwinner_odds_tuples, manual_entry_by_market):
    "Send a warning email if we have any missing candidates, including markets that are entirely failing"

    missing_candidates_by_market = {}
    for market in NONEMPTY_USED_MARKETS:
        missing_candidates_by_market[market] = []
        for contract_index, finalwinner_odds_tuples_for_contract in enumerate(finalwinner_odds_tuples):
            candidate_expected = bool(manual_entry_by_market[market][contract_index][0])
            candidate_missing = market not in finalwinner_odds_tuples_for_contract['odds_by_market']
            if candidate_missing and candidate_expected:
                missing_candidates_by_market[market].append(finalwinner_odds_tuples_for_contract['name'])

    message = ""

    if EMPTY_USED_MARKETS:
        message += "These markets are missing *every* candidate: " + repr(list(EMPTY_USED_MARKETS)) + "\n\n"

    if any(missing_candidates_by_market.values()):
        message += "The following markets are missing the following expected candidates:\n\n"

    for market, missing_candidates in missing_candidates_by_market.items():
        if missing_candidates:
            message += market + ":\n"
            for candidate in missing_candidates:
                message += "  * " + candidate + "\n"

    if message:
        message = "Race: " + column_title + "\n\n" + message
        warning_email("Missing candidates in scraped market(s)", message)

# Cut down on annoyances wherein some of these are not defined in the variables file because they're not needed there
# Eventually this should be moved to a common import library, of course. once we can do actual imports.
if 'MARKET_BETFAIR' not in locals():
    MARKET_BETFAIR = "Betfair"
if 'MARKET_PREDICTIT' not in locals():
    MARKET_PREDICTIT = "PredictIt"
if 'MARKET_FTX' not in locals():
    MARKET_FTX = "FTX"
if 'MARKET_SMARKETS' not in locals():
    MARKET_SMARKETS = "Smarkets"
if 'MARKET_POLYMARKET_NEW' not in locals():
    MARKET_POLYMARKET_NEW = "Polymarket"
if 'MARKET_KALSHI' not in locals():
    MARKET_KALSHI = "Kalshi"

manual_entry_by_market = {}
if 'Polymarket_new_manual_entry' in locals():
    manual_entry_by_market[MARKET_POLYMARKET_NEW] = Polymarket_new_manual_entry
if 'Kalshi_manual_entry' in locals():
    manual_entry_by_market[MARKET_KALSHI] = Kalshi_manual_entry
if 'Betfair_manual_entry' in locals():
    manual_entry_by_market[MARKET_BETFAIR] = Betfair_manual_entry
if 'FTX_manual_entry' in locals():
    manual_entry_by_market[MARKET_FTX] = FTX_manual_entry
if 'PredictIt_manual_entry' in locals():
    manual_entry_by_market[MARKET_PREDICTIT] = PredictIt_manual_entry
if 'Smarkets_manual_entry' in locals():
    manual_entry_by_market[MARKET_SMARKETS] = Smarkets_manual_entry

if 'SCRAPING_ERRORS_ALWAYS_RECOVER' not in locals():
    SCRAPING_ERRORS_ALWAYS_RECOVER = False

"""
Format should be like:

BOOTSTRAPPED_MARKET_VOLUMES_LAST_QUARTER = {
    MARKET_FTX: 10000,
}
"""
if 'BOOTSTRAPPED_MARKET_VOLUMES_LAST_QUARTER' not in locals():
    BOOTSTRAPPED_MARKET_VOLUMES_LAST_QUARTER = {}

def config_sanity_check():
    # Make sure that the second column (the value that is basically used as an "ID" for the candidate) is consistent across all markets.
    # This is particularly important now because one of the USED_MARKETS will be arbitrarily chosen to represent the csv columns.
    # We want to make sure the behavior is predictable
    for market_1 in USED_MARKETS:
        for market_2 in USED_MARKETS:
            manual_entry_1 = manual_entry_by_market[market_1]
            manual_entry_2 = manual_entry_by_market[market_2]
            for market_1_row, market_2_row in zip(manual_entry_1, manual_entry_2):
                if market_1_row[1] != market_2_row[1]:
                    assert market_1_row[1] == market_2_row[1], (
                        "Inconsistent second column for manual_entry between %s and %s: %s vs %s"
                          % (market_1, market_2, market_1_row[1], market_2_row[1])
                    )
config_sanity_check()

data_file_system = import_module('/python/', 'data_file_system')
render_html = import_module('/python/', 'render_html')

AVERAGE = 'AVERAGE' # Works as a "market" for the purpose of these files
WEIGHTED_AVERAGE = 'WEIGHTED_AVERAGE' # Works as a "market" for the purpose of these files

def get_history_candidate_fields():
    manual_entry = manual_entry_by_market[USED_MARKETS[0]]
    return [entry[1] for entry in manual_entry]

history_data_set = data_file_system.HistoryDataFileSet(
    get_history_candidate_fields(),
    my_root,
    USED_MARKETS + [AVERAGE, WEIGHTED_AVERAGE],
    rewrite_mismatching_headers=True,
)

# Commenting out for production obviously
#history_data_set.test_history()

def history_file_write_for_average(data_counter, unix_time, local_time, odds_data, volume, manual_entry):
    if not SKIP_WRITING_HISTORY:
        history_data_set.write_for_csv_name(AVERAGE, data_counter, unix_time, local_time, odds_data, volume)

def history_file_write_for_weighted_average(data_counter, unix_time, local_time, odds_data, volume, manual_entry):
    if not SKIP_WRITING_HISTORY:
        history_data_set.write_for_csv_name(WEIGHTED_AVERAGE, data_counter, unix_time, local_time, odds_data, volume)

def history_file_read_average():
    return history_data_set.read_for_csv_name(AVERAGE, timedelta(days=7), unix_time)

def history_file_read_weighted_average():
    return history_data_set.read_for_csv_name(WEIGHTED_AVERAGE, timedelta(days=7), unix_time)

#1 ALL errors cause failure. Thought fixed?... examine
#1.1# write data saving so it preserves market columns?
#2# add transparency about volumes
#2.1# are file saves fully working?
#3# add transparency about bid/asks for each candidate?
### finding data_counter, which determines running 4hr/day/week etc

### finding time
if USE_CANNED_TIMESTAMP:
    now = ' 10:08PM EDT on Feb 4, 2021'
    unix_time = 1612494538
    local_time = datetime(2021, 2, 4, 22, 8, 58, 448715)
else:
    now = str(time.strftime('%l:%M%p %Z on %b %d, %Y'))
    unix_time = int(time.time())
    local_time = datetime.now()
logging.debug("now: %s", now)

# Create empty chart file if it doesn't exist.
if not os.path.exists('/python/'+my_root+'/WIN_chart_data'+my_ticker+'.txt'):
    open('/python/'+my_root+'/WIN_chart_data'+my_ticker+'.txt', 'a').close()

if USE_WEIGHTED_AVERAGES:
    data_history = history_file_read_weighted_average()
else:
    data_history = history_file_read_average()

data_counter = data_history.get_next_data_counter()
time_since_start = data_history.get_time_since_start(unix_time)

start_reading_market_data_history = time.time()
QUARTER_YEAR = timedelta(days=int(365.0 / 4))
market_data_history = {
    market: history_data_set.read_for_csv_name(market, QUARTER_YEAR, unix_time)
    for market in USED_MARKETS
}
logging.info("Loading market data history took: %s seconds", time.time() - start_reading_market_data_history)

logging.info("How much csv data we have in memory for data_history: %s", str(data_history.timespan_loaded(unix_time)))
logging.info("How much csv data we have in memory for each market_data_history: %s", {market: str(market_data_history[market].timespan_loaded(unix_time)) for market in market_data_history})

# Want to set them here, but we need them now in pres/Betfarer.py.
# Just assert them here instead I guess, to make sure nothing changed, and so we can easily see that it's the case when working with the code.
# And/or on the off chance it's used for another market, this makes sure it's set properly there as well.
assert len(set(USED_MARKETS)) == len(USED_MARKETS), "Oops, you listed a market more than once in USED_MARKETS"
#assert set(USED_MARKETS) <= {MARKET_BETFAIR, MARKET_PREDICTIT, MARKET_FTX, MARKET_SMARKETS, MARKET_POLYMARKET, MARKET_POLYMARKET_CLOB}, "Oops, you have an invalid market in USED_MARKETS"
#assert len(USED_MARKETS) > 1, "We don't support having only one market, just yet"

num_markets = len(USED_MARKETS)

CIRCUIT_BREAKER_LARGE_SPREADS = False
CIRCUIT_BREAKER_LARGE_SPREADS_THRESHOLD = .2
# We should alter handle the above with public warnings. As of now, gets in the way too much
CIRCUIT_BREAKER_NEGATIVE_SPREAD = True
CIRCUIT_BREAKER_ODDS_SUMMED = True
CIRCUIT_BREAKER_ODDS_SUMMED_THRESHOLD = .2

def scrape_betfair():
    scrape_failed = False

    ### Scraping raw
    try:
        if USE_CACHED_RESPONSES:
            Betfair_WINNER_raw = open('cached/Betfair_WINNER_raw', 'r').read()
        else:
            headers = {
            "Cookie": "bfsd=ts=$(date +%s)000|st=p; betexPtk=betexCurrency%3DUSD%7EbetexTimeZone%3DAmerica%2FNew_York%7EbetexRegion%3DGBR%7EbetexLocale%3Den"
            }
            response = requests.get(my_Betfair_URL, headers=headers)
            Betfair_WINNER_raw = response.content
            if SET_CACHED_RESPONSES:
                open('cached/Betfair_WINNER_raw', 'w').write(Betfair_WINNER_raw)

        # TODO - try to put fewer capital letter things in the URL
        Betfair_WINNER_json = json.loads(Betfair_WINNER_raw)

        # Some sanity checks. If these fail, maybe something else is not as we expect.
        assert Betfair_WINNER_json['currencyCode'].lower() == "usd", "Betfair: currencyCode unexpectedly " + jl['currencyCode']
        assert len(Betfair_WINNER_json['eventTypes']) == 1, "Betfair: unexpected multiple eventTypes. inspect json to make sense of it."
        assert len(Betfair_WINNER_json['eventTypes'][0]['eventNodes']) == 1, "Betfair: unexpected multiple eventNodes. inspect json to make sense of it."
        assert len(Betfair_WINNER_json['eventTypes'][0]['eventNodes'][0]['marketNodes']) == 1, "Betfair: unexpected multiple marketNodes. inspect json to make sense of it."

        Betfair_runners = Betfair_WINNER_json['eventTypes'][0]['eventNodes'][0]['marketNodes'][0]['runners']
        Betfair_exchanges_by_runner_name = {runner['description']['runnerName']: runner['exchange'] for runner in Betfair_runners}
        betfair_volume = float(Betfair_WINNER_json['eventTypes'][0]['eventNodes'][0]['marketNodes'][0]['state']['totalMatched'])

        logging.debug("If you're just creating a new race, you can use this to start off Betfair_manual_entry:")
        logging.debug("\n%s", pformat([
            tuple([repr(runner['description']['runnerName'])] * 2 + [""])
            for runner in Betfair_runners
        ]))

        logging.info("Betfair scraped")
        sys.stdout.flush()
    except Exception,e:
        warning_message = "Error scraping Betfair (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)
        logging.warning(full_stack())
        sys.stdout.flush()

        # Send this out even if we crash (and thus send another email). We
        # ought to get a stack trace of the scrape error. If this is too many
        # emails, we can refactor it later.
        warning_email(warning_message, full_stack())

        Betfair_exchanges_by_runner_name = {}
        betfair_volume = 0

    return scrape_failed, Betfair_exchanges_by_runner_name, betfair_volume

def scrape_predictit():
    scrape_failed = False

    try:
        if USE_CACHED_RESPONSES:
            PredictIt_WINNER_raw = open('cached/PredictIt_WINNER_raw', 'r').read()
        else:
            headers = {
                "Cookie": "bfsd=ts=$(date +%s)000|st=p; betexPtk=betexCurrency%3DUSD%7EbetexTimeZone%3DAmerica%2FNew_York%7EbetexRegion%3DGBR%7EbetexLocale%3Den"
            }
            response = requests.get(my_PredictIt_URL, headers=headers)
            PredictIt_WINNER_raw = response.content
            if SET_CACHED_RESPONSES:
                open('cached/PredictIt_WINNER_raw', 'w').write(PredictIt_WINNER_raw)

        PredictIt_WINNER_raw = unicode(PredictIt_WINNER_raw.decode('utf-8'))

        parsable_PredictIt_WINNER_raw = PredictIt_WINNER_raw.replace('"', '')
        parsable_PredictIt_WINNER_raw = ''.join(parsable_PredictIt_WINNER_raw.split())
        logging.info("PredictIt scraped")
        sys.stdout.flush()

        PredictIt_volume_URL = str(my_PredictIt_URL) + "/Contracts/Stats"
        PredictIt_volume_URL = PredictIt_volume_URL.replace("marketdata/markets","Market")
        def getTotalOpenInterest(url):
            if USE_CACHED_RESPONSES:
                content = open('cached/PredictItTotalOpenInterest', 'r').read()
                json_data = json.loads(content)
            else:
                resp = requests.get(url)
                json_data = json.loads(resp.content)
                if SET_CACHED_RESPONSES:
                    open('cached/PredictItTotalOpenInterest', 'w').write(resp.content)
            costs = []
            if isinstance(json_data, unicode) or isinstance(json_data, str):
                raise FTXUniversalException('Error getting PredictIt Open Interest: ' + repr(json_data))
            for foo in json_data:
                costs.append(foo['openInterest'])
            total = sum(costs)
            return total
        predictit_volume = getTotalOpenInterest(PredictIt_volume_URL)
        #adjusting for peculiarities of Pred volume reporting
        predictit_volume = predictit_volume # / (len(PredictIt_manual_entry) / 2)
    except Exception,e:
        warning_message = "Error scraping PredictIt (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)
        logging.warning(full_stack())
        sys.stdout.flush()

        # Send this out even if we crash (and thus send another email). We
        # ought to get a stack trace of the scrape error. If this is too many
        # emails, we can refactor it later.
        warning_email(warning_message, full_stack())

        parsable_PredictIt_WINNER_raw = ''
        predictit_volume = 0

    return scrape_failed, parsable_PredictIt_WINNER_raw, predictit_volume

def scrape_ftx():
    scrape_failed = False

    try:
        def getBidAsk(cand_FULL_name):
            url = my_FTX_URL + cand_FULL_name
            logging.debug(url)
            if USE_CACHED_RESPONSES:
                content = open('cached/FTX_getBidAsk_' + cand_FULL_name, 'r').read()
                my_dict = json.loads(content)
            else:
                resp = requests.get(url)
                my_dict = json.loads(resp.content)
                if SET_CACHED_RESPONSES:
                    open('cached/FTX_getBidAsk_' + cand_FULL_name, 'w').write(resp.content)
            if "error" in my_dict:
                logging.warning(u"Error getting FTX odds for " + repr(cand_FULL_name) + u": " + repr(my_dict['error']))
                return

            result = {
                'bid': my_dict['result']['bid'],
                'ask': my_dict['result']['ask'],
            }
            logging.debug(result)
            sys.stdout.flush()
            return result

        def getOpenInterest(cand_FULL_name):
            url = "https://ftx.com/api/futures/" + cand_FULL_name + "/stats"
            logging.debug(url)
            if USE_CACHED_RESPONSES:
                content = open('cached/FTXgetOpenInterest_' + cand_FULL_name, 'r').read()
                my_dict = json.loads(content)
            else:
                resp = requests.get(url)
                my_dict = json.loads(resp.content)
                if SET_CACHED_RESPONSES:
                    open('cached/FTXgetOpenInterest_' + cand_FULL_name, 'w').write(resp.content)
            if "error" in my_dict:
                logging.warning("Error getting FTX volume for " + cand_FULL_name + ": " + my_dict['error'])
                return

            obtained_volume = my_dict["result"]["openInterest"]
            logging.debug("FTX_volume for candidate x: %s", obtained_volume)
            return obtained_volume

        ftx_scraped_data = {}
        for (cand_FULL_name, _, _) in FTX_manual_entry:
            if cand_FULL_name:
                bid_ask = getBidAsk(cand_FULL_name)
                volume = getOpenInterest(cand_FULL_name)
                if volume is None or bid_ask is None:
                    # Omit both if either of these is missing. This will keep the volume more tied to the candidates presented.
                    continue
                ftx_scraped_data[cand_FULL_name] = {
                    'bid': bid_ask['bid'],
                    'ask': bid_ask['ask'],
                    'volume': volume,
                }

        if len(ftx_scraped_data) == 0:
            # NOTE: further down the process, we have a warning email for any markets with zero candidate data found
            logging.warning("No candidates succeeded for FTX. (Either bid/ask, volume or both failed) (will try to recover with other markets)")

        logging.info("FTX scraped")
        sys.stdout.flush()
    except Exception,e:
        warning_message = "Error scraping FTX (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)
        logging.warning(full_stack())
        sys.stdout.flush()

        # Send this out even if we crash (and thus send another email). We
        # ought to get a stack trace of the scrape error. If this is too many
        # emails, we can refactor it later.
        warning_email(warning_message, full_stack())

        ftx_scraped_data = {}

    return scrape_failed, ftx_scraped_data

def scrape_smarkets():
    scrape_failed = False

    # Scraping Smarkets
    try:

        # This URL seems to cover all races on Smarkets. Otherwise we would have a my_Smarkets_URL specific to presidency.
        url = "https://api.smarkets.com/oddsfeed.xml.gz?affiliate_key=Fg41peK2pkvrTyFo"

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36",
        }

        SMARKETS_TEMP_PATH = "/python/temp"
        SMARKETS_GZ_FNAME = os.path.join(SMARKETS_TEMP_PATH, "smarkets-oddsfeed.xml.gz")
        SMARKETS_XML_FNAME = os.path.join(SMARKETS_TEMP_PATH, "smarkets-oddsfeed.xml")
        SMARKETS_CACHE_GZ_FNAME = "/python/cached/smarkets-oddsfeed.xml.gz"

        # TODO - We could possibly just requests.get the gz file,
        # put the body into a StringIO "file-like" object, send that
        # to gzip.open, and parse the xml in-memory. But,
        # let's not mess with that until after the election.

        def smarkets_make_dir():
            if not os.path.exists(SMARKETS_TEMP_PATH):
                os.mkdir(SMARKETS_TEMP_PATH)

        def smarkets_get_cached_gz():
            shutil.copy(SMARKETS_CACHE_GZ_FNAME, SMARKETS_GZ_FNAME)

        def smarkets_set_cached_gz():
            shutil.copy(SMARKETS_GZ_FNAME, SMARKETS_CACHE_GZ_FNAME)

        def smarkets_get_gz(url):
            r = requests.get(url=url, headers=headers, verify=False)
            with open(SMARKETS_GZ_FNAME, "wb") as gz:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        gz.write(chunk)
            logging.debug("Smarkets downloaded, saving to %s", SMARKETS_GZ_FNAME)

        def smarkets_get_gunzipped(gz_fname):
            logging.debug("gunzipping file")
            with gzip.open(gz_fname, 'rb') as f_in:
                with open(SMARKETS_XML_FNAME, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            logging.debug("Smarkets gunzipped")

        def smarkets_parse_xml():
            logging.debug("parsing smarkets xml")
            for parse_event, element in ET.iterparse(SMARKETS_XML_FNAME):
                if parse_event == "end" and element.tag == "event" and element.attrib.get('name').lower() == my_Smarkets_market_name.lower():
                    # Found the right tag. Don't care about the rest of the file.
                    # This saves a ton of time compared to a full tree parse
                    return element.find('market')
            raise FTXUniversalException("No event called '" + my_Smarkets_market_name + "' found in " + SMARKETS_XML_FNAME + " (including with case insensitive comparison)")

        smarkets_make_dir()
        if USE_CACHED_RESPONSES:
            smarkets_get_cached_gz()
        else:
            smarkets_get_gz(url=url)
            if SET_CACHED_RESPONSES:
                smarkets_set_cached_gz()
        smarkets_get_gunzipped(gz_fname=SMARKETS_GZ_FNAME)
        smarkets_market_element = smarkets_parse_xml()

        smarkets_volume = float(smarkets_market_element.attrib['traded_volume'])
        smarkets_contracts_by_name = {
            element.attrib['name']: element
            for element
            in smarkets_market_element.findall("./contract")
        }

        logging.info("Smarkets scraped")
        
    except Exception,e:
        warning_message = "Error scraping Smarkets (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)
        logging.warning(full_stack())
        sys.stdout.flush()

        # Send this out even if we crash (and thus send another email). We
        # ought to get a stack trace of the scrape error. If this is too many
        # emails, we can refactor it later.
        warning_email(warning_message, full_stack())

        smarkets_volume = 0
        smarkets_contracts_by_name = {}

    return scrape_failed, smarkets_volume, smarkets_contracts_by_name

def scrape_polymarket_new():
    scrape_failed = False

    # Scraping Polymarket (Direct, Clob API and Gamma API)
    polymarket_contracts_by_id = {}
    try:

        # Extract PRICES using Polymarket Clob API
        def get_json(polymarket_clob_url):
            clob_api_raw = requests.get(polymarket_clob_url, verify=False,timeout=5).content
            resp_data = json.loads(clob_api_raw)
            return resp_data
        
        pm_ids = set([])
        for (cand_FULL_name, _, _) in Polymarket_new_manual_entry:
            if cand_FULL_name:
                (pm_id, _) = cand_FULL_name
                # We'll get mixed up if we're not on the same page about whether this is an int or a string
                assert isinstance(pm_id, int), "Polymarket ids should be integers, not strings"
                pm_ids.add(pm_id)
        polymarket_ids = [str(pm_id) for pm_id in pm_ids]
        polymarket_url = my_Polymarket_URL
        if USE_CACHED_RESPONSES:
            polymarket_raw = open('cached/polymarket_raw', 'r').read()
        else:
            polymarket_raw = requests.get(polymarket_url, verify=False)
            if SET_CACHED_RESPONSES:
                open('cached/polymarket_raw', 'w').write(polymarket_raw)
        html_content = polymarket_raw.text

        # Find the script tag with id="__NEXT_DATA__" using regex
        script_tag_match = re.search(r'<script\s+id="__NEXT_DATA__"\s+type="application/json"\s+crossorigin="anonymous">(.+?)</script>', html_content)

        if script_tag_match:
            # Extract JSON data from the matched script tag
            json_data = json.loads(script_tag_match.group(1))

            event_id = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['id']
            # Extract VOLUME using direct scrape
            polymarket_volume_direct = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['volume']

            # Extract content for each ID in the list
            for id_to_extract in pm_ids:
                for market in json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['markets']:
                    if market['id'] == str(id_to_extract):

                        ### UPDATED THIS PART as of May 24, 2024 ###
                        yes_token_id = market['clobTokenIds'][0]
                        no_token_id = market['clobTokenIds'][1]

                        # Extract BID & ASK PRICES using Polymarket Clob API
                        price_url_base = 'https://clob.polymarket.com/price'
                        # First outcome
                        yes_bid_query_fields = '?side=buy&token_id={}'.format(str(yes_token_id))
                        yes_ask_query_fields = '?side=sell&token_id={}'.format(str(yes_token_id))
                        yes_bid_price = get_json(price_url_base + yes_bid_query_fields)
                        yes_ask_price = get_json(price_url_base + yes_ask_query_fields)

                        # Second outcome
                        no_bid_query_fields = '?side=buy&token_id={}'.format(str(no_token_id))
                        no_ask_query_fields = '?side=sell&token_id={}'.format(str(no_token_id))
                        no_bid_price = get_json(price_url_base + no_bid_query_fields)
                        no_ask_price = get_json(price_url_base + no_ask_query_fields)

                        market['outcomesPrice'] = [{'outcome': outcome, 'bid': None, 'ask': None} for outcome in market['outcomes']]                        
                        # Add 'bid' and 'ask' fields to the market dictionary
                        market['outcomesPrice'][0]['bid'] = yes_bid_price
                        market['outcomesPrice'][0]['ask'] = yes_ask_price
                        market['outcomesPrice'][1]['bid'] = no_bid_price
                        market['outcomesPrice'][1]['ask'] = no_ask_price
                        polymarket_contracts_by_id[id_to_extract] = market
                        break
                        #### END OF UPDATED PART ###
                    
        # Extract VOLUME using gamma-api.polymarket.com
        gamma_response = requests.get("https://gamma-api.polymarket.com/events/" + event_id, verify=False)
        if gamma_response.status_code == 200:
            gamma_api_data = gamma_response.content
            try:
                gamma_api_data = json.loads(gamma_api_data)
                polymarket_volume_gamma = gamma_api_data.get('volume', 0)  # Default to 0 if 'volume' key is not present
                polymarket_volume = polymarket_volume_gamma
            except ValueError:
                polymarket_volume = polymarket_volume_direct
        else:
            # Use polymarket_volume_direct as fallback if the response is not successful
            polymarket_volume = polymarket_volume_direct

        # Just check that we got all of the ids we asked for:
        found_ids = set(polymarket_contracts_by_id.keys())
        if pm_ids - found_ids != set(): # Not every expected ID was found
            logging.warning("Polymarket API did not return these expected ids: " + ', '.join(map(str, (pm_ids - found_ids))))
        if pm_ids - found_ids == pm_ids: # Not *any* expected ID was found
            # NOTE: further down the process, we have a warning email for any markets with zero candidate data found
            logging.warning("Polymarket API did not return any expected ids. (will try to recover with other markets)")

    except Exception as e:
        warning_message = "Error scraping Polymarket (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)
        logging.warning(full_stack())
        sys.stdout.flush()

        # Send this out even if we crash (and thus send another email). We
        # ought to get a stack trace of the scrape error. If this is too many
        # emails, we can refactor it later.
        warning_email(warning_message, full_stack())

        polymarket_contracts_by_id = {}
        polymarket_volume = 0

    return scrape_failed, polymarket_contracts_by_id, polymarket_volume

def scrape_kalshi():
    scrape_failed = False

    try:
        if USE_CACHED_RESPONSES:
            content = open('cached/Kalshi', 'r').read()
            json_data = json.loads(content)
        else:
            resp = requests.get("https://trading-api.kalshi.com/v1/events/" + Kalshi_ticker)
            json_data = json.loads(resp.content)
            if SET_CACHED_RESPONSES:
                open('cached/Kalshi', 'w').write(resp.content)

        candidate_data_by_ticker = {candidate['ticker_name']: candidate for candidate in json_data['event']['markets']}

        kalshi_scraped_data = {}
        for (cand_FULL_name, _, _) in Kalshi_manual_entry:
            if cand_FULL_name:
                entry = candidate_data_by_ticker[cand_FULL_name]
                kalshi_scraped_data[cand_FULL_name] = {
                    'bid': entry['yes_bid'],
                    'ask': entry['yes_ask'],
                    'volume': entry['volume'],

                    # Could hardcode something here for "status": "finalized", avoid annoying problems we
                    # sometimes have
                    "status": entry['status'],
                }

    except Exception,e:
        warning_message = "Error scraping Kalshi (may try to recover with other markets)"

        scrape_failed = True

        logging.warning(warning_message)
        logging.warning(full_stack())
        sys.stdout.flush()

        # Send this out even if we crash (and thus send another email). We
        # ought to get a stack trace of the scrape error. If this is too many
        # emails, we can refactor it later.
        warning_email(warning_message, full_stack())

        kalshi_scraped_data = {}

    return scrape_failed, kalshi_scraped_data

###### Betfair ######
def parse_betfair_odds(Betfair_exchanges_by_runner_name, cand_FULL_name):
    if cand_FULL_name in Betfair_exchanges_by_runner_name:
        exchanges_for_runner = Betfair_exchanges_by_runner_name[cand_FULL_name]

        availableToLay = exchanges_for_runner.get('availableToLay', [])
        availableToBack = exchanges_for_runner.get('availableToBack', [])

        # makes sure there are sellers and executes normally if so, otherwise sets to 100
        if len(availableToBack) == 0:
            Candidate_ask = 1
            logging.debug("zero sellers for the following candidate")
            sys.stdout.flush()
        else:
            # Pull out the ask price
            Candidate_ask = 1.0 / availableToBack[0]['price']

        if len(availableToLay) == 0:
            Candidate_bid = 0
            logging.debug("zero bidders for the following candidate")
        else:
            # Pull out the bid price
            Candidate_bid = 1.0 / availableToLay[0]['price']

        # If low liquidity, go with bid. Else, take avg of bid and ask to get market value estimate
        if Candidate_ask - Candidate_bid > .1:
            Candidate_odds = Candidate_bid
            logging.debug("Low liquidity for following candidate! Ask used as estimate.")
            sys.stdout.flush()
        else:
            Candidate_odds = (Candidate_bid+Candidate_ask)/2

        if Candidate_ask == 1 and Candidate_bid > .6:
            # Presumably only hit this condition if there were no asks and we set it to 1 ourselves.
            # If there's some bid above 1%, we assume the candidate won (.999). Otherwise, we
            # assume the candidate is basically at 0%.
            Candidate_odds = .999

        if Candidate_bid < 0.01 and Candidate_ask > .4:
            Candidate_odds = .0001
        if Candidate_bid < 0.01 and Candidate_ask > .03:
            Candidate_odds = Candidate_bid

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }

###### Smarkets ######
def parse_smarkets_odds(smarkets_contracts_by_name, cand_FULL_name):
    if cand_FULL_name in smarkets_contracts_by_name:

        def get_smarkets_value(bid_or_ask, fallback):
            try:
                percent = smarkets_contracts_by_name[cand_FULL_name].find(bid_or_ask).attrib['percent']
            except Exception,e:
                logging.debug("%s does NOT have a %s for Smarkets contract. Falling back to %s", cand_FULL_name, bid_or_ask, fallback)
                percent = fallback
            return percent

        # Pull out the bid and ask prices
        Candidate_bid = float(get_smarkets_value("./bids/price", 0)) / 100
        Candidate_ask = float(get_smarkets_value("./offers/price", 100)) / 100

        # If low liquidity, go with bid. Else, take avg of bid and ask to get market value estimate
        if Candidate_ask - Candidate_bid > .12:
            Candidate_odds = Candidate_bid
            logging.debug("%s: has low liquidity! Ask used as estimate.", cand_FULL_name)
            sys.stdout.flush()
        else:
            Candidate_odds = (Candidate_bid+Candidate_ask)/2

        if Candidate_ask == 1 and Candidate_bid > .6:
            # Presumably only hit this condition if there were no asks and we set it to 1 ourselves.
            # If there's some bid above 1%, we assume the candidate won (.999). Otherwise, we
            # assume the candidate is basically at 0%.
            Candidate_odds = .999

        if Candidate_bid < 0.01 and Candidate_ask > .4:
            Candidate_odds = .0001
        if Candidate_bid < 0.01 and Candidate_ask > .03:
            Candidate_odds = Candidate_bid

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }

###### PredictIt ######
def parse_predictit_odds(parsable_PredictIt_WINNER_raw, cand_FULL_name):
    search_name = u"shortName:" + unicode(cand_FULL_name) + u",status"
    logging.debug(search_name)
    if search_name in parsable_PredictIt_WINNER_raw:
        Candidate_raw_step_1 = parsable_PredictIt_WINNER_raw.split(search_name)[1]
        #print Candidate_raw_step_1
        Candidate_raw_step_2 = Candidate_raw_step_1.split("Image")[0]
        #print Candidate_raw_step_2
        # find bid
        Candidate_raw_step_3 = Candidate_raw_step_2.split("bestSellYesCost:")[1]
        logging.debug(Candidate_raw_step_3)
        Candidate_raw_step_4 = Candidate_raw_step_3.split(",bestSellNoCost:")[0]
        logging.debug(Candidate_raw_step_4)
        if Candidate_raw_step_4 == "null":
            # find last trade (final, settled) price
            Candidate_raw_step_LT = Candidate_raw_step_2.split("lastTradePrice:")[1]
            Candidate_raw_step_4 = Candidate_raw_step_LT.split(",bestBuyYesCost")[0]
            Candidate_raw_step_4 = 0 # Copied from Predictit_Machine.py. Don't know why, but you said it works!
            Candidate_bid = float(Candidate_raw_step_4)
        else:
            Candidate_bid = float(Candidate_raw_step_4)
        # find ask
        Candidate_raw_ASK_step_3 = Candidate_raw_step_2.split("bestBuyYesCost:")[1]
        Candidate_raw_ASK_step_4 = Candidate_raw_ASK_step_3.split(",bestBuyNoCost:")[0]
        if Candidate_raw_ASK_step_4 == "null":
            Candidate_ask = Candidate_odds = float(Candidate_raw_step_4)
        else:
            Candidate_ask = float(Candidate_raw_ASK_step_4)
        # If low liquidity, go with bid. Else, take avg of bid and ask to get market value estimate
        if Candidate_ask - Candidate_bid > .1:
            Candidate_odds = Candidate_bid
        else:
            Candidate_odds = (Candidate_bid+Candidate_ask)/2

        if Candidate_ask == 1 and Candidate_bid > .6:
            # Presumably only hit this condition if there were no asks and we set it to 1 ourselves.
            # If there's some bid above 1%, we assume the candidate won (.999). Otherwise, we
            # assume the candidate is basically at 0%.
            Candidate_odds = .999

        if Candidate_bid < 0.001:
            Candidate_odds = .0001

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }

###### FTX ######
def parse_ftx_odds(ftx_scraped_data, cand_FULL_name):
    logging.debug("FTX:")
    sys.stdout.flush()

    if cand_FULL_name in ftx_scraped_data:
        logging.debug("candidate contract listed")
        # Get Ask

        Candidate_ask = ftx_scraped_data[cand_FULL_name]['ask']
        logging.debug(("Candidate_ask: ",Candidate_ask))
        #Get Bid
        Candidate_bid = ftx_scraped_data[cand_FULL_name]['bid']
        logging.debug(("Candidate_bid: ",Candidate_bid))
        sys.stdout.flush()

        # If low liquidity, go with bid. Else, take avg of bid and ask to get market value estimate
        if Candidate_bid is None:
            logging.debug("cand set to zero due to no bids")
            Candidate_bid = .0001
            Candidate_ask = .0001
            Candidate_odds = .0001
        else:
            if Candidate_ask - Candidate_bid > .1:
                Candidate_odds = Candidate_bid
            else:
                #99% of the time, this is the used line:
                Candidate_odds = (Candidate_bid+Candidate_ask)/2
            if Candidate_ask == 1 and Candidate_bid > .6:
                # Presumably only hit this condition if there were no asks and we set it to 1 ourselves.
                # If there's some bid above 1%, we assume the candidate won (.999). Otherwise, we
                # assume the candidate is basically at 0%.
                Candidate_odds = .999

            if Candidate_bid < 0.001:
                Candidate_odds = .0001

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }

###### Polymarket NEW ######
def parse_polymarket_new_odds(polymarket_contracts_by_id, cand_FULL_name):
    # In the case of Polymarket Clob API, we will denote skipping a candidate with an empty string or a None
    pm_id, pm_outcome = cand_FULL_name
    ### UPDATED THIS PART as of May 24, 2024 ###
    if pm_id in polymarket_contracts_by_id and pm_outcome in polymarket_contracts_by_id[pm_id]['outcomes']:
        outcome_index = polymarket_contracts_by_id[pm_id]['outcomes'].index(pm_outcome)

        # TODO - handle odd cases like low liquidity like the other markets?
        Candidate_ask = float(polymarket_contracts_by_id[pm_id]['outcomesPrice'][outcome_index]['ask']['price'])
        Candidate_bid = float(polymarket_contracts_by_id[pm_id]['outcomesPrice'][outcome_index]['bid']['price'])
        Candidate_odds = (Candidate_bid+Candidate_ask)/2

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }
    ### END OF UPDATED PART ###

###### Kalshi ######
def parse_kalshi_odds(kalshi_scraped_data, cand_FULL_name):
    logging.debug("Kalshi:")
    sys.stdout.flush()

    if cand_FULL_name in kalshi_scraped_data:
        logging.debug("candidate contract listed")

        # Get Ask
        Candidate_ask = kalshi_scraped_data[cand_FULL_name]['ask'] / 100
        logging.debug(("Candidate_ask: ",Candidate_ask))
        #Get Bid
        Candidate_bid = kalshi_scraped_data[cand_FULL_name]['bid'] / 100
        logging.debug(("Candidate_bid: ",Candidate_bid))
        sys.stdout.flush()

        # If low liquidity, go with bid. Else, take avg of bid and ask to get market value estimate
        # For now, unlike FTX, we're assuming that bid and ask will never be `None` at this point

        if Candidate_ask - Candidate_bid > .1:
            Candidate_odds = Candidate_bid
        else:
            #99% of the time, this is the used line:
            Candidate_odds = (Candidate_bid+Candidate_ask)/2
        if Candidate_ask == 1 and Candidate_bid > .6:
            # Presumably only hit this condition if there were no asks and we set it to 1 ourselves.
            # If there's some bid above 1%, we assume the candidate won (.999). Otherwise, we
            # assume the candidate is basically at 0%.
            Candidate_odds = .999

        if Candidate_bid < 0.001:
            Candidate_odds = .0001

        return {
            'Candidate_found': True,
            'Candidate_bid': Candidate_bid,
            'Candidate_ask': Candidate_ask,
            'Candidate_odds': Candidate_odds,
        }
    else:
        return {
            'Candidate_found': False,
        }


### Betfair ###
def parse_betfair_volume(betfair_volume):
    return betfair_volume

### Smarkets ###
def parse_smarkets_volume(smarkets_volume):
    return smarkets_volume

### PredictIt ###
def parse_predictit_volume(predictit_volume):
    return predictit_volume

### FTX ###
def parse_ftx_volume(ftx_scraped_data):
    volume = 0
    for x in range (0, len(FTX_manual_entry)): ###~!!! MUST CHANGE PRED TO FTX
        if FTX_manual_entry[x][0] in ftx_scraped_data:
            volume += ftx_scraped_data[FTX_manual_entry[x][0]]['volume']
    return volume

### Polymarket NEW ###
def parse_polymarket_new_volume(polymarket_volume):
    return polymarket_volume

### Kalshi ###
def parse_kalshi_volume(kalshi_scraped_data):
    volume = 0
    for x in range (0, len(Kalshi_manual_entry)):
        if Kalshi_manual_entry[x][0] in kalshi_scraped_data:
            volume += kalshi_scraped_data[Kalshi_manual_entry[x][0]]['volume']
    return volume

# "recent" is in regard to trying to recover from failed markets.
def has_recent_data(history):
    SCRAPE_RECOVERY_THRESHOLD = timedelta(seconds=0, minutes=0, hours=8, days=0)
    time_since_last_data = history.get_time_since_last_data(unix_time)
    return (
        time_since_last_data is not None and
        time_since_last_data <= SCRAPE_RECOVERY_THRESHOLD
    )

scrape_failures = {}

if MARKET_BETFAIR in USED_MARKETS:
    scrape_failures[MARKET_BETFAIR], Betfair_exchanges_by_runner_name, betfair_volume = scrape_betfair()
if MARKET_PREDICTIT in USED_MARKETS:
    scrape_failures[MARKET_PREDICTIT], parsable_PredictIt_WINNER_raw, predictit_volume = scrape_predictit()
if MARKET_FTX in USED_MARKETS:
    scrape_failures[MARKET_FTX], ftx_scraped_data = scrape_ftx()
if MARKET_SMARKETS in USED_MARKETS:
    scrape_failures[MARKET_SMARKETS], smarkets_volume, smarkets_contracts_by_name = scrape_smarkets()
if MARKET_POLYMARKET_NEW in USED_MARKETS:
    scrape_failures[MARKET_POLYMARKET_NEW], polymarket_contracts_by_id, polymarket_volume = scrape_polymarket_new()
if MARKET_KALSHI in USED_MARKETS:
    scrape_failures[MARKET_KALSHI], kalshi_scraped_data = scrape_kalshi()

# ex:
# scrape_failures = {MARKET_BETFAIR: True, MARKET_SMARKETS: False}
# scrape_failed_markets = [MARKET_BETFAIR]
scrape_failed_markets = [
    market
    for market, market_failed
    in scrape_failures.items()
    if market_failed
]

# In the case of scrape error(s), we want to try to recover without the failed markets if it's been a long time since
# we had a successful scrape and data write for the errored market (i.e. nothing non-blank in that market's csv).
#
# This means that if a market is down for a long time, we'll fail to generate the page for a while. After that, we will
# attempt to recover and generate the page without the down market. Assuming that works, it will write blank data to
# the csv. Thus, in the subsequent run, there will still be no new non-blank data written to its csv, and we will again
# recover without that market.

if scrape_failed_markets and not SCRAPING_ERRORS_ALWAYS_RECOVER:

    # Look for "unrecoverable" markets - failed, but still have recent non-blank data
    unrecoverable_markets = []
    for market in scrape_failed_markets:
        if has_recent_data(market_data_history[market]):
            logging.debug("We have scrape errors for %s. It has some recent successful scrapes, so we won't be recovering without it yet.", market)
            unrecoverable_markets.append(market)

    if any(unrecoverable_markets):
        raise FTXUniversalException("Error scraping market(s): {markets}".format(markets=scrape_failed_markets))


def get_corrected_market_value(volumes):
    """
    Given a lot of adjacent volume values, find what is more likely a valid
    value by removing 0s (invalid prima facie) and then take something close to
    the median to remove other big outliers.
    """
    nonzero_volumes = [vol for vol in volumes if vol]

    # Everything came up 0! (or maybe `None`)
    if not nonzero_volumes:
        return None

    # Return something close to the median
    return sorted(nonzero_volumes)[int(len(nonzero_volumes)/2)]

### PARSING ODDS

# NOTE
# might not even need all of these parameters
# dummy means "record the data into the log or not". only want to do it once per "scrape"
# Button - name variable or something

def program(dummy,diff_time_delay,button,html_title):
    global data_counter
    global formatted_WIN_chart_data
    global finalwinner_odds_tuples
    # What comes straight from the market's server. Used for writing to history, and
    # for finding corrected_market_volumes
    market_volumes = {}

    # The median(-ish) of the most recent market volumes in history and the
    # current live value. Tries to avoids crazy values coming from the market's
    # servers. Used for display and calculations.
    corrected_market_volumes = {}

    # The difference between the corrected market volumes and what we find in the CSVs
    # from about a quarter year ago (similarly corrected for crazines) or the
    # BOOTSTRAPPED_MARKET_VOLUMES_LAST_QUARTER
    quarterly_market_volumes = {}

    # NOTE - winner data for each market, before averaging it out and stuff
    finalwinner_odds_tuples = None

    # Bid and ask for each user per each market, normalized for normalized markets
    bid_ask_for_users_by_market_normalized = None

    ### RUN FOR EACH MARKET
    for current_market_index, current_market in enumerate(USED_MARKETS):
        logging.debug("Market: " + current_market)

        manual_entry = manual_entry_by_market[current_market]
        CAND_dict = {}

        sys.stdout.flush()

        # Use the scraped data to grab the ask/bid/odds/etc for the given candidate
        # (at least this is the ideal case; FTX still scrapes in the "parse" function as of this writing)
        def oddsfinder(current_contract_index, cand_FULL_name, cand_last_name):
            logging.debug("oddsfinder for " + current_market + " " + str(cand_FULL_name))
            sys.stdout.flush()
            if cand_FULL_name:
                if current_market == MARKET_BETFAIR:
                    Candidate_parsed_data = parse_betfair_odds(Betfair_exchanges_by_runner_name, cand_FULL_name)

                if current_market == MARKET_SMARKETS:
                    Candidate_parsed_data = parse_smarkets_odds(smarkets_contracts_by_name, cand_FULL_name)

                if current_market == MARKET_PREDICTIT:
                    Candidate_parsed_data = parse_predictit_odds(parsable_PredictIt_WINNER_raw, cand_FULL_name)

                if current_market == MARKET_FTX:
                    Candidate_parsed_data = parse_ftx_odds(ftx_scraped_data, cand_FULL_name)

                if current_market == MARKET_POLYMARKET_NEW:
                    Candidate_parsed_data = parse_polymarket_new_odds(polymarket_contracts_by_id, cand_FULL_name)

                if current_market == MARKET_KALSHI:
                    Candidate_parsed_data = parse_kalshi_odds(kalshi_scraped_data, cand_FULL_name)

                if Candidate_parsed_data['Candidate_found']:
                    CAND_dict[cand_last_name] = {}

                    # automatically handles binary markets if user makes both cand_FULL_names the SAME:
                    if manual_entry[0][0] == cand_FULL_name and current_contract_index >= 1:
                        logging.info("Binary contract detected! Taking 1 - odds")
                        # NOTE - ask and bid are swapped here given that we're flipping the probability over
                        CAND_dict[cand_last_name]['bid'] = 1 - Candidate_parsed_data['Candidate_ask']
                        CAND_dict[cand_last_name]['ask'] = 1 - Candidate_parsed_data['Candidate_bid']
                        CAND_dict[cand_last_name]['odds'] = 1 - Candidate_parsed_data['Candidate_odds']
                    else:
                        CAND_dict[cand_last_name]['bid'] = Candidate_parsed_data['Candidate_bid']
                        CAND_dict[cand_last_name]['ask'] = Candidate_parsed_data['Candidate_ask']
                        CAND_dict[cand_last_name]['odds'] = Candidate_parsed_data['Candidate_odds']

                    logging.info("%s %s bid / ask / odds: ", current_market, cand_FULL_name)

                    logging.info(CAND_dict[cand_last_name]['bid'])
                    logging.info(CAND_dict[cand_last_name]['ask'])
                    logging.info(CAND_dict[cand_last_name]['odds'])
                else:
                    logging.info("bid / ask / odds NOT FOUND for '%s' on %s", manual_entry[current_contract_index][1], current_market)
            else:
                logging.info("SKIPPING '%s' on %s", manual_entry[current_contract_index][1], current_market)

            sys.stdout.flush()

        # NOTE - Finding Volume. probably coded well
        # For purpose of: adjusted averages (my task), and hover info on site

        # Find VOLUME from the market's server. This is the raw value we'll write to the
        # csv. We'll use corrected_market_volumes for display and calculating
        # weights, etc.
        if current_market == MARKET_BETFAIR:
            market_volumes[MARKET_BETFAIR] =  parse_betfair_volume(betfair_volume)

        if current_market == MARKET_SMARKETS:
            market_volumes[MARKET_SMARKETS] = parse_smarkets_volume(smarkets_volume)

        if current_market == MARKET_PREDICTIT:
            market_volumes[MARKET_PREDICTIT] = parse_predictit_volume(predictit_volume)

        if current_market == MARKET_FTX:
            market_volumes[MARKET_FTX] = parse_ftx_volume(ftx_scraped_data)

        if current_market == MARKET_POLYMARKET_NEW:
            market_volumes[MARKET_POLYMARKET_NEW] = parse_polymarket_new_volume(polymarket_volume)

        if current_market == MARKET_KALSHI:
            market_volumes[MARKET_KALSHI] = parse_kalshi_volume(kalshi_scraped_data)

        # Find a decent current market volume by sampling some of of the most
        # recent values: The current one coming from the market's server, and
        # and the most recent few items from the CSV. Try to find a good value
        # from among them.
        corrected_market_volumes[current_market] = get_corrected_market_value(
            market_data_history[current_market].get_past_volumes(unix_time, timedelta(days=0), 4)
            + [market_volumes[current_market]]
        )

        if corrected_market_volumes[current_market] is None:
            if market_data_history[current_market].has_data():
                raise FTXUniversalException("Can't find a valid market value for right now, for " + current_market)
            else:
                raise FTXUniversalException("Can't find a valid market value for right now, for " + current_market + ". This is the first run for this market. The server must be telling us that the volume is 0.")

        if current_market in BOOTSTRAPPED_MARKET_VOLUMES_LAST_QUARTER:
            logging.info("quarterly_market_volumes: Using BOOTSTRAPPED value for %s", current_market)
            # The race hasn't been running for a quarter yet, and we have a "bootstrapped" value
            # set to an estimated volume as of a quarter before data started getting collected.
            # Use that along with the current volume (for which we presume to have a reasonable
            # value now) to determine the quarterly volume. The values can get wonky over time,
            # even removing the crazy outliers, so if it's negative just call it zero.
            quarterly_market_volumes[current_market] = max(
                0, corrected_market_volumes[current_market] - BOOTSTRAPPED_MARKET_VOLUMES_LAST_QUARTER[current_market]
            )
        elif market_data_history[current_market].has_data():
            logging.info("quarterly_market_volumes: Using normal calculation for %s", current_market)

            # Find a decent market volume from one quarter year ago (or as far back as we can get) by sampling multiple
            # consecutive volumes from a quarter year ago from the CSV. Try to find a good value from among them.
            market_volume_last_quarter = get_corrected_market_value(
                market_data_history[current_market].get_past_volumes(unix_time, QUARTER_YEAR, 5)
            )

            if market_volume_last_quarter is None:
                raise FTXUniversalException("Can't find a valid market value for a quarter year ago, for " + current_market)

            # Now that we presumably have reasonable volumes for now and (up to) one quarter year
            # ago, determine a quarterly volume. The values can get wonky over time,
            # even removing the crazy outliers, so if it's negative just call it zero.
            quarterly_market_volumes[current_market] = max(
                0, corrected_market_volumes[current_market] - market_volume_last_quarter
            )
        else:
            logging.info("quarterly_market_volumes: Setting 0 for %s", current_market)

            # Don't crash the first run (when the csv has no data) The quarterly
            # volume is 0 at this point.
            quarterly_market_volumes[current_market] = 0

        # finds number of candidates/contracts being searched for
        num_contracts = len(manual_entry_by_market[USED_MARKETS[0]])
        
        # setup needed for upcoming normalization
        odds_summed = 0

        #!# THIS LINE EXECUTES THE CALCULATIONS #!#
        for x in range(0, num_contracts):
            oddsfinder(x, manual_entry[x][0], manual_entry[x][1])
            # calculating normalization factor
            if manual_entry[x][1] in CAND_dict:
                odds_summed += CAND_dict[manual_entry[x][1]]["odds"]

        market_missing_odds = len(CAND_dict) != len(manual_entry)

        if CIRCUIT_BREAKER_ODDS_SUMMED:
            if binary_creator == 0:
                if odds_summed < CIRCUIT_BREAKER_ODDS_SUMMED_THRESHOLD and not market_missing_odds:
                    raise FTXUniversalException(
                        "odds_summed = {odds_summed} on {market}! (threshold = {threshold})".format(
                            odds_summed=odds_summed,
                            market=current_market,
                            threshold=CIRCUIT_BREAKER_ODDS_SUMMED_THRESHOLD,
                        )
                    )
            else:
                if odds_summed < CIRCUIT_BREAKER_ODDS_SUMMED_THRESHOLD / 2:
                    raise FTXUniversalException(
                        "odds_summed = {odds_summed} on {market}! (threshold = {threshold} for binary market)".format(
                            odds_summed=odds_summed,
                            market=current_market,
                            threshold=CIRCUIT_BREAKER_ODDS_SUMMED_THRESHOLD / 2,
                        )
                    )

        if CIRCUIT_BREAKER_NEGATIVE_SPREAD:
            # If bid is ever less than ask, raise exception
            for x in range(0, num_contracts):
                if manual_entry[x][1] in CAND_dict and CAND_dict[manual_entry[x][1]]["bid"] > CAND_dict[manual_entry[x][1]]["ask"]:
                    raise FTXUniversalException("Bid > Ask for {name} on {market}! Bid:{bid} Ask:{ask}".format(
                        name=manual_entry[x][1],
                        market=current_market,
                        bid=CAND_dict[manual_entry[x][1]]["bid"],
                        ask=CAND_dict[manual_entry[x][1]]["ask"],
                    ))

        if CIRCUIT_BREAKER_LARGE_SPREADS:
            # If ask - bid is > 20% for all candidates, raise exception
            normal_spread_found = False
            for x in range(0, num_contracts):
                if manual_entry[x][1] in CAND_dict and CAND_dict[manual_entry[x][1]]["ask"] - CAND_dict[manual_entry[x][1]]["bid"] < CIRCUIT_BREAKER_LARGE_SPREADS_THRESHOLD:
                    normal_spread_found = True
                    break

            if not normal_spread_found:
                raise FTXUniversalException("Bid - Ask > {threshold} for every candidate on {market}!".format(
                    threshold=CIRCUIT_BREAKER_LARGE_SPREADS_THRESHOLD,
                    market=current_market,
                ))

        # Creating normalizer
        # NOTE - can't go past 100%. Correct for this in case percentages go up that high.
        # TODO - would be smarter to just leave it at 1 for non-NORMALIZED_MARKETS, and avoid checks below
        WINNER_normalizer = 1
        # can't normalize on a binary contract because it's automatically normal
        # TODO - we should maybe clean up this logic thusly:
        # * Before this if statement, throw an error `if current_market in NORMALIZED_MARKETS and binary_creator`. It'll be less confusing to debug later.
        # * Change this if statment to: if current_market in NORMALIZED_MARKETS (which now assumes no binary)
        # * Remove reference to NORMALIZED_MARKETS elsewhere and always normalize; if it's not in the NORMALIZED_MARKETS, the normalizer is 1 so who cares
        if binary_creator == 0:
            if odds_summed > 1 or NormUnder100 == 1:
                WINNER_normalizer = 1/odds_summed

        logging.info("Odds summed for %s %s", current_market, odds_summed)
        logging.info("Normalizer for %s %s", current_market, WINNER_normalizer)

        if binary_creator == 1:
            if manual_entry[1][1] not in CAND_dict or manual_entry[0][1] not in CAND_dict:
                raise FTXUniversalException("For binary races we can't allow missing candidates.")

            # NOTE - "WINNER" - is irrelevant. it's a fossil. Used to be a distinction.
            # NOTE - Swapping "bid" and "ask" so that the latter stays greater than the former
            CAND_dict[manual_entry[1][1]]["bid"] = 1- CAND_dict[manual_entry[0][1]]["ask"]
            CAND_dict[manual_entry[1][1]]["ask"] = 1- CAND_dict[manual_entry[0][1]]["bid"]
            CAND_dict[manual_entry[1][1]]["odds"] = 1- CAND_dict[manual_entry[0][1]]["odds"]

        ### Putting them all together as a tuple.
        logging.debug("current_market_index = market_number: %s", current_market_index)
        logging.debug("num_contracts: %s", num_contracts)
        logging.debug("manual_entry[x][1]: %s", manual_entry[x][1])

        # If we're on out first market, initialize finalwinner_odds_tuples with the name
        # TODO - move this to before the loop
        if current_market_index == 0:
            finalwinner_odds_tuples = [
                {'name': manual_entry[x][1], 'odds_by_market': {}} # Set the name, initialize the odds by market
                for x in range (num_contracts)
            ]


        # Basically since we wipe out CAND_dict, we need to do this to keep it alive this way
        if bid_ask_for_users_by_market_normalized == None:
            bid_ask_for_users_by_market_normalized = [dict() for x in range(0, num_contracts)]

        for x in range(0, num_contracts):
            if manual_entry[x][1] in CAND_dict:
                bid_for_user = CAND_dict[manual_entry[x][1]]["bid"]
                ask_for_user = CAND_dict[manual_entry[x][1]]["ask"]
                if current_market in NORMALIZED_MARKETS:
                    bid_for_user *= WINNER_normalizer
                    ask_for_user *= WINNER_normalizer
                bid_ask_for_users_by_market_normalized[x][current_market] = {
                    "bid": bid_for_user,
                    "ask": ask_for_user,
                }

        # Go through each contract, add the odds for this market to finalwinner_odds_tuples
        for contract_index, finalwinner_odds_tuples_for_contract in enumerate(finalwinner_odds_tuples):
            if manual_entry[contract_index][1] in CAND_dict:
                logging.debug("normalizing and adding to finalwinner_odds_tuples: %s (%s)", contract_index, manual_entry[contract_index][1])

                logging.debug(
                    """contract_index: %x finalwinner_odds_tuples_for_contract: %s  CAND_dict[manual_entry[contract_index][1]]["odds"]: %s""",
                    contract_index, finalwinner_odds_tuples_for_contract, CAND_dict[manual_entry[contract_index][1]]["odds"]
                )

                odds = CAND_dict[manual_entry[contract_index][1]]["odds"]
                if current_market in NORMALIZED_MARKETS:
                    logging.debug("appending normalizer: %s", WINNER_normalizer)
                    odds *= WINNER_normalizer
                logging.debug(
                    "appending odds for %s. raw: %s (optionally) normalized: %s",
                    manual_entry[contract_index][1],
                    odds,
                    CAND_dict[manual_entry[contract_index][1]]["odds"],
                )
                finalwinner_odds_tuples_for_contract['odds_by_market'][current_market] = odds

        logging.debug("finalwinner_odds_tuples: %s", pformat(finalwinner_odds_tuples))

        # NOTE - Write history

        ##################!!#########################
        #FILE WRITING SHOULD GO ***HERE***, NOT BELOW
        #EXCEPT...... WHAT IF ERROR? THAT IS REASON BELOW MAY BE BETTER... THEN JUST NEED DIFF VARS...
        # OTOH.... WHAT IF ERROR IS IN ONLY 1 MKT? THEN MAYBE BETTER TO HAVE AT LEAST ONE MKT HERE?.... GETS COMPLEX....
        ##################!!#########################

        if dummy == 1:
            # finalwinner_odds_tuples[candidate_index]['odds_by_market'] won't contain the market if there's not a value for that market
            # That's a legitimate case. So, we say .get(current_market, None) so that it defaults to empty string in the csv
            odds_data_to_write = [x['odds_by_market'].get(current_market, None) for x in finalwinner_odds_tuples]
            if not SKIP_WRITING_HISTORY:
                history_data_set.write_for_csv_name(current_market, data_counter, unix_time, local_time, odds_data_to_write, market_volumes[current_market])


        ##################!!####################
        # if on final market, then AVERAGE the odds accross markets here
        #!# ALL the rest except historical file writing should then be based on that!!
        #!# but also need new universal historial filewrite

        # NOTE - Once we have data from all markets, average them and append one more item at the end, unless
        #      - we only have one market, in which case we just have the one item which is already an average
        ### Stuff to do ONLY on final market:
        # TODO - move this to after the loop
        if current_market_index == num_markets - 1:
            # If any candidate has no data, that's a show stopper. We don't know what to display for them.
            EMPTY_CANDIDATES = [
                finalwinner_odds_tuples_for_contract['name'] for finalwinner_odds_tuples_for_contract in finalwinner_odds_tuples
                if not finalwinner_odds_tuples_for_contract['odds_by_market']
            ]
            if EMPTY_CANDIDATES:
                raise FTXUniversalException("One or more candidates are missing from EVERY market! %s" % repr(EMPTY_CANDIDATES))

            # Account for down markets or markets where every candidate happens to have disappeared
            NONEMPTY_USED_MARKETS = set()
            for x in finalwinner_odds_tuples:
                NONEMPTY_USED_MARKETS = NONEMPTY_USED_MARKETS.union(set(x['odds_by_market']))
            EMPTY_USED_MARKETS = set(USED_MARKETS) - NONEMPTY_USED_MARKETS

            missing_candidates_warning_email(
                NONEMPTY_USED_MARKETS,
                EMPTY_USED_MARKETS,
                finalwinner_odds_tuples,
                manual_entry_by_market,
            )

            logging.info("FINAL Volumes: %s", market_volumes)
            logging.info("FINAL Corrected Volumes: %s", corrected_market_volumes)
            logging.info("FINAL Quarterly Volumes: %s", quarterly_market_volumes)
            total_volume = sum(market_volumes.values())
            corrected_total_volume = sum(corrected_market_volumes.values())

            publishable_total_volume = str("{:,.0f}".format(corrected_total_volume))
            logging.debug("publishable_total_volume %s", publishable_total_volume)

            logging.debug(
                "num_contracts: %s num_markets %s", num_contracts, num_markets,
            )

            # In case of zero volume, avoid divide-by-zero in super rare cases, or perhaps oddball
            # candidates only in one oddball market. Or perhaps just when a market just gets added
            # and we have no quarterly volume yet.
            EPSILON = 0.001

            # Go through each contract, calcualte the average(s) for finalwinner_odds_tuples
            for contract_index, finalwinner_odds_tuples_for_contract in enumerate(finalwinner_odds_tuples):
                candidate_markets = list(finalwinner_odds_tuples[contract_index]['odds_by_market'])

                # `candidate_volume_factor` is the total volume for *all* candidates across all markets
                # in the last quarter year, *where this particular candidate participates*. Ideally we'd deal
                # in per-candidate volumes but that's not available yet.

                candidate_volume_factor = sum((corrected_market_volumes[market] or EPSILON) for market in candidate_markets)
                candidate_market_weighting_factors = {market: float(corrected_market_volumes[market] or EPSILON) / candidate_volume_factor for market in candidate_markets}
                logging.debug(
                    "contract_index: %s candidate_market_weighting_factors %s", contract_index, candidate_market_weighting_factors,
                )

                combined_odds = sum(
                    finalwinner_odds_tuples[contract_index]['odds_by_market'].values()
                ) / len(finalwinner_odds_tuples[contract_index]['odds_by_market'])
                combined_odds_weighted = sum(
                    candidate_market_weighting_factors[market] * finalwinner_odds_tuples[contract_index]['odds_by_market'][market]
                    for market in candidate_markets
                )
                #actually adds to the matrix:

                finalwinner_odds_tuples_for_contract['combined_odds'] = combined_odds
                finalwinner_odds_tuples_for_contract['combined_odds_weighted'] = combined_odds_weighted
                if USE_WEIGHTED_AVERAGES: # Which combined_odds will we use for display, delta, and charts?
                    finalwinner_odds_tuples_for_contract['combined_odds_used'] = combined_odds_weighted
                else:
                    finalwinner_odds_tuples_for_contract['combined_odds_used'] = combined_odds
                logging.info(
                    "candidate_market_weighting_factors for %s: \n%s",
                    finalwinner_odds_tuples[contract_index]['name'],
                    pformat(candidate_market_weighting_factors),
                )
                logging.debug("finalwinner_odds_tuples incl. avg %s", finalwinner_odds_tuples)
                #combinedwinner_odds_tuples = [tuple(l) for l in finalwinner_odds_tuples]

                combinedwinner_odds_tuples = finalwinner_odds_tuples
                #formatting for historical data file

            logging.info("USED_MARKETS: %s", USED_MARKETS)
            logging.info("market_volumes: \n%s", pformat(market_volumes))

            general_volume_factor = sum((corrected_market_volumes[market] or EPSILON) for market in corrected_market_volumes)
            general_market_weighting_factors = {market: float(corrected_market_volumes[market] or EPSILON) / general_volume_factor for market in corrected_market_volumes}

            logging.info(
                "general_market_weighting_factors (Just Informational. Candidate-specific QUARTERLY factors are used for weighing odds.): \n%s",
                pformat(general_market_weighting_factors)
            )
            logging.info("finalwinner_odds_tuples: \n%s", pformat(finalwinner_odds_tuples))

            # NOTE - pulling from combined price log, find where it was in the past, find comparison

            past_WIN_odds = data_history.get_past_win_odds_row(unix_time, diff_time_delay)
            
            # NOTE - this contains the data that shows up on html page
            #!# This is the most important list of tuples, containing: (NAME, ODDS, CHANGE, ARROW COLOR, formerly WIKI LINKS)
            finalwinner_odds_w_changes_tuples = []

            logging.debug("num_contracts: %s", num_contracts)
            for x in range (0, num_contracts):
                logging.debug("past_WIN_odds[x], %s", past_WIN_odds[x])

                if past_WIN_odds[x] is not None:
                    print "normal detected. calculating diff..."
                    win_diff = combinedwinner_odds_tuples[x]['combined_odds_used']-past_WIN_odds[x]
                else:
                    print "missing value detected. can't get a real diff, treating diff as zero."
                    win_diff = 0

                finalwinner_odds_w_changes_tuples.append((
                    manual_entry[x][1],
                    combinedwinner_odds_tuples[x]['combined_odds_used'],
                    win_diff,
                    render_html.arrowfinder(win_diff),
                    "<a>",
                    bid_ask_for_users_by_market_normalized[x],
                ))

            logging.debug("test")
            #Sorting the above tuple list. Note: finalwinner_odds_w_changes_tuples itself remains UNSORTED & usable for static comparison.
            WIN_odds_sorted = sorted(finalwinner_odds_w_changes_tuples, key=lambda finalwinner_odds_w_changes: finalwinner_odds_w_changes[1], reverse=True)

            # NOTE - CHART WRITING
            logging.debug("~~~~~~~~~~~~~~~~\nWIN_odds_sorted\n\n%s\n~~~~~~~~~~~~~~~~", WIN_odds_sorted)

            def month_adjuster(date_unadjusted):
                date_pt_1 = date_unadjusted.split(",,")[0]
                date_pt_2 = date_unadjusted.split(",,")[1]
                date_pt_3 = date_unadjusted.split(",,")[2]
                date_month = float(date_pt_2)-1
                date_adjusted = str(date_pt_1)+","+str(int(date_month))+","+str(date_pt_3)
                return date_adjusted

            if dummy == 1:            
                ## formatting data for WIN chart
                if USE_CACHED_RESPONSES:
                    WIN_chart_date = month_adjuster(str(time.strftime('[new Date(2020,,09,,30,20,52,58),')))
                else:
                    WIN_chart_date = month_adjuster(str(time.strftime('[new Date(%Y,,%m,,%d,%H,%M,%S),')))

                logging.debug("test")
                WIN_chart_odds = ""
                #!# the loop that formats for chart
                for x in range(0, num_contracts):
                    WIN_chart_odds = WIN_chart_odds + (str(round(combinedwinner_odds_tuples[x]['combined_odds_used']*100,1))+",")
                # dates chart
                formatted_WIN_chart_data = str(str(WIN_chart_date)+ str(WIN_chart_odds) + "],")
                logging.debug("formatted_WIN_chart_data %s", formatted_WIN_chart_data)
                
                # writing new chart data to file
                fy = open('/python/'+my_root+'/WIN_chart_data_full'+my_ticker+'.txt','a')
                # NOTE - make sure this is combined data at this point. this goes in the chart to display to user.
                if not SKIP_WRITING_HISTORY:
                    fy.write(str(formatted_WIN_chart_data))
                fy.close()
                logging.debug("test1")
                if (float(data_counter/12)).is_integer() == 1:
                    try:
                        fy = open('/python/'+my_root+'/WIN_chart_data'+my_ticker+'.txt','a')
                        if not SKIP_WRITING_HISTORY:
                            fy.write(str(formatted_WIN_chart_data))
                        fy.close()
                    except Exception,e:
                        pass
            logging.debug("test2")
            if data_counter != 1:
                fz = open('/python/'+my_root+'/WIN_chart_data'+my_ticker+'.txt','r')
                WIN_ingested_data = fz.read()
                fz.close()
            else:
                fz = open('/python/'+my_root+'/WIN_chart_data_full'+my_ticker+'.txt','r')
                WIN_ingested_data = fz.read()
                fz.close()        
            logging.debug("test3")
            # formatting chart data for html
            chart_rows_created = "data.addColumn('datetime', 'X');"
            for x in range (0, num_contracts):
                if custom_chart_labels == "":
                    chart_rows_created = chart_rows_created +"""data.addColumn('number', '"""+str(manual_entry[x][1]).replace("'","")+"""');"""
                else:
                    chart_rows_created = chart_rows_created +"""data.addColumn('number', '"""+str(custom_chart_labels[x]).replace("'","")+"""');"""
            logging.debug("test4")
            # if exists and set above, creates a line for "none of the above" implied odds
            
            limited_rows = num_contracts
            if num_contracts >= MAX_LIMITED_ROWS:
                limited_rows = MAX_LIMITED_ROWS
            
            odds_summed_averaged = 0
            for x in range (0, limited_rows):
                odds_summed_averaged = odds_summed_averaged + WIN_odds_sorted[x][1]
            logging.info("Odds summed (all market avg):")
            logging.info(odds_summed_averaged)
            
            Other_bar = ''
            if OthersOnPage == 1:
                if odds_summed_averaged < 1:
                    Other_bar ='''<tr>
                                <td align="right" bgcolor="#FFFFFF"><img src="/Other.png" width="100" height="140"></td>		
                                    <td bgcolor="#FFFFFF"><p style="font-size: 55pt; margin-bottom:-10px">'''+str(round((1-odds_summed_averaged)*100,1))+'''%</p></td>
                                  </tr>'''

            UK_FLAG_EMOJI = "&#x1F1EC&#x1F1E7"
            US_FLAG_EMOJI = "&#x1F1FA&#x1F1F8"
            GLOBE_EMOJI = "&#x1F30E"
            MARKET_TOOLTIP_DISPLAY = {
                MARKET_FTX: "FTX " + GLOBE_EMOJI,
                MARKET_BETFAIR: "Betfair " + UK_FLAG_EMOJI,
                MARKET_PREDICTIT: "PredictIt " + US_FLAG_EMOJI,
                MARKET_SMARKETS: "Smarkets " + UK_FLAG_EMOJI,
                MARKET_POLYMARKET_NEW: "Polymarket " + GLOBE_EMOJI,
                MARKET_KALSHI: "Kalshi " + US_FLAG_EMOJI,
            }

            # Put MARKET_FTX first any time we display it
            DISPLAYED_USED_MARKETS = sorted(NONEMPTY_USED_MARKETS, key=lambda market : market != MARKET_FTX)

            def make_bid_ask_tooltip(x):
                tooltip_markets = sorted(
                    [market for market in DISPLAYED_USED_MARKETS if market in WIN_odds_sorted[x][5]],
                    key=lambda m:99999999999999999 if m == MARKET_FTX else corrected_market_volumes[m],
                    reverse=True,
                )

                headers = ["Markets", "Range (Bid-Ask)"]
                headers.append("Total $ Bet")
                #headers.append("Quarterly $ Bet")

                table_data = []
                for market in tooltip_markets:
                    row = [
                        MARKET_TOOLTIP_DISPLAY[market],
                        (
                            str(round(WIN_odds_sorted[x][5][market]['bid']*100, 1)) +
                            '-' +
                            str(round(WIN_odds_sorted[x][5][market]['ask']*100, 1)) +
                            '%'
                        ),
                    ]

                    row.append('$' + str("{:,.0f}".format(market_volumes[market])))
                    #row.append('$' + str("{:,.0f}".format(quarterly_market_volumes[market])))

                    table_data.append(row)

                # Try to match how it's placed in the html generator, just for readability of html source.
                indent = " " * 24
                return (
                    "\n" +
                    WIN_odds_sorted[x][0] +
                    " details" +
                    "<div style='padding-left: 1em'>" +
                    "\n<table>" +

                    # Table headers, separated by the empty spacer headers.
                    "<tr>\n" +
                    "\n<td>&nbsp&nbsp&nbsp</td>\n".join("<td><u>" + header + "</u></td>" for header in headers) +
                    "\n</tr>" +

                    # Spacer row
                    "\n<tr></tr>" +

                    # Table data, row for row
                    "\n<tr>" +
                    "</tr>\n<tr>".join(
                        # row data, col for col, with blank columns
                        # corresponding to the empty spacer headers above.
                        "<td></td>".join("<td>" + col + "</td>" for col in row)
                        for row in table_data
                    ) +
                    "</tr>" +

                    "\n</table>" +
                    "</div>"
                ).replace('\n', '\n' + indent)

            rows_created = render_html.first_candidate_row(
                cand_name=str(WIN_odds_sorted[0][0]),
                odds_percentage=str(round(WIN_odds_sorted[0][1]*100,1)),
                change_percentage=str(round(WIN_odds_sorted[0][2]*100,1)),
                arrow_img=str(WIN_odds_sorted[0][3]),
                link_open_tag=str(WIN_odds_sorted[0][4]),
                button=button,
                my_html_address=my_html_address,
                tooltip_text=make_bid_ask_tooltip(0),
                tooltip_visible=BID_ASK_TOOLTIP,
            )

            for x in range (1, limited_rows):
                rows_created = rows_created + render_html.next_candidate_row(
                    cand_name=str(WIN_odds_sorted[x][0]),
                    odds_percentage=str(round(WIN_odds_sorted[x][1]*100,1)),
                    change_percentage=str(round(WIN_odds_sorted[x][2]*100,1)),
                    arrow_img=str(WIN_odds_sorted[x][3]),
                    link_open_tag=str(WIN_odds_sorted[x][4]),
                    button=button, # NOTE: unused, I think
                    my_html_address=my_html_address,
                    tooltip_text=make_bid_ask_tooltip(x),
                    tooltip_visible=BID_ASK_TOOLTIP,
                )

            if num_markets == 1:
                pub_odds_from = ("Odds on this page are from " + MARKET_LINKS[DISPLAYED_USED_MARKETS[0]])
            else:
                pub_odds_from = (
                    "Odds for this page are averaged between " +
                    ", ".join([MARKET_LINKS[market] for market in DISPLAYED_USED_MARKETS[:-1]]) + # First N-1 comma sepaated
                    " and " +
                    MARKET_LINKS[DISPLAYED_USED_MARKETS[-1]] # Last one
                )

            # ... "Nomination odds are from Betfair." - Keeping this around since it was hanging around before this cleanup, commented out.

            #~# Import nav bars from text file
            fa = open('/python/Nav_bar.txt','r')
            Nav_bar = fa.read()
            fa.close()
            fc = open('/python/Chart_nav_bar.txt','r')
            Chart_nav_bar = fc.read()
            fc.close()

            ### ! THIS IS HTML STRING FOR *EVERYTHING* 
            finalwinner_HTML_string = render_html.page(
                now=now,
                Nav_bar=Nav_bar,
                Chart_nav_bar=Chart_nav_bar,
                Ad_bar=Ad_bar,
                Other_bar=Other_bar,
                column_title=column_title,
                race_description=race_description,
                publishable_total_volume=publishable_total_volume,
                rows_created=rows_created,
                chart_rows_created=chart_rows_created,
                WIN_ingested_data=WIN_ingested_data,
                formatted_WIN_chart_data=formatted_WIN_chart_data,
                chart_colors=chart_colors,
                chart_label_ordering=chart_label_ordering,
            )

            # automatically formats API
            api_xml = '''<?xml version="1.0" encoding="UTF-8" ?><BettingData xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'''
            for x in range (0,num_contracts):
                api_xml = api_xml + """
                <""" + manual_entry[x][1] + """>"""+str(round(finalwinner_odds_w_changes_tuples[x][1]*100,1))+"""</"""+manual_entry[x][1]+""">"""
            api_xml = api_xml + """
        <Time>"""+str(now)+"""</Time></BettingData>"""

            if dummy == 1:
                history_file_write_for_average(
                    data_counter,
                    unix_time,
                    local_time,
                    [x['combined_odds'] for x in finalwinner_odds_tuples],
                    total_volume,
                    manual_entry
                )

                history_file_write_for_weighted_average(
                    data_counter,
                    unix_time,
                    local_time,
                    [x['combined_odds_weighted'] for x in finalwinner_odds_tuples],
                    total_volume,
                    manual_entry
                )

                # TODO - In the old data format, it was advancing data_counter before writing to the file, because it was
                # writing the _next_ data_counter variable as part of the process, I think. But it kept data_counter incremented.
                # I'm keeping this around for now just in case, but I don't think we really need it. We should remove it if that's the case.
                data_counter = data_counter + 1

            ##### FTP! (or local output) :) #####
            """
            print "writing directly to server"
            fg = open('/var/www/predictionmarketodds.com/'+html_title,'w')
            fg.write(str(finalwinner_HTML_string))
            fg.close()
            print "PrecictionMarketOdds.com... Successfully uploaded!"
            """
            print "writing to server"
            fg = open('/var/www/178.62.65.243/'+html_title,'w')
            fg.write(str(finalwinner_HTML_string))
            fg.close()
            print "Mirror 178.62.65.243... Also Success! (Unless immediately followed by error message)"

            print "writing to server"
            fg = open('/var/www/electionbettingodds.com/'+html_title,'w')
            fg.write(str(finalwinner_HTML_string))
            fg.close()
            print "ElectionBettingOdds.com... Also Success! (Unless immediately followed by error message)"

            if eboconfig.EBOFTP.enabled:
                ftp = FTP('ftp.electionbettingodds.com', timeout=8)
                ftp.login(eboconfig.EBOFTP.user, eboconfig.EBOFTP.password)
                converted_WIN_HTML_string = io.BytesIO(finalwinner_HTML_string)
                ftp.storbinary(html_title, converted_WIN_HTML_string)
                logging.info("ElectionBettingOdds.com... Success! (Unless immediately followed by error message)")
                ## API
                ftp = FTP('ftp.electionbettingodds.com', timeout=8)
                ftp.login(eboconfig.EBOFTP.user, eboconfig.EBOFTP.password)
                converted_WIN_HTML_string = io.BytesIO(api_xml)
                ftp.storbinary("STOR public_html/"+my_html_address+"_api", converted_WIN_HTML_string)
                logging.info("API... Success! (Unless immediately followed by error message)")

            if eboconfig.MirrorFTP.enabled:
                ftp = FTP(eboconfig.MirrorFTP.host, timeout=8)
                ftp.login(eboconfig.MirrorFTP.user, eboconfig.MirrorFTP.password)
                converted_WIN_HTML_string = io.BytesIO(finalwinner_HTML_string)
                html_title_trimmed = str(html_title).replace("public_html/","files/")
                ftp.storbinary(html_title_trimmed, converted_WIN_HTML_string)
                logging.info(html_title_trimmed)
                logging.info("ElectionBettingOdds.com... Success! (Unless immediately followed by error message)")
                ## API
                ftp = FTP(eboconfig.MirrorFTP.host, timeout=8)
                ftp.login(eboconfig.MirrorFTP.user, eboconfig.MirrorFTP.password)
                converted_WIN_HTML_string = io.BytesIO(api_xml)
                ftp.storbinary("STOR files/"+my_html_address+"_api", converted_WIN_HTML_string)
                logging.info("API... Success! (Unless immediately followed by error message)")

            if eboconfig.TripodFTP.enabled:
                import socket
                socket.setdefaulttimeout(60)
                logging.info("running tripod ftp...")
                ftp = FTP('ftp.tripod.com')
                ftp.login(eboconfig.TripodFTP.user, eboconfig.TripodFTP.password)
                converted_WIN_HTML_string = io.BytesIO(finalwinner_HTML_string)
                html_title_trimmed = "STOR " + str(html_title).replace("public_html","")
                ftp.storbinary(html_title_trimmed, converted_WIN_HTML_string)
                logging.info("TRIPOD... Success! (Unless immediately followed by error message)")
                ftp.quit()

            if eboconfig.LocalOutput.enabled:
                html_title_trimmed = str(html_title).replace("STOR public_html/","")
                assert ".." not in html_title_trimmed
                local_output_filename = os.path.join(eboconfig.LocalOutput.parent_path, html_title_trimmed)
                local_output_dirname = os.path.dirname(local_output_filename)
                if not os.path.exists(local_output_dirname): # TODO - python 3, just use exist_ok with makdirs
                    os.makedirs(local_output_dirname)
                local_output_file = open(local_output_filename, "w")
                local_output_file.write(finalwinner_HTML_string)
                logging.debug("Wrote to: %s", local_output_filename)
                ## API
                local_output_filename = os.path.join(eboconfig.LocalOutput.parent_path, html_title_trimmed + "_api")
                local_output_file = open(local_output_filename, "w")
                local_output_file.write(api_xml)
                logging.debug("Wrote to: %s", local_output_filename)
                sys.stdout.flush()


##### dummy ... if set to 0 it won't write to any files...   
##### html_title option must be set to STOR public_html/ plus the page name.
##### diff_time_delay should the value of the historical timestamp at the time you want.

data_start_time = local_time - time_since_start
time_created = data_start_time.strftime('Since %-I') + data_start_time.strftime('%p').lower() + data_start_time.strftime(' %b %d')
since_time = '''<option value="/'''+my_html_address+'''.html">'''+time_created+'''</option>'''
since_time_selected = '''<option value="/'''+my_html_address+'''.html" selected">'''+time_created+'''</option>'''

#since_time = "in last day" #'''<option value="/'''+my_html_address+'''.html">'''+time_created+'''</option>'''
#since_time_selected = "in last day" #'''<option value="/'''+my_html_address+'''.html" selected">'''+time_created+'''</option>'''

if time_since_start < timedelta(hours=4):
    # runs program from creation before 4 hours
    if time_since_start <= timedelta(0):
        logging.info("detected: FIRST RUN")
    else:
        logging.info("detected: under 4h")
    program(1,timedelta(days=1),since_time,"public_html/"+my_html_address+".html")
elif time_since_start < timedelta(days=1):
    # runs program between 4 hours and a day after creation
    logging.info("detected: 4hr - day")
    start_time = since_time_selected + '''<option value="/'''+my_html_address+'''_4hr.html">in last 4hr</option>'''
    four_hr = since_time + '''<option value="/'''+my_html_address+'''_4hr.html" selected>in last 4hr</option>'''
    program(1,timedelta(hours=4),four_hr,"public_html/"+my_html_address+"_4hr.html")
    program(0,timedelta(days=1),start_time,"public_html/"+my_html_address+".html")
    # 4hr standard: data_counter-12*4
elif time_since_start < timedelta(days=7):
    # runs program between a day and a week after creation
    logging.info("detected: day - week")
    four_hr = '''<option value="/'''+my_html_address+'''_4hr.html" selected>in last 4hr</option>
<option value="/'''+my_html_address+'''.html">in last day</option>'''
    daily = '''<option value="/'''+my_html_address+'''_4hr.html">in last 4hr</option>
<option value="/'''+my_html_address+'''.html" selected>in last day</option>'''
    program(1,timedelta(hours=4),four_hr,"public_html/"+my_html_address+"_4hr.html")
    program(0,timedelta(days=1),daily,"public_html/"+my_html_address+".html")
    # day standard: data_counter-12*24
else:
    # runs program after week after creation
    logging.info("detected: week+")
    four_hr = '''<option value="/'''+my_html_address+'''_4hr.html" selected>in last 4hr</option>
<option value="/'''+my_html_address+'''.html">in last day</option>
<option value="/'''+my_html_address+'''_week.html">in last wk</option>'''
    daily = '''<option value="/'''+my_html_address+'''_4hr.html">in last 4hr</option>
<option value="/'''+my_html_address+'''.html" selected>in last day</option>
<option value="/'''+my_html_address+'''_week.html">in last wk</option>'''
    weekly = '''<option value="/'''+my_html_address+'''_4hr.html">in last 4hr</option>
<option value="/'''+my_html_address+'''.html">in last day</option>
<option value="/'''+my_html_address+'''_week.html" selected>in last wk</option>'''
    program(1,timedelta(hours=4),four_hr,"public_html/"+my_html_address+"_4hr.html")
    program(0,timedelta(days=1),daily,"public_html/"+my_html_address+".html")
    program(0,timedelta(days=7),weekly,"public_html/"+my_html_address+"_week.html")
    # week standard: data_counter-12*24*7





# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~





    
# if you need a 5 min adjuster in the future: time.sleep(int(round(60*5*[adj factor])))
# AD text: <a href="https://www.tezos.com"><img src="http://maximwebsite.tripod.com/vertise_tezos-2.png"></a>