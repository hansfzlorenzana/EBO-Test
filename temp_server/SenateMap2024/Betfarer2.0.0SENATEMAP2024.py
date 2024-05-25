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
import json
import re
import requests

### START OF CONFIG ###
category = "us-senate" # Added: presidential or us-senate
year = "2024"
folder_name = "SenateMap2024" # This is the folder path; also the name of the html file - .html extension is automatically added
page_title = "Senate Seats 2024" # This is the title displayed on the page
states_without_data_but_republican = [] # no data but safe republican on label
states_without_data_but_democratic = [] # no data but safe democratic on label
states_without_data_no_senate_race = ['AL', 'AK', 'AR', 'CO', 'GA', 'ID', 'IL', 'IA', 'KS', 'KY', 'LA', 'ME', 'NH', 'NC', 'OK', 'OR', 'SC', 'SD', 'VT', 'ME1', 'NE2']

url_dict = ("alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana","nebraska","nevada","new-hampshire","new-jersey","new-mexico","new-york","north-carolina","north-dakota","ohio","oklahoma","oregon","pennsylvania","rhode-island","south-carolina","south-dakota","tennessee","texas","utah","vermont","virginia","washington","west-virginia","wisconsin","wyoming","congressional-district-2nd-maine","congressional-district-2nd-nebraska",)
spec_format = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,)
spec_detail = ("Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat",)
st_dict = ("AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","ME2","NE2")
rep_cands_list = ("Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican","Republican",)
dem_cands_list = ("Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat","Democrat",)

votes_dict = (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,)
REP_votes = 0
DEM_votes = 3
source_header = 'Odds from <a href="https://polymarket.com/>Polymarket</a>'

### END OF CONFIG ###

### INITIAL VALUES - DO NOT CHANGE VALUES ###
ST_counter = 0
final_dict = {}
Betfair_dummy = 0
source_footer = ''
US_stCAND_dict = {}
stCAND_dict = {}
votes_finder = {}
ST_raw_history = ""

