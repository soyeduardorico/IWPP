from flask import Flask, render_template_string, render_template, request, jsonify, session, send_from_directory
import os
import time
import folium
import json
import IWPP_maps
import IWPP_functions
import pandas as pd
from tinydb import TinyDB


#------------------------------------------------------------------------------------
# Basic settings
#------------------------------------------------------------------------------------

# Set the secret key for session encryption
secret_key = os.urandom(24)
print(secret_key)
app = Flask(__name__)
app.secret_key = secret_key

# file locations
absFilePath = os.path.dirname(__file__)
mapData = os.path.join(absFilePath,  'map')
rootData = os.path.join(absFilePath,  'data')
compensations_path = os.path.join(mapData,  'compensations.geojson')
developments_path = os.path.join(mapData,  'developments.geojson')
WWTP_path = os.path.join(mapData,  'WWTP.geojson')
river_segments_path = os.path.join(mapData,  'river_segment_render2.geojson')
CSO_nodes_path = os.path.join(mapData,  'CSO_nodes.geojson')
databse_path = os.path.join(mapData,  'aggregated_results_webpage.xlsx')
water_source_nodes_path = os.path.join(mapData,  'water_sources.geojson')
assets_sewers_path = os.path.join(mapData,  'assets_sewers.geojson')
assets_pumping_path = os.path.join(mapData,  'assets_pumping.geojson')


# returns the positionin of the first '1' in a list or '0' if none
def position (list):
    try:
        # Try to find the index of the first '1'
        index = list.index(1)+1
    except ValueError:
        # If '1' is not in the list, set index to 0
        index = 0    
    return index

# returns the positionin the excel of a given status
def status_position (databse_path, status_list):
    # Transforms the status list into a list of integers
    int_status_list = [int(item) for item in status_list]
    # Break the status_list into three lists at positions 3 and 6   
    status_list1 = int_status_list[:3]
    status_list2 = int_status_list[3:6]
    status_list3 = int_status_list[6:]

    # Read the Excel file and opens one of the sheets to read the headings
    df = pd.read_excel(databse_path, sheet_name='mean_flow')

    # Get the column names
    column_names = df.columns
    # Convert column_names to a list
    column_names_list = column_names.tolist()
    # Find the index of status id
    #index = column_names_list.index('002')

    index1 = position(status_list1)
    index2 = position(status_list2)
    index3 = position(status_list3)
    index_status = str(index1) + str(index2) + str(index3)
    
    index = column_names_list.index(index_status)

    return index

# Read the Excel file
df = pd.read_excel(databse_path, sheet_name='mean_flow')
# Exclude the first column
df = df.iloc[:, 1:]
# Calculate the maximum and minimum
max_value = df.max().max()
min_value = df.min().min()

print('Maximum:', max_value)
print('Minimum:', min_value)