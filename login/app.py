# from flask import Flask, render_template, request, redirect, url_for, session
# import sqlite3
# import re
# import os
# import random

# app = Flask(__name__)

# app.secret_key = 'your secret key'

# # Use the SQLite database file in the same directory as app.py
# db_path = os.path.join(os.path.dirname(__file__), 'user_database.db')

# app.config['DATABASE'] = db_path

# def connect_db():
#     return sqlite3.connect(app.config['DATABASE'])

# # def init_db():
# #     with app.app_context():
# #         db = connect_db()
# #         with app.open_resource('schema.sql', mode='r') as f:
# #             db.cursor().executescript(f.read())
# #         db.commit()

# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         con = connect_db()
#         cur = con.cursor()
#         cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
#         account = cur.fetchone()
#         con.close()
#         if account:
#             session['loggedin'] = True
#             session['id'] = account[0]
#             session['username'] = account[1]
#             msg = 'Logged in successfully!'
#             return render_template('order.html', msg=msg)
#         else:
#             msg = 'Incorrect username / password!'
#     return render_template('login.html', msg=msg)


# @app.route('/order',methods=['GET', 'POST'])
# def order():
#     # Check if the user is logged in before allowing access to the order page
#     if 'loggedin' in session:
#         return render_template('waiting_time.html')
#     else:
#         return redirect(url_for('login'))


# @app.route('/waiting_time',methods=['GET','POST'])
# def waiting_time():
#     if request.method == 'POST':
#         # Assuming you have processed the order and calculated/waiting for the waiting time
#         # Replace the random waiting time generation with your actual logic
#         estimated_waiting_time = random.randint(5, 30)  # Replace this with your waiting time calculation

#         return render_template('waiting_time.html', estimated_waiting_time=estimated_waiting_time)
#     else:
#         # Redirect to the order page if someone tries to access the waiting_time page directly
#         return redirect(url_for('order'))



# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#         con = connect_db()
#         cur = con.cursor()
#         cur.execute('SELECT * FROM users WHERE username = ?', (username,))
#         account = cur.fetchone()
#         if account:
#             msg = 'Account already exists!'
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = 'Invalid email address!'
#         elif not re.match(r'[A-Za-z0-9]+', username):
#             msg = 'Username must contain only characters and numbers!'
#         elif not username or not password or not email:
#             msg = 'Please fill out the form!'
#         else:
#             cur.execute('INSERT INTO users VALUES (?, ?, ?)', (username, password, email))
#             con.commit()
#             con.close()
#             msg = 'You have successfully registered!'
#     elif request.method == 'POST':
#         msg = 'Please fill out the form!'
#     return render_template('register.html', msg=msg)

# if __name__ == "__main__":
#     app.run(debug=True)

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
from scipy.stats import mode
from sklearn import preprocessing
from sklearn.preprocessing import PolynomialFeatures
import optuna
from category_encoders import TargetEncoder
import re
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import mean_squared_error
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np 
import sqlite3

df = pd.read_csv("train_folds_washing.csv")

bins = [0, 30, 45, 60, 75, 90]
labels = [0, 1, 2, 3, 4]

df['WashingTime'] = pd.cut(df['WashingTime'], bins=bins, labels=labels, include_lowest=True)

useful_features = [c for c in df.columns if c not in ("kfold", "WashingTime")]

poly = PolynomialFeatures(degree=3, interaction_only=True, include_bias=False)

df_train = df[useful_features]

train_poly = poly.fit_transform(df_train)

df_poly = pd.DataFrame(train_poly, columns=[f"poly_{i}" for i in range(train_poly.shape[1])])

df = pd.concat([df, df_poly], axis=1)

label_encoder = LabelEncoder()
df["WashingTimeClassEncoded"] = label_encoder.fit_transform(df["WashingTime"])

train_features = df.drop(columns=["kfold", "WashingTime", "WashingTimeClassEncoded"])
train_targets = df["WashingTimeClassEncoded"]

# Instantiate RandomForestClassifier for multiclass classification
clf = RandomForestClassifier(n_estimators=50, max_features='sqrt', random_state=42)

# Fit the classifier
clf.fit(train_features, train_targets)

# Create a DataFrame to visualize feature importances
features_importance = pd.DataFrame()
features_importance['feature'] = train_features.columns
features_importance['importance'] = clf.feature_importances_
features_importance.sort_values(by=['importance'], ascending=False, inplace=True)

