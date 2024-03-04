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
river_segments_path = os.path.join(mapData,  'river_segment_render.geojson')
flow_risk_points_path = os.path.join(mapData,  'flow_risk_points_render.geojson')
CSO_nodes_path = os.path.join(mapData,  'CSO_nodes_render.geojson')
databse_path = os.path.join(mapData,  'aggregated_results_webpage.xlsx')
databse_brent_path = os.path.join(mapData,  'aggregated_results_brent_webpage.xlsx')
water_source_nodes_path = os.path.join(mapData,  'water_sources.geojson')
assets_sewers_path = os.path.join(mapData,  'assets_sewers.geojson')
assets_pumping_path = os.path.join(mapData,  'assets_pumping.geojson')
asset_databse_path = os.path.join(mapData,  'asset_data.xlsx')


development_items_path = os.path.join(mapData,  'Development.xlsx')
data = pd.read_excel(development_items_path)

#------------------------------------------------------------------------------------
# Processing and starting edpoints
#------------------------------------------------------------------------------------

# fabricates a url for non static folder a seen in https://www.youtube.com/watch?v=Y2fMCxLz6wM
@app.route('/data/<filename>')
def data(filename):
    target_directory = 'data/' + session['user']
    return send_from_directory(target_directory, filename)


# closes session
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return 'Dropped'


# receives a list of polygons from the map and saves it as a JSON file
@app.route('/savePolygons', methods=['POST'])
def savePolygons():
    # get the JSON data from the request body
    json_data = request.get_json()

    # get the user session folder
    user_folder = session.get('user')
    session_folder = os.path.join(rootData, user_folder)

    # save the JSON data as a file in the user session folder
    json_file = os.path.join(session_folder, user_folder+'_polygons.json')
    with open(json_file, 'w') as f:
        json.dump(json_data, f)

    return jsonify({'message': 'JSON data saved successfully.'})


# receives rectangle data from the map adjustment exercise and saves it as a JSON file
@app.route('/saveRect', methods=['POST'])
def send_rect():
    # get the rectangle data from the request body
    rect = request.get_json()

    # get the user session folder
    user_folder = session.get('user')
    session_folder = os.path.join(rootData, user_folder)

    # save the rectangle data as a JSON file in the user session folder
    rect_file = os.path.join(session_folder, user_folder+'_rect.json')
    with open(rect_file, 'w') as f:
        json.dump(rect, f)

    return jsonify({'message': 'Rectangle data saved successfully.'})


# handles image upload requestand saves to the user session folder
@app.route('/uploadImage', methods=['POST'])
def uploadImage():
    file = request.files['image']
    name = session.get('user')   
    file.save('data/'+name+'/' + name + 'image.jpg')
    return 'Image uploaded successfully'


@app.route('/bringRect', methods=['POST'])
def bringRect():
    # get the user session folder
    session_name = session.get('user')
    session_folder = os.path.join(rootData, session_name)
    rect_file_name = os.path.join(session_folder, session_name +'_rect.json')
    # Load the contents of the JSON file into a dictionary
    with open(rect_file_name, 'r') as f:
        data = json.load(f)
        coordinates = data['features'][0]['geometry']['coordinates'][0]
    return jsonify(IWPP_functions.invert(coordinates))


@app.route('/getRect', methods=['GET'])
def getRect():
    user_folder = session.get('user')
    session_folder = os.path.join(rootData, user_folder)
    rect_file_name = os.path.join(session_folder, user_folder+'_rect.json')
    with open(rect_file_name, 'r') as f:
        data = json.load(f)
    return jsonify(data)


#------------------------------------------------------------------------------------
# Endpoints for pages
#------------------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template('0_0.html')


@app.route("/S_0")
def S_0():
    return render_template('S_0.html')


# @app.route("/S_3_2")
# def S_3_2():
#     m = IWPP_maps.map_base_S_3()
#     return render_template('S_3_2.html', map=m.get_root().render())


