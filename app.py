#APPLICATION FOR MEDICAL COST PREDICTION IN FOUR BIGGEST REGIONS IN USA. 

"""
!!!DISCLAIMER!!
All data are protected by US Office Of Government Ethics (OGE).
Commerical purposes are restricted, any modifications are expected to have permission from US Authorities.
"""

import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, request, render_template
import pickle
import pyodbc

#Connecting to database - SQL SERVER
#change the connect query corresponding to your device. The format shall look like these:
#DRIVER={Devart ODBC Driver for SQL Server};Server=myserver;Database=mydatabase;Port=myport;User ID=myuserid;Password=mypassword
#Note:
#Most of regular cases, the "DRIVER" term should be {SQL Server}, if not work then try using {SQL Server Native Client 11.0}
#If still having problem, please refer to other sources for best solution.
#In case of window authentication, replace the "user ID and Password" with "trusted_connection=true"
#My current port is 8008, if this port in your device is occupied then switch to other ports.
conn = pyodbc.connect("DRIVER={SQL Server};Server=WINDOWS-11\SQLEXPRESS;" +
                      "Database=QA_TEST;Port=8008;trusted_connection=true")

#Flask class - Web application. 
app = Flask(__name__)

#Load the trained model and encoder. (Pickle file)
model = pickle.load(open('models/svr_model.pkl', 'rb'))
scaler = pickle.load(open('models/mm_encoder.pkl', 'rb'))
lmbda_charges = pickle.load(open('models/lmbda_price.pkl', 'rb'))

#Function for inverse the power transformation
def inverse_transform(x, lmbda):
        x_inv = np.zeros_like(x)
        pos = x >= 0

        # when x >= 0
        if abs(lmbda) < np.spacing(1.0):
            x_inv[pos] = np.exp(x[pos]) - 1
        else:  # lmbda != 0
            x_inv[pos] = np.power(x[pos] * lmbda + 1, 1 / lmbda) - 1

        # when x < 0
        if abs(lmbda - 2) > np.spacing(1.0):
            x_inv[~pos] = 1 - np.power(-(2 - lmbda) * x[~pos] + 1, 1 / (2 - lmbda))
        else:  # lmbda == 2
            x_inv[~pos] = 1 - np.exp(-x[~pos])

        return x_inv

def insert_to_inputdata(data):
    cursor = conn.cursor()
    cursor.execute("insert into InputData (Age, Sex, BMI, NumOfChildren, isSmoking," +
                   "Region, Prediction, TimeDate) values(?, ?, ?, ?, ?, ?, ?, ?)", 
                   (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
    conn.commit()

def inputdata_to_totalpred():
    cursor = conn.cursor()
    cursor.execute("select count(*) from Inputdata")
    result = cursor.fetchone()[0]
    return result

#Define the route to be home. 
#Here, home function is with '/', our root directory. 
#Running the app sends us to index.html.
#Note that render_template means it looks for the file in the templates folder. 
#use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def home():
    return render_template('index.html', total_pred=inputdata_to_totalpred())

#GET: A GET message is send, and the server returns data
#POST: Used to send HTML form data to the server.
#Add Post method to the decorator to allow for form submission. 
#Redirect to /predict page with the output
@app.route('/predict',methods=['POST']) #Do not add two method may make app crashed
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
    features = pd.DataFrame({"age":[ageinput], "sex":[genderinput], "bmi":[bmiinput], 
                             "children":[childinput], "smoker":[smokinginput], "region":[regioninput]}) 
    
    features = features.replace('male', 1)
    features = features.replace('female', 0)
    features = features.replace('yes', 1)
    features = features.replace('no', 0)
    
    features = features.replace('northwest', 0)
    features = features.replace('northeast', 1)
    features = features.replace('southwest', 2)
    features = features.replace('southeast', 3)
    
    features = scaler.transform(features)   
    prediction = model.predict(features)
    prediction = inverse_transform(prediction, lmbda_charges)
    prediction = np.round_(prediction, 2)[0]

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    features_to_database = [ageinput, genderinput, bmiinput, childinput, 
                            smokinginput, regioninput, prediction, current_time]
    insert_to_inputdata(features_to_database)

    #final section -> send data back to front page
    return render_template('index.html', age=ageinput, gender=gender_display, bmi=bmiinput, child=childinput,
                        smoking=smokinginput, region=regioninput, prediction_text= prediction, 
                        total_pred=inputdata_to_totalpred())

if __name__ == "__main__":
    app.run()