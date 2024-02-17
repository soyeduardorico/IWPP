from flask import Flask, render_template, request, jsonify
import json
import os
import folium
import pandas as pd
import IWPP_functions
import branca.colormap as cm

#file paths
absFilePath = os.path.dirname(__file__)
rootData = os.path.join(absFilePath,  'data')
mapData = os.path.join(absFilePath,  'map')

# Set initial location and zoom level
width_map=800
height_map=800
location_S_3=[51.54, -0.14]
zoom_start_S_3=11.4  
location_S_4=[51.54, -0.25]
zoom_start_S_4=12

# Set lists of colours for rendering features in maps
colourlists={'red': ['yellow','red','brown'],
             'green': ['yellow','green'],
             'blue': ['yellow','green','blue'],
             'black': ['grey','black']
             }

#------------------------------------------------------------------------------------
# Remap values for thickness of lines
#------------------------------------------------------------------------------------
def remap_values(value, from_min, from_max, to_min, to_max):
    # Figure out how 'wide' each range is
    from_span = from_max - from_min
    to_span = to_max - to_min

    # Convert the left range into a 0-1 range (float)
    value_scaled = float(value - from_min) / float(from_span)

    # Convert the 0-1 range into a value in the right range.
    return to_min + (value_scaled * to_span)


#------------------------------------------------------------------------------------
# Generates the folium map for the S_4 pages bringing the mapbox studio base
#------------------------------------------------------------------------------------
def map_base_S_3():
    # Create a map
    m = folium.Map(location=location_S_3, 
                   control_scale=True, 
                   zoom_start=zoom_start_S_3,
                   width=800, 
                   height=800,)

    # Add a custom tile layer to the map
    folium.TileLayer(
        tiles="https://api.mapbox.com/styles/v1/soyeduardorico/clqp9dr8s00v201qrcb2acjki/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1Ijoic295ZWR1YXJkb3JpY28iLCJhIjoiY2tnbDFpOGRqMDV2ZzM5cnh0bjR5Z3FsdSJ9.pStbCDRInR4xBYG9cXq3bA",
        attr='Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        name='map'
    ).add_to(m)

    return m


#------------------------------------------------------------------------------------
# Generates the folium map for the S_4 pages bringing the mapbox studio base
#------------------------------------------------------------------------------------
def map_base_S_4():
    # Create a map
    m = folium.Map(location=location_S_4, 
                   control_scale=True, 
                   zoom_start=zoom_start_S_4,
                   width=800, 
                   height=800,)

    # Add a custom tile layer to the map
    folium.TileLayer(
        tiles="https://api.mapbox.com/styles/v1/soyeduardorico/clrqxkxsk00di01pedathcp14/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1Ijoic295ZWR1YXJkb3JpY28iLCJhIjoiY2tnbDFpOGRqMDV2ZzM5cnh0bjR5Z3FsdSJ9.pStbCDRInR4xBYG9cXq3bA",
        attr='Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        name='map'
    ).add_to(m)

    return m


# def map_base_S_4():
#     m = folium.Map(
#     location=location_S_4, 
#     width=800, 
#     height=800,
#     zoom_start=zoom_start_S_4,  # Set initial zoom level
#     tiles=f"https://api.mapbox.com/styles/v1/soyeduardorico/clrqxkxsk00di01pedathcp14/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token=pk.eyJ1Ijoic295ZWR1YXJkb3JpY28iLCJhIjoiY2tnbDFpOGRqMDV2ZzM5cnh0bjR5Z3FsdSJ9.pStbCDRInR4xBYG9cXq3bA",
#     attr='Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
#     name='map'
# )
#     return m


#------------------------------------------------------------------------------------
# Adds areas from a geojson colourcoded by status to a given map
#------------------------------------------------------------------------------------
def add_areas_colourcoded (map, geometry_file_path):
    m = map 
    with open(geometry_file_path) as l: area_data = json.load(l)
    def style_function(feature):
        status = feature['properties']['status']
        if status == 1:
            return {'fillColor': '#ffff00', 'color': '#ffff00'}  # Yellow
        elif status == 2:
            return {'fillColor': '#ffa500', 'color': '#ffa500'}  # Orange
        else:
            return {'fillColor': '#ff0000', 'color': '#ff0000'}  # Red
    
    # Add the GeoJSON layer
    j = folium.GeoJson(
        area_data,
        name='developments',
        style_function=style_function,
    ).add_to(m)

    # Add a tooltip for each feature
    j.add_child(folium.features.GeoJsonTooltip(fields=list(area_data['features'][0]['properties'].keys())))

    return m

