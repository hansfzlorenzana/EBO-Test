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
MARKET_POLYMARKET = "Polymarket_Old"
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
    MARKET_BETFAIR,
    #MARKET_POLYMARKET,
    MARKET_PREDICTIT,
    MARKET_SMARKETS,
    #MARKET_FTX,
    MARKET_POLYMARKET_NEW,
]

NORMALIZED_MARKETS = USED_MARKETS

my_ticker = "_PRES_2024"
my_html_address = "President2024" #program automatically inserts ".html"
my_root = "2024/PRESIDENT"# no slashes before or after

my_Smarkets_market_name = "2024 presidential election winner"
my_Betfair_URL = "https://ero.betfair.ro/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=USD&locale=en_GB&marketIds=1.176878927&rollupLimit=25&rollupModel=STAKE&types=MARKET_STATE,MARKET_RATES,MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_STATE,RUNNER_EXCHANGE_PRICES_BEST,RUNNER_METADATA,MARKET_LICENCE,MARKET_LINE_RANGE_INFO"
#H#For Predict, only enter the ID# below. Do not edit "my_PredictIt_URL" directly. You'll find ID in the url of the Betfair market. ID looks like, e.g.: 6867
PredictIt_ID = "7456"
my_PredictIt_URL = "https://www.predictit.org/api/marketdata/markets/"+str(PredictIt_ID)
my_FTX_URL = "https://ftx.com/api/futures/"
my_Polymarket_URL = "https://polymarket.com/event/presidential-election-winner-2024"

column_title = "US Presidency 2024"

time_created = "Since 10am Jan 2"

# below must be reflected in price_log file
# 1)name to search in Betfair, 2)name in price log & photo, 3)wiki

