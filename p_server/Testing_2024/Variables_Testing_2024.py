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
# from Tkinter import Tk
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
    eboconfig = imp.load_source("eboconfig", "EBO-Test/p_server/eboconfig.py")
except:
    print ("Error: Need a valid ./p_server/eboconfig.py file. See ./p_server/eboconfig.py.example for reference.")
    raise

MAX_LIMITED_ROWS = 50 # max number of contracts to list, to avoid overwhelming people

#time.sleep(60*60*5)
counter = 0
error_counter = 0

#Consts for the different markets, used in various places in the code
MARKET_BETFAIR = "Betfair"
MARKET_PREDICTIT = "PredictIt"
MARKET_FTX = "FTX"
MARKET_SMARKETS = "Smarkets"
MARKET_POLYMARKET_NEW = "Polymarket"

MARKET_LINKS = {
        MARKET_SMARKETS: '<a href="https://smarkets.com">Smarkets</a>',
        MARKET_PREDICTIT: '<a href="https://www.predictit.org">PredictIt</a>',
        MARKET_FTX: '<a href="https://ftx.com">FTX.com</a>',
        MARKET_BETFAIR: '<a href="https://www.betfair.com/exchange/plus/american-football/market/1.168283812">Betfair</a>',
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

###########HUMAN EDITED#############
USED_MARKETS = [
    # MARKET_BETFAIR,
    # MARKET_PREDICTIT,
    # # #MARKET_POLYMARKET,
    # MARKET_SMARKETS,
    #MARKET_FTX,
    #MARKET_POLYMARKET_CLOB,
    MARKET_POLYMARKET_NEW,
]
my_ticker = "Testing_2024" #MUST be in the title of "price_log" file
my_html_address = "Testing_2024" #program automatically inserts ".html"
my_root = "Testing_2024"# no slashes before or after


NORMALIZED_MARKETS = USED_MARKETS

# For Smarkets, find the market name in the this link: https://api.smarkets.com/oddsfeed.xml.gz?affiliate_key=Fg41peK2pkvrTyFo
my_Smarkets_market_name = "2024 Republican VP nominee" #INSTEAD of URL. Case sensitive
#For Betfair, it's the "1.223236887" that needs to be replaced, based on the similarly-formatted number in the Betfair URL
my_Betfair_URL = "https://ero.betfair.ro/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=USD&locale=en_GB&marketIds=1.190717853&rollupLimit=25&rollupModel=STAKE&types=MARKET_STATE,MARKET_RATES,MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_STATE,RUNNER_EXCHANGE_PRICES_BEST,RUNNER_METADATA,MARKET_LICENCE,MARKET_LINE_RANGE_INFO"
#For PredictIt, the last 4 digits correspond with the 4-digit code in the PredictIt URL
my_PredictIt_URL = "https://www.predictit.org/api/marketdata/markets/8069" 
#For PolyMarket, just use the url of the market to query
my_Polymarket_URL = "https://polymarket.com/event/republican-vp-nominee"

column_title = "GOP VP Nominee"

time_created = "Since 11am Jan 24"

# below must be reflected in price_log file
# Betfair 1st col format is generally "firstname lastname". 1st col is used for scraping, 2nd for internal handling
Betfair_manual_entry = [
        ("Elise Stefanik","Stefanik",""),
        ("Kristi Noem","Noem",""),
        ("Tim Scott","TimScott",""),
        ("Vivek Ramaswamy","Ramaswamy",""),
        ("Nikki Haley","Haley",""),
        ("Kari Lake","Lake",""),
        ("Byron Donalds","Donalds",""),
        ("Ron DeSantis","DeSantis",""),
        ("Robert F.Kennedy Jr","Kennedy",""),
        ("Ben Carson","Carson",""),
        ("J.D. Vance","Vance",""),
        ]
FTX_manual_entry = [
        ("Trump","Trump",""),
        ("DeSantis","DeSantis",""),
        ("Haley","Haley",""),
        ("Ramaswamy","Ramaswamy","")]
Smarkets_manual_entry = [
        ("Elise Stefanik","Stefanik",""),
        ("Kristi Noem","Noem",""),
        ("Tim Scott","TimScott",""),
        ("Vivek Ramaswamy","Ramaswamy",""),
        ("Nikki Haley","Haley",""),
        ("Kari Lake","Lake",""),
        (None,"Donalds",""),
        ("Ron DeSantis","DeSantis",""),
        (None,"Kennedy",""),
        ("Ben Carson","Carson",""),
        ("JD Vance","Vance",""),
        ]
# PredictIt 1st col format is generally just "lastname". In the raw, it's what's in <ShortName></ShortName>
PredictIt_manual_entry = [
        ("Stefanik","Stefanik",""),
        ("Noem","Noem",""),
        ("Scott","TimScott",""),
        ("Ramaswamy","Ramaswamy",""),
        ("Haley","Haley",""),
        ("Lake","Lake",""),
        ("Donalds","Donalds",""),
        ("DeSantis","DeSantis",""),
        ("RFK Jr.","Kennedy",""),
        (None,"Carson",""),
        (None,"Vance",""),
        ]

# For Polymarket, find the market ID by searching the url: 
Polymarket_new_manual_entry = [
        ((253993,"Yes"),"Stefanik",""),
        ((253994,"Yes"),"Noem",""),
        ((253992,"Yes"),"TimScott",""),
        ((253995,"Yes"),"Ramaswamy",""),
        ((253996,"Yes"),"Haley",""),
        ((253997,"Yes"),"Lake",""),
        ((253998,"Yes"),"Donalds",""),
        ((254000,"Yes"),"DeSantis",""),
        ((253999,"Yes"),"Kennedy",""),
        ((254005,"Yes"),"Carson",""),
        ((254112,"Yes"),"Vance",""),
        ]

race_description = """Republican Vice Presidential Nominee in 2024"""

### CHARTING ENTRIES
custom_chart_labels = ""
# below always starts with 0. make string empty for defaults
chart_label_ordering = ""
#!# NOTE: if you move a label up, must move color with it. Color is stuck to position.
# Make string empty for defaults
chart_colors = ""

# Dummy that controls whether "other" % shows at bottom
OthersOnPage = 1
# Dummy; 1 = normalize if sum of odds < 1. 0 if don't normalize for that due  
NormUnder100 = 0

###########END HUMAN EDITED#############

#~# this should be moved to a seperate page and called from there to make changes easier
Ad_bar = ''''''

# allow binary creator
binary_creator = 0

# price_log must be made to match if you add any

# Actually runs program
try:
    with open ("./p_server/FTX_Universal_Machine.py", "r") as myfile:
        PredictIt_Machine_Code = myfile.read()

    exec(PredictIt_Machine_Code)

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
        print "error at:"+str(now)+"... trying again in 60 seconds..."
        # CREATING THE E-MAIL VARIABLES AND SETS DEFAULT VALUES
        g = open('./p_server/'+my_root+'/error_email'+my_ticker+'.txt','w')
        g.write(str(e))
        g = open('./p_server/'+my_root+'/error_email'+my_ticker+'.txt','r')
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SMTP_USERNAME = "maxims.program@gmail.com"
        SMTP_PASSWORD = "Koins1.-"
        EMAIL_TO = ["maxim.lott@gmail.com"]
        EMAIL_FROM = "maxims.program@gmail.com"
        EMAIL_SUBJECT = "Betfarer Error"
        DATE_FORMAT = "%m/%d/%Y"
        EMAIL_SPACE = ", "
        # Sets the body of the e-mail to the contents of the daily ranking list
        DATA= g.read()
        # DEFINES THE STRUCTURE OF THE E-MAIL TO BE SENT
        def send_email():
            msg = MIMEText(DATA)
            msg['Subject'] = EMAIL_SUBJECT
            msg['To'] = EMAIL_SPACE.join(EMAIL_TO)
            msg['From'] = EMAIL_FROM
            mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            mail.starttls()
            mail.login(SMTP_USERNAME, SMTP_PASSWORD)
            mail.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
            mail.quit()
        print str(e)
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
