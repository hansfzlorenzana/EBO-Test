#!/usr/bin/python
#import library to do http requests:
from __future__ import division             #enables division with decimals
import requests
import json
import os
import copy
import math                                 #enables calculation of square roots
import urllib2                            #enables loading web links
import httplib2                             #html parser
from xml.dom.minidom import parseString     #xml parser
import datetime                             #Allows date calculation
import calendar                             #Allows date calculation
from datetime import datetime               #Allows date calculation
import decimal                              #Allows decimal rounding
import re
from ftplib import FTP
import io
import time				    #Allows program sleep
from datetime import date                   #Allows date formation in e-mail
from email.mime.text import MIMEText        #Allows e-mail sending
import smtplib                              #Allows e-mail sending
import pprint
import random
from Tkinter import Tk
import thread
from xml.etree import ElementTree as ET
from decimal import Decimal
import collections
import socket
socket.setdefaulttimeout(8)
import subprocess
import imp
import sys

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

try:
    eboconfig = imp.load_source("eboconfig", "/python/eboconfig.py")
except:
    print ("Error: Need a valid /python/eboconfig.py file. See /python/eboconfig.py.example for reference.")
    raise

#time.sleep(60*60*5)
counter = 0
error_counter = 0

# Consts for the different markets, used in various places in the code

MARKET_BETFAIR = "Betfair"
MARKET_PREDICTIT = "PredictIt"
MARKET_FTX = "FTX"
MARKET_SMARKETS = "Smarkets"
MARKET_POLYMARKET = "Polymarket Old"
MARKET_POLYMARKET_NEW = "Polymarket"

MARKET_LINKS = {
        MARKET_SMARKETS: '<a href="https://smarkets.com/event/41938283/politics/us/2024-presidential-election/2024-presidential-winner">Smarkets</a>',
        MARKET_PREDICTIT: '<a href="https://www.predictit.org/promo/electionbetting">PredictIt</a>',
        MARKET_FTX: '<a href="https://ftx.com/">FTX.com</a>',
        MARKET_BETFAIR: '<a href="https://www.betfair.com/exchange/plus/politics">Betfair</a>',
        MARKET_POLYMARKET: '<a href="https://polymarket.com/market/will-andrew-yang-win-the-democratic-primary-for-mayor-of-new-york-city-in-2021>Polymarket Old</a>',
        MARKET_POLYMARKET_NEW: '<a href="https://polymarket.com/market/will-andrew-yang-win-the-democratic-primary-for-mayor-of-new-york-city-in-2021>Polymarket</a>'

}

# MARKET SELECTION INSTRUCTIONS:
#
# USED_MARKETS describes which markets are active. It also determines the
# order in which they are processed, and as such appear in the "tuples"
# structures in program output as well as the various price logs. Feel free
# to just comment out the ones you don't use if that's simpler.
#
# If the first market listed in USED_MARKETS is MARKET_BETFAIR or MARKET_SMARKETS,
# the results from that first market will be used as the "fallback" market. This
# means that if a candidate from our grand list is not listed in a subsequent market,
# that candidate's value from the fallback market will be used in its place. If the
# first market listed is not one of those two, there will be no fallback market.
# Instead, unlisted candidates will default to having 0 odds.
#
# LIMITATIONS:
# * For the time being, it will (purposely, explicitly) fail if you only select only one market.
#      This should be fixed long before election day. I just want to test that it doesn't break the price log situation.
# * List each market at most once (probably goes without saying)
# * Don't list anything other than the 4 given markets (probably goes without saying)

MAX_LIMITED_ROWS = 8

USED_MARKETS = [
    # MARKET_PREDICTIT,
    #MARKET_POLYMARKET,
    MARKET_SMARKETS,
    #MARKET_FTX,
    MARKET_BETFAIR,
    MARKET_POLYMARKET_NEW,
]

NORMALIZED_MARKETS = USED_MARKETS

my_ticker = "_GOPPRIMARY_2024"
my_html_address = "GOPPrimary2024" #program automatically inserts ".html"
my_root = "2024/GOPPRIMARY"# no slashes before or after

