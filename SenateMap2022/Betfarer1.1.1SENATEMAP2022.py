#!/usr/bin/python
#import library to do http requests:
from __future__ import division             #enables division with decimals
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
socket.setdefaulttimeout(35)
import subprocess
ST_counter = 0
url_dict = ("7609","7749","7769","7884","7016","7017","7024","7085","7107","7112","7130","7131","7132","7176","7204","7208","7532","7548")
spec_format = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,)
spec_detail = ("Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic",)
st_dict = ("VT","OR","WA","IL","PA","NC","FL","OH","GA","AZ","NH","NV","WI","AK","MO","IA","UT","CO",)
rep_cands_list = ("Malloy","Perkins","Smiley","Salvi","Oz","Budd","Rubio","Vance","Walker","Masters","Bolduc","Laxalt","Johnson","Republican","Schmitt","Grassley","Republican","ODea",)
dem_cands_list = ("Welch","Wyden","Murray","Duckworth","Fetterman","Beasley","Demings","Ryan","Warnock","Kelly","Hassan","Cortez Masto","Barnes","Democratic","Valentine","Franken","Democratic","Bennet",) 

votes_dict = (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,)
final_dict = {}
Betfair_dummy = 0
source_header = 'Odds from <a href="http://www.predictit.org/promo/electionbetting>PredictIt</a>'
source_footer = ''
US_stCAND_dict = {}
stCAND_dict = {}
votes_finder = {}
ST_raw_history = ""
REP_votes = 41#(12 up with no bets; 29 not up)
DEM_votes = 41#(5 up with no bets; 36 not up)

def US_oddsfinder(state,race,cand_FULL_name,cand_last_name_PLUS_bid_PLUS_race,cand_last_name_PLUS_ask_PLUS_race,cand_last_name_PLUS_odds_PLUS_race):
    global ST_raw_history
    global ST_data_counter
    global now
    user_PREDICTIT_STATE = "https://www.predictit.org/api/marketdata/markets/"+str(url)
    time.sleep(3)
    #### BETFAIR HERE

    with open ("/python/SenateMap2022/Betfarer/price_log_"+str(state)+".txt", "r") as myfile:
        ST_raw_history = myfile.read()
    #print ST_raw_history
    find_ST_data_counter_1 = ST_raw_history.split("***data_counter***")
    ## "[::-1]" is an odd piece of code that reverses the list
    find_ST_data_counter_2= find_ST_data_counter_1[::-1]
    ST_data_counter = int(find_ST_data_counter_2[0])
    print ST_data_counter

    now = str(time.strftime('%l:%M%p %Z on %b %d, %Y'))
    print now

    ### BETFAIR MACHINE HERE WHEN ADDING
        
    ###US_PREDICT_IT###DEM
    print "user_PREDICTIT_STATE"
    print user_PREDICTIT_STATE
    #US_STATE_raw = urllib2.urlopen(str(user_PREDICTIT_STATE)).read()
    US_STATE_raw = subprocess.check_output(["curl", "-H", "Cookie: bfsd=ts=$(date +%s)000|st=p; betexPtk=betexCurrency%3DUSD%7EbetexTimeZone%3DAmerica%2FNew_York%7EbetexRegion%3DGBR%7EbetexLocale%3Den", user_PREDICTIT_STATE], shell=False)

    parsable_US_STATE_raw = US_STATE_raw.replace('"', '')    
    parsable_US_STATE_raw = parsable_US_STATE_raw.replace('Democractic', 'Democratic')
    parsable_US_STATE_raw = ''.join(parsable_US_STATE_raw.split())
    print parsable_US_STATE_raw

    search_name = "shortName:"+str(cand_FULL_name)+",status"
    Candidate_raw_step_1 = eval(str("parsable_US_"+race+"_raw")).split(str(search_name))[1]
    Candidate_raw_step_2 = Candidate_raw_step_1.split("image")[0]
    print "test2"
    # find bid
    Candidate_raw_step_3 = Candidate_raw_step_2.split("bestSellYesCost:")[1]
    Candidate_raw_step_4 = Candidate_raw_step_3.split(",bestSellNoCost:")[0]
    if Candidate_raw_step_4 == "null":
        # find last trade (final, settled) price
        Candidate_raw_step_LT = Candidate_raw_step_2.split("lastTradePrice:")[1]
        Candidate_raw_step_4 = Candidate_raw_step_LT.split(",bestBuyYesCost")[0]
        US_bid = float(Candidate_raw_step_4)
    else:
        US_bid = float(Candidate_raw_step_4)
    print "test3"
    # find ask
    Candidate_raw_ASK_step_3 = Candidate_raw_step_2.split("bestBuyYesCost:")[1]
    Candidate_raw_ASK_step_4 = Candidate_raw_ASK_step_3.split(",bestBuyNoCost:")[0]
    if Candidate_raw_ASK_step_4 == "null":
        US_ask = US_odds = float(Candidate_raw_step_4)
    else: 
        US_ask = float(Candidate_raw_ASK_step_4)
    print "test4"
    # If low liquidity, go with bid. Else, take avg of bid and ask to get market value estimate
    if US_ask - US_bid > .1:
        US_odds = US_bid
    elif US_bid == 0:
        US_odds = 0
    else:
        US_odds = (US_bid+US_ask)/2
            
    US_stCAND_dict[cand_last_name_PLUS_bid_PLUS_race] = US_bid
    US_stCAND_dict[cand_last_name_PLUS_ask_PLUS_race] = US_ask
    US_stCAND_dict[cand_last_name_PLUS_odds_PLUS_race] = US_odds
    print cand_FULL_name
    print "PREDICT_IT"
    print state
    print US_stCAND_dict[cand_last_name_PLUS_bid_PLUS_race]
    print US_stCAND_dict[cand_last_name_PLUS_ask_PLUS_race]
    print US_stCAND_dict[cand_last_name_PLUS_odds_PLUS_race]
    #print "*** full dict:"
    #print US_stCAND_dict
        

