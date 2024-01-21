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



from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import re
import os
import random
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
        con.close()
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
            trousers = int(request.form['trousers'])
            estimated_waiting_time = random.randint(5, 30)
            # Create a new order and add it to the database
            con = connect_db()
            cur = con.cursor()
            cur.execute('INSERT INTO queue (Email, Time,Jackets, Undergarments, Shirts, Trousers,WaitingTime) VALUES (?, ?,?, ?, ?, ?,?)',
                        (session['username'],10, jackets, undergarments, shirts, trousers,20))
            con.commit()
            cur.execute('SELECT Email FROM queue ASC LIMIT 2')
            queue_result = cur.fetchall()
            con.close()
            if len(queue_result) >= 2:
             email_first_in_queue = queue_result[0][0]
             email_second_in_queue = queue_result[1][0]

            # # Fetch email addresses of the first and second person from the user table
            # email_first_in_queue = fetch_user_email(user_id_first_in_queue)
            # email_second_in_queue = fetch_user_email(user_id_second_in_queue)

            # Send emails to the first and second person
            send_email(email_first_in_queue, "Collect your clothes", estimated_waiting_time)
            send_email(email_second_in_queue, "Your turn at the washing machine", estimated_waiting_time)
            con = connect_db()
            cur = con.cursor()
            cur.execute('DELETE FROM queue WHERE Email = ?', (email_first_in_queue,))
            con.commit()
            con.close()
            print("done")

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
def send_email(recipient, subject, estimated_waiting_time):
    msg = Message(subject,
                  sender='FreshMailSystem@gmail.com',
                  recipients=[recipient])

    msg.body = f"Hello,\n\n{subject}. Your estimated waiting time is {estimated_waiting_time} minutes.\n\nBest regards,\nYour App Team"

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
            con.close()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)


if __name__ == "__main__":
    app.run(debug=True)