my_Smarkets_market_name = "2024 Republican presidential nominee"
my_Betfair_URL = "https://ero.betfair.ro/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=USD&locale=en_GB&marketIds=1.178163916&rollupLimit=25&rollupModel=STAKE&types=MARKET_STATE,MARKET_RATES,MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_STATE,RUNNER_EXCHANGE_PRICES_BEST,RUNNER_METADATA,MARKET_LICENCE,MARKET_LINE_RANGE_INFO"
my_PredictIt_URL = "https://www.predictit.org/api/marketdata/markets/7053"
my_FTX_URL = "https://ftx.com/api/markets/"
my_Polymarket_URL = "https://polymarket.com/event/republican-nominee-2024"

column_title = "GOP Nomination 2024"

time_created = "Since 1pm Jan 21"

# below must be reflected in price_log file
# 1)name to search in Betfair, 2)name in price log & photo, 3)wiki
manual_entry = []
#Betfair
Betfair_manual_entry = [
    ("Donald Trump","Trump",  ""),
    ("Mike Pence","Pence",  ""),
    ("Marco Rubio","Rubio",  ""),
    ("Tom Cotton","Cotton",  ""),
    ("Ted Cruz","Cruz",  ""),
    ("Nikki Haley", "Haley",""),
    ("Josh Hawley", "Hawley",""),
    ("Donald Trump Jr.","Trump_Jr",  ""),
    ("Ivanka Trump","I_Trump",  ""),
    ("Mike Pompeo","Pompeo",  ""),
    ("Kristi Noem","Noem",  ""),
    ("Tucker Carlson","Carlson",  ""),    
    (None,"Crenshaw",  ""), 
    ("Ron DeSantis","DeSantis",  ""), 
    ("Rick Scott","RickScott",  ""), 
    ("Tim Scott","TimScott",  ""),
    ("Vivek Ramaswamy","Ramaswamy",  ""), 
    ("Chris Christie","Christie",  ""), 
    ("Larry Elder","Elder",  ""), 
]
#PredictIt
PredictIt_manual_entry = [
    ("Trump","Trump",  ""),
    ("Pence","Pence",  ""),
    ("Rubio","Rubio",  ""),
    ("Cotton","Cotton",  ""),
    ("Cruz","Cruz",  ""),
    ("Haley", "Haley",""),
    ("Hawley", "Hawley",""),
    ("TrumpJr.","Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    ("Pompeo","Pompeo",  ""),
    ("Noem","Noem",  ""),
    ("Carlson","Carlson",  ""),
    (None,"Crenshaw",  ""),
    ("DeSantis","DeSantis",  ""),
    ("R.Scott","RickScott",  ""),
    ("T.Scott","TimScott",  ""),
    ("Ramaswamy","Ramaswamy",  ""), 
    ("Christie","Christie",  ""), 
    (None,"Elder",  ""), 
]
#FTX
FTX_manual_entry = [
    ("TRUMP","Trump",  "https://ftx.com/trade/TRUMP"),
    ("WARREN","Warren",  "https://ftx.com/trade/WARREN"),
    ("Mike Pence","Pence",  ""),
    ("Michelle Obama","Obama",  ""),
    ("BERNIE","Sanders",  "https://ftx.com/trade/BERNIE"),
    ("Julian Castro","Castro",  ""),
    ("Marco Rubio","Rubio",  ""),
    ("Andrew Cuomo","Cuomo",  ""),
    ("Hillary Clinton","Clinton",  ""),
    ("Paul Ryan","Ryan",  ""),
    ("BLOOMBERG","Bloomberg",  "https://ftx.com/trade/BLOOMBERG"),
    ("Booker","Booker",  ""),
    ("BIDEN","Biden",  "https://ftx.com/trade/BIDEN"),
    ("Ted Cruz","Cruz",  ""),
    ("Tim Kaine","Kaine",  ""),
    ("Kamala Harris","Harris",  ""),
    ("John Kasich","Kasich",  ""),
    ("Ivanka Trump","I_Trump",  ""),
    ("Oprah Winfrey","Winfrey",  ""),
    ("Trey Gowdy","Gowdy",  ""),
    ("Mark Zuckerberg","Zuckerberg",  ""),
    ("Dwayne Johnson","DJohnson",  ""),
    ("Mark Cuban","Cuban",  ""),
    ("Kirsten Gillibrand","Gillibrand",  ""),
    ("Tulsi Gabbard","Gabbard",  ""),
    ("Beto O'Rourke","ORourke",  ""),
    ("Sherrod Brown","Brown",  ""),
    ("Amy Klobuchar", "Klobuchar",""),
    ("Michael Avenatti", "Avenatti",""),
    ("Andrew Yang", "Yang",""),
    ("PETE", "Buttigieg", "https://ftx.com/trade/PETE"),
    ("Nikki Haley", "Haley",""),
]
#Smarkets
Smarkets_manual_entry = [
    ("Donald Trump","Trump",  ""),
    ("Mike Pence","Pence",  ""),
    ("Marco Rubio","Rubio",  ""),
    ("Tom Cotton","Cotton",  ""),
    ("Ted Cruz","Cruz",  ""),
    ("Nikki Haley", "Haley",""),
    ("Josh Hawley", "Hawley",""),
    ("Donald Trump Jr.","Trump_Jr",  ""),
    ("Ivanka Trump","I_Trump",  ""),
    ("Mike Pompeo","Pompeo",  ""),
    ("Kristi Noem","Noem",  ""),
    ("Tucker Carlson","Carlson",  ""),    
    ("Dan Crenshaw","Crenshaw",  ""), 
    ("Ron DeSantis","DeSantis",  ""), 
    ("Rick Scott","RickScott",  ""), 
    ("Tim Scott","TimScott",  ""), 
    ("Vivek Ramaswamy","Ramaswamy",  ""), 
    ("Chris Christie","Christie",  ""), 
    ("Larry Elder","Elder",  ""), 
]
#Polymarket
Polymarket_manual_entry = [
    ((240380,"Yes"),"Trump", ""),
    (None,"Pence", ""),
    (None,"Rubio", ""),
    (None,"Cotton", ""),
    (None,"Cruz", ""),
    ((240381,"Yes"), "Haley",""),
    (None, "Hawley",""),
    (None,"Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    (None,"Pompeo",  ""),
    (None,"Noem",  ""),
    (None,"Carlson",  ""),
    (None,"Crenshaw",  ""),
    (None,"DeSantis",  ""),
    (None,"RickScott",  ""),
    (None,"TimScott",  ""),
    (None,"Ramaswamy",  ""),
    (None,"Christie",  ""),
    (None,"Elder",  ""),
]
Polymarket_new_manual_entry = [
    ((253691,"Yes"),"Trump", ""),
    (None,"Pence", ""),
    (None,"Rubio", ""),
    (None,"Cotton", ""),
    (None,"Cruz", ""),
    ((253695,"Yes"), "Haley",""),
    (None, "Hawley",""),
    (None,"Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    (None,"Pompeo",  ""),
    (None,"Noem",  ""),
    (None,"Carlson",  ""),
    (None,"Crenshaw",  ""),
    ((253692,"Yes"),"DeSantis",  ""),
    (None,"RickScott",  ""),
    (None,"TimScott",  ""),
    ((253693,"Yes"),"Ramaswamy",  ""),
    (None,"Christie",  ""),
    (None,"Elder",  ""),
]
race_description = """GOP Nominee for the Presidential election to be held on Nov 5 2024"""

### CHARTING ENTRIES
custom_chart_labels = ""
# below always starts with 0. make string empty for defaults
chart_label_ordering = "var viewColumns = [0, 1, 14, 17, 3, 4, 2, 6, 7, 8, 5, 10, 11, 12, 13, 15, 16];view.setColumns(viewColumns);"
#!# NOTE: if you move a label up, must move color with it. Color is stuck to position.
# Make string empty for defaults
chart_colors = "colors: ['DarkOrange', '#33ff77', 'blue', 'red', 'gold', 'teal', '#FF1493', 'brown', '#778899', 'orange', '#000000', '#8B0000', '#00FFFF','#ccccff','#800000',],"

# Dummy that controls whether "other" % shows at bottom
OthersOnPage = 1
# Dummy; 1 = normalize if sum of odds < 1. 0 if don't normalize to 100% 
NormUnder100 = 0

#~# this should be moved to a seperate page and called from there to make changes easier
#~# Import nav bars from text file
fa = open('/python/ad_bar.txt','r')
ad_bar = fa.read()
fa.close()
    
Ad_bar = ad_bar

# allow binary creator
binary_creator = 0

# price_log must be made to match if you add any

try:
    with open ("/python/FTX_Universal_Machine.py", "r") as myfile:
        Betfarer_Machine_Code = myfile.read()

    competition = 0# set to 0 to lose "chance of winning" on page
    if competition == 0:
        Betfarer_Machine_Code = Betfarer_Machine_Code.replace("Chance of winning...","")
    
    exec(Betfarer_Machine_Code)

##### END OF INSTANCE #####

### Set time lag, in seconds, before it runs again
    time.sleep(int(round(60*0/1.125)))

### HANDLE ALL ERRORS
except httplib2.ServerNotFoundError:
    #now = time.strftime('%l:%M%p %Z on %b %d, %Y')
    #print "Connection error at: ", now, "... trying again in 30 seconds..."
    time.sleep(30)
    pass
except urllib2.URLError, e:
    #now = time.strftime('%l:%M%p %Z on %b %d, %Y')
    #print "Connection error at: ", now, "... trying again in 30 seconds..."
    time.sleep(30)
    pass
except socket.timeout, e:
    now = time.strftime('%l:%M%p %Z on %b %d, %Y')
    #print now
    #print "Error with Server! Immediately trying again."
    time.sleep(.1)
    pass
except Exception,e:
    try:
        now = datetime.now()
        print "!!!!!!!!!!!!! ERROR !!!!!!!!!!!!!!!"
        print full_stack()
        print "error at:"+str(now)+"... trying again in 60 seconds..."
        sys.stdout.flush()
        # CREATING THE E-MAIL VARIABLES AND SETS DEFAULT VALUES
        g = open('/python/'+my_root+'/error_email'+my_ticker+'.txt','w')
        g.write(str(e))
        g = open('/python/'+my_root+'/error_email'+my_ticker+'.txt','r')
        EMAIL_TO = ["maxim.lott@gmail.com"]
        EMAIL_FROM = "maxims.program@gmail.com" # TODO - probably set same as eboconfig.Email.smpt_username but think aobut it later
        EMAIL_SUBJECT = "Betfarer Error"
        DATE_FORMAT = "%m/%d/%Y"
        EMAIL_SPACE = ", "
        # Sets the body of the e-mail to the contents of the daily ranking list
        DATA= g.read()
        # DEFINES THE STRUCTURE OF THE E-MAIL TO BE SENT
        def send_email():
            if not eboconfig.Email.enabled:
                print "Email not enabled, skipping error report email"
                return

            msg = MIMEText(DATA)
            msg['Subject'] = EMAIL_SUBJECT
            msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
            msg['From'] = EMAIL_FROM
            mail = smtplib.SMTP(eboconfig.Email.smtp_server, eboconfig.Email.smtp_port)
            mail.starttls()
            mail.login(eboconfig.Email.smtp_username, eboconfig.Email.smtp_password)
            mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            mail.quit()
        print str(e)
        sys.stdout.flush()
        send_email()
        g.close()
    except Exception,e:
        print "!!! EMAIL NOT WORKING !!!"
        print str(e)
        pass

### Version tracking
# 1.0.1 - 1.0.3: Many various fixes
# 1.0.4: Added robustness to error emails, so that email failure no longer crashes the program
# 1.0.5: Minor html text changes
# 1.0.6: Major bug fixed; contracts had been setting to zero based on Betfair's NEXT contract rather than
# ...the one in quesiton. Caused Sanders, Huckabee, Kasich, to be wrongly set to 0 and thus slightly off.
# ... for future data adjustments: Sanders +3.2%, Kasich +0%, Huckabee +.1%. Or look at daily emails.
# 1.0.7: Added Stossel to html. Added several important changes,
# ... such as twitter handles and, more majorly, Google chart-formatted data tracking.
# ... most critically, this is the first server version!
# ... if you ever have to convert that "data counter" data format to Google format manually again
# ... you must first do a manual find / replace to eliminate all ^p and all double-spaces
# 1.0.8: Added drop-down menus!
#