# Visualize feature importances
features_importance.plot(kind='barh', figsize=(12, 8), legend=False, title='Feature Importances')

# Choose the top k most important features
k = 14
selected_features = features_importance.head(k)['feature'].tolist()

print(selected_features)

final_predictions = []

# def run(trial):
accuracy_scores = []

for fold in range(5):

    # learning_rate = trial.suggest_float("learning_rate", 1e-2, 0.25, log=True)
    # reg_lambda = trial.suggest_loguniform("reg_lambda", 1e-8, 100.0)
    # reg_alpha = trial.suggest_loguniform("reg_alpha", 1e-8, 100.0)
    # subsample = trial.suggest_float("subsample", 0.1, 1.0)
    # colsample_bytree = trial.suggest_float("colsample_bytree", 0.1, 1.0)
    # max_depth = trial.suggest_int("max_depth", 1, 7)
    # n_estimators = trial.suggest_int("n_estimators", 50, 1000)

    xtrain = df[df.kfold != fold].reset_index(drop=True)
    xvalid = df[df.kfold == fold].reset_index(drop=True)

    ytrain = xtrain.WashingTime
    yvalid = xvalid.WashingTime

    xtrain = xtrain[selected_features]
    xvalid = xvalid[selected_features]

    # Select categorical columns
#     categorical_cols = [cname for cname in xtrain.columns if
#                         xtrain[cname].nunique() < 10 and 
#                         xtrain[cname].dtype == "object"]

#     # Select numerical columns
#     numerical_cols = [cname for cname in xtrain.columns if 
#                       xtrain[cname].dtype in ['int64', 'float64']]

#     # Keep selected columns only
#     my_cols = categorical_cols + numerical_cols

#     # Normalization((x-mu)/sigma)

#     scaler = preprocessing.StandardScaler()
#     xtrain[numerical_cols_1] = scaler.fit_transform(xtrain[numerical_cols_1])
#     xvalid[numerical_cols_1] = scaler.transform(xvalid[numerical_cols_1])
#     xtest[numerical_cols_1] = scaler.transform(xtest[numerical_cols_1])

    # Define model
    model = XGBClassifier(objective='multi:softmax', num_class=5, n_estimators=100, learning_rate=0.019391533676654422, max_depth=4, reg_alpha=0.8511059335413129, subsample=0.4378621338516323, n_jobs=5)

    model.fit(xtrain, ytrain)

    preds_valid = model.predict(xvalid)
    print(fold, accuracy_score(yvalid, preds_valid))

    accuracy_scores.append(accuracy_score(yvalid, preds_valid))

def time_predicted(input_pred):

    value_mapping = {0: 30, 1: 45, 2: 60, 3: 75, 4: 90}

    input_train = input_pred[useful_features]

    train_poly = poly.fit_transform(input_train)

    inp_poly = pd.DataFrame(train_poly, columns=[f"poly_{i}" for i in range(train_poly.shape[1])])

    input_pred = pd.concat([input_pred, inp_poly], axis=1)

    input_pred=input_pred[selected_features]
    
    output_pred = model.predict(input_pred)
    mapped_value = value_mapping.get(output_pred, None)
    print(input_pred)

    return mapped_value




from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import os
import random
import time
from flask_mail import Mail, Message

app = Flask(__name__)

# Configure Flask-Mail for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'cswaroop2004@gmail.com'  # Your Gmail email address
app.config['MAIL_PASSWORD'] = 'ojxd zthe nrmz fzop'  # Your Gmail app password or account password

mail = Mail(app)

app.secret_key = 'your_secret_key'

# Use the SQLite database file in the same directory as app.py
db_path = os.path.join(os.path.dirname(__file__), 'user_database.db')

app.config['DATABASE'] = db_path

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# def init_db():
#     with app.app_context():
#         db = connect_db()
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        account = cur.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            msg = 'Logged in successfully!'
            return render_template('order.html', msg=msg)
        else:
            msg = 'Incorrect username / password!'
    return render_template('login.html', msg=msg)

