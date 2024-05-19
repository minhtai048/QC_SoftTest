class DataModel():
    def __init__(self, conn):
        self.conn = conn
        self.user_id = ""

    # function for login checking
    def check_login(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM Users WHERE Username = ? AND Password = ?", 
                    (username, password))
        self.user_id = cursor.fetchone()
        if (self.user_id is not None):
            self.user_id = self.user_id[0]
            return True, self.user_id
        return False, self.user_id
    
    # function for validating request
    def is_valid_request(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT username FROM Users WHERE Username = ?", 
                       (username))
        valid = cursor.fetchone()
        if (valid is not None):
            return True
        return False

    # get data for total predition
    def inputdata_to_totalpred(self):
        cursor = self.conn.cursor()
        cursor.execute("select count(*) from Inputdata where username = ?", (self.user_id))
        result = cursor.fetchone()[0]
        return result

    # insert new input to database
    def insert_to_inputdata(self, data):
        cursor = self.conn.cursor()
        cursor.execute("insert into InputData (Age, Sex, BMI, NumOfChildren, isSmoking," +
                    "Region, Prediction, TimeDate, username) values(?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                    (data[0], data[1], data[2], data[3], data[4], data[5], 
                     data[6], data[7], self.user_id))
        self.conn.commit()

    # sign up new account
    def account_sign_up(self, username, password, sr_quest):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username))
        result = cursor.fetchone()
        if result is not None:
            return False
        
        cursor.execute("INSERT INTO Users (Username, Password, SR_Quest) VALUES (?, ?, ?)", 
                    (username, password, sr_quest))
        self.conn.commit()
        return True

    # recover password of an account
    def recover_password(self, username, password, sr_quest):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ? AND SR_Quest = ?", 
                    (username, sr_quest))
        result = cursor.fetchone()
        if result is None:
            return False
        
        cursor.execute("UPDATE Users SET Password = ? WHERE Username = ?", 
                    (password, username))
        self.conn.commit()
        return True
    
    # display history usage of user
    def display_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT Age, Sex, BMI, numofchildren, issmoking, region, prediction, timedate " +
                        "FROM inputdata WHERE Username = ?", (self.user_id))
        result = cursor.fetchall()
        if result is None:
            return None
        return result