def US_oddsfinder(state,race,cand_FULL_name,cand_last_name_PLUS_bid_PLUS_race,cand_last_name_PLUS_ask_PLUS_race,cand_last_name_PLUS_odds_PLUS_race):
    global ST_raw_history
    global ST_data_counter
    global now
    predictit_state_urls = [
        "https://polymarket.com/event/"+str(url)+"-"+str(category)+"-election-winner",
        "https://polymarket.com/event/"+str(url)+"-"+str(category)+"-election-winner-"+str(year),
    ]
    time.sleep(3)
    #### BETFAIR HERE
    # TODO: Handle file not found 
    with open ("temp_server/"+str(folder_name)+"/Betfarer/price_log_"+str(state)+".txt", "r") as myfile:
        ST_raw_history = myfile.read()
    #print ST_raw_history
    find_ST_data_counter_1 = ST_raw_history.split("***data_counter***")
    ## "[::-1]" is an odd piece of code that reverses the list
    find_ST_data_counter_2= find_ST_data_counter_1[::-1]
    ST_data_counter = int(find_ST_data_counter_2[0])

    now = str(time.strftime('%l:%M%p %Z on %b %d, %Y'))
    print now

    # Extract PRICES using Polymarket Clob API
    def get_json(polymarket_clob_url):
        clob_api_raw = requests.get(polymarket_clob_url, verify=False,timeout=5).content
        resp_data = json.loads(clob_api_raw)
        return resp_data
    
    ### POLYMARKET
    # Attempt to fetch HTML content from Polymarket state URLs
    html_content = None
    for user_PREDICTIT_STATE  in predictit_state_urls:
        try:
            html_content = urllib2.urlopen(str(user_PREDICTIT_STATE )).read()
            script_tag_match = re.search(r'<script\s+id="__NEXT_DATA__"\s+type="application/json"\s+crossorigin="anonymous">(.+?)</script>', html_content)

            if script_tag_match:
                # Extract JSON data from the matched script tag
                json_data = json.loads(script_tag_match.group(1))
                markets = json_data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['markets']

                # Extracting IDs from markets
                ids = [market['id'] for market in markets]
                for id_to_extract in ids:
                    for market in markets:
                        if market['id'] == str(id_to_extract):
                            if market['groupItemTitle'] == str(cand_FULL_name):
                                yes_token_id = market['clobTokenIds'][0]
                                price_url_base = 'https://clob.polymarket.com/price'
                                bid_query_fields = '?side=buy&token_id={}'.format(str(yes_token_id))
                                ask_query_fields = '?side=sell&token_id={}'.format(str(yes_token_id))
                                bid_price = get_json(price_url_base + bid_query_fields)
                                ask_price = get_json(price_url_base + ask_query_fields)
                                break
            if html_content:
                break  # Exit the loop if a response is received
        except Exception as e:
            print "Failed to fetch data from "+str(user_PREDICTIT_STATE)+" for "+str(state)+" state."
            pass

    ### GET ASK and BID; ODD COMPUTATION
    try:
        US_bid = float(bid_price['price'])
        US_ask = float(ask_price['price'])
        if US_ask - US_bid > .1:
            US_odds = US_bid
        elif US_bid == 0:
            US_odds = 0
        else:
            US_odds = (US_bid + US_ask) / 2

        US_stCAND_dict[cand_last_name_PLUS_bid_PLUS_race] = US_bid
        US_stCAND_dict[cand_last_name_PLUS_ask_PLUS_race] = US_ask
        US_stCAND_dict[cand_last_name_PLUS_odds_PLUS_race] = US_odds

        print(str(cand_FULL_name)+" DATA")
        print("Provider: POLYMARKET")
        print(state)
        print(US_stCAND_dict[cand_last_name_PLUS_bid_PLUS_race])
        print(US_stCAND_dict[cand_last_name_PLUS_ask_PLUS_race])
        print(US_stCAND_dict[cand_last_name_PLUS_odds_PLUS_race])
        print()

    except Exception as e:
        print "No data found for this state."
        pass
    