#------------------------------------------------------------------------------------
# Adds points from a geojson colourcoded by status to a given map
#------------------------------------------------------------------------------------
def add_points_colourcoded (map, point_file_path, label, pointsize):  
    m = map

    # Read the GeoJSON data
    with open(point_file_path) as f: compensations_data = json.load(f)

    # Create a FeatureGroup
    compensations = folium.FeatureGroup(name=label)

    # Add the GeoJSON data to the FeatureGroup
    for feature in compensations_data['features']:
        if feature['geometry']['type'] == 'Point':
            status = feature['properties']['status']
            color = '#ffff00' if status == 1 else '#ffa500' if status == 2 else '#ff0000'

            properties = feature['properties']
            popup_text = '<br>'.join([f'{k}: {v}' for k, v in properties.items()])  # Create the popup text
            folium.CircleMarker(
                location=feature['geometry']['coordinates'][::-1],  # Reverse the coordinates because GeoJSON uses (longitude, latitude) while Folium uses (latitude, longitude)
                radius=pointsize,  # Set the radius of the circle markers
                color=color,  # Set the color of the circle markers
                fill=True,
                fill_color=color,  # Set the fill color of the circle markers
            ).add_child(
                folium.Tooltip(popup_text)  # Add a popup for each property
            ).add_to(compensations)

    # Add the FeatureGroup to the map
    compensations.add_to(m)

    return m


#------------------------------------------------------------------------------------
# Adds colourcoded (colourcoded=True) or thickness(colourcoded-False) rendered features from a geojson to a given map
#------------------------------------------------------------------------------------
def add_features (map, geometry_file_path, variable, legend ,colourcoded, colour, status_list, property_list_path=None):
    m = map 

    # Read the Excel file
    df = pd.read_excel(property_list_path, sheet_name=variable)

    # obtains the position in the excel related to the status_list
    position = IWPP_functions.status_position(property_list_path, status_list)
   
    # updates the values in the geojson with the data related to the status to later display it
    variable_to_add = df.iloc[:, position].tolist() # Get the nth column (assuming n is 0-indexed)   
    variable_to_add_baseline = df.iloc[:, 1].tolist() # brings the baseline data to compare

    # Calculate the maximum and minimum
    df = df.iloc[:, 1:] # Exclude the first column
    max_value = df.max().max()
    min_value = df.min().min()

    # generates a new geogson with the old geometry and the new properties
    map_data = IWPP_functions.update_values(geometry_file_path,variable_to_add, variable_to_add_baseline, legend)

    if colourcoded == True:
        # Define a colormap
        colormap = cm.LinearColormap(colors=colourlists[colour], vmin=min_value, vmax=max_value)

        # Add features to the map
        j = folium.GeoJson(
            map_data,
            name=variable,
            style_function=lambda feature: {
                'color': colormap(feature['properties'][legend]),
                'weight': 8,
            }
        ).add_to(m)
    else:              
        j = folium.GeoJson(
            map_data,
            name=variable,
            style_function=lambda feature: {
                'color': '#0000FF', # Uses blue by default
                'weight': remap_values(feature['properties'][legend], min_value, max_value, 2, 20),  # Set the thickness of the lines based on a value,
            }
        ).add_to(m)

    # Add a tooltip for each feature
    j.add_child(folium.features.GeoJsonTooltip(fields=list(map_data['features'][0]['properties'].keys())))

    return m


def add_points (map, point_file_path, variable, legend ,colourcoded, colour, status_list=None, property_list_path=None):
    m = map 

    # Read the Excel file
    df = pd.read_excel(property_list_path, sheet_name=variable)

    # obtains the position in the excel related to the status_list
    position = IWPP_functions.status_position(property_list_path, status_list)
   
    # updates the values in the geojson with the data related to the status to later display it
    variable_to_add = df.iloc[:, position].tolist() # Get the nth column (assuming n is 0-indexed)   
    variable_to_add_baseline = df.iloc[:, 1].tolist() # brings the baseline data to compare

    # Calculate the maximum and minimum
    df = df.iloc[:, 1:] # Exclude the first column
    max_value = df.max().max()
    min_value = df.min().min()

    # generates a new geogson with the old geometry and the new properties
    map_data = IWPP_functions.update_values(point_file_path,variable_to_add, variable_to_add_baseline, legend)

    # Define a colormap
    # at the moment min and max are 0-1, but they should be the min and max of the property
    colormap = cm.LinearColormap(colors=colourlists[colour], vmin=min_value, vmax=max_value)
     

    # Create a FeatureGroup
    point_map = folium.FeatureGroup(name=variable)

    # Add the GeoJSON data to the FeatureGroup
    for feature in map_data['features']:
        properties = feature['properties']
        popup_text = '<br>'.join([f'{k}: {v}' for k, v in properties.items()])  # Create the popup text
        if colourcoded == True:
            rad=10
            col=colormap(feature['properties'][legend])
        else:
            rad = remap_values(feature['properties'][legend], min_value, max_value, 2, 20)
            col='#0000FF'
        folium.CircleMarker(
            location=feature['geometry']['coordinates'][::-1],  # Reverse the coordinates because GeoJSON uses (longitude, latitude) while Folium uses (latitude, longitude)
            radius= rad,  # Set the radius of the circle markers
            color=col,  # Set the color of the circle markers
            fill=True,
            fill_color=col,  # Set the fill color of the circle markers
        ).add_child(
            folium.Tooltip(popup_text)  # Add a popup for each property
        ).add_to(point_map)

    # Add the FeatureGroup to the map
    point_map.add_to(m)

    return m



