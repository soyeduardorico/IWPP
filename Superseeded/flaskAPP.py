import flask

from flask import Flask, render_template, url_for, request, jsonify, send_from_directory, session, redirect, make_response, flash
import time
import os
import json
from tinydb import TinyDB, Query


app = Flask(__name__)
app.secret_key = os.urandom(24)
absFilePath = os.path.dirname(__file__)
rootData = os.path.join(absFilePath,  'data')

# this is to exchange x-y coordinates that gets messed up when sent from the front end.
def invert(array):
    inverted = []
    for i in range(0, int(len(array))):
       inverted.append([array[i][1],array[i][0]])
    return inverted

# -----------------------------------------------------------------------------------------
# renders intro page for old leaflet version of development
# -----------------------------------------------------------------------------------------
# @app.route ('/')
# def index():
#     millis = int(round(time.time() * 1000))
#     variable = str(millis)
#     variable = '1694644359383'
#     session['user'] = variable
#     return render_template('basic2.html')



# -----------------------------------------------------------------------------------------
# renders intro page
# -----------------------------------------------------------------------------------------
@app.route ('/')
def index():
    millis = int(round(time.time() * 1000))
    variable = str(millis)
    #variable = '1694644359383'
    session['user'] = variable
    sessionFolder=os.path.join(rootData, variable)

    # generates local folder
    os.mkdir(sessionFolder)

    # generates local database
    userDatabase =os.path.join(sessionFolder,variable + '_database.json')
    db = TinyDB(userDatabase)
    db.close()
    user_id = session.get('user')
    #return render_template ('importImage.html')
    
    return render_template('importImage.html', session_name=session['user'])
    #return render_template('drawNetwork.html', session_name=session['user'])


# -----------------------------------------------------------------------------------------
# closes session
# -----------------------------------------------------------------------------------------
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return 'Dropped'


# -----------------------------------------------------------------------------------------
# fabricates a url for non static folder a seen in https://www.youtube.com/watch?v=Y2fMCxLz6wM
# -----------------------------------------------------------------------------------------
@app.route('/data/<filename>')
def data(filename):
    target_directory = 'data/' + session['user']
    return send_from_directory(target_directory, filename)


# -----------------------------------------------------------------------------------------
# routes for main webpages drawDevelopment
# -----------------------------------------------------------------------------------------
@app.route('/drawDevelopment')
def drawDevelopment():
    #json_data = request.args.get('json_data')
    user_id = session.get('user')
    return render_template('drawDevelopment.html', session_name=session['user'])
    #return render_template('drawDevelopment.html')


# @app.route('/developmentMap')
# def drawNetwork():
#     return render_template('developmentMap.html')


@app.route('/drawNetwork')
def drawNetwork():
    return render_template('drawNetwork.html')

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
    return jsonify(invert(coordinates))


@app.route('/getRect', methods=['GET'])
def getRect():
    user_folder = session.get('user')
    session_folder = os.path.join(rootData, user_folder)
    rect_file_name = os.path.join(session_folder, user_folder+'_rect.json')
    with open(rect_file_name, 'r') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    millis=0
    points = []
    number_iterations  = 1
    # serve(app, host='0.0.0.0', port=80)
    app.run(debug=True, threaded=True)# requires threads to run parallel requests independetly