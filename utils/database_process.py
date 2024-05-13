# function for login checking
def check_login(username, password, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Username = ? AND Password = ?", 
                   (username, password))
    result = cursor.fetchone()
    return result is not None

# get data for total predition
def inputdata_to_totalpred(conn):
    cursor = conn.cursor()
    cursor.execute("select count(*) from Inputdata")
    result = cursor.fetchone()[0]
    return result

# insert new input to database
def insert_to_inputdata(data, conn):
    cursor = conn.cursor()
    cursor.execute("insert into InputData (Age, Sex, BMI, NumOfChildren, isSmoking," +
                   "Region, Prediction, TimeDate) values(?, ?, ?, ?, ?, ?, ?, ?)", 
                   (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
    conn.commit()

# sign up new account
def account_sign_up(username, password, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE Username = ?", (username))
    result = cursor.fetchone()
    if result is not None:
        return False
    else:
        cursor.execute("INSERT INTO Users (Username, Password) VALUES (?, ?)", 
                        (username, password))
        conn.commit()
    return True