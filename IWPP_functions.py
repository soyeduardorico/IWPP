from flask import Flask, render_template, request, jsonify
import json
import os
import folium
import pandas as pd

absFilePath = os.path.dirname(__file__)
rootData = os.path.join(absFilePath,  'data')
mapData = os.path.join(absFilePath,  'map')
offset_items_path = os.path.join(mapData,  'Offset.xlsx')
development_items_path = os.path.join(mapData,  'Development.xlsx')
river_segmments_path = os.path.join(mapData,  'river_segments.geojson')

def invert(array):
    inverted = []
    print(int(len(array)-1))
    for i in range(0, int(len(array))):
       inverted.append([array[i][1],array[i][0]])
    return inverted

#------------------------------------------------------------------------------------
# Round up the data of the geojson to one decimal space
#------------------------------------------------------------------------------------
def round_attributes(geojson, precision):
    for feature in geojson['features']:
        properties = feature['properties']
        for key, value in properties.items():
            if isinstance(value, float):
                properties[key] = round(value, precision)

#------------------------------------------------------------------------------------
# returns the positionin of the first '1' in a list or '0' if none
#------------------------------------------------------------------------------------
def position (list):
    try:
        # Try to find the index of the first '1'
        index = list.index(1)+1
    except ValueError:
        # If '1' is not in the list, set index to 0
        index = 0    
    return index

#------------------------------------------------------------------------------------
# returns the positionin the excel of a given status
#------------------------------------------------------------------------------------
def status_position (databse_path, status_list):
    # Transforms the status list into a list of integers
    int_status_list = [int(item) for item in status_list]
    # Break the status_list into three lists at positions 3 and 6   
    status_list1 = int_status_list[:3]
    status_list2 = int_status_list[3:6]
    status_list3 = int_status_list[6:]

    # Read the Excel file and opens one of the sheets to read the headings. The sheet name is not relevant
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


#------------------------------------------------------------------------------------
# Reads area geojson and updates its properties with the data from the excel 
#------------------------------------------------------------------------------------
def update_values(file,data, baseline_data, baseline_data_brent, legend):
    # open the original file
    with open(file) as f: areasdict = json.load(f)
    areasdict['features'] = sorted(areasdict['features'], key=lambda feature: feature['properties']['id'])

    # Iterate over the features and update the property value
    for feature in areasdict['features']:
        if data is not None:
            d1=data.pop(0)
            d2=baseline_data.pop(0)
            d3=baseline_data_brent.pop(0)
            feature['properties'][legend] = d1
            feature['properties']['%increase'] = (d1-d2)/d1*100
            feature['properties']['%brent'] = (d1-d3)/d1*100

    round_attributes(areasdict, 1)
    return areasdict


#------------------------------------------------------------------------------------
# Generates a summary to show in teh webapp from the excel of offests
#------------------------------------------------------------------------------------
def summarize_offsets():
    # Load the Excel file
    data = pd.read_excel(offset_items_path)

    # Sum the first two columns
    sum_first_column = data.iloc[:, 0].astype(int).sum()
    sum_second_column = data.iloc[:, 1].astype(int).sum()

    # Sum values by category in the third column
    sums_by_category = data.groupby(data.columns[2])[data.columns[0:2]].sum().astype(int)
    sums_by_category_list = [list(values) for values in sums_by_category.values]

    # Define items to return
    offset_people=int(sum_first_column)
    offset_volume=int(sum_second_column)   
    offset_people_by_status=sums_by_category['people'].values.tolist()
    offset_volume_by_status=sums_by_category['m3/d'].values.tolist()
    
    # Creates a list
    offset_summary = [offset_people, offset_volume, offset_people_by_status,offset_volume_by_status]

    return offset_summary


#------------------------------------------------------------------------------------
# Generates a summary to show in teh webapp from the excel of developments
#------------------------------------------------------------------------------------
def summarize_devlopments():
    # Load the Excel file
    data = pd.read_excel(development_items_path)

    # Sum the first two columns
    sum_first_column = data.iloc[:, 0].astype(int).sum()


    # Sum values by category in the third column
    sums_by_category = data.groupby(data.columns[2])[data.columns[0:2]].sum().astype(int)

    # Define items to return
    development_area=int(sum_first_column)
    development_area_by_status=sums_by_category['plan_area'].values.tolist()

    # Creates a list
    development_summary = [development_area, development_area_by_status]

    return development_summary


#------------------------------------------------------------------------------------
# Brings pre-calculated information from WSIMOD
#------------------------------------------------------------------------------------
def read_data_from_database(database_path, sheet_name, column):

    # Load the Excel file
    df = pd.read_excel(database_path, sheet_name=sheet_name)

    # Get the nth column (assuming n is 0-indexed)
    n = column  # replace with your desired column index
    column_data = df.iloc[:, n]

    # Convert the column data to a list
    column_data_list = column_data.tolist()

    return column_data_list
