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
url_dict = ("6625","6591","5596","6597","6611","5605","6587","6636","5544","5604","6631","6623","6613","6572","5603","6627","6592","6617","6571","6593","6596","5545","5597","6628","6581","6606","6624","5601","5598","6580","6573","6612","5599","6637","5600","6616","6582","5543","6629","6609","6638","6586","5798","6585","6633","5602","6598","6615","5542","6632","6190","6608",)
spec_format = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,)
spec_detail = ("Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic",)
st_dict = ("AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","ME2","NE2")
rep_cands_list = ("Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican",)

dem_cands_list = ("Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic","Democratic",)

votes_dict = (9,3,11,6,55,9,7,3,29,16,4,4,20,11,6,6,8,8,3,10,11,16,10,6,10,3,4,6,4,14,5,29,15,3,18,7,7,20,4,9,3,11,38,6,3,13,12,5,10,3,1,1,)
final_dict = {}
Betfair_dummy = 0
source_header = 'Odds from <a href="http://www.predictit.org/promo/electionbetting>PredictIt</a>'
source_footer = ''
US_stCAND_dict = {}
stCAND_dict = {}
votes_finder = {}
ST_raw_history = ""
REP_votes = 0
DEM_votes = 3 #DC

def US_oddsfinder(state,race,cand_FULL_name,cand_last_name_PLUS_bid_PLUS_race,cand_last_name_PLUS_ask_PLUS_race,cand_last_name_PLUS_odds_PLUS_race):
    global ST_raw_history
    global ST_data_counter
    global now
    user_PREDICTIT_STATE = "https://www.predictit.org/api/marketdata/markets/"+str(url)
    time.sleep(3)
    #### BETFAIR HERE

    with open ("/python/StateMap2020/Betfarer/price_log_"+str(state)+".txt", "r") as myfile:
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
    US_STATE_raw = urllib2.urlopen(str(user_PREDICTIT_STATE)).read()
    parsable_US_STATE_raw = US_STATE_raw.replace('"', '')
    parsable_US_STATE_raw = ''.join(parsable_US_STATE_raw.split())
    print "test1"

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
for number in range(0,52):
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
    key_1 = "***data_counter***"+str(ST_data_counter-66) #-int(round((12*24*7),0 "116" "116" #
    key_2 = "***data_counter***"+str(ST_data_counter) #-int(round((12*24*7),0 "117" "117" # (oldest possible)
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
    fp = open("/python/StateMap2020/Betfarer/price_log_"+str(state)+".txt",'a')
    fp.write(str(now)+" "), fp.write(str(odds_tuples)+"*WIN*["), fp.write('***data_counter***'+str(ST_data_counter)+' ')
    fp.close()
    print "info successfully saved"
    time.sleep(1)

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
<div id="selected-state"><span><b><u>Electoral College</u> (estimate: <font color=#0000ff>'''+str(DEM_votes)+'''</font>-<font color=#ff0000>'''+str(REP_votes)+'''</font>. Hover over states)</b><span style="font-size: 14pt;"><br><b>270 electoral votes needed to win</b></span></span></div></div>
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
AL: {fill: "#'''+str(color_AL)+'''",'stroke-width': 1.5,'stroke': "#000000"},
AK: {fill: "#'''+str(color_AK)+'''",'stroke-width': 1.5,'stroke': "#000000"},
AZ: {fill: "#'''+str(color_AZ)+'''",'stroke-width': 1.5,'stroke': "#000000"},
AR: {fill: "#'''+str(color_AR)+'''",'stroke-width': 1.5,'stroke': "#000000"},
CA: {fill: "#'''+str(color_CA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
CO: {fill: "#'''+str(color_CO)+'''",'stroke-width': 1.5,'stroke': "#000000"},
CT: {fill: "#'''+str(color_CT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
DE: {fill: "#'''+str(color_DE)+'''",'stroke-width': 1.5,'stroke': "#000000"},
FL: {fill: "#'''+str(color_FL)+'''",'stroke-width': 1.5,'stroke': "#000000"},
GA: {fill: "#'''+str(color_GA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
HI: {fill: "#'''+str(color_HI)+'''",'stroke-width': 1.5,'stroke': "#000000"},
ID: {fill: "#'''+str(color_ID)+'''",'stroke-width': 1.5,'stroke': "#000000"},
IL: {fill: "#'''+str(color_IL)+'''",'stroke-width': 1.5,'stroke': "#000000"},
IN: {fill: "#'''+str(color_IN)+'''",'stroke-width': 1.5,'stroke': "#000000"},
IA: {fill: "#'''+str(color_IA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
KS: {fill: "#'''+str(color_KS)+'''",'stroke-width': 1.5,'stroke': "#000000"},
KY: {fill: "#'''+str(color_KY)+'''",'stroke-width': 1.5,'stroke': "#000000"},
LA: {fill: "#'''+str(color_LA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
ME: {fill: "#'''+str(color_ME)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MD: {fill: "#'''+str(color_MD)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MA: {fill: "#'''+str(color_MA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MI: {fill: "#'''+str(color_MI)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MN: {fill: "#'''+str(color_MN)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MS: {fill: "#'''+str(color_MS)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MO: {fill: "#'''+str(color_MO)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MT: {fill: "#'''+str(color_MT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NE: {fill: "#'''+str(color_NE)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NV: {fill: "#'''+str(color_NV)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NH: {fill: "#'''+str(color_NH)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NJ: {fill: "#'''+str(color_NJ)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NM: {fill: "#'''+str(color_NM)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NY: {fill: "#'''+str(color_NY)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NC: {fill: "#'''+str(color_NC)+'''",'stroke-width': 1.5,'stroke': "#000000"},
ND: {fill: "#'''+str(color_ND)+'''",'stroke-width': 1.5,'stroke': "#000000"},
OH: {fill: "#'''+str(color_OH)+'''",'stroke-width': 1.5,'stroke': "#000000"},
OK: {fill: "#'''+str(color_OK)+'''",'stroke-width': 1.5,'stroke': "#000000"},
OR: {fill: "#'''+str(color_OR)+'''",'stroke-width': 1.5,'stroke': "#000000"},
PA: {fill: "#'''+str(color_PA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
RI: {fill: "#'''+str(color_RI)+'''",'stroke-width': 1.5,'stroke': "#000000"},
SC: {fill: "#'''+str(color_SC)+'''",'stroke-width': 1.5,'stroke': "#000000"},
SD: {fill: "#'''+str(color_SD)+'''",'stroke-width': 1.5,'stroke': "#000000"},
TN: {fill: "#'''+str(color_TN)+'''",'stroke-width': 1.5,'stroke': "#000000"},
TX: {fill: "#'''+str(color_TX)+'''",'stroke-width': 1.5,'stroke': "#000000"},
UT: {fill: "#'''+str(color_UT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
VT: {fill: "#'''+str(color_VT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
VA: {fill: "#'''+str(color_VA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
WA: {fill: "#'''+str(color_WA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
WV: {fill: "#'''+str(color_WV)+'''",'stroke-width': 1.5,'stroke': "#000000"},
WI: {fill: "#'''+str(color_WI)+'''",'stroke-width': 1.5,'stroke': "#000000"},
WY: {fill: "#'''+str(color_WY)+'''",'stroke-width': 1.5,'stroke': "#000000"},
},

stateSpecificHoverStyles: {
'AL': {fill: "#'''+str(color_AL)+'''",'stroke-width': 3,'stroke': "#000000"},
'AK': {fill: "#'''+str(color_AK)+'''",'stroke-width': 3,'stroke': "#000000"},
'AZ': {fill: "#'''+str(color_AZ)+'''",'stroke-width': 3,'stroke': "#000000"},
'AR': {fill: "#'''+str(color_AR)+'''",'stroke-width': 3,'stroke': "#000000"},
'CA': {fill: "#'''+str(color_CA)+'''",'stroke-width': 3,'stroke': "#000000"},
'CO': {fill: "#'''+str(color_CO)+'''",'stroke-width': 3,'stroke': "#000000"},
'CT': {fill: "#'''+str(color_CT)+'''",'stroke-width': 3,'stroke': "#000000"},
'DE': {fill: "#'''+str(color_DE)+'''",'stroke-width': 3,'stroke': "#000000"},
'FL': {fill: "#'''+str(color_FL)+'''",'stroke-width': 3,'stroke': "#000000"},
'GA': {fill: "#'''+str(color_GA)+'''",'stroke-width': 3,'stroke': "#000000"},
'HI': {fill: "#'''+str(color_HI)+'''",'stroke-width': 3,'stroke': "#000000"},
'ID': {fill: "#'''+str(color_ID)+'''",'stroke-width': 3,'stroke': "#000000"},
'IL': {fill: "#'''+str(color_IL)+'''",'stroke-width': 3,'stroke': "#000000"},
'IN': {fill: "#'''+str(color_IN)+'''",'stroke-width': 3,'stroke': "#000000"},
'IA': {fill: "#'''+str(color_IA)+'''",'stroke-width': 3,'stroke': "#000000"},
'KS': {fill: "#'''+str(color_KS)+'''",'stroke-width': 3,'stroke': "#000000"},
'KY': {fill: "#'''+str(color_KY)+'''",'stroke-width': 3,'stroke': "#000000"},
'LA': {fill: "#'''+str(color_LA)+'''",'stroke-width': 3,'stroke': "#000000"},
'ME': {fill: "#'''+str(color_ME)+'''",'stroke-width': 3,'stroke': "#000000"},
'MD': {fill: "#'''+str(color_MD)+'''",'stroke-width': 3,'stroke': "#000000"},
'MA': {fill: "#'''+str(color_MA)+'''",'stroke-width': 3,'stroke': "#000000"},
'MI': {fill: "#'''+str(color_MI)+'''",'stroke-width': 3,'stroke': "#000000"},
'MN': {fill: "#'''+str(color_MN)+'''",'stroke-width': 3,'stroke': "#000000"},
'MS': {fill: "#'''+str(color_MS)+'''",'stroke-width': 3,'stroke': "#000000"},
'MO': {fill: "#'''+str(color_MO)+'''",'stroke-width': 3,'stroke': "#000000"},
'MT': {fill: "#'''+str(color_MT)+'''",'stroke-width': 3,'stroke': "#000000"},
'NE': {fill: "#'''+str(color_NE)+'''",'stroke-width': 3,'stroke': "#000000"},
'NV': {fill: "#'''+str(color_NV)+'''",'stroke-width': 3,'stroke': "#000000"},
'NH': {fill: "#'''+str(color_NH)+'''",'stroke-width': 3,'stroke': "#000000"},
'NJ': {fill: "#'''+str(color_NJ)+'''",'stroke-width': 3,'stroke': "#000000"},
'NM': {fill: "#'''+str(color_NM)+'''",'stroke-width': 3,'stroke': "#000000"},
'NY': {fill: "#'''+str(color_NY)+'''",'stroke-width': 3,'stroke': "#000000"},
'NC': {fill: "#'''+str(color_NC)+'''",'stroke-width': 3,'stroke': "#000000"},
'ND': {fill: "#'''+str(color_ND)+'''",'stroke-width': 3,'stroke': "#000000"},
'OH': {fill: "#'''+str(color_OH)+'''",'stroke-width': 3,'stroke': "#000000"},
'OK': {fill: "#'''+str(color_OK)+'''",'stroke-width': 3,'stroke': "#000000"},
'OR': {fill: "#'''+str(color_OR)+'''",'stroke-width': 3,'stroke': "#000000"},
'PA': {fill: "#'''+str(color_PA)+'''",'stroke-width': 3,'stroke': "#000000"},
'RI': {fill: "#'''+str(color_RI)+'''",'stroke-width': 3,'stroke': "#000000"},
'SC': {fill: "#'''+str(color_SC)+'''",'stroke-width': 3,'stroke': "#000000"},
'SD': {fill: "#'''+str(color_SD)+'''",'stroke-width': 3,'stroke': "#000000"},
'TN': {fill: "#'''+str(color_TN)+'''",'stroke-width': 3,'stroke': "#000000"},
'TX': {fill: "#'''+str(color_TX)+'''",'stroke-width': 3,'stroke': "#000000"},
'UT': {fill: "#'''+str(color_UT)+'''",'stroke-width': 3,'stroke': "#000000"},
'VT': {fill: "#'''+str(color_VT)+'''",'stroke-width': 3,'stroke': "#000000"},
'VA': {fill: "#'''+str(color_VA)+'''",'stroke-width': 3,'stroke': "#000000"},
'WA': {fill: "#'''+str(color_WA)+'''",'stroke-width': 3,'stroke': "#000000"},
'WV': {fill: "#'''+str(color_WV)+'''",'stroke-width': 3,'stroke': "#000000"},
'WI': {fill: "#'''+str(color_WI)+'''",'stroke-width': 3,'stroke': "#000000"},
'WY': {fill: "#'''+str(color_WY)+'''",'stroke-width': 3,'stroke': "#000000"},
},

    mouseover: function(event, data) {
var description = "No state info loaded for this state.";
    switch(data.name) {
case 'AL':            
description = '<b>Alabama: <font color=#'''+str(first_color_to_display_AL)+str(first_result_to_display_AL)+'''%</font> vs <font color=#'''+str(second_color_to_display_AL)+str(second_result_to_display_AL)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_AL)+'''</font>'''+str(change_to_display_AL)+'''% in last day. Electoral votes: '''+str(votes_dict[0])+'''</font></b>';
break;
case 'AK':            
description = '<b>Alaska: <font color=#'''+str(first_color_to_display_AK)+str(first_result_to_display_AK)+'''%</font> vs <font color=#'''+str(second_color_to_display_AK)+str(second_result_to_display_AK)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_AK)+'''</font>'''+str(change_to_display_AK)+'''% in last day. Electoral votes: '''+str(votes_dict[1])+'''</font></b>';
break;
case 'AZ':            
description = '<b>Arizona: <font color=#'''+str(first_color_to_display_AZ)+str(first_result_to_display_AZ)+'''%</font> vs <font color=#'''+str(second_color_to_display_AZ)+str(second_result_to_display_AZ)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_AZ)+'''</font>'''+str(change_to_display_AZ)+'''% in last day. Electoral votes: '''+str(votes_dict[2])+'''</font></b>';
break;
case 'AR':            
description = '<b>Arkansas: <font color=#'''+str(first_color_to_display_AR)+str(first_result_to_display_AR)+'''%</font> vs <font color=#'''+str(second_color_to_display_AR)+str(second_result_to_display_AR)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_AR)+'''</font>'''+str(change_to_display_AR)+'''% in last day. Electoral votes: '''+str(votes_dict[3])+'''</font></b>';
break;
case 'CA':            
description = '<b>California: <font color=#'''+str(first_color_to_display_CA)+str(first_result_to_display_CA)+'''%</font> vs <font color=#'''+str(second_color_to_display_CA)+str(second_result_to_display_CA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_CA)+'''</font>'''+str(change_to_display_CA)+'''% in last day. Electoral votes: '''+str(votes_dict[4])+'''</font></b>';
break;
case 'CO':            
description = '<b>Colorado: <font color=#'''+str(first_color_to_display_CO)+str(first_result_to_display_CO)+'''%</font> vs <font color=#'''+str(second_color_to_display_CO)+str(second_result_to_display_CO)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_CO)+'''</font>'''+str(change_to_display_CO)+'''% in last day. Electoral votes: '''+str(votes_dict[5])+'''</font></b>';
break;
case 'CT':            
description = '<b>Connecticut: <font color=#'''+str(first_color_to_display_CT)+str(first_result_to_display_CT)+'''%</font> vs <font color=#'''+str(second_color_to_display_CT)+str(second_result_to_display_CT)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_CT)+'''</font>'''+str(change_to_display_CT)+'''% in last day. Electoral votes: '''+str(votes_dict[6])+'''</font></b>';
break;
case 'DE':            
description = '<b>Delaware: <font color=#'''+str(first_color_to_display_DE)+str(first_result_to_display_DE)+'''%</font> vs <font color=#'''+str(second_color_to_display_DE)+str(second_result_to_display_DE)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_DE)+'''</font>'''+str(change_to_display_DE)+'''% in last day. Electoral votes: '''+str(votes_dict[7])+'''</font></b>';
break;
case 'FL':            
description = '<b>Florida: <font color=#'''+str(first_color_to_display_FL)+str(first_result_to_display_FL)+'''%</font> vs <font color=#'''+str(second_color_to_display_FL)+str(second_result_to_display_FL)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_FL)+'''</font>'''+str(change_to_display_FL)+'''% in last day. Electoral votes: '''+str(votes_dict[8])+'''</font></b>';
break;
case 'GA':            
description = '<b>Georgia: <font color=#'''+str(first_color_to_display_GA)+str(first_result_to_display_GA)+'''%</font> vs <font color=#'''+str(second_color_to_display_GA)+str(second_result_to_display_GA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_GA)+'''</font>'''+str(change_to_display_GA)+'''% in last day. Electoral votes: '''+str(votes_dict[9])+'''</font></b>';
break;
case 'HI':            
description = '<b>Hawaii: <font color=#'''+str(first_color_to_display_HI)+str(first_result_to_display_HI)+'''%</font> vs <font color=#'''+str(second_color_to_display_HI)+str(second_result_to_display_HI)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_HI)+'''</font>'''+str(change_to_display_HI)+'''% in last day. Electoral votes: '''+str(votes_dict[10])+'''</font></b>';
break;
case 'ID':            
description = '<b>Idaho: <font color=#'''+str(first_color_to_display_ID)+str(first_result_to_display_ID)+'''%</font> vs <font color=#'''+str(second_color_to_display_ID)+str(second_result_to_display_ID)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_ID)+'''</font>'''+str(change_to_display_ID)+'''% in last day. Electoral votes: '''+str(votes_dict[11])+'''</font></b>';
break;
case 'IL':            
description = '<b>Illinois: <font color=#'''+str(first_color_to_display_IL)+str(first_result_to_display_IL)+'''%</font> vs <font color=#'''+str(second_color_to_display_IL)+str(second_result_to_display_IL)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_IL)+'''</font>'''+str(change_to_display_IL)+'''% in last day. Electoral votes: '''+str(votes_dict[12])+'''</font></b>';
break;
case 'IN':            
description = '<b>Indiana: <font color=#'''+str(first_color_to_display_IN)+str(first_result_to_display_IN)+'''%</font> vs <font color=#'''+str(second_color_to_display_IN)+str(second_result_to_display_IN)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_IN)+'''</font>'''+str(change_to_display_IN)+'''% in last day. Electoral votes: '''+str(votes_dict[13])+'''</font></b>';
break;
case 'IA':            
description = '<b>Iowa: <font color=#'''+str(first_color_to_display_IA)+str(first_result_to_display_IA)+'''%</font> vs <font color=#'''+str(second_color_to_display_IA)+str(second_result_to_display_IA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_IA)+'''</font>'''+str(change_to_display_IA)+'''% in last day. Electoral votes: '''+str(votes_dict[14])+'''</font></b>';
break;
case 'KS':            
description = '<b>Kansas: <font color=#'''+str(first_color_to_display_KS)+str(first_result_to_display_KS)+'''%</font> vs <font color=#'''+str(second_color_to_display_KS)+str(second_result_to_display_KS)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_KS)+'''</font>'''+str(change_to_display_KS)+'''% in last day. Electoral votes: '''+str(votes_dict[15])+'''</font></b>';
break;
case 'KY':            
description = '<b>Kentucky: <font color=#'''+str(first_color_to_display_KY)+str(first_result_to_display_KY)+'''%</font> vs <font color=#'''+str(second_color_to_display_KY)+str(second_result_to_display_KY)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_KY)+'''</font>'''+str(change_to_display_KY)+'''% in last day. Electoral votes: '''+str(votes_dict[16])+'''</font></b>';
break;
case 'LA':            
description = '<b>Louisiana: <font color=#'''+str(first_color_to_display_LA)+str(first_result_to_display_LA)+'''%</font> vs <font color=#'''+str(second_color_to_display_LA)+str(second_result_to_display_LA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_LA)+'''</font>'''+str(change_to_display_LA)+'''% in last day. Electoral votes: '''+str(votes_dict[17])+'''</font></b>';
break;
case 'ME':            
description = '<b>Maine: <font color=#'''+str(first_color_to_display_ME)+str(first_result_to_display_ME)+'''%</font> vs <font color=#'''+str(second_color_to_display_ME)+str(second_result_to_display_ME)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_ME)+'''</font>'''+str(change_to_display_ME)+'''% in last day. Electoral votes: '''+str(votes_dict[18])+'''</font></b>';
break;
case 'MD':            
description = '<b>Maryland: <font color=#'''+str(first_color_to_display_MD)+str(first_result_to_display_MD)+'''%</font> vs <font color=#'''+str(second_color_to_display_MD)+str(second_result_to_display_MD)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MD)+'''</font>'''+str(change_to_display_MD)+'''% in last day. Electoral votes: '''+str(votes_dict[19])+'''</font></b>';
break;
case 'MA':            
description = '<b>Massachusetts: <font color=#'''+str(first_color_to_display_MA)+str(first_result_to_display_MA)+'''%</font> vs <font color=#'''+str(second_color_to_display_MA)+str(second_result_to_display_MA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MA)+'''</font>'''+str(change_to_display_MA)+'''% in last day. Electoral votes: '''+str(votes_dict[20])+'''</font></b>';
break;
case 'MI':            
description = '<b>Michigan: <font color=#'''+str(first_color_to_display_MI)+str(first_result_to_display_MI)+'''%</font> vs <font color=#'''+str(second_color_to_display_MI)+str(second_result_to_display_MI)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MI)+'''</font>'''+str(change_to_display_MI)+'''% in last day. Electoral votes: '''+str(votes_dict[21])+'''</font></b>';
break;
case 'MN':            
description = '<b>Minnesota: <font color=#'''+str(first_color_to_display_MN)+str(first_result_to_display_MN)+'''%</font> vs <font color=#'''+str(second_color_to_display_MN)+str(second_result_to_display_MN)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MN)+'''</font>'''+str(change_to_display_MN)+'''% in last day. Electoral votes: '''+str(votes_dict[22])+'''</font></b>';
break;
case 'MS':            
description = '<b>Mississippi: <font color=#'''+str(first_color_to_display_MS)+str(first_result_to_display_MS)+'''%</font> vs <font color=#'''+str(second_color_to_display_MS)+str(second_result_to_display_MS)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MS)+'''</font>'''+str(change_to_display_MS)+'''% in last day. Electoral votes: '''+str(votes_dict[23])+'''</font></b>';
break;
case 'MO':            
description = '<b>Missouri: <font color=#'''+str(first_color_to_display_MO)+str(first_result_to_display_MO)+'''%</font> vs <font color=#'''+str(second_color_to_display_MO)+str(second_result_to_display_MO)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MO)+'''</font>'''+str(change_to_display_MO)+'''% in last day. Electoral votes: '''+str(votes_dict[24])+'''</font></b>';
break;
case 'MT':            
description = '<b>Montana: <font color=#'''+str(first_color_to_display_MT)+str(first_result_to_display_MT)+'''%</font> vs <font color=#'''+str(second_color_to_display_MT)+str(second_result_to_display_MT)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_MT)+'''</font>'''+str(change_to_display_MT)+'''% in last day. Electoral votes: '''+str(votes_dict[25])+'''</font></b>';
break;
case 'NE':            
description = '<b>Nebraska: <font color=#'''+str(first_color_to_display_NE)+str(first_result_to_display_NE)+'''%</font> vs <font color=#'''+str(second_color_to_display_NE)+str(second_result_to_display_NE)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NE)+'''</font>'''+str(change_to_display_NE)+'''% in last day. Electoral votes: '''+str(votes_dict[26])+'''</font></b>';
break;
case 'NV':            
description = '<b>Nevada: <font color=#'''+str(first_color_to_display_NV)+str(first_result_to_display_NV)+'''%</font> vs <font color=#'''+str(second_color_to_display_NV)+str(second_result_to_display_NV)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NV)+'''</font>'''+str(change_to_display_NV)+'''% in last day. Electoral votes: '''+str(votes_dict[27])+'''</font></b>';
break;
case 'NH':            
description = '<b>N Hampshire: <font color=#'''+str(first_color_to_display_NH)+str(first_result_to_display_NH)+'''%</font> vs <font color=#'''+str(second_color_to_display_NH)+str(second_result_to_display_NH)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NH)+'''</font>'''+str(change_to_display_NH)+'''% in last day. Electoral votes: '''+str(votes_dict[28])+'''</font></b>';
break;
case 'NJ':            
description = '<b>New Jersey: <font color=#'''+str(first_color_to_display_NJ)+str(first_result_to_display_NJ)+'''%</font> vs <font color=#'''+str(second_color_to_display_NJ)+str(second_result_to_display_NJ)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NJ)+'''</font>'''+str(change_to_display_NJ)+'''% in last day. Electoral votes: '''+str(votes_dict[29])+'''</font></b>';
break;
case 'NM':            
description = '<b>New Mexico: <font color=#'''+str(first_color_to_display_NM)+str(first_result_to_display_NM)+'''%</font> vs <font color=#'''+str(second_color_to_display_NM)+str(second_result_to_display_NM)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NM)+'''</font>'''+str(change_to_display_NM)+'''% in last day. Electoral votes: '''+str(votes_dict[30])+'''</font></b>';
break;
case 'NY':            
description = '<b>New York: <font color=#'''+str(first_color_to_display_NY)+str(first_result_to_display_NY)+'''%</font> vs <font color=#'''+str(second_color_to_display_NY)+str(second_result_to_display_NY)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NY)+'''</font>'''+str(change_to_display_NY)+'''% in last day. Electoral votes: '''+str(votes_dict[31])+'''</font></b>';
break;
case 'NC':            
description = '<b>North Carolina: <font color=#'''+str(first_color_to_display_NC)+str(first_result_to_display_NC)+'''%</font> vs <font color=#'''+str(second_color_to_display_NC)+str(second_result_to_display_NC)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_NC)+'''</font>'''+str(change_to_display_NC)+'''% in last day. Electoral votes: '''+str(votes_dict[32])+'''</font></b>';
break;
case 'ND':            
description = '<b>North Dakota: <font color=#'''+str(first_color_to_display_ND)+str(first_result_to_display_ND)+'''%</font> vs <font color=#'''+str(second_color_to_display_ND)+str(second_result_to_display_ND)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_ND)+'''</font>'''+str(change_to_display_ND)+'''% in last day. Electoral votes: '''+str(votes_dict[33])+'''</font></b>';
break;
case 'OH':            
description = '<b>Ohio: <font color=#'''+str(first_color_to_display_OH)+str(first_result_to_display_OH)+'''%</font> vs <font color=#'''+str(second_color_to_display_OH)+str(second_result_to_display_OH)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_OH)+'''</font>'''+str(change_to_display_OH)+'''% in last day. Electoral votes: '''+str(votes_dict[34])+'''</font></b>';
break;
case 'OK':            
description = '<b>Oklahoma: <font color=#'''+str(first_color_to_display_OK)+str(first_result_to_display_OK)+'''%</font> vs <font color=#'''+str(second_color_to_display_OK)+str(second_result_to_display_OK)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_OK)+'''</font>'''+str(change_to_display_OK)+'''% in last day. Electoral votes: '''+str(votes_dict[35])+'''</font></b>';
break;
case 'OR':            
description = '<b>Oregon: <font color=#'''+str(first_color_to_display_OR)+str(first_result_to_display_OR)+'''%</font> vs <font color=#'''+str(second_color_to_display_OR)+str(second_result_to_display_OR)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_OR)+'''</font>'''+str(change_to_display_OR)+'''% in last day. Electoral votes: '''+str(votes_dict[36])+'''</font></b>';
break;
case 'PA':            
description = '<b>Pennsylvania: <font color=#'''+str(first_color_to_display_PA)+str(first_result_to_display_PA)+'''%</font> vs <font color=#'''+str(second_color_to_display_PA)+str(second_result_to_display_PA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_PA)+'''</font>'''+str(change_to_display_PA)+'''% in last day. Electoral votes: '''+str(votes_dict[37])+'''</font></b>';
break;
case 'RI':            
description = '<b>Rhode Island: <font color=#'''+str(first_color_to_display_RI)+str(first_result_to_display_RI)+'''%</font> vs <font color=#'''+str(second_color_to_display_RI)+str(second_result_to_display_RI)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_RI)+'''</font>'''+str(change_to_display_RI)+'''% in last day. Electoral votes: '''+str(votes_dict[38])+'''</font></b>';
break;
case 'SC':            
description = '<b>South Carolina: <font color=#'''+str(first_color_to_display_SC)+str(first_result_to_display_SC)+'''%</font> vs <font color=#'''+str(second_color_to_display_SC)+str(second_result_to_display_SC)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_SC)+'''</font>'''+str(change_to_display_SC)+'''% in last day. Electoral votes: '''+str(votes_dict[39])+'''</font></b>';
break;
case 'SD':            
description = '<b>South Dakota: <font color=#'''+str(first_color_to_display_SD)+str(first_result_to_display_SD)+'''%</font> vs <font color=#'''+str(second_color_to_display_SD)+str(second_result_to_display_SD)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_SD)+'''</font>'''+str(change_to_display_SD)+'''% in last day. Electoral votes: '''+str(votes_dict[40])+'''</font></b>';
break;
case 'TN':            
description = '<b>Tennessee: <font color=#'''+str(first_color_to_display_TN)+str(first_result_to_display_TN)+'''%</font> vs <font color=#'''+str(second_color_to_display_TN)+str(second_result_to_display_TN)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_TN)+'''</font>'''+str(change_to_display_TN)+'''% in last day. Electoral votes: '''+str(votes_dict[41])+'''</font></b>';
break;
case 'TX':            
description = '<b>Texas: <font color=#'''+str(first_color_to_display_TX)+str(first_result_to_display_TX)+'''%</font> vs <font color=#'''+str(second_color_to_display_TX)+str(second_result_to_display_TX)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_TX)+'''</font>'''+str(change_to_display_TX)+'''% in last day. Electoral votes: '''+str(votes_dict[42])+'''</font></b>';
break;
case 'UT':            
description = '<b>Utah: <font color=#'''+str(first_color_to_display_UT)+str(first_result_to_display_UT)+'''%</font> vs <font color=#'''+str(second_color_to_display_UT)+str(second_result_to_display_UT)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_UT)+'''</font>'''+str(change_to_display_UT)+'''% in last day. Electoral votes: '''+str(votes_dict[43])+'''</font></b>';
break;
case 'VT':            
description = '<b>Vermont: <font color=#'''+str(first_color_to_display_VT)+str(first_result_to_display_VT)+'''%</font> vs <font color=#'''+str(second_color_to_display_VT)+str(second_result_to_display_VT)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_VT)+'''</font>'''+str(change_to_display_VT)+'''% in last day. Electoral votes: '''+str(votes_dict[44])+'''</font></b>';
break;
case 'VA':            
description = '<b>Virginia: <font color=#'''+str(first_color_to_display_VA)+str(first_result_to_display_VA)+'''%</font> vs <font color=#'''+str(second_color_to_display_VA)+str(second_result_to_display_VA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_VA)+'''</font>'''+str(change_to_display_VA)+'''% in last day. Electoral votes: '''+str(votes_dict[45])+'''</font></b>';
break;
case 'WA':            
description = '<b>Washington: <font color=#'''+str(first_color_to_display_WA)+str(first_result_to_display_WA)+'''%</font> vs <font color=#'''+str(second_color_to_display_WA)+str(second_result_to_display_WA)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_WA)+'''</font>'''+str(change_to_display_WA)+'''% in last day. Electoral votes: '''+str(votes_dict[46])+'''</font></b>';
break;
case 'WV':            
description = '<b>West Virginia: <font color=#'''+str(first_color_to_display_WV)+str(first_result_to_display_WV)+'''%</font> vs <font color=#'''+str(second_color_to_display_WV)+str(second_result_to_display_WV)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_WV)+'''</font>'''+str(change_to_display_WV)+'''% in last day. Electoral votes: '''+str(votes_dict[47])+'''</font></b>';
break;
case 'WI':            
description = '<b>Wisconsin: <font color=#'''+str(first_color_to_display_WI)+str(first_result_to_display_WI)+'''%</font> vs <font color=#'''+str(second_color_to_display_WI)+str(second_result_to_display_WI)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_WI)+'''</font>'''+str(change_to_display_WI)+'''% in last day. Electoral votes: '''+str(votes_dict[48])+'''</font></b>';
break;
case 'WY':            
description = '<b>Wyoming: <font color=#'''+str(first_color_to_display_WY)+str(first_result_to_display_WY)+'''%</font> vs <font color=#'''+str(second_color_to_display_WY)+str(second_result_to_display_WY)+'''%</font></b><span style="font-size: 14pt;"><br><font color=#'''+str(first_color_to_display_WY)+'''</font>'''+str(change_to_display_WY)+'''% in last day. Electoral votes: '''+str(votes_dict[49])+'''</font></b>';
break;}                       
            $('#selected-state > span').html(description).css({"font-weight": "bold", "color": "#000000"});
    },
    
    mouseout: function(event, data) {
      $('#selected-state > span').html('<b><u>Electoral Votes</u> (estimate: <font color=#0000ff>'''+str(DEM_votes)+'''</font>-<font color=#ff0000>'''+str(REP_votes)+'''</font>. Hover over states)</b><span style="font-size: 14pt;"><br><b>270 electoral votes needed to win</b></span>').css({"font-weight": "normal", "color": "#000000"});
    },
      click: function(event, data) {
        $('#clicked-state').text('You clicked: '+data.name).parent().effect('highlight', {color: '#C7F464'}, 2000);
      },
    });
//# sourceURL=pen.js
</script>
<span style="font-size: 11pt;">
<font color=#000000>State election odds update every 20 minutes. Last updated: '''+str(now)+'''<br>
Over $1 million bet. Betting is from <a href="https://www.predictit.org/">PredictIt</a>. <a href="https://ftx.com/trade/TRUMP">FTX.com</a> and <a href="https://www.betfair.com/exchange/plus/politics">Betfair</a> to be added if liquid state market available<br></span>
</html>

    </td>
        </tr>
    </table>
    <!--...-->
</center>
''')
print "here?"

##### FTP! :) #####
ftp = FTP('ftp.electionbettingodds.com', timeout=8)
ftp.login('fmdoepu9s27b','r52y3!pZK')
converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
ftp.storbinary(str("STOR public_html/StateMap2020.html"), converted_DEM_HTML_string)
print "State page... Success! (Unless immediately followed by error message)"
ftp.quit()

mirror = 1
if mirror == 1:
    ftp = FTP('72.14.177.84', timeout=8)
    ftp.login('ebo', 'anlliG0HoQ8ZNVh')
    converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
    ftp.storbinary("STOR files/SenateMap2020.html", converted_DEM_HTML_string)
    print "MIRROR ElectionBettingOdds.com... Success! (Unless immediately followed by error message)"

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
