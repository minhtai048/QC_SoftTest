#APPLICATION FOR MEDICAL COST PREDICTION IN FOUR BIGGEST REGIONS IN USA. 

"""
!!!DISCLAIMER!!
All data are protected by US Office Of Government Ethics (OGE).
Commerical purposes are restricted, any modifications are 
expected to have permission from US Authorities.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, request, render_template, Response
from flask import redirect, url_for, jsonify, make_response
from utils.app_process import *
from utils.database_process import *
import pickle
import pyodbc
import json

# connection string
conn = pyodbc.connect("DRIVER={SQL Server};Server=WINDOWS-11\SQLEXPRESS;" +
                      "Database=QA_TEST;Port=8008;trusted_connection=true")

#Load the trained model and encoder. (Pickle file)
model = pickle.load(open('models/svr_model.pkl', 'rb'))
scaler = pickle.load(open('models/mm_encoder.pkl', 'rb'))
lmbda_charges = pickle.load(open('models/lmbda_price.pkl', 'rb'))

#Flask class - Web application. 
app = Flask(__name__)

# homepage - login UI. 
@app.route('/')
def home():
    return render_template('login.html')

# get user login and process
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if check_login(username, password, conn):
        return redirect(url_for('menu'))
    else:
        message = {'message' : 
                   f'Username or password incorrect, return and try again'}
        return make_response(jsonify(message), 403)

# menu input - prediction UI
@app.route('/menu')
def menu():
    return render_template('menu.html')

# get predicted result from inputs
@app.route('/predict',methods=['POST']) # Do not add two methods
def predict():
    #input section
    ageinput = request.form.get('ageinput')
    genderinput = request.form.get('genderinput')
    bmiinput = request.form.get('bmiinput')
    childinput = request.form.get('childinput')
    smokinginput = request.form.get('smokinginput')
    regioninput = request.form.get('regioninput')   

    gender_display = genderinput 
    #feature transformation section
    features = pd.DataFrame({"age":[ageinput], "sex":[genderinput], 
                             "bmi":[bmiinput], "children":[childinput], 
                             "smoker":[smokinginput], "region":[regioninput]}) 
    
    features = features_transform(features)
    
    features = scaler.transform(features)   
    prediction = model.predict(features)
    prediction = inverse_transform(prediction, lmbda_charges)
    prediction = np.round_(prediction, 2)[0]

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    features_to_database = [ageinput, genderinput, bmiinput, childinput, 
                            smokinginput, regioninput, prediction, current_time]
    insert_to_inputdata(features_to_database, conn)

    #final section -> send data back to front page
    return render_template('index.html', age=ageinput, gender=gender_display, 
                           bmi=bmiinput, child=childinput, smoking=smokinginput, 
                           region=regioninput, prediction_text= prediction, 
                           total_pred=inputdata_to_totalpred(conn))

if __name__ == "__main__":
    app.run()