"""
for number in range(0,24):
    state = st_dict[counter]
    counter = counter + 1    
    eval("US_stCAND_dict[Democratic_odds_"+str(state)+"] == 0")
    print "bing"
"""
################################################!!############### INSTANCE
for number in range(0,18):
    # should Have try!!!
    url = url_dict[ST_counter]
    state = st_dict[ST_counter]
    votes = votes_dict[ST_counter]
    votes_finder[state] = votes
    spec_binary = spec_format[ST_counter]
    detail = spec_detail[ST_counter]
    rep_cand = rep_cands_list[ST_counter]
    dem_cand = dem_cands_list[ST_counter]
    ST_counter = ST_counter + 1

    if spec_binary == 0:
        US_oddsfinder(str(state),"STATE","Democratic","Democratic_bid_"+str(state),"Democratic_ask_"+str(state),"Democratic_odds_"+str(state))
        US_oddsfinder(str(state),"STATE","Republican","Republican_bid_"+str(state),"Republican_ask_"+str(state),"Republican_odds_"+str(state))
        print "GATHERING WORKED"
    """
    if spec_binary == 1:
        US_oddsfinder(str(state),"STATE",str(detail),"Republican_bid_"+str(state),"Republican_ask_"+str(state),"Republican_odds_"+str(state))
        US_stCAND_dict["Democratic_bid_"+str(state)]= 1 - US_stCAND_dict["Republican_bid_"+str(state)]
        US_stCAND_dict["Democratic_ask_"+str(state)]= 1 - US_stCAND_dict["Republican_ask_"+str(state)]
        US_stCAND_dict["Democratic_odds_"+str(state)]= 1 - US_stCAND_dict["Republican_odds_"+str(state)]
    if spec_binary == 2:
        US_oddsfinder(str(state),"STATE",str(detail),"Democratic_bid_"+str(state),"Democratic_ask_"+str(state),"Democratic_odds_"+str(state))
        US_stCAND_dict["Republican_bid_"+str(state)]= 1 - US_stCAND_dict["Democratic_bid_"+str(state)]
        US_stCAND_dict["Republican_ask_"+str(state)]= 1 - US_stCAND_dict["Democratic_ask_"+str(state)]
        US_stCAND_dict["Republican_odds_"+str(state)]= 1 - US_stCAND_dict["Democratic_odds_"+str(state)]
    """ 
    if Betfair_dummy == 0:
        stCAND_dict = {}
        stCAND_dict.clear()
        stCAND_dict = US_stCAND_dict
   
    print US_stCAND_dict
    odds_total = eval("US_stCAND_dict['Democratic_odds_"+str(state)+"']+US_stCAND_dict['Republican_odds_"+str(state)+"']")
    # + US_stCAND_dict['Republican_odds_"+str(state)+"']")
    print odds_total
    if odds_total > 1:    
        US_STATE_normalizer = 1/odds_total
        if US_STATE_normalizer > 1:
            US_STATE_normalizer = 1   
    else:
        US_STATE_normalizer = 1
    BETFAIR_STATE_normalizer = US_STATE_normalizer

    print US_STATE_normalizer
    print "b"
    print BETFAIR_STATE_normalizer
    #########
    ###ODDS##
    #########

    ### Putting them all together as a tuple
    odds_tuples = [
        (str(state)+'_DEM', eval("(stCAND_dict['Democratic_odds_"+str(state)+"']*BETFAIR_STATE_normalizer + US_stCAND_dict['Democratic_odds_"+str(state)+"']*US_STATE_normalizer)/2")),
        (str(state)+'_GOP', eval("(stCAND_dict['Republican_odds_"+str(state)+"']*BETFAIR_STATE_normalizer + US_stCAND_dict['Republican_odds_"+str(state)+"']*US_STATE_normalizer)/2")),
    ]
    print odds_tuples
    print "worked 33"
    ## sorting the odds
    odds_sorted = sorted(odds_tuples, key=lambda odds: odds[1], reverse=True)
    print odds_sorted

    ### RETRIEVING PAST ODDS
    ### NOTE: This section MUST have a past odds file with past data to run off of. Must exist before running pgrm. Use backup file if needed.
    key_1 = "***data_counter***"+str(ST_data_counter-41) #-int(round((12*24*7),0 "116" "116" #
    key_2 = "***data_counter***"+str(ST_data_counter-40) #-int(round((12*24*7),0 "117" "117" # (oldest possible)
    print key_1
    print key_2
    selector_1 = ST_raw_history.split(str(key_1))
    #print "selector_1: ",selector_1
    #print "selector_1[1}: ",selector_1[1]
    selector_2 = selector_1[1]
    #print "selector_2: ",selector_2
    selector_3 = selector_2.split(str(key_2))
    #print "selector_3: ",selector_3
    selector_4 = selector_3[0]
    #print "selector_4: ",selector_4
    # now we have the correct slice, just need to split by party & kill timestamp
    selector_1 = selector_4.split("]*WIN*[")[0]
    #print "selector_1: ", selector_1
    selection = selector_1.split("[")[1]
    print "good"
    print selection

    # final tuples (eval makes them active tuples rather than just strings.)
    past_odds = eval(selection)
    print "hi"

    def arrowfinder(a):
        if a <= -.0005:
            a = '<img src="red.png" width="14" height="14">'
        elif a >= 0.0005:
            a = '<img src="green.png" width="14" height="14"> '
        elif a >= 0 and a < .001:
            a = '+'
        else:
            a = ""
        return a
    print "hi"

    
    odds_w_changes_tuples = [
        (str(state)+'_DEM', (stCAND_dict["Democratic_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Democratic_odds_"+str(state)]*US_STATE_normalizer)/2,(stCAND_dict["Democratic_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Democratic_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[0][1],arrowfinder((stCAND_dict["Democratic_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Democratic_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[0][1])),
        (str(state)+'_GOP', (stCAND_dict["Republican_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Republican_odds_"+str(state)]*US_STATE_normalizer)/2,(stCAND_dict["Republican_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Republican_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[1][1],arrowfinder((stCAND_dict["Republican_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Republican_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[1][1])),
    ]
    
    print "hi"
    odds_sorted = sorted(odds_w_changes_tuples, key=lambda odds_w_changes: odds_w_changes[1], reverse=True)
    exec("odds_sorted"+str(state)+" = odds_sorted")
    
    print "~~~~~~~~~~~~~~~~"
    print state
    print str("odds_sorted"+str(state))
    print "~~~~~~~~~~~~~~~~"

    def killer(a):
        if a == 0:
            a = a #""
        else:
            a = a
        return a

    final_dict[state] = odds_w_changes_tuples

    ### Color-coding
    print "hi"
    print "boo!"
    if eval("odds_sorted"+str(state)+"[0][0]") == str(state+'_DEM'):
        exec("first_result_to_display_"+str(state)+" = round(100*final_dict[state][0][1],1)")
        exec("first_color_to_display_"+str(state)+" = '0000ff>"+str(dem_cand)+": '")
        exec("second_result_to_display_"+str(state)+" = round(100*final_dict[state][1][1],1)")
        exec("second_color_to_display_"+str(state)+" = 'ff0000>"+str(rep_cand)+": '")
        exec("change_to_display_"+str(state)+" = str(final_dict[state][0][3]) + str(round(100*final_dict[state][0][2],1))")
        print "final display odds for: " + str(state)+" = DEM " + str(eval("first_result_to_display_"+str(state)))
        DEM_votes = DEM_votes + votes
        print "DEM is leading in "+str(state)
        if eval("odds_sorted"+str(state)+"[0][1]") >= .9:
            exec("color_"+str(state)+"= '0000b3'")
        elif eval("odds_sorted"+str(state)+"[0][1]") >= .8:
            exec("color_"+str(state)+"= '0000ff'")
        elif eval("odds_sorted"+str(state)+"[0][1]") >= .7:
            exec("color_"+str(state)+"= '4d4dff'")
        elif eval("odds_sorted"+str(state)+"[0][1]") >= .6:
            exec("color_"+str(state)+"= '9999ff'")
        elif eval("odds_sorted"+str(state)+"[0][1]") > .5:
            exec("color_"+str(state)+"= 'e6e6ff'")
        else:#if UNDER 50%, only relevant if 3rd parties
            exec("color_"+str(state)+"= 'ffffff'")
                
    else:
        print "REP is leading in "+str(state)

    if eval("odds_sorted"+str(state)+"[0][0]") == str(state+'_GOP'):
        exec("first_result_to_display_"+str(state)+" = round(100*final_dict[state][1][1],1)")
        exec("first_color_to_display_"+str(state)+" = 'ff0000>"+str(rep_cand)+": '")
        exec("second_result_to_display_"+str(state)+" = round(100*final_dict[state][0][1],1)")
        exec("second_color_to_display_"+str(state)+" = '0000ff>"+str(dem_cand)+": '")
        exec("change_to_display_"+str(state)+" = str(final_dict[state][1][3]) + str(round(100*final_dict[state][1][2],1))")
        print "final display odds for: " + str(state)+" = GOP " + str(eval("second_result_to_display_"+str(state)))
        REP_votes = REP_votes + votes
        if eval("odds_sorted"+str(state)+"[0][1]") >= .9:
            exec("color_"+str(state)+"= 'b30000'")
        elif eval("odds_sorted"+str(state)+"[0][1]") >= .8:
            exec("color_"+str(state)+"= 'ff0000'")
        elif eval("odds_sorted"+str(state)+"[0][1]") >= .7:
            exec("color_"+str(state)+"= 'ff4d4d'")
        elif eval("odds_sorted"+str(state)+"[0][1]") >= .6:
            exec("color_"+str(state)+"= 'ff9999'")
        elif eval("odds_sorted"+str(state)+"[0][1]") > .5:
            exec("color_"+str(state)+"= 'ffe6e6'")
        else:#if UNDER 50%, only relevant if 3rd parties
            exec("color_"+str(state)+"= 'ffffff'")
    else:
        print ""

    
    ## write past data into file
    ST_data_counter = ST_data_counter + 1
    # store to file  ## Note: "test" in label is fine...
    fp = open("/python/SenateMap2022/Betfarer/price_log_"+str(state)+".txt",'a')
    fp.write(str(now)+" "), fp.write(str(odds_tuples)+"*WIN*["), fp.write('***data_counter***'+str(ST_data_counter)+' ')
    fp.close()
    print "info successfully saved"
    print "sleeping for 3 seconds so PredictIt can handle this"
    time.sleep(10)

print "votes_finder",votes_finder
    
### ! THIS IS ACTUALLY HTML STRING FOR *EVERYTHING*, DESPITE THE NAME
finalwinner_HTML_string = ('''
<!--...-->
    <table border=0 class="inlineTable">
        <tr>
            <td>

            <style class="cp-pen-styles">

#selected-state {
font-size: 21pt;
margin-bottom: 20px;
font-style: bold;
font-family: "Times New Roman" !important;
}

#map {width: 700px; height: 450px; ;}
</style>
<div id="selected-state"><span><b><u>Senate Seats 2022</u> (estimate: <font color=#0000ff>'''+str(DEM_votes)+'''</font>-<font color=#ff0000>'''+str(REP_votes)+'''</font>. Hover over states)</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span></span></div></div>
<div id="map"></div>
<script src='https://electionbettingodds.com/stopExecutionOnTimeout.js?t=1'></script>
<script src='https://electionbettingodds.com/jquery.min.js'></script>
<script src='https://electionbettingodds.com/raphael-min.js'></script>
<script src='https://electionbettingodds.com/jquery.usmap.js'></script>
<script src='https://electionbettingodds.com/color.jquery.js'></script>
<script>$(document).ready(function () {
$('#map').usmap({
mouseover: function(event, data) {
  $('#selected-state > span').text(data.name).css({"font-weight": "bold", "color": "#FFFFFF"});
    },
    mouseout: function (event, data) {
        $('#selected-state > span').html('<b>Hover over it to find out</b>').css({
            'font-weight': 'normal',
            'color': '#FFFFFF'
        });
    }
});
});
    $('#map').usmap({
showLabels: false,
      'stateStyles': {
        fill: "#FFFFFF",
        stroke: "#000000",
        "stroke-width": 3,
        "stroke-linejoin": "round",
        scale: [1, 1]
      },
      stateHoverStyles: {
        fill: "#000000",
        stroke: "#000000",
        scale: [1.1, 1.1]
      },
      labelBackingStyles: {
        fill: "#000000",
        stroke: "#000000",
        "stroke-width": 1,
        "stroke-linejoin": "round",
        scale: [1, 1]
      },
      
      // The styles for the hover
      labelBackingHoverStyles: {
        fill: "#000000",
        stroke: "#000000",
      },
      labelTextStyles: {
      fill: "#222",
        'stroke': 'none',
        'font-weight': 300,
        'stroke-width': 0,
        'font-size': '21pt'
      },
stateSpecificStyles: {
AL: {fill: "#b30000",'stroke-width': 1.5,'stroke': "#000000"},
AK: {fill: "#'''+str(color_AK)+'''",'stroke-width': 1.5,'stroke': "#000000"},
AZ: {fill: "#'''+str(color_AZ)+'''",'stroke-width': 1.5,'stroke': "#000000"},
AR: {fill: "#b30000",'stroke-width': 1.5,'stroke': "#000000"},
CA: {fill: "#0000b3",'stroke-width': 1.5,'stroke': "#000000"},
CO: {fill: "#'''+str(color_CO)+'''",'stroke-width': 1.5,'stroke': "#000000"},
CT: {fill: "#0000b3", 'stroke-width': 1.5,'stroke': "#000000"},
DE: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
FL: {fill: "#'''+str(color_FL)+'''",'stroke-width': 1.5,'stroke': "#000000"},
GA: {fill: "#'''+str(color_GA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
HI: {fill: "#0000b3", 'stroke-width': 1.5,'stroke': "#000000"},
ID: {fill: "#b30000",'stroke-width': 1.5,'stroke': "#000000"},
IL: {fill: "#'''+str(color_IL)+'''",'stroke-width': 1.5,'stroke': "#000000"},
IN: {fill: "#b30000",'stroke-width': 1.5,'stroke': "#000000"},
IA: {fill: "#'''+str(color_IA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
KS: {fill: "#b30000", 'stroke-width': 1.5,'stroke': "#000000"},
KY: {fill: "#b30000", 'stroke-width': 1.5,'stroke': "#000000"},
LA: {fill: "#b30000",'stroke-width': 1.5,'stroke': "#000000"},
ME: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
MD: {fill: "#0000b3",'stroke-width': 1.5,'stroke': "#000000"},
MA: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
MI: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
MN: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
MS: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
MO: {fill: "#'''+str(color_MO)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MT: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
NE: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
NV: {fill: "#'''+str(color_NV)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NH: {fill: "#'''+str(color_NH)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NJ: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
NM: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
NY: {fill: "#0000b3",'stroke-width': 1.5,'stroke': "#000000"},
NC: {fill: "#'''+str(color_NC)+'''",'stroke-width': 1.5,'stroke': "#000000"},
ND: {fill: "#b30000",'stroke-width': 1.5,'stroke': "#000000"},
OH: {fill: "#'''+str(color_OH)+'''",'stroke-width': 1.5,'stroke': "#000000"},
OK: {fill: "#b30000", 'stroke-width': 1.5,'stroke': "#000000"},
OR: {fill: "#'''+str(color_OR)+'''",'stroke-width': 1.5,'stroke': "#000000"},
PA: {fill: "#'''+str(color_PA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
RI: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
SC: {fill: "#b30000", 'stroke-width': 1.5,'stroke': "#000000"},
SD: {fill: "#b30000", 'stroke-width': 1.5,'stroke': "#000000"},
TN: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
TX: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
UT: {fill: "#'''+str(color_UT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
VT: {fill: "#'''+str(color_VT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
VA: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
WA: {fill: "#'''+str(color_WA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
WV: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
WI: {fill: "#'''+str(color_WI)+'''",'stroke-width': 1.5,'stroke': "#000000"},
WY: {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
},

stateSpecificHoverStyles: {
'AL': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'AK': {fill: "#'''+str(color_AK)+'''",'stroke-width': 3,'stroke': "#000000"},
'AZ': {fill: "#'''+str(color_AZ)+'''",'stroke-width': 3,'stroke': "#000000"},
'AR': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'CA': {fill: "#0000b3",'stroke-width': 3,'stroke': "#000000"},
'CO': {fill: "#'''+str(color_CO)+'''",'stroke-width': 3,'stroke': "#000000"},
'CT': {fill: "#0000b3",'stroke-width': 3,'stroke': "#000000"},
'DE': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'FL': {fill: "#'''+str(color_FL)+'''",'stroke-width': 3,'stroke': "#000000"},
'GA': {fill: "#'''+str(color_GA)+'''",'stroke-width': 3,'stroke': "#000000"},
'HI': {fill: "#0000b3",'stroke-width': 3,'stroke': "#000000"},
'ID': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'IL': {fill: "#'''+str(color_IL)+'''",'stroke-width': 3,'stroke': "#000000"},
'IN': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'IA': {fill: "#'''+str(color_IA)+'''",'stroke-width': 3,'stroke': "#000000"},
'KS': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'KY': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'LA': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'ME': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'MD': {fill: "#0000b3",'stroke-width': 3,'stroke': "#000000"},
'MA': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'MI': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'MN': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'MS': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'MO': {fill: "#'''+str(color_MO)+'''",'stroke-width': 3,'stroke': "#000000"},
'MT': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'NE': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'NV': {fill: "#'''+str(color_NV)+'''",'stroke-width': 3,'stroke': "#000000"},
'NH': {fill: "#'''+str(color_NH)+'''",'stroke-width': 3,'stroke': "#000000"},
'NJ': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'NM': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'NY': {fill: "#0000b3",'stroke-width': 3,'stroke': "#000000"},
'NC': {fill: "#'''+str(color_NC)+'''",'stroke-width': 3,'stroke': "#000000"},
'ND': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'OH': {fill: "#'''+str(color_OH)+'''",'stroke-width': 3,'stroke': "#000000"},
'OK': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'OR': {fill: "#'''+str(color_OR)+'''",'stroke-width': 3,'stroke': "#000000"},
'PA': {fill: "#'''+str(color_PA)+'''",'stroke-width': 3,'stroke': "#000000"},
'RI': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'SC': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'SD': {fill: "#b30000",'stroke-width': 3,'stroke': "#000000"},
'TN': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'TX': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'UT': {fill: "#'''+str(color_UT)+'''",'stroke-width': 3,'stroke': "#000000"},
'VT': {fill: "#'''+str(color_VT)+'''",'stroke-width': 3,'stroke': "#000000"},
'VA': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'WA': {fill: "#'''+str(color_WA)+'''",'stroke-width': 3,'stroke': "#000000"},
'WV': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
'WI': {fill: "#'''+str(color_WI)+'''",'stroke-width': 3,'stroke': "#000000"},
'WY': {fill: "#FFFFFF", 'stroke-width': .5, 'stroke': "#000000"},
},

    mouseover: function(event, data) {
var description = "No state info loaded for this state.";
    switch(data.name) {
case 'AL':            
description = '<b>Alabama: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'AK':            
description = '<b>Alaska: <font color=#'''+str(first_color_to_display_AK)+str(first_result_to_display_AK)+'''%</font> vs <font color=#'''+str(second_color_to_display_AK)+str(second_result_to_display_AK)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_AK)+'''</font>'''+str(change_to_display_AK)+'''% in last day.</font></b>';
break;
case 'AZ':            
description = '<b>Arizona: <font color=#'''+str(first_color_to_display_AZ)+str(first_result_to_display_AZ)+'''%</font> vs <font color=#'''+str(second_color_to_display_AZ)+str(second_result_to_display_AZ)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_AZ)+'''</font>'''+str(change_to_display_AZ)+'''% in last day.</font></b>';
break;
case 'AR':            
description = '<b>Arkansas: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'CA':            
description = '<b>California: <font color=#000000>No bets; considered safe Democratic</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'CO':            
description = '<b>Colorado: <font color=#'''+str(first_color_to_display_CO)+str(first_result_to_display_CO)+'''%</font> vs <font color=#'''+str(second_color_to_display_CO)+str(second_result_to_display_CO)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_CO)+'''</font>'''+str(change_to_display_CO)+'''% in last day.</font></b>';
break;
case 'CT':            
description = '<b>Connecticut: <font color=#000000>No bets; considered safe Democratic</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'DE':            
description = '<b>Delaware: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'FL':            
description = '<b>Florida: <font color=#'''+str(first_color_to_display_FL)+str(first_result_to_display_FL)+'''%</font> vs <font color=#'''+str(second_color_to_display_FL)+str(second_result_to_display_FL)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_FL)+'''</font>'''+str(change_to_display_FL)+'''% in last day.</font></b>';
break;
case 'GA':            
description = '<b>Georgia: <font color=#'''+str(first_color_to_display_GA)+str(first_result_to_display_GA)+'''%</font> vs <font color=#'''+str(second_color_to_display_GA)+str(second_result_to_display_GA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_GA)+'''</font>'''+str(change_to_display_GA)+'''% in last day.</font></b>';
break;
case 'HI':            
description = '<b>Hawaii: <font color=#000000>No bets; considered safe Democratic</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'ID':            
description = '<b>Idaho: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'IL':            
description = '<b>Illinois: <font color=#'''+str(first_color_to_display_IL)+str(first_result_to_display_IL)+'''%</font> vs <font color=#'''+str(second_color_to_display_IL)+str(second_result_to_display_IL)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_IL)+'''</font>'''+str(change_to_display_IL)+'''% in last day.</font></b>';
break;
case 'IN':            
description = '<b>Indiana: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'IA':            
description = '<b>Iowa: <font color=#'''+str(first_color_to_display_IA)+str(first_result_to_display_IA)+'''%</font> vs <font color=#'''+str(second_color_to_display_IA)+str(second_result_to_display_IA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_IA)+'''</font>'''+str(change_to_display_IA)+'''% in last day.</font></b>';
break;
case 'KS':            
description = '<b>Kansas: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'KY':            
description = '<b>Kentucky: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'LA':            
description = '<b>Louisiana: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'ME':            
description = '<b>Maine: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'MD':            
description = '<b>Maryland: <font color=#000000>No bets; considered safe Democratic</font></b><span style="font-size: 14pt;"><br><font color=#000000>Current Senate is 50-50</font></b>';
break;
case 'MA':            
description = '<b>Massachusetts: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'MI':            
description = '<b>Michigan: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'MN':            
description = '<b>Minnesota: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'MS':            
description = '<b>Mississippi: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'MO':            
description = '<b>Missouri: <font color=#'''+str(first_color_to_display_MO)+str(first_result_to_display_MO)+'''%</font> vs <font color=#'''+str(second_color_to_display_MO)+str(second_result_to_display_MO)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MO)+'''</font>'''+str(change_to_display_MO)+'''% in last day.</font></b>';
break;
case 'MT':            
description = '<b>Montana: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'NE':            
description = '<b>Nebraska: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'NV':            
description = '<b>Nevada: <font color=#'''+str(first_color_to_display_NV)+str(first_result_to_display_NV)+'''%</font> vs <font color=#'''+str(second_color_to_display_NV)+str(second_result_to_display_NV)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NV)+'''</font>'''+str(change_to_display_NV)+'''% in last day.</font></b>';
break;
case 'NH':            
description = '<b>N Hampshire: <font color=#'''+str(first_color_to_display_NH)+str(first_result_to_display_NH)+'''%</font> vs <font color=#'''+str(second_color_to_display_NH)+str(second_result_to_display_NH)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NH)+'''</font>'''+str(change_to_display_NH)+'''% in last day.</font></b>';
break;
case 'NJ':            
description = '<b>New Jersey: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'NM':            
description = '<b>New Mexico: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'NY':            
description = '<b>New York: <font color=#000000>No bets; considered safe Democratic</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'NC':            
description = '<b>North Carolina: <font color=#'''+str(first_color_to_display_NC)+str(first_result_to_display_NC)+'''%</font> vs <font color=#'''+str(second_color_to_display_NC)+str(second_result_to_display_NC)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NC)+'''</font>'''+str(change_to_display_NC)+'''% in last day.</font></b>';
break;
case 'ND':            
description = '<b>North Dakota: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'OH':            
description = '<b>Ohio: <font color=#'''+str(first_color_to_display_OH)+str(first_result_to_display_OH)+'''%</font> vs <font color=#'''+str(second_color_to_display_OH)+str(second_result_to_display_OH)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_OH)+'''</font>'''+str(change_to_display_OH)+'''% in last day.</font></b>';
break;
case 'OK':            
description = '<b>Oklahoma: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'OR':            
description = '<b>Oregon: <font color=#'''+str(first_color_to_display_OR)+str(first_result_to_display_OR)+'''%</font> vs <font color=#'''+str(second_color_to_display_OR)+str(second_result_to_display_OR)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_OR)+'''</font>'''+str(change_to_display_OR)+'''% in last day.</font></b>';
break;
case 'PA':            
description = '<b>Pennsylvania: <font color=#'''+str(first_color_to_display_PA)+str(first_result_to_display_PA)+'''%</font> vs <font color=#'''+str(second_color_to_display_PA)+str(second_result_to_display_PA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_PA)+'''</font>'''+str(change_to_display_PA)+'''% in last day.</font></b>';
break;
case 'RI':            
description = '<b>Rhode Island: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'SC':            
description = '<b>South Carolina: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'SD':            
description = '<b>South Dakota: <font color=#000000>No bets; considered safe Republican</font></b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'TN':            
description = '<b>Tennessee: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'TX':            
description = '<b>Texas: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'UT':            
description = '<b>Utah: <font color=#'''+str(first_color_to_display_UT)+str(first_result_to_display_UT)+'''%</font> vs <font color=#'''+str(second_color_to_display_UT)+str(second_result_to_display_UT)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_UT)+'''</font>'''+str(change_to_display_UT)+'''% in last day.</font></b>';
break;
case 'VT':            
description = '<b>Vermont: <font color=#'''+str(first_color_to_display_VT)+str(first_result_to_display_VT)+'''%</font> vs <font color=#'''+str(second_color_to_display_VT)+str(second_result_to_display_VT)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_VT)+'''</font>'''+str(change_to_display_VT)+'''% in last day.</font></b>';
break;
case 'VA':            
description = '<b>Virginia: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'WA':            
description = '<b>Washington: <font color=#'''+str(first_color_to_display_WA)+str(first_result_to_display_WA)+'''%</font> vs <font color=#'''+str(second_color_to_display_WA)+str(second_result_to_display_WA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_WA)+'''</font>'''+str(change_to_display_WA)+'''% in last day.</font></b>';
break;
case 'WV':            
description = '<b>West Virginia: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;
case 'WI':            
description = '<b>Wisconsin: <font color=#'''+str(first_color_to_display_WI)+str(first_result_to_display_WI)+'''%</font> vs <font color=#'''+str(second_color_to_display_WI)+str(second_result_to_display_WI)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_WI)+'''</font>'''+str(change_to_display_WI)+'''% in last day.</font></b>';
break;
case 'WY':            
description = '<b>Wyoming: No senate race this year</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>';
break;}     
            $('#selected-state > span').html(description).css({"font-weight": "bold", "color": "#000000"});
    },
    
    mouseout: function(event, data) {
      $('#selected-state > span').html('<b><u>Senate Seats 2022</u> (estimate: <font color=#0000ff>'''+str(DEM_votes)+'''</font>-<font color=#ff0000>'''+str(REP_votes)+'''</font>. Hover over states)</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>').css({"font-weight": "normal", "color": "#000000"});
    },
      click: function(event, data) {
        $('#clicked-state').text('You clicked: '+data.name).parent().effect('highlight', {color: '#C7F464'}, 2000);
      },
    });
//# sourceURL=pen.js
</script>
<span style="font-size: 11pt;">
<b><font color=#000000>Last updated: '''+str(now)+'''<br>
Over $750k bet. State betting is from <a href="https://www.predictit.org/">PredictIt</a><br><a href="https://www.betfair.com/exchange/plus/politics">Betfair</a> to be added if liquid state market available<br></span>
</html>

    </td>
        </tr>
    </table>
    <!--...-->
</center>
''')
print "here?"