@app.route("/S_3_3")
def S_3_3():
    m = IWPP_maps.map_base_S_3()
    m= IWPP_maps.add_points_colourcoded (m, compensations_path, 'Compensations', 2)
    m= IWPP_maps.add_areas_colourcoded (m, developments_path)
    folium.LayerControl(position='topleft').add_to(m)
    offset_summary = IWPP_functions.summarize_offsets()
    development_summary = IWPP_functions.summarize_devlopments()
    return render_template('S_3_3.html', map=m.get_root().render(), 
                           development_area=development_summary[0], 
                           offset_volume=offset_summary[1], 
                           development_area_by_status=development_summary[1],
                           offset_volume_by_status=offset_summary[3])


# Needed to read the current status list to render the appropriate data in the map
@app.route("/S_3_4_register", methods=['GET', 'POST'])
def S_3_4_register():
    status_List = request.get_json()
    session['status_List'] = status_List
    return jsonify({'message': 'status set successfully'})


@app.route("/S_3_4")
def S_3_4():
    # Get the status list from the session
    status_List = session['status_List']

    # Generates map and layers  
    m = IWPP_maps.map_base_S_3()
    m= IWPP_maps.add_features (m, river_segments_path, 'mean_flow' ,'m3/sec', False, None ,status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_features (m, river_segments_path, 'drought_risk' ,'days', True, 'red',  status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_points (m, flow_risk_points_path, 'highflow_risk' ,'days', False, 'blue', status_List, databse_path, databse_brent_path)

    # Create a separate layer control for additional layers
    layer_control = folium.LayerControl(position='topleft', collapsed=False)

    # Add features and points to the map
    m.add_child(layer_control)
    return render_template('S_3_4.html', map=m.get_root().render(), status_List=status_List)


# Needed to read the current status list to render the appropriate data in the map
@app.route("/S_3_5_register", methods=['GET', 'POST'])
def S_3_5_register():
    status_List = request.get_json()
    session['status_List'] = status_List
    return jsonify({'message': 'status set successfully'})


@app.route("/S_3_5")
def S_3_5():
    # Get the status list from the session
    status_List = session['status_List']
    
    # Generates map and layers
    m = IWPP_maps.map_base_S_3()
    m= IWPP_maps.add_features (m, river_segments_path, 'ammonia_conc' ,'mg/l',True, 'red' ,status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_features (m, river_segments_path, 'nitrate_conc' ,'mg/l',True, 'red' ,status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_features (m, river_segments_path, 'phosphate_conc' ,'mg/l',True, 'red' ,status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_points (m, CSO_nodes_path, 'CSO_events' ,'m3/d', False, 'blue', status_List, databse_path, databse_brent_path)

    # Create a separate layer control for additional layers
    layer_control = folium.LayerControl(position='topleft', collapsed=False)

    # Add features and points to the map
    m.add_child(layer_control)

    return render_template('S_3_5.html', map=m.get_root().render(), status_List=status_List)


# Needed to read the current status list to render the appropriate data in the map
@app.route("/S_3_6_register", methods=['GET', 'POST'])
def S_3_6_register():
    status_List = request.get_json()
    session['status_List'] = status_List
    return jsonify({'message': 'status set successfully'})


@app.route("/S_3_6")
def S_3_6():      
    # Get the status list from the session
    status_List = session['status_List']

    # Generates map and layers
    m = IWPP_maps.map_base_S_3()

    m= IWPP_maps.add_features (m, WWTP_path, 'ammonia_load' ,'kg/year',True, 'red', status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_features (m, WWTP_path, 'nitrate_load' ,'kg/year', True, 'red', status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_features (m, WWTP_path, 'phosphate_load' ,'kg/year', True, 'red', status_List, databse_path, databse_brent_path)
    m= IWPP_maps.add_points (m, water_source_nodes_path, 'water_demand' ,'m3/day',False, 'blue', status_List, databse_path, databse_brent_path)

    # Create a separate layer control for additional layers
    layer_control = folium.LayerControl(position='topleft', collapsed=False)

    # Add features and points to the map
    m.add_child(layer_control)

    return render_template('S_3_6.html', map=m.get_root().render(), status_List=status_List)


@app.route("/S_3_7")
def S_3_7():
    return render_template('S_3_7.html')


@app.route('/S_3_dataviz')
def S_3_dataviz():
    return render_template('S_3_dataviz.html', statuses=data['status'].unique())


@app.route('/get_data', methods=['POST'])
def get_data():
    status = request.form.get('status')
    filtered_data = data[data['status'] == int(status)]
    return filtered_data.to_json(orient='records')


@app.route("/S_4_1")
def S_4_1():
    m = IWPP_maps.map_base_S_4()
    return render_template('S_4_1.html', map=m.get_root().render())


@app.route("/S_4_2")
def S_4_2():
    m = IWPP_maps.map_base_S_4()
    m= IWPP_maps.add_points_colourcoded (m, compensations_path,'Compensations', 2)
    m= IWPP_maps.add_areas_colourcoded (m, developments_path)
    folium.LayerControl(position='topleft').add_to(m)
    offset_summary = IWPP_functions.summarize_offsets()
    development_summary = IWPP_functions.summarize_devlopments()
    return render_template('S_4_2.html', map=m.get_root().render(), 
                           development_area=development_summary[0], 
                           offset_volume=offset_summary[1], 
                           development_area_by_status=development_summary[1],
                           offset_volume_by_status=offset_summary[3])


@app.route("/S_4_2_register", methods=['GET', 'POST'])
def S_4_2_register():
    status_List = request.get_json()
    session['status_List'] = status_List
    return jsonify({'message': 'status set successfully'})


@app.route("/S_4_3")
def S_4_3():
    # Get the status list from the session
    status_List = session['status_List']

    # Generates map and layers
    m = IWPP_maps.map_base_S_4()
    m= IWPP_maps.add_features (m, assets_sewers_path, 'asset_sewers_status' ,'status', True, 'red', status_List, asset_databse_path, asset_databse_path)
    m= IWPP_maps.add_points (m, assets_pumping_path, 'asset_pumping_status' ,'status',False, 'blue', status_List, asset_databse_path, asset_databse_path)

    # Create a separate layer control for additional layers
    layer_control = folium.LayerControl(position='topleft', collapsed=False)

    # Add features and points to the map
    m.add_child(layer_control)

    return render_template('S_4_3.html', map=m.get_root().render(), status_List=status_List)


@app.route("/S_4_3_register", methods=['GET', 'POST'])
def S_4_3_register():
    status_List = request.get_json()
    session['status_List'] = status_List
    return jsonify({'message': 'status set successfully'})


@app.route("/D_1")
def D_1():
    return render_template('D_1.html')


@app.route ('/D_2_0 ')
def D_2_0():
    millis = int(round(time.time() * 1000))
    variable = str(millis)
    variable = '1706397151890'
    session['user'] = variable
    sessionFolder=os.path.join(rootData, variable)

    # generates local folder
    #os.mkdir(sessionFolder)

    # generates local database
    userDatabase =os.path.join(sessionFolder,variable + '_database.json')
    db = TinyDB(userDatabase)
    db.close()
    user_id = session.get('user')

    m = IWPP_maps.map_base_S_4()
    #m = m.get_root().render()
    #m = m._repr_html_()
    #return render_template('D_2_0.html', map=m)
    return render_template('D_2_0.html', session_name=session['user'])


# @app.route('/D_2_1')
# def D_2_1():
#     #json_data = request.args.get('json_data')
#     user_id = session.get('user')
#     return render_template('D_2_1.html', session_name=session['user'])


@app.route('/D_2_1')
def D_2_1():
    #json_data = request.args.get('json_data')
    user_id = session.get('user')
    return render_template('D_2_1.html', session_name=session['user'])


# @app.route('/D_3')
# def D_3():
#     #json_data = request.args.get('json_data')
#     user_id = session.get('user')
#     return render_template('D_3.html', session_name=session['user'])



@app.route('/D_3')
def D_3():
    #json_data = request.args.get('json_data')
    user_id = session.get('user')
    return render_template('D_3.html', session_name=session['user'])

#------------------------------------------------------------------------------------
# Starts the server
#------------------------------------------------------------------------------------
if __name__ == "__main__":
    app.static_folder = 'static'
    app.run(debug=True)
    
    