### START OF MAIN INSTANCE ###
for number in range(0,52):
    try:
        # should Have try!!! - handled now :)
        url = url_dict[ST_counter]
        state = st_dict[ST_counter]
        votes = votes_dict[ST_counter]
        votes_finder[state] = votes
        spec_binary = spec_format[ST_counter]
        detail = spec_detail[ST_counter]
        rep_cand = rep_cands_list[ST_counter]
        dem_cand = dem_cands_list[ST_counter]
        ST_counter = ST_counter + 1

        print "============= "+str(state)+" ==================="

        # FETCHING DATA FROM POLYMARKET
        if spec_binary == 0:
            US_oddsfinder(str(state),"STATE","Democrat","Democratic_bid_"+str(state),"Democratic_ask_"+str(state),"Democratic_odds_"+str(state))
            US_oddsfinder(str(state),"STATE","Republican","Republican_bid_"+str(state),"Republican_ask_"+str(state),"Republican_odds_"+str(state))
            print "SCRAPE DONE."
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
        ## sorting the odds
        odds_sorted = sorted(odds_tuples, key=lambda odds: odds[1], reverse=True)
        print odds_sorted

        ### RETRIEVING PAST ODDS
        # TODO: Handle retrieving past odds. Maybe append new data line by line.
        ### NOTE: This section MUST have a past odds file with past data to run off of. Must exist before running pgrm. Use backup file if needed.
        key_1 = "***data_counter***"+str(ST_data_counter-1) #-int(round((12*24*7),0 "116" "116" #
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
        print selection

        # final tuples (eval makes them active tuples rather than just strings.)
        past_odds = eval(selection)

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

        
        odds_w_changes_tuples = [
            (str(state)+'_DEM', (stCAND_dict["Democratic_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Democratic_odds_"+str(state)]*US_STATE_normalizer)/2,(stCAND_dict["Democratic_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Democratic_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[0][1],arrowfinder((stCAND_dict["Democratic_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Democratic_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[0][1])),
            (str(state)+'_GOP', (stCAND_dict["Republican_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Republican_odds_"+str(state)]*US_STATE_normalizer)/2,(stCAND_dict["Republican_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Republican_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[1][1],arrowfinder((stCAND_dict["Republican_odds_"+str(state)]*BETFAIR_STATE_normalizer+US_stCAND_dict["Republican_odds_"+str(state)]*US_STATE_normalizer)/2-past_odds[1][1])),
        ]
        
        print "hi"
        odds_sorted = sorted(odds_w_changes_tuples, key=lambda odds_w_changes: odds_w_changes[1], reverse=True)
        print odds_sorted
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
        ### COLOR CODING FOR DEMOCRATIC ###
        if eval("odds_sorted"+str(state)+"[0][0]") == str(state+'_DEM'):
            exec("first_result_to_display_"+str(state)+" = round(100*final_dict[state][0][1],1)")
            exec("first_color_to_display_"+str(state)+" = '0000ff>"+str(dem_cand)+": '")
            exec("second_result_to_display_"+str(state)+" = round(100*final_dict[state][1][1],1)")
            exec("second_color_to_display_"+str(state)+" = 'ff0000>"+str(rep_cand)+": '")
            exec("change_to_display_"+str(state)+" = str(final_dict[state][0][3]) + str(round(100*final_dict[state][0][2],1))")
            # Added - dynamic coloring
            exec("votes_"+str(state)+" = votes_finder[state]")
            exec("html_attribute_" + str(state) + " = \"<font color=#{0}{1}%</font> vs <font color=#{2}{3}%</font></b><span style=\\\"font-size: 14pt;\\\"><br><font color=#{0}</font>{4}% in last day. Electoral votes: {5}</font></b>'\".format(" +
                "first_color_to_display_" + str(state) + "," +
                "first_result_to_display_" + str(state) + "," +
                "second_color_to_display_" + str(state) + "," +
                "second_result_to_display_" + str(state) + "," +
                "change_to_display_" + str(state) + "," +
                "votes_" + str(state) +
            ")")
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

        ### COLOR CODING FOR REPUBLICAN ###
        if eval("odds_sorted"+str(state)+"[0][0]") == str(state+'_GOP'):
            exec("first_result_to_display_"+str(state)+" = round(100*final_dict[state][1][1],1)")
            exec("first_color_to_display_"+str(state)+" = 'ff0000>"+str(rep_cand)+": '")
            exec("second_result_to_display_"+str(state)+" = round(100*final_dict[state][0][1],1)")
            exec("second_color_to_display_"+str(state)+" = '0000ff>"+str(dem_cand)+": '")
            exec("change_to_display_"+str(state)+" = str(final_dict[state][1][3]) + str(round(100*final_dict[state][1][2],1))")
            # Added - dynamic coloring
            exec("votes_"+str(state)+" = votes_finder[state]")
            exec("html_attribute_" + str(state) + " = \"<font color=#{0}{1}%</font> vs <font color=#{2}{3}%</font></b><span style=\\\"font-size: 14pt;\\\"><br><font color=#{0}</font>{4}% in last day. Electoral votes: {5}</font></b>'\".format(" +
                "first_color_to_display_" + str(state) + "," +
                "first_result_to_display_" + str(state) + "," +
                "second_color_to_display_" + str(state) + "," +
                "second_result_to_display_" + str(state) + "," +
                "change_to_display_" + str(state) + "," +
                "votes_" + str(state) +
            ")")
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
        fp = open("temp_server/"+str(folder_name)+"/Betfarer/price_log_"+str(state)+".txt",'a')
        fp.write(str(now)+" "), fp.write(str(odds_tuples)+"*WIN*["), fp.write('***data_counter***'+str(ST_data_counter)+' ')
        fp.close()
        print "Info successfully saved."
        print "========== END of "+str(state)+" ================"
        print ""
        print "Waiting for 3 seconds before trying the next state."
        time.sleep(3)
    # Added - Error handler
    except Exception as e:
        print e
        states_without_data_no_race.append(state)

        # Handling states that have no data
        if state in states_without_data_but_democratic:
            exec("color_"+str(state)+"= 'ffffff'")
            exec("html_attribute_" + str(state) + " = \"<font color=#000000>No bets; considered safe Democratic</font></b><span style=\\\"font-size: 14pt;\\\"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>'\"")
        if state in states_without_data_but_republican:
            exec("color_"+str(state)+"= 'ffffff'")
            exec("html_attribute_" + str(state) + " = \"<font color=#000000>No bets; considered safe Republican</font></b><span style=\\\"font-size: 14pt;\\\"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>'\"")
        if state in states_without_data_no_race:
            exec("color_"+str(state)+"= 'ffffff'")
            exec("html_attribute_" + str(state) + " = \"No race this year</b><span style=\\\"font-size: 14pt;\\\"><br><b>Current is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>'\"")
        print "No data for "+str(state)+". Trying the next one..."
        print "========== END of "+str(state)+" ================"
        print ""

        pass
print "States without data:"
print states_without_data_no_race

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
<div id="selected-state"><span><b><u>'''+str(page_title)+'''</u> (estimate: <font color=#0000ff>'''+str(DEM_votes)+'''</font>-<font color=#ff0000>'''+str(REP_votes)+'''</font>. Hover over states)</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span></span></div></div>
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
ME2: {fill: "#'''+str(color_ME2)+'''",'stroke-width': 1.5,'stroke': "#000000"},
ME: {fill: "#'''+str(color_ME)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MD: {fill: "#'''+str(color_MD)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MA: {fill: "#'''+str(color_MA)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MI: {fill: "#'''+str(color_MI)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MN: {fill: "#'''+str(color_MN)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MS: {fill: "#'''+str(color_MS)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MO: {fill: "#'''+str(color_MO)+'''",'stroke-width': 1.5,'stroke': "#000000"},
MT: {fill: "#'''+str(color_MT)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NE: {fill: "#'''+str(color_NE)+'''",'stroke-width': 1.5,'stroke': "#000000"},
NE2: {fill: "#'''+str(color_NE2)+'''",'stroke-width': 1.5,'stroke': "#000000"},
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
'ME2': {fill: "#'''+str(color_ME2)+'''",'stroke-width': 3,'stroke': "#000000"},
'ME': {fill: "#'''+str(color_ME)+'''",'stroke-width': 3,'stroke': "#000000"},
'MD': {fill: "#'''+str(color_MD)+'''",'stroke-width': 3,'stroke': "#000000"},
'MA': {fill: "#'''+str(color_MA)+'''",'stroke-width': 3,'stroke': "#000000"},
'MI': {fill: "#'''+str(color_MI)+'''",'stroke-width': 3,'stroke': "#000000"},
'MN': {fill: "#'''+str(color_MN)+'''",'stroke-width': 3,'stroke': "#000000"},
'MS': {fill: "#'''+str(color_MS)+'''",'stroke-width': 3,'stroke': "#000000"},
'MO': {fill: "#'''+str(color_MO)+'''",'stroke-width': 3,'stroke': "#000000"},
'MT': {fill: "#'''+str(color_MT)+'''",'stroke-width': 3,'stroke': "#000000"},
'NE': {fill: "#'''+str(color_NE)+'''",'stroke-width': 3,'stroke': "#000000"},
'NE2': {fill: "#'''+str(color_NE2)+'''",'stroke-width': 3,'stroke': "#000000"},
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
description = '<b>Alabama: '''+str(html_attribute_AL)+''';
break;
case 'AK':
description = '<b>Alaska: '''+str(html_attribute_AK)+''';
break;
case 'AZ':
description = '<b>Arizona: '''+str(html_attribute_AZ)+''';
break;
case 'AR':
description = '<b>Arkansas: '''+str(html_attribute_AR)+''';
break;
case 'CA':
description = '<b>California: '''+str(html_attribute_CA)+''';
break;
case 'CO':
description = '<b>Colorado: '''+str(html_attribute_CO)+''';
break;
case 'CT':
description = '<b>Connecticut: '''+str(html_attribute_CT)+''';
break;
case 'DE':
description = '<b>Delaware: '''+str(html_attribute_DE)+''';
break;
case 'FL':
description = '<b>Florida: '''+str(html_attribute_FL)+''';
break;
case 'GA':
description = '<b>Georgia: '''+str(html_attribute_GA)+''';
break;
case 'HI':
description = '<b>Hawaii: '''+str(html_attribute_HI)+''';
break;
case 'ID':
description = '<b>Idaho: '''+str(html_attribute_ID)+''';
break;
case 'IL':
description = '<b>Illinois: '''+str(html_attribute_IL)+''';
break;
case 'IN':
description = '<b>Indiana: '''+str(html_attribute_IN)+''';
break;
case 'IA':
description = '<b>Iowa: '''+str(html_attribute_IA)+''';
break;
case 'KS':
description = '<b>Kansas: '''+str(html_attribute_KS)+''';
break;
case 'KY':
description = '<b>Kentucky: '''+str(html_attribute_KY)+''';
break;
case 'LA':
description = '<b>Louisiana: '''+str(html_attribute_LA)+''';
break;
case 'ME2':
description = '<b>Maine (2nd Congressional District): '''+str(html_attribute_ME2)+''';
break;
case 'ME':
description = '<b>Maine: '''+str(html_attribute_ME)+''';
break;
case 'MD':
description = '<b>Maryland: '''+str(html_attribute_MD)+''';
break;
case 'MA':
description = '<b>Massachusetts: '''+str(html_attribute_MA)+''';
break;
case 'MI':
description = '<b>Michigan: '''+str(html_attribute_MI)+''';
break;
case 'MN':
description = '<b>Minnesota: '''+str(html_attribute_MN)+''';
break;
case 'MS':
description = '<b>Mississippi: '''+str(html_attribute_MS)+''';
break;
case 'MO':
description = '<b>Missouri: '''+str(html_attribute_MO)+''';
break;
case 'MT':
description = '<b>Montana: '''+str(html_attribute_MT)+''';
break;
case 'NE':
description = '<b>Nebraska: '''+str(html_attribute_NE)+''';
break;
case 'NE2':
description = '<b>Nebraska (2nd Congressional District): '''+str(html_attribute_NE2)+''';
break;
case 'NV':
description = '<b>Nevada: '''+str(html_attribute_NV)+''';
break;
case 'NH':
description = '<b>New Hampshire: '''+str(html_attribute_NH)+''';
break;
case 'NJ':
description = '<b>New Jersey: '''+str(html_attribute_NJ)+''';
break;
case 'NM':
description = '<b>New Mexico: '''+str(html_attribute_NM)+''';
break;
case 'NY':
description = '<b>New York: '''+str(html_attribute_NY)+''';
break;
case 'NC':
description = '<b>North Carolina: '''+str(html_attribute_NC)+''';
break;
case 'ND':
description = '<b>North Dakota: '''+str(html_attribute_ND)+''';
break;
case 'OH':
description = '<b>Ohio: '''+str(html_attribute_OH)+''';
break;
case 'OK':
description = '<b>Oklahoma: '''+str(html_attribute_OK)+''';
break;
case 'OR':
description = '<b>Oregon: '''+str(html_attribute_OR)+''';
break;
case 'PA':
description = '<b>Pennsylvania: '''+str(html_attribute_PA)+''';
break;
case 'RI':
description = '<b>Rhode Island: '''+str(html_attribute_RI)+''';
break;
case 'SC':
description = '<b>South Carolina: '''+str(html_attribute_SC)+''';
break;
case 'SD':
description = '<b>South Dakota: '''+str(html_attribute_SD)+''';
break;
case 'TN':
description = '<b>Tennessee: '''+str(html_attribute_TN)+''';
break;
case 'TX':
description = '<b>Texas: '''+str(html_attribute_TX)+''';
break;
case 'UT':
description = '<b>Utah: '''+str(html_attribute_UT)+''';
break;
case 'VT':
description = '<b>Vermont: '''+str(html_attribute_VT)+''';
break;
case 'VA':
description = '<b>Virginia: '''+str(html_attribute_VA)+''';
break;
case 'WA':
description = '<b>Washington: '''+str(html_attribute_WA)+''';
break;
case 'WV':
description = '<b>West Virginia: '''+str(html_attribute_WV)+''';
break;
case 'WI':
description = '<b>Wisconsin: '''+str(html_attribute_WI)+''';
break;
case 'WY':
description = '<b>Wyoming: '''+str(html_attribute_WY)+''';
break;}      
            $('#selected-state > span').html(description).css({"font-weight": "bold", "color": "#000000"});
    },
    
    mouseout: function(event, data) {
    $('#selected-state > span').html('<b><u>'''+str(page_title)+'''</u> (estimate: <font color=#0000ff>'''+str(DEM_votes)+'''</font>-<font color=#ff0000>'''+str(REP_votes)+'''</font>. Hover over states)</b><span style="font-size: 14pt;"><br><b>Current senate is <font color=#0000ff>50</font>-<font color=#ff0000>50</font></b></span>').css({"font-weight": "normal", "color": "#000000"});
    },
    click: function(event, data) {
        $('#clicked-state').text('You clicked: '+data.name).parent().effect('highlight', {color: '#C7F464'}, 2000);
    },
    });
//# sourceURL=pen.js
</script>
<span style="font-size: 11pt;">
<font color=#000000>State election odds update every 20 minutes. Last updated: '''+str(now)+'''<br>
Over $1 million bet. State betting is from <a href="https://www.polymarket.com/">Polymarket</a>. Others to be added if liquid state market available.<br></span>
</html>

    </td>
        </tr>
    </table>
    <!--...-->
</center>
''')
print "here?"

### WRITE HTML in local directory ###
file_path = str(folder_name)+".html"
# converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
with open(file_path, "wb") as file:
    file.write(finalwinner_HTML_string)

print "HTML page saved locally as:", file_path

# print "mirror?"
# mirror = 0
# if mirror == 1:
#     print "attempting mirror"
#     ftp = FTP('72.14.177.84', timeout=8)
#     ftp.login('ebo', 'anlliG0HoQ8ZNVh')
#     print "attempting mirror 2"
#     converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
#     print "attempting mirror 3/ String:  "
#     print converted_DEM_HTML_string
#     ftp.storbinary(str("STOR files/"+str(folder_name)+".html"), converted_DEM_HTML_string)
#     print "MIRROR ElectionBettingOdds.com... Success! (Unless immediately followed by error message)"

# ##### FTP! :) #####
# print "writing to server"
# fg = open('/var/www/predictionmarketodds.com/public_html/'+str(folder_name)+'.html','w')
# fg.write(str(finalwinner_HTML_string))
# fg.close()
# print "PrecictionMarketOdds.com... Also Success! (Unless immediately followed by error message)"

# print "writing to server"
# fg = open('/var/www/178.62.65.243/public_html/'+str(folder_name)+'.html','w')
# fg.write(str(finalwinner_HTML_string))
# fg.close()
# print "Mirror 178.62.65.243... Also Success! (Unless immediately followed by error message)"

# print "writing to server"
# fg = open('/var/www/electionbettingodds.com/public_html/'+str(folder_name)+'.html','w')
# fg.write(str(finalwinner_HTML_string))
# fg.close()
# print "ElectionBettingOdds.com... Also Success! (Unless immediately followed by error message)"


"""
ftp = FTP('ftp.electionbettingodds.com', timeout=8)
ftp.login('fmdoepu9s27b','r52y3!pZK')
converted_DEM_HTML_string = io.BytesIO(finalwinner_HTML_string)
ftp.storbinary(str("STOR public_html/SenateMap2024.html"), converted_DEM_HTML_string)
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
