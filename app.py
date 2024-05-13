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
from flask import Flask, request, render_template
from flask import redirect, url_for, jsonify, make_response
from utils.app_process import *
from utils.database_process import *

#global variables
is_valid_request = False

# connection string
conn = pyodbc.connect("DRIVER={SQL Server};Server=LAPTOP-8MJ97B04;" +
                      "Database=QA_TEST;Port=8008;trusted_connection=true")

#Load the trained model and encoder. (Pickle file)
model = pickle.load(open('models/svr_model.pkl', 'rb'))
scaler = pickle.load(open('models/mm_encoder.pkl', 'rb'))
lmbda = pickle.load(open('models/lmbda_price.pkl', 'rb'))

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
        global is_valid_request; is_valid_request = True
        return redirect(url_for('menu'))
    else:
        message = {'message' : 
                   f'Username or password incorrect, return and try again'}
        return make_response(jsonify(message), 403)

# menu input - prediction UI
@app.route('/menu')
def menu():
    if (is_valid_request == True):
        return render_template('menu.html')
    if (is_valid_request == False):
        message = {'message' : 
                   f'Unauthorized request'}
        return make_response(jsonify(message), 405)


@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        sr_quest = request.form.get('SR_Quest')  # Thêm dòng này
        # Xử lý yêu cầu đăng ký ở đây
        # Kiểm tra xem tên người dùng đã tồn tại chưa
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        result = cursor.fetchone()
        if result is not None:
            message = {'message' : 'Username already exists, please choose another username'}
            return make_response(jsonify(message), 403)
        else:
            # Nếu tên người dùng chưa tồn tại, thêm người dùng mới vào cơ sở dữ liệu
            cursor.execute("INSERT INTO Users (Username, Password, SR_Quest) VALUES (?, ?, ?)", (username, password, sr_quest))  # Chỉnh sửa dòng này
            conn.commit()
            #return redirect(url_for('login'))
    else:
        return render_template('sign_up.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        sr_quest = request.form.get('SR_Quest')
        new_password = request.form.get('new_password')
        # Xử lý yêu cầu đặt lại mật khẩu ở đây
        # Kiểm tra xem email và SR_Quest có khớp với dữ liệu trong cơ sở dữ liệu không
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ? AND SR_Quest = ?", (email, sr_quest))
        result = cursor.fetchone()
        if result is None:
            message = {'message' : 'Email or secret question incorrect, return and try again'}
            return make_response(jsonify(message), 403)
        else:
            # Nếu email và SR_Quest khớp, cập nhật mật khẩu mới trong cơ sở dữ liệu
            cursor.execute("UPDATE Users SET Password = ? WHERE Username = ?", (new_password, email))
            conn.commit()
            return redirect(url_for('login'))
    return render_template('forgot_password.html')


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

    # male and female will be transformed to 0 and 1
    # gender_display will be used to display client's input
    gender_display = genderinput 
    
    #transformation section
    features = pd.DataFrame({"age":[int(ageinput)], "sex":[genderinput], 
                             "bmi":[float(bmiinput)], "children":[int(childinput)], 
                             "smoker":[smokinginput], "region":[regioninput]})
    
    # validating section
    if (validate_input(features) == -1):
        message = {'message' : 
                   f'incorrect input data'}
        return make_response(jsonify(message), 403)
    
    # predicting section
    prediction = predict_(features, scaler, model, lmbda)

    # update input to database
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    features_to_database = [ageinput, genderinput, bmiinput, childinput, 
                            smokinginput, regioninput, prediction, current_time]
    insert_to_inputdata(features_to_database, conn)

    global is_valid_request; is_valid_request = False
    #final section -> send data back to front page
    return render_template('menu.html', age=ageinput, gender=gender_display, 
                           bmi=bmiinput, child=childinput, smoking=smokinginput, 
                           region=regioninput, prediction_text= prediction, 
                           total_pred=inputdata_to_totalpred(conn))

if __name__ == "__main__":
    app.run()
