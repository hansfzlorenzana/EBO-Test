#!/usr/bin/python
#import library to do http requests:
from __future__ import division             #enables division with decimals
import math                                 #enables calculation of square roots
import urllib2                            #enables loading web links
import httplib2                             #html parser
from xml.dom.minidom import parseString     #xml parser
import datetime                             #Allows date calculation
import calendar                             #Allows date calculation
import datetime               #Allows date calculation
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

input_file_paths = [
    "temp_server/RepublicanVicePresident_2024/WIN_chart_dataRepublicanVicePresident_2024.txt",
    "temp_server/RepublicanVicePresident_2024/WIN_chart_data_fullRepublicanVicePresident_2024.txt"
]

def add_candidate_column_chart(input_file_path):
    with open(input_file_path, "r") as myfile:
        long_file = myfile.read()
            
        new_long_file_1 = long_file.replace("],","0.0,],")
        # If you want to perform additional replacements, uncomment and add here.
        # new_long_file_1 = long_file.replace("]***",", ['Newsom', 0.0]***")
        # new_long_file_1 = new_long_file_1.replace(",,",",")
        
        print new_long_file_1

    output_file_path = input_file_path
    with open(output_file_path, 'w') as fy:
        fy.write(new_long_file_1)

for input_file in input_file_paths:
    add_candidate_column_chart(input_file)