import sqlite3

def view_users():
    # Connect to the SQLite database
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()

    # Execute SQL query to retrieve all users
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    # Display user details
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

    
    print(len(users))

    # Close the database connection
    conn.close()

if __name__ == "__main__":
    view_users()