print "mirror?"
mirror = 0
if mirror == 1:
    print "attempting mirror"
    ftp = FTP('72.14.177.84', timeout=8)
    ftp.login('ebo', 'anlliG0HoQ8ZNVh')
    print "attempting mirror 2"
    converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
    print "attempting mirror 3/ String:  "
    print converted_DEM_HTML_string
    ftp.storbinary(str("STOR files/SenateMap2022.html"), converted_DEM_HTML_string)
    print "MIRROR ElectionBettingOdds.com... Success! (Unless immediately followed by error message)"

##### FTP! :) #####
print "writing to server"
fg = open('/var/www/predictionmarketodds.com/public_html/SenateMap2022.html','w')
fg.write(str(finalwinner_HTML_string))
fg.close()
print "PrecictionMarketOdds.com... Also Success! (Unless immediately followed by error message)"

print "writing to server"
fg = open('/var/www/178.62.65.243/public_html/SenateMap2022.html','w')
fg.write(str(finalwinner_HTML_string))
fg.close()
print "Mirror 178.62.65.243... Also Success! (Unless immediately followed by error message)"

print "writing to server"
fg = open('/var/www/electionbettingodds.com/public_html/SenateMap2022.html','w')
fg.write(str(finalwinner_HTML_string))
fg.close()
print "ElectionBettingOdds.com... Also Success! (Unless immediately followed by error message)"


"""
ftp = FTP('ftp.electionbettingodds.com', timeout=8)
ftp.login('fmdoepu9s27b','r52y3!pZK')
converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
ftp.storbinary(str("STOR public_html/SenateMap2022.html"), converted_DEM_HTML_string)
print "State page... Success! (Unless immediately followed by error message)"
ftp.quit()
"""

'''
fg = open('/var/www/html/nh.html','w')
fg.write(str(finalwinner_HTML_string))
fg.close()
print "PrecictionMarketOdds.com... Also Success! (Unless immediately followed by error message)"
'''
##### END OF INSTANCE #####

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