# def add_points (map, point_file_path, variable, legend ,colourcoded, status_list=None, property_list_path=None):
#     m = map 
#     with open(point_file_path) as l: point_data = json.load(l)

#     # updates the values in the geojson with the data related to the status to later display it
#     if status_list is not None:
#         variable_to_add = IWPP_functions.read_data_from_database(property_list_path, variable, 0)
#         variable_to_add_copy = variable_to_add.copy()
#         point_data = IWPP_functions.update_values(point_file_path,variable_to_add, legend)

#     # Define a colormap
#     # at the moment min and max are 0-1, but they should be the min and max of the property
#     colormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=0, vmax=1)  
#     from_min = min(variable_to_add_copy)
#     from_max = max(variable_to_add_copy)
    
#     # Create a FeatureGroup
#     point_map = folium.FeatureGroup(name=variable)

#     # Add the GeoJSON data to the FeatureGroup
#     for feature in point_data['features']:
#         properties = feature['properties']
#         popup_text = '<br>'.join([f'{k}: {v}' for k, v in properties.items()])  # Create the popup text
#         if colourcoded == True:
#             rad=10
#             col=colormap(feature['properties'][legend])
#         else:
#             rad = remap_values(feature['properties'][legend], from_min, from_max, 2, 20)
#             col='#0000FF'
#         folium.CircleMarker(
#             location=feature['geometry']['coordinates'][::-1],  # Reverse the coordinates because GeoJSON uses (longitude, latitude) while Folium uses (latitude, longitude)
#             radius= rad,  # Set the radius of the circle markers
#             color=col,  # Set the color of the circle markers
#             fill=True,
#             fill_color=col,  # Set the fill color of the circle markers
#         ).add_child(
#             folium.Tooltip(popup_text)  # Add a popup for each property
#         ).add_to(point_map)

#     # Add the FeatureGroup to the map
#     point_map.add_to(m)

#     return m



# #------------------------------------------------------------------------------------
# # Adds points from a geojson to a map. Can be colourcoded
# #------------------------------------------------------------------------------------
# def add_points(map, point_file_path, label, pointsize, colourcode):  
#     m = map

#     # Read the GeoJSON data
#     with open(point_file_path) as f: compensations_data = json.load(f)

#     # Create a FeatureGroup
#     compensations = folium.FeatureGroup(name=label)

#     # Add the GeoJSON data to the FeatureGroup
#     for feature in compensations_data['features']:
#         if feature['geometry']['type'] == 'Point':
#             if colourcode:
#                 status = feature['properties']['status']
#                 color = '#ffff00' if status == 1 else '#ffa500' if status == 2 else '#ff0000'
#             else:
#                 color = '#0000ff'
#             properties = feature['properties']
#             popup_text = '<br>'.join([f'{k}: {v}' for k, v in properties.items()])  # Create the popup text
#             folium.CircleMarker(
#                 location=feature['geometry']['coordinates'][::-1],  # Reverse the coordinates because GeoJSON uses (longitude, latitude) while Folium uses (latitude, longitude)
#                 radius=pointsize,  # Set the radius of the circle markers
#                 color=color,  # Set the color of the circle markers
#                 fill=True,
#                 fill_color=color,  # Set the fill color of the circle markers
#             ).add_child(
#                 folium.Tooltip(popup_text)  # Add a popup for each property
#             ).add_to(compensations)

#     # Add the FeatureGroup to the map
#     compensations.add_to(m)

#     return m


# river_segmments_path = os.path.join(mapData,  'river_segments.geojson')
# CSO_nodes_path = os.path.join(mapData,  'CSO_nodes.geojson')
# river_segment_pollution_path = os.path.join(mapData,  'River_segment_pollution.xlsx')


