#APPLICATION FOR MEDICAL COST PREDICTION IN FOUR BIGGEST REGIONS IN USA. 

"""
!!!DISCLAIMER!!
All data are protected by US Office Of Government Ethics (OGE).
Commerical purposes are restricted, any modifications are 
expected to have permission from US Authorities.
"""

import numpy as np
import pandas as pd
import pickle
import pyodbc
from datetime import datetime
from flask import Flask, request, render_template, flash
from flask import redirect, url_for, jsonify, make_response
from utils.app_process import *
from utils.database_process import *

# global variables
logged_id = None
is_predicted = False
predicted_value = None

# connection string
conn = pyodbc.connect("DRIVER={SQL Server};Server=WINDOWS-11\SQLEXPRESS;" +
                      "Database=QA_TEST;Port=8008;trusted_connection=true")
datamodel = DataModel(conn)

#Load the trained model and encoder. (Pickle file)
model = pickle.load(open('models/svr_model.pkl', 'rb'))
scaler = pickle.load(open('models/mm_encoder.pkl', 'rb'))
lmbda = pickle.load(open('models/lmbda_price.pkl', 'rb'))

#Flask class - Web application. 
app = Flask(__name__)
app.secret_key = "QCTESTING"

# homepage - login UI. 
@app.route('/')
def home():
    return render_template('login.html')

# get user login and process
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        is_valid_log, logged_id_to_valid = datamodel.check_login(username, password)
        if is_valid_log:
            return redirect(url_for('menu', logged_id=logged_id_to_valid))
        
        message = {'message' : 
                f'Username or password incorrect, return and try again'}
        return make_response(jsonify(message), 400)
    
    return render_template('login.html')

# menu input - prediction UI
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    global logged_id, is_predicted, predicted_value

    #input section
    ageinput = request.form.get('ageinput')
    genderinput = request.form.get('genderinput')
    bmiinput = request.form.get('bmiinput')
    childinput = request.form.get('childinput')
    smokinginput = request.form.get('smokinginput')
    regioninput = request.form.get('regioninput')

    # male and female will be transformed to 0 and 1
    # gender_display will be used to display client's input
    gender_display = genderinput 

    if (request.method == 'GET'):
        logged_id = request.args.get('logged_id', None)

        # render to menu page with predicted values
        if (datamodel.is_valid_request(logged_id) and is_predicted is True):
            is_predicted = False
            return render_template('menu.html', age=ageinput, gender=gender_display, 
                           bmi=bmiinput, child=childinput, smoking=smokinginput, 
                           region=regioninput, prediction_text=predicted_value, 
                           total_pred=datamodel.inputdata_to_totalpred(),
                           display_data=datamodel.display_data())
        
        # render to menu without predicted values
        if (datamodel.is_valid_request(logged_id)):
            return render_template('menu.html', 
                                total_pred=datamodel.inputdata_to_totalpred(),
                                display_data=datamodel.display_data())
        
    if (request.method == 'POST'):  
        if (logged_id is None):
            message = {'message' : 
                       f'Username or password incorrect, return and try again'}
            return make_response(jsonify(message), 400)
        
        #transformation section
        features = pd.DataFrame({"age":[int(ageinput)], "sex":[genderinput], 
                                "bmi":[float(bmiinput)], "children":[int(childinput)], 
                                "smoker":[smokinginput], "region":[regioninput]})
        
        # validating section
        if (validate_input(features) == -1):
            message = {'message' : f'incorrect input data'}
            return make_response(jsonify(message), 400)
        
        # predicting section
        prediction = predict_(features, scaler, model, lmbda)

        # update input to database
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        features_to_database = [ageinput, genderinput, bmiinput, childinput, 
                                smokinginput, regioninput, prediction, current_time]
        datamodel.insert_to_inputdata(features_to_database)

        is_predicted = True
        predicted_value = prediction
        #final section -> send data back to front page
        return redirect(url_for('menu', logged_id=logged_id))
    
    message = {'message' : f'Unauthorized request'}
    return make_response(jsonify(message), 405)

# sign up input - sign up UI
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        sr_quest = request.form.get('SR_Quest')

        # if the new account is not duplicated
        # pop up message and update the information to database
        if datamodel.account_sign_up(username, password, sr_quest):
            message = "Create new user success!"
            return render_template('sign_up.html', message_signup=message)

        message = {'message' : 
                    'Username already exists, please try again'}
        return make_response(jsonify(message), 400)

    return render_template('sign_up.html')


# recover password - recover UI
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
        email = request.form.get('email')
        sr_quest = request.form.get('SR_Quest')
        new_password = request.form.get('new_password')

        if datamodel.recover_password(email, new_password, sr_quest):
            message = "User password has been updated!"
            return render_template('forgot_password.html', message_recover=message)

        message = {'message' : 
                    'Email or secret question incorrect, return and try again'}
        return make_response(jsonify(message), 400)
        
    return render_template('forgot_password.html')


if __name__ == "__main__":
    app.run()