#Betfair
Betfair_manual_entry = [
    ("Kamala Harris","Harris",  ""),
    ("Joe Biden","Biden",  ""),
    ("Donald Trump","Trump",  ""),
    ("Mike Pence","Pence",  ""),
    ("Bernie Sanders","Sanders",  ""),
    ("Marco Rubio","Rubio",  ""),
    ("Andrew Cuomo","Cuomo",  ""),
    ("Tom Cotton","Cotton",  ""),
    ("Ted Cruz","Cruz",  ""),
    ("Nikki Haley", "Haley",""),
    ("Alexandria Ocasio-Cortez", "Cortez",""),
    ("Josh Hawley", "Hawley",""),
    ("Donald Trump Jr.","Trump_Jr",  ""),
    ("Ivanka Trump","I_Trump",  ""),
    ("Michelle Obama", "Obama",""),
    ("Elizabeth Warren","Warren",  ""),
    ("Mike Pompeo","Pompeo",  ""),
    ("Ron DeSantis","DeSantis",  ""),
    ("Pete Buttigieg","Buttigieg",  ""),
    ("Tucker Carlson","Carlson",  ""),
    ("Kristi Noem","Noem",  ""),
    ("Gavin Newsom","Newsom",  ""),
    ("Vivek Ramaswamy","Ramaswamy",  ""), 
    ("Robert F.Kennedy Jr","Kennedy",  ""), 
    ("Chris Christie","Christie",  ""), 
]
#PredictIt
PredictIt_manual_entry = [
    ("Harris","Harris",  ""),
    ("Biden","Biden",  ""),
    ("Trump","Trump",  "https://ftx.com/trade/TRUMP"),
    (None,"Pence",  ""),
    (None,"Sanders",  ""),
    (None,"Rubio",  ""),
    (None,"Cuomo",  ""),
    (None,"Cotton",  ""),
    (None,"Cruz",  ""),
    (None, "Haley",""),
    (None, "Cortez",""),
    (None, "Hawley",""),
    (None,"Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    (None, "Obama",""),
    (None,"Warren",  ""),
    (None,"Pompeo",  ""),
    ("DeSantis","DeSantis",  ""),
    (None,"Buttigieg",  ""),
    (None,"Carlson",  ""),
    (None,"Noem",  ""),
    (None,"Newsom",  ""),
    (None,"Ramaswamy",  ""), 
    (None,"Kennedy",  ""), 
    (None,"Christie",  ""), 
]
#FTX
FTX_manual_entry = [
    (None,"Harris",  ""),
    (None,"Biden",  ""),
    ("TRUMP2024","Trump",  "https://ftx.com/trade/TRUMP"),
    (None,"Pence",  ""),
    (None,"Sanders",  ""),
    (None,"Rubio",  ""),
    (None,"Cuomo",  ""),
    (None,"Cotton",  ""),
    (None,"Cruz",  ""),
    (None, "Haley",""),
    (None, "Cortez",""),
    (None, "Hawley",""),
    (None,"Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    (None, "Obama",""),
    (None,"Warren",  ""),
    (None,"Pompeo",  ""),
    (None,"DeSantis",  ""),
    (None,"Buttigieg",  ""),
    (None,"Carlson",  ""),
    (None,"Noem",  ""),
    (None,"Newsom",  ""),
    (None,"Christie",  ""), 
]
#Smarkets
Smarkets_manual_entry = [
    ("Kamala Harris","Harris",  ""),
    ("Joe Biden","Biden",  ""),
    ("Donald Trump","Trump",  ""),
    ("Mike Pence","Pence",  ""),
    ("Bernie Sanders","Sanders",  ""),
    ("Marco Rubio","Rubio",  ""),
    ("Andrew Cuomo","Cuomo",  ""),
    ("Tom Cotton","Cotton",  ""),
    ("Ted Cruz","Cruz",  ""),
    ("Nikki Haley", "Haley",""),
    ("Alexandria Ocasio-Cortez", "Cortez",""),
    ("Josh Hawley", "Hawley",""),
    ("Donald Trump Jr.","Trump_Jr",  ""),
    ("Ivanka Trump","I_Trump",  ""),
    ("Michelle Obama", "Obama",""),
    ("Elizabeth Warren","Warren",  ""),
    ("Mike Pompeo","Pompeo",  ""),
    ("Ron DeSantis","DeSantis",  ""),
    ("Pete Buttigieg","Buttigieg",  ""),
    ("Tucker Carlson","Carlson",  ""),
    ("Kristi Noem","Noem",  ""),
    ("Gavin Newsom","Newsom",  ""),
    ("Vivek Ramaswamy","Ramaswamy",  ""), 
    ("Robert F. Kennedy Jr.","Kennedy",  ""), 
    ("Chris Christie","Christie",  ""), 
]

Polymarket_manual_entry = [
    ((253597,"Yes"),"Harris",  ""),
    ((253592,"Yes"),"Biden",  ""),
    ((253591,"Yes"),"Trump",  ""),
    (None,"Pence",  ""),
    ((253640,"Yes"),"Sanders",  ""),
    (None,"Rubio",  ""),
    (None,"Cuomo",  ""),
    (None,"Cotton",  ""),
    (None,"Cruz",  ""),
    ((253593,"Yes"), "Haley",""),
    ((253635,"Yes"), "Cortez",""),
    (None, "Hawley",""),
    (None,"Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    ((253609,"Yes"), "Obama",""),
    ((253639,"Yes"),"Warren",  ""),
    (None,"Pompeo",  ""),
    ((253596,"Yes"),"DeSantis",  ""),
    (None,"Buttigieg",  ""),
    (None,"Carlson",  ""),
    (None,"Noem",  ""),
    ((253594,"Yes"),"Newsom",  ""),
    ((253598,"Yes"),"Ramaswamy",  ""), 
    ((253595,"Yes"),"Kennedy",  ""), 
    ((253634,"Yes"),"Christie",  ""), ]

Polymarket_new_manual_entry = [
    ((253597,"Yes"),"Harris",  ""),
    ((253592,"Yes"),"Biden",  ""),
    ((253591,"Yes"),"Trump",  ""),
    (None,"Pence",  ""),
    ((253640,"Yes"),"Sanders",  ""),
    (None,"Rubio",  ""),
    (None,"Cuomo",  ""),
    (None,"Cotton",  ""),
    (None,"Cruz",  ""),
    ((253593,"Yes"), "Haley",""),
    ((253635,"Yes"), "Cortez",""),
    (None, "Hawley",""),
    (None,"Trump_Jr",  ""),
    (None,"I_Trump",  ""),
    ((253609,"Yes"), "Obama",""),
    ((253639,"Yes"),"Warren",  ""),
    (None,"Pompeo",  ""),
    ((253596,"Yes"),"DeSantis",  ""),
    (None,"Buttigieg",  ""),
    (None,"Carlson",  ""),
    (None,"Noem",  ""),
    ((253594,"Yes"),"Newsom",  ""),
    ((253598,"Yes"),"Ramaswamy",  ""), 
    ((253595,"Yes"),"Kennedy",  ""), 
    ((253634,"Yes"),"Christie",  ""), ]

Smarets_excluded = ""
race_description = """Winner of Presidential election held on Nov 5 2024"""

### CHARTING ENTRIES
custom_chart_labels = ""
# below always starts with 0. make string empty for defaults
chart_label_ordering = "var viewColumns = [0, 1, 2, 3, 10, 18, 22, 17, 19, 23, 24];view.setColumns(viewColumns);"
#!# NOTE: if you move a label up, must move color with it. Color is stuck to position.
# Make string empty for defaults
chart_colors = "colors: ['purple', 'blue', 'DarkOrange', '#FF1493', '#33ff77', 'gold', 'pink', '#33fc78', '#778899',],"

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