@app.route('/order',methods=['GET', 'POST'])
def order():
    # Check if the user is logged in before allowing access to the order page
    if 'loggedin' in session:
        if request.method == 'POST':
            # Retrieve data from the form
            jackets = int(request.form['jackets'])
            undergarments = int(request.form['undergarments'])
            shirts = int(request.form['shirts'])
            pants = int(request.form['pants'])
            estimated_waiting_time = random.randint(5, 30)
              # Creating a DataFrame
            # data = {
            # 'Jackets': jackets,
            # 'Shirts': shirts,
            # 'Pants': pants,
            # 'Undergarments': undergarments
            # }
            # df = pd.DataFrame(data)
            washing_time=10
            print('hey')

            # Create a new order and add it to the database
            con = connect_db()
            cur = con.cursor()
            cur.execute('INSERT INTO queue (Email, Time,Jackets, Undergarments, Shirts, Pants,WaitingTime) VALUES (?, ?,?, ?, ?, ?,?)',
                        (session['username'],30, jackets, undergarments, shirts, pants,50))
            con.commit()
            cur.execute('SELECT COUNT(*) FROM queue')
            row_count = cur.fetchone()[0]
            print(washing_time)
            # Creating a DataFrame
         
 
           
            while row_count!=0:
               cur.execute('SELECT COUNT(*) FROM queue')
               row_count = cur.fetchone()[0]
               cur.execute('SELECT Email,Time FROM queue ORDER BY Time ASC LIMIT 2')
               queue_result = cur.fetchall()
               print(queue_result)
               print(row_count)
               if(row_count>0):
                email_first_in_queue,duration= queue_result[0]
               if len(queue_result)>1:
                   email_second_in_queue,duration2 = queue_result[1]
              
            #    print(duration)
               start_time=time.time()
               #send mail to the first person in queue once his WashingTime (WashingTime is a column in the table)is done and at the same time inform te second person that his turn at the washing machine and at the same time pop the first persons record off the queue table in the db
               while time.time()-start_time < duration:
                time.sleep(1)

               if(row_count>0):
                send_email(email_first_in_queue, "Collect your clothes",)
               if len(queue_result)>1:
                   send_email(email_second_in_queue, "Your turn at the washing machine",)
                
               con = connect_db()
               cur = con.cursor()
               if(row_count>0):
                cur.execute('DELETE FROM queue WHERE Email = ?', (email_first_in_queue,))
               print('ok')
               con.commit()
           
                

        return render_template('waiting_time.html', estimated_waiting_time=estimated_waiting_time)

    
       

        #     # Redirect to a confirmation or waiting page
        #     return render_template('waiting_time.html')
        # else:
        #     return render_template('order.html')
    else:
        return redirect(url_for('login'))




@app.route('/waiting_time', methods=['GET', 'POST'])
# def waiting_time():
   
#         # Assuming you have processed the order and calculated/waiting for the waiting time
#         # Replace the random waiting time generation with your actual logic
#         estimated_waiting_time = random.randint(5, 30)  # Replace this with your waiting time calculation

#         # Fetch the first and second person in the queue from the queue table
#         con = connect_db()
#         cur = con.cursor()
#         cur.execute('SELECT Email FROM queue ASC LIMIT 2')
#         queue_result = cur.fetchall()
#         con.close()

#         if len(queue_result) >= 2:
#             user_id_first_in_queue = queue_result[0][0]
#             user_id_second_in_queue = queue_result[1][0]

#             # Fetch email addresses of the first and second person from the user table
#             email_first_in_queue = fetch_user_email(user_id_first_in_queue)
#             email_second_in_queue = fetch_user_email(user_id_second_in_queue)

#             # Send emails to the first and second person
#             send_email(email_first_in_queue, "Collect your clothes", estimated_waiting_time)
#             send_email(email_second_in_queue, "Your turn at the washing machine", estimated_waiting_time)

#         return render_template('waiting_time.html', estimated_waiting_time=estimated_waiting_time)
 
        # # Redirect to the order page if someone tries to access the waiting_time page directly
        # return redirect(url_for('order'))

# Function to send email
def send_email(recipient, subject):
    msg = Message(subject,
                  sender='cswaroop2004@gmail.com',
                  recipients=[recipient])

    msg.body = f"Hello,"

    try:
        mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

# # Function to fetch user email from the user table
# def fetch_user_email(user_id):
#     con = connect_db()
#     cur = con.cursor()
#     cur.execute('SELECT email FROM users WHERE user_id = ?', (user_id,))
#     email_result = cur.fetchone()
#     con.close()

#     return email_result[0] if email_result else None



@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        con = connect_db()
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username,))
        account = cur.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            cur.execute('INSERT INTO users VALUES (?, ?, ?)', (username, password, email))
            con.commit()
       
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)





if __name__ == "__main__":
    app.run(debug=True)
 
   