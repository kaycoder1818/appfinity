from flask import Flask, jsonify, request
# from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
import os
from swagger.swaggerui import setup_swagger
import datetime
import random
import string

from flask_cors import CORS

# app = Flask(__name__)
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and all origins

# Optional: Restrict CORS to specific domains
# If you want to allow only your front-end domain instead of "*", you can specify it:
# CORS(app, resources={r"/*": {"origins": ["https://web-lyart-one-16.vercel.app"]}})

# Set up Swagger
setup_swagger(app)

# Load environment variables from .env file
# load_dotenv()

# # Retrieve MySQL connection details from environment variable
# mysql_details = os.getenv('MYSQL_DETAILS')

# if mysql_details:
#     # Split the details by "@"
#     details = mysql_details.split('@')
    
#     # Extract the individual values
#     host = details[0]
#     user = details[1]
#     password = details[2]
#     database = details[3]
#     port = int(details[4])

#     # MySQL connection setup
#     try:
#         db_connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database,
#             port=port
#         )
#         print("Connection successful")
    
#     except mysql.connector.Error as err:
#         print(f"Error connecting to MySQL: {e}")
#         db_connection = None
# else:
#     print("MYSQL_DETAILS environment variable is not set.")
#     db_connection = None

# Check if the file "dev" exists
if not os.path.exists('dev'):
    # Retrieve MySQL connection details from environment variable
    mysql_details = os.getenv('MYSQL_DETAILS')

    if mysql_details:
        # Split the details by "@"
        details = mysql_details.split('@')

        # Extract the individual values
        host = details[0]
        user = details[1]
        password = details[2]
        database = details[3]
        port = int(details[4])

        # MySQL connection setup
        try:
            db_connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            print("Connection successful")

        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            db_connection = None
    else:
        print("MYSQL_DETAILS environment variable is not set.")
        db_connection = None
else:
    print("File 'dev' exists. Skipping MySQL connection setup.")


def get_connection():
    global db_connection
    
    if db_connection and db_connection.is_connected():
        return db_connection  # Return the existing connection if it's valid
    
    # If there is no connection or it's invalid, try to reconnect
    if reconnect_to_mysql():
        return db_connection
    else:
        return None


# Helper function to reconnect to MySQL
def reconnect_to_mysql():
    global db_connection

    mysql_details = os.getenv('MYSQL_DETAILS')

    if mysql_details:
        # Split the details by "@"
        details = mysql_details.split('@')

        # Extract the individual values
        host = details[0]
        user = details[1]
        password = details[2]
        database = details[3]
        port = int(details[4])

        # MySQL connection setup
        try:
            db_connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                port=port
            )
            print("Reconnection successful")
            return True

        except mysql.connector.Error as err:
            print(f"Error reconnecting to MySQL: {err}")
            db_connection = None
            return False
    else:
        print("MYSQL_DETAILS environment variable is not set.")
        db_connection = None
        return False



def generate_random_string(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_cursor():
    if db_connection:
        return db_connection.cursor()
    else:
        return None

def is_mysql_available():
    return db_connection is not None

# Route to handle MySQL errors
def handle_mysql_error(e):
    print(f"MySQL Error: {e}")
    return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

# Initial list of fields
field_db = [
    ["app_status", "idle"],
    ["app_timestamp", "idle"],
]

@app.route('/create-table-datawatch', methods=['GET'])
def create_datawatch_table():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            # Check if table 'datawatch' exists
            cursor.execute("SHOW TABLES LIKE 'datawatch'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                cursor.close()
                return jsonify({"message": "Table 'datawatch' already exists"}), 200
            else:
                # Define SQL query to create table if it doesn't exist
                sql_create_table = """
                CREATE TABLE datawatch (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    field TEXT,
                    value TEXT
                )
                """
                cursor.execute(sql_create_table)
                db_connection.commit()
                cursor.close()
                return jsonify({"message": "Table 'datawatch' created successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-users', methods=['GET'])
def create_table_users():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()
        
        if cursor:
            # Check if the 'users' table already exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'")
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                return jsonify({"message": "Table 'users' already exists."}), 200
            
            # SQL to create the new table with the specified columns
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name TEXT,
                password_hash TEXT,
                role TEXT,
                email TEXT,
                status TEXT,
                token TEXT,
                rfid TEXT,
                assignedslot TEXT,
                timestamp DATETIME
            );
            """
            
            # Execute the create table query
            cursor.execute(create_table_sql)
            
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "Table 'users' created successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-stores', methods=['GET'])
def create_table_stores():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # SQL to create the 'stores' table with the specified columns
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS stores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                unique_id TEXT,
                slot1 TEXT,
                slot2 TEXT,
                slot3 TEXT,
                slot4 TEXT,
                slot5 TEXT,
                slot6 TEXT,
                slot7 TEXT,
                slot8 TEXT,
                slot9 TEXT,
                slot10 TEXT,
                slot11 TEXT,
                slot12 TEXT,
                slot13 TEXT,
                slot14 TEXT,
                slot15 TEXT,
                slot16 TEXT
            );
            """

            # Execute the create table query
            cursor.execute(create_table_sql)

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Table 'stores' created successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-profile', methods=['GET'])
def create_table_profile():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'profile' table already exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'profile'")
            table_exists = cursor.fetchone()[0]

            if table_exists:
                cursor.close()
                return jsonify({"message": "Table 'profile' already exists."}), 200
            
            # SQL to create the new table with the specified columns
            create_table_sql = """
            CREATE TABLE profile (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name TEXT,
                full_name TEXT,
                id_number TEXT,
                plate_number TEXT,
                vehicle_type TEXT,
                vehicle_model TEXT,
                role TEXT,      
                phone_number TEXT,
                image_link TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Execute the create table query
            cursor.execute(create_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close cursor
            cursor.close()

            return jsonify({"message": "Table 'profile' created successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-notifications', methods=['GET'])
def create_table_notifications():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'notifications' table already exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'notifications'")
            table_exists = cursor.fetchone()[0]

            if table_exists:
                cursor.close()
                return jsonify({"message": "Table 'notifications' already exists."}), 200
            
            # SQL to create the 'notifications' table with the specified columns
            create_table_sql = """
            CREATE TABLE notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,        
                uniqueId VARCHAR(255) NOT NULL,         
                role VARCHAR(255),                       
                status VARCHAR(255),                    
                message TEXT,             
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Execute the create table query
            cursor.execute(create_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'notifications' created successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-violations', methods=['GET'])
def create_table_violations():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'violations' table already exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'violations'")
            table_exists = cursor.fetchone()[0]

            if table_exists:
                cursor.close()
                return jsonify({"message": "Table 'violations' already exists."}), 200
            
            # SQL to create the 'violations' table with the specified columns
            create_table_sql = """
            CREATE TABLE violations (
                id INT AUTO_INCREMENT PRIMARY KEY,          
                name VARCHAR(255) NOT NULL,                  
                role VARCHAR(255),                          
                status VARCHAR(255),                       
                type VARCHAR(255),                         
                info TEXT,                                  
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
            );
            """

            # Execute the create table query
            cursor.execute(create_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'violations' created successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-parking-history', methods=['GET'])
def create_table_parking_history():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'parking_history' table already exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'parking_history'")
            table_exists = cursor.fetchone()[0]

            if table_exists:
                cursor.close()
                return jsonify({"message": "Table 'parking_history' already exists."}), 200
            
            # SQL to create the 'parking_history' table with the specified columns
            create_table_sql = """
            CREATE TABLE parking_history (
                id INT AUTO_INCREMENT PRIMARY KEY,          
                name TEXT,                                  
                role TEXT,                                  
                status TEXT,                               
                type TEXT,                                 
                info TEXT,                                 
                slotname TEXT,                             
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP 
            );
            """

            # Execute the create table query
            cursor.execute(create_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'parking_history' created successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/create-table-message', methods=['GET'])
def create_table_message():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # SQL to create the 'message' table with the specified columns
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS message (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name TEXT,
                status TEXT,
                type TEXT,
                `group` TEXT,
                sender TEXT,
                receiver TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """

            # Execute the create table query
            cursor.execute(create_table_sql)

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Table 'message' created successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/delete-table-datawatch', methods=['GET'])
def delete_datawatch_table():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'datawatch' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'datawatch'")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.close()
                return jsonify({"error": "Table 'datawatch' does not exist."}), 404

            # SQL to drop the 'datawatch' table
            drop_table_sql = "DROP TABLE datawatch"
            cursor.execute(drop_table_sql)

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Table 'datawatch' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/delete-table-users', methods=['GET'])
def delete_table_users():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()
        
        if cursor:
            # Check if the 'users' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'users'")
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return jsonify({"message": "Table 'users' does not exist."}), 404
            
            # SQL to drop the 'users' table
            drop_table_sql = "DROP TABLE users;"
            
            # Execute the drop table query
            cursor.execute(drop_table_sql)
            
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "Table 'users' deleted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/delete-stores-table/', methods=['GET'])
def delete_stores_table():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'stores' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'stores'")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.close()
                return jsonify({"error": "Table 'stores' does not exist."}), 404

            # SQL to drop the 'stores' table
            drop_table_sql = "DROP TABLE stores"
            cursor.execute(drop_table_sql)

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Table 'stores' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/delete-table-profile', methods=['GET'])
def delete_table_profile():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'profile' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'profile'")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.close()
                return jsonify({"message": "Table 'profile' does not exist."}), 200

            # SQL to drop the 'profile' table
            drop_table_sql = "DROP TABLE profile;"

            # Execute the drop table query
            cursor.execute(drop_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'profile' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/delete-table-notifications', methods=['GET'])
def delete_table_notifications():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'notifications' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'notifications'")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.close()
                return jsonify({"message": "Table 'notifications' does not exist."}), 200

            # SQL to drop the 'notifications' table
            drop_table_sql = "DROP TABLE notifications;"

            # Execute the drop table query
            cursor.execute(drop_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'notifications' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/delete-table-violations', methods=['GET'])
def delete_table_violations():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'violations' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'violations'")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.close()
                return jsonify({"message": "Table 'violations' does not exist."}), 200

            # SQL to drop the 'violations' table
            drop_table_sql = "DROP TABLE violations;"

            # Execute the drop table query
            cursor.execute(drop_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'violations' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/delete-table-parking-history', methods=['GET'])
def delete_table_parking_history():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()
        
        if cursor:
            # Check if the 'parking_history' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'parking_history'")
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                return jsonify({"message": "Table 'parking_history' does not exist."}), 404
            
            # SQL to drop the 'parking_history' table
            drop_table_sql = "DROP TABLE parking_history;"
            
            # Execute the drop table query
            cursor.execute(drop_table_sql)
            
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "Table 'parking_history' deleted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/delete-table-message', methods=['GET'])
def delete_table_message():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the 'message' table exists
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'message'")
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.close()
                return jsonify({"message": "Table 'message' does not exist."}), 200

            # SQL to drop the 'message' table
            drop_table_sql = "DROP TABLE message;"

            # Execute the drop table query
            cursor.execute(drop_table_sql)

            # Commit the changes to the database
            db_connection.commit()

            # Close the cursor
            cursor.close()

            return jsonify({"message": "Table 'message' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


## insert the initial records for datawatch
@app.route('/insert-data-to-datawatch', methods=['GET'])
def insert_data():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            for field in field_db:
                name = field[0]
                value = field[1]
                
                # Check if the field already exists
                sql_select = "SELECT * FROM datawatch WHERE field = %s"
                cursor.execute(sql_select, (name,))
                existing_field = cursor.fetchone()
                
                if not existing_field:
                    # Insert new field if it doesn't exist
                    sql_insert = "INSERT INTO datawatch (field, value) VALUES (%s, %s)"
                    cursor.execute(sql_insert, (name, value))
            
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Data inserted successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## insert the initial records for users
@app.route('/insert-data-to-users', methods=['GET'])
def insert_users():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()

        # List of users to insert 
        users_db = [
            {
                "name": "testuser",
                "password_hash": "12345x",
                "role": "admin", 
                "email": "-",
                "rfid": "53FC0727",
                "assignedslot": "slot1",
                "token": "-",
            },
            {
                "name": "guestuser",
                "password_hash": "12345",
                "role": "guest", 
                "email": "-",
                "rfid": "23XX0725",
                "assignedslot": "slot2s",
                "token": "-",
            }
        ]
        
        if cursor:
            # Prepare the SQL statement to insert data into 'users' table
            insert_sql = """
            INSERT INTO users (name, password_hash, role, email, token, rfid, assignedslot, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW());
            """
            
            # Iterate over users_db to insert users one by one
            for user in users_db:
                # Check if the user with the same name already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (user['name'],))
                user_exists = cursor.fetchone()[0]
                
                if user_exists:
                    return jsonify({"error": f"User with name '{user['name']}' already exists."}), 400
                
                try:
                    # Execute the insert query for the user if the name doesn't exist
                    cursor.execute(insert_sql, (user['name'], user['password_hash'], user['role'], user['email'], user['token'], user['rfid'], user['assignedslot']))
                except mysql.connector.Error as e:
                    print(f"Error inserting user {user['name']}: {e}")
                    db_connection.rollback()  # Rollback on error
                    return jsonify({"error": f"Failed to insert user '{user['name']}'. Please check the data."}), 500
            
            # Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "Users inserted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

## insert the initial records for stores
@app.route('/insert-data-to-stores', methods=['GET'])
def insert_stores():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        

        # Get a database cursor
        cursor = get_cursor()

        # Hardcoded stores data
        stores_db = [
            {
                "unique_id": "12345",
                "slot1": "available",
                "slot2": "available",
                "slot3": "available",
                "slot4": "available",
                "slot5": "available",
                "slot6": "available",
                "slot7": "available",
                "slot8": "available",
                "slot9": "available",
                "slot10": "available",
                "slot11": "available",
                "slot12": "available",
                "slot13": "available",
                "slot14": "available",
                "slot15": "available",
                "slot16": "available"
            },
            # Uncomment and add more entries if needed
            # {
            #     "unique_id": "67890",
            #     "slot1": "available",
            #     "slot2": "available",
            #     "slot3": "available",
            #     "slot4": "available",
            #     "slot5": "taken",
            #     "slot6": "taken",
            #     "slot7": "available",
            #     "slot8": "taken",
            #     "slot9": "available",
            #     "slot10": "available",
            #     "slot11": "available",
            #     "slot12": "available",
            #     "slot13": "taken",
            #     "slot14": "available",
            #     "slot15": "available",
            #     "slot16": "available"
            # }
        ]

        if cursor:
            # Iterate over each store entry in the stores_db list
            for store in stores_db:
                # Check if required fields are present
                required_fields = ["unique_id", "slot1", "slot2", "slot3", "slot4", "slot5", 
                                   "slot6", "slot7", "slot8", "slot9", "slot10", "slot11", 
                                   "slot12", "slot13", "slot14", "slot15", "slot16"]

                # Ensure all required fields are present in the store record
                if not all(field in store for field in required_fields):
                    return jsonify({"error": "Missing required fields in store record."}), 400

                # Check if the unique_id already exists in the stores table
                cursor.execute("SELECT COUNT(*) FROM stores WHERE unique_id = %s", (store["unique_id"],))
                unique_id_exists = cursor.fetchone()[0]

                if unique_id_exists:
                    continue  # Skip insertion if the unique_id already exists

                # Prepare the insert SQL query
                insert_sql = """
                INSERT INTO stores (unique_id, slot1, slot2, slot3, slot4, slot5, slot6, slot7, 
                                    slot8, slot9, slot10, slot11, slot12, slot13, slot14, slot15, slot16)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """

                # Execute the insertion for each store entry
                cursor.execute(insert_sql, (
                    store["unique_id"], store["slot1"], store["slot2"], store["slot3"], 
                    store["slot4"], store["slot5"], store["slot6"], store["slot7"], 
                    store["slot8"], store["slot9"], store["slot10"], store["slot11"], 
                    store["slot12"], store["slot13"], store["slot14"], store["slot15"], store["slot16"]
                ))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": f"{len(stores_db)} store records inserted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

# Insert the initial records for profile
@app.route('/insert-data-to-profile', methods=['GET'])
def bulk_insert_profiles():
    try:
        # Check if the 'profile' table exists
        cursor = get_cursor()

        # Updated profile_db with new fields: 'role', 'phone_number', 'image_link'
        profile_db = [
            {
                "name": "testuser",
                "full_name": "Test User",
                "id_number": "TUPM-21-25344",
                "plate_number": "453QUM",
                "vehicle_type": "MOTORCYCLE",
                "vehicle_model": "HONDA CLICK",
                "role": "user",             
                "phone_number": "1234567890",  
                "image_link": "http://example.com/image.jpg" 
            },
            # Add more records here if needed
        ]

        if cursor:
            # Iterate over the profile_db list to insert each record into the profile table
            for profile in profile_db:
                name = profile["name"]
                full_name = profile["full_name"]
                id_number = profile["id_number"]
                plate_number = profile["plate_number"]
                vehicle_type = profile["vehicle_type"]
                vehicle_model = profile["vehicle_model"]
                role = profile["role"]            
                phone_number = profile["phone_number"]  
                image_link = profile["image_link"]    

                # Check if the profile already exists based on 'name' or 'full_name'
                cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s OR full_name = %s", (name, full_name))
                profile_exists = cursor.fetchone()[0]

                if profile_exists:
                    continue  # Skip the current record if it already exists

                # Insert new profile record into the 'profile' table
                insert_sql = """
                INSERT INTO profile (name, full_name, id_number, plate_number, vehicle_type, vehicle_model, role, phone_number, image_link)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (name, full_name, id_number, plate_number, vehicle_type, vehicle_model, role, phone_number, image_link))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Profiles inserted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

# Insert the initial records for notifications
@app.route('/insert-data-to-notifications', methods=['GET'])
def insert_notifications():
    try:
        # Step 1: Check if MySQL is available (Database service check)
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Step 2: Get a database cursor
        cursor = get_cursor()

        # Step 3: List of notifications to insert
        notifications_db = [
            {"uniqueId": "notif-001", "role": "admin", "message": "System update scheduled for tomorrow.", "status": "new"},
            {"uniqueId": "notif-002", "role": "user", "message": "Your password was successfully changed.", "status": "new"},
            {"uniqueId": "notif-003", "role": "admin", "message": "New user registration pending approval.", "status": "new"},
            {"uniqueId": "notif-004", "role": "user", "message": "Maintenance window scheduled for 2 AM.", "status": "new"},
            {"uniqueId": "notif-005", "role": "admin", "message": "Database backup completed successfully.", "status": "new"}
        ]
        
        if cursor:
            # Step 4: Prepare the SQL statement to insert data into 'notifications' table
            insert_sql = """
            INSERT INTO notifications (uniqueId, role, status, message, timestamp)
            VALUES (%s, %s, %s, %s, NOW());
            """
            
            # Step 5: Iterate over notifications_db to insert notifications one by one
            for notification in notifications_db:
                # Check if the notification with the same uniqueId already exists
                cursor.execute("SELECT COUNT(*) FROM notifications WHERE uniqueId = %s", (notification['uniqueId'],))
                notification_exists = cursor.fetchone()[0]
                
                if notification_exists:
                    return jsonify({"error": f"Notification with uniqueId '{notification['uniqueId']}' already exists."}), 400
                
                # Step 6: Execute the insert query for the notification if the uniqueId doesn't exist
                cursor.execute(insert_sql, (notification['uniqueId'], notification['role'], notification['status'], notification['message']))
            
            # Step 7: Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            # Step 8: Return success message
            return jsonify({"message": "Notifications inserted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        # Step 9: Handle MySQL errors
        return handle_mysql_error(e)

# Insert the initial records for violations
@app.route('/insert-data-to-violations', methods=['GET'])
def insert_violations():
    try:
        # Step 1: Check if MySQL is available (Database service check)
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Step 2: Get a database cursor
        cursor = get_cursor()

        # Step 3: List of violations to insert
        violations_db = [
            {"name": "Violation 001", "role": "admin", "status": "new", "type": "speeding", "info": "Exceeded speed limit by 20 km/h"},
            {"name": "Violation 002", "role": "user", "status": "new", "type": "parking", "info": "Parked in a no-parking zone"},
            {"name": "Violation 003", "role": "admin", "status": "new", "type": "speeding", "info": "Exceeded speed limit by 15 km/h"},
            {"name": "Violation 004", "role": "user", "status": "new", "type": "signal violation", "info": "Ran a red light"},
            {"name": "Violation 005", "role": "admin", "status": "new", "type": "parking", "info": "Parking in a handicapped spot without permit"}
        ]
        
        if cursor:
            # Step 4: Prepare the SQL statement to insert data into 'violations' table
            insert_sql = """
            INSERT INTO violations (name, role, status, type, info, timestamp)
            VALUES (%s, %s, %s, %s, %s, NOW());
            """
            
            # Step 5: Iterate over violations_db to insert violations one by one
            for violation in violations_db:
                # Check if the violation with the same name already exists
                cursor.execute("SELECT COUNT(*) FROM violations WHERE name = %s", (violation['name'],))
                violation_exists = cursor.fetchone()[0]
                
                if violation_exists:
                    return jsonify({"error": f"Violation with name '{violation['name']}' already exists."}), 400
                
                # Step 6: Execute the insert query for the violation if the name doesn't exist
                cursor.execute(insert_sql, (violation['name'], violation['role'], violation['status'], violation['type'], violation['info']))
            
            # Step 7: Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            # Step 8: Return success message
            return jsonify({"message": "Violations inserted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as error:
        # Step 9: Handle MySQL errors by calling a custom error handler
        return handle_mysql_error(error)

# Insert the initial records for parking history
@app.route('/insert-data-to-parking-history', methods=['GET'])
def insert_parking_history():
    try:
        # Step 1: Check if MySQL is available (Database service check)
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Step 2: Get a database cursor
        cursor = get_cursor()

        # Step 3: List of parking history to insert
        parking_history_db = [
            {"name": "testuser", "role": "user", "status": "-", "type": "-", "info": "-", "slotname": "-"}
        ]
        
        if cursor:
            # Step 4: Prepare the SQL statement to insert data into 'parking_history' table
            insert_sql = """
            INSERT INTO parking_history (name, role, status, type, info, slotname, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, NOW());
            """
            
            # Step 5: Iterate over parking_history_db to insert parking history one by one
            for parking in parking_history_db:
                # Check if the parking record with the same name and slot already exists
                cursor.execute("SELECT COUNT(*) FROM parking_history WHERE name = %s AND slotname = %s", (parking['name'], parking['slotname']))
                record_exists = cursor.fetchone()[0]
                
                if record_exists:
                    return jsonify({"error": f"Parking history for '{parking['name']}' in slot '{parking['slotname']}' already exists."}), 400
                
                # Step 6: Execute the insert query for the parking history if it doesn't exist
                cursor.execute(insert_sql, (parking['name'], parking['role'], parking['status'], parking['type'], parking['info'], parking['slotname']))
            
            # Step 7: Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            # Step 8: Return success message
            return jsonify({"message": "Parking history data inserted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as error:
        # Step 9: Handle MySQL errors by calling a custom error handler
        return handle_mysql_error(error)

# Insert the initial records for message
@app.route('/insert-data-to-message', methods=['GET'])
def bulk_insert_messages():
    try:
        # Get a database cursor
        cursor = get_cursor()

        # Mockup message data
        message_db = [
            {
                "name": "testuser",
                "status": "unread",
                "type": "info",
                "group": "general",
                "sender": "user",
                "receiver": "admin",
                "message": "Hi admin!"
            },
            {
                "name": "superuser",
                "status": "read",
                "type": "alert",
                "group": "general",
                "sender": "admin",
                "receiver": "user",
                "message": "Welcome to the system!"
            }
            # Add more mock messages here if needed
        ]

        if cursor:
            for msg in message_db:
                name = msg["name"]
                status = msg["status"]
                type = msg["type"]
                group = msg["group"]
                sender = msg["sender"]
                receiver = msg["receiver"]
                message_text = msg["message"]

                # Optional: prevent duplicates (you can adjust criteria)
                cursor.execute("""
                    SELECT COUNT(*) FROM message 
                    WHERE name = %s AND sender = %s AND receiver = %s AND message = %s
                """, (name, sender, receiver, message_text))
                message_exists = cursor.fetchone()[0]

                if message_exists:
                    continue  # Skip existing message

                # Insert new message
                insert_sql = """
                INSERT INTO message (name, status, type, `group`, sender, receiver, message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (name, status, type, group, sender, receiver, message_text))

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Mock messages inserted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


## show the all the records of table 'datawatch'
@app.route('/field', methods=['GET'])
def get_fields():
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            cursor.execute("SELECT * FROM datawatch")
            fields = cursor.fetchall()
            cursor.close()
            return jsonify(fields)
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## add or update a field with post parameters: field and value
@app.route('/field', methods=['POST'])
def add_field():
    data = request.json
    if not data or 'field' not in data or 'value' not in data:
        return jsonify({"error": "Field and value are required"}), 400

    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_insert = "INSERT INTO datawatch (field, value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE value = %s"
            cursor.execute(sql_insert, (data['field'], data['value'], data['value']))
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Field added or updated successfully"}), 201
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## get the records by field
@app.route('/field/<name>', methods=['GET'])
def get_field_by_name(name):
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_select = "SELECT * FROM datawatch WHERE field = %s"
            cursor.execute(sql_select, (name,))
            field = cursor.fetchone()
            cursor.close()
            if field:
                return jsonify(field)
            else:
                return jsonify({"error": "Field not found"}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## update the value of "<field-name>_status" or "<field-name>_state" by field-name then also, it will update its "<field-name>_timestamp" or "<field-name>_last", respectively.
@app.route('/field/<name>', methods=['PUT'])
def update_field_by_name(name):
    data = request.json
    if not data or 'value' not in data:
        return jsonify({"error": "Value field is required"}), 400

    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            # Update the specified field
            sql_update = "UPDATE datawatch SET value = %s WHERE field = %s"
            cursor.execute(sql_update, (data['value'], name))
            db_connection.commit()

            # Check if the updated field ends with '_status' or '_state'
            if name.endswith('_status'):
                # Update corresponding timestamp field
                timestamp_name = f"{name.split('_status')[0]}_timestamp"
                current_time = datetime.now().strftime("%Y/%m/%d-%H/%M/%S")
                cursor.execute(sql_update, (current_time, timestamp_name))
                db_connection.commit()
            elif name.endswith('_state'):
                # Update corresponding timestamp field
                timestamp_name = f"{name.split('_state')[0]}_last"
                current_time = datetime.now().strftime("%Y/%m/%d-%H/%M/%S")
                cursor.execute(sql_update, (current_time, timestamp_name))
                db_connection.commit()

            cursor.close()
            return jsonify({"message": "Field updated successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## delete a record by field
@app.route('/field/<name>', methods=['DELETE'])
def delete_field_by_name(name):
    try:
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        cursor = get_cursor()
        if cursor:
            sql_delete = "DELETE FROM datawatch WHERE field = %s"
            cursor.execute(sql_delete, (name,))
            db_connection.commit()
            cursor.close()
            return jsonify({"message": "Field deleted successfully"}), 200
        else:
            return jsonify({"error": "Database connection not available"}), 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## get the value's value by field
@app.route('/field/value/<name>', methods=['GET'])
def get_fieldvalue_by_name(name):
    try:
        if not is_mysql_available():
            return "MySQL database not responding, please check the database service", 500
        
        cursor = get_cursor()
        if cursor:
            sql_select = "SELECT value FROM datawatch WHERE field = %s"
            cursor.execute(sql_select, (name,))
            field_value = cursor.fetchone()

            if field_value:
                # Update corresponding _timestamp or _last field
                if name.endswith('_status'):
                    timestamp_name = f"{name.split('_status')[0]}_timestamp"
                elif name.endswith('_state'):
                    timestamp_name = f"{name.split('_state')[0]}_last"
                else:
                    timestamp_name = None

                if timestamp_name:
                    current_time = datetime.now().strftime("%Y/%m/%d-%H/%M/%S")
                    sql_update = "UPDATE datawatch SET value = %s WHERE field = %s"
                    cursor.execute(sql_update, (current_time, timestamp_name))
                    db_connection.commit()

                return str(field_value[0])  # Return value as string
            else:
                return "Field not found", 404
        else:
            return "Database connection not available", 500
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/check_rfid/<rfid>', methods=['GET'])
def check_rfid(rfid):
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the RFID exists in the users table and fetch the assignedslot
            cursor.execute("SELECT assignedslot FROM users WHERE rfid = %s LIMIT 1", (rfid,))
            user = cursor.fetchone()

            if user:
                assignedslot = user[0]
                
                # Get the columns of the stores table
                cursor.execute("SHOW COLUMNS FROM stores")
                store_columns = [column[0] for column in cursor.fetchall()]

                # Check if the assignedslot exists as a column in the stores table
                if assignedslot not in store_columns:
                    return jsonify({"error": f"'{assignedslot}' column does not exist in the stores table."}), 400

                # Now, using the hardcoded unique_id ('12345'), fetch the value from the stores table
                cursor.execute(f"SELECT {assignedslot} FROM stores WHERE unique_id = '12345' LIMIT 1")
                store_value = cursor.fetchone()

                if store_value:
                    return jsonify({assignedslot: store_value[0]}), 200
                else:
                    return jsonify({"error": f"No data found for column '{assignedslot}' in the stores table."}), 404
            else:
                return jsonify({"error": "RFID not found in users table."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

# @app.route('/update_slot_for_entry/<rfid>', methods=['POST'])
# def update_slot_for_entry(rfid):
#     try:
#         # Validate that 'rfid' is provided
#         if not rfid:
#             return jsonify({"error": "'rfid' is required."}), 400

#         # Check if MySQL is available
#         if not is_mysql_available():
#             return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

#         # Get a database connection and cursor
#         connection = get_connection()  # Get the MySQL connection
#         if connection is None:
#             return jsonify({"error": "Failed to connect to the database"}), 500

#         cursor = connection.cursor()

#         if cursor:
#             # Step 1: Check if the RFID exists in the users table and fetch the name
#             cursor.execute("SELECT name FROM users WHERE rfid = %s LIMIT 1", (rfid,))
#             user = cursor.fetchone()

#             if user:
#                 extracted_name = user[0]
                
#                 # Step 2: Check if the extracted_name is already assigned to any slot in stores table
#                 cursor.execute("SHOW COLUMNS FROM stores")
#                 store_columns = [column[0] for column in cursor.fetchall()]

#                 # Check if any column is already assigned to the extracted_name
#                 for column in store_columns:
#                     if column.startswith('slot') and column != 'unique_id':
#                         cursor.execute(f"SELECT {column} FROM stores WHERE unique_id = '12345'")
#                         slot_value = cursor.fetchone()
#                         if slot_value and slot_value[0] == extracted_name:
#                             return jsonify({"error": f"User '{extracted_name}' is already assigned to the slot {column}."}), 400

#                 # Step 3: Check for the first available slot in the stores table
#                 for column in store_columns:
#                     if column.startswith('slot') and column != 'unique_id':  # Skip unique_id column
#                         cursor.execute(f"SELECT {column} FROM stores WHERE unique_id = '12345'")
#                         slot_value = cursor.fetchone()
#                         if slot_value and slot_value[0] == "available":
#                             # Assign the extracted_name to the first available slot
#                             cursor.execute(f"UPDATE stores SET {column} = %s WHERE unique_id = '12345'", (extracted_name,))
                            
#                             # Step 4: Update the 'assignedslot' field in the users table with the assigned slot name
#                             cursor.execute("UPDATE users SET assignedslot = %s WHERE rfid = %s", (column, rfid))
                            
#                             # Commit the changes
#                             connection.commit()
                            
#                             return jsonify({"message": f"{column} successfully updated to '{extracted_name}'."}), 200

#                 return jsonify({"error": "There's no available slot."}), 400

#             else:
#                 return jsonify({"error": "RFID not found in users table."}), 404

#         else:
#             return jsonify({"error": "Database connection not available"}), 500

#     except mysql.connector.Error as e:
#         print(f"Database error: {e}")
#         return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

#     finally:
#         if cursor:
#             cursor.close()
#         if connection:
#             connection.close()


@app.route('/update_slot_for_entry/<rfid>', methods=['POST'])
def update_slot_for_entry(rfid):
    try:
        # Validate that 'rfid' is provided
        if not rfid:
            return jsonify({"error": "'rfid' is required."}), 400

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Step 1: Check if the RFID exists in the users table and fetch the name
            cursor.execute("SELECT name FROM users WHERE rfid = %s LIMIT 1", (rfid,))
            user = cursor.fetchone()

            if user:
                extracted_name = user[0]
                
                # Step 2: Check if the extracted_name is already assigned to any slot in stores table
                cursor.execute("SHOW COLUMNS FROM stores")
                store_columns = [column[0] for column in cursor.fetchall()]

                for column in store_columns:
                    if column.startswith('slot') and column != 'unique_id':
                        cursor.execute(f"SELECT {column} FROM stores WHERE unique_id = '12345'")
                        slot_value = cursor.fetchone()
                        if slot_value and slot_value[0] == extracted_name:
                            return jsonify({"error": f"User '{extracted_name}' is already assigned to the slot {column}."}), 400

                # Step 3: Check for the first available slot in the stores table
                for column in store_columns:
                    if column.startswith('slot') and column != 'unique_id':
                        cursor.execute(f"SELECT {column} FROM stores WHERE unique_id = '12345'")
                        slot_value = cursor.fetchone()
                        if slot_value and slot_value[0] == "available":
                            # Step 4: Assign the extracted_name to the slot
                            cursor.execute(f"UPDATE stores SET {column} = %s WHERE unique_id = '12345'", (extracted_name,))
                            cursor.execute("UPDATE users SET assignedslot = %s WHERE rfid = %s", (column, rfid))

                            # Step 5: Add parking history
                            insert_sql = """
                            INSERT INTO parking_history (name, role, status, type, info, slotname)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            name = extracted_name
                            role = "user"
                            status = "active"
                            type = "rfid"
                            info = "Entry approved – RFID recognized."
                            slotname = column

                            cursor.execute(insert_sql, (name, role, status, type, info, slotname))


                            # Commit all changes
                            connection.commit()

                            return jsonify({"message": f"{column} successfully updated to '{extracted_name}'."}), 200

                return jsonify({"error": "There's no available slot."}), 400

            else:
                return jsonify({"error": "RFID not found in users table."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# @app.route('/update_slot_for_exit/<rfid>', methods=['POST'])
# def update_slot_for_exit(rfid):
#     connection = None
#     cursor = None
#     try:
#         # Check if MySQL is available
#         if not is_mysql_available():
#             return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
#         # Get a database connection and cursor
#         connection = get_connection()  # Get the MySQL connection
#         if connection is None:
#             return jsonify({"error": "Failed to connect to the database"}), 500
        
#         cursor = connection.cursor()

#         if cursor:
#             # Step 1: Check if the RFID exists in the users table and fetch the assignedslot
#             cursor.execute("SELECT assignedslot FROM users WHERE rfid = %s LIMIT 1", (rfid,))
#             user = cursor.fetchone()

#             if user:
#                 assignedslot = user[0]
                
#                 # Step 2: Check if the assignedslot column exists in the stores table
#                 cursor.execute("SHOW COLUMNS FROM stores")
#                 store_columns = [column[0] for column in cursor.fetchall()]

#                 if assignedslot not in store_columns:
#                     return jsonify({"error": f"'{assignedslot}' column does not exist in the stores table."}), 400

#                 # Step 3: Now, using the hardcoded unique_id ('12345'), fetch the current value from the stores table
#                 cursor.execute(f"SELECT {assignedslot} FROM stores WHERE unique_id = '12345' LIMIT 1")
#                 store_value = cursor.fetchone()

#                 if store_value:
#                     # Check if the store_value is not 'available'
#                     if store_value[0] != 'available':
#                         # Step 4: Update the slot value to 'available' because the user is exiting
#                         cursor.execute(f"UPDATE stores SET {assignedslot} = 'available' WHERE unique_id = '12345'")
#                         connection.commit()  # Commit the changes to the database
#                         return jsonify({"message": f"{assignedslot} successfully updated to 'available'."}), 200
#                     else:
#                         return jsonify({"error": f"{assignedslot} is already marked as 'available', cannot update."}), 400
#                 else:
#                     return jsonify({"error": f"No data found for column '{assignedslot}' in the stores table."}), 404
#             else:
#                 return jsonify({"error": "RFID not found in users table."}), 404

#         else:
#             return jsonify({"error": "Database connection not available"}), 500

#     except mysql.connector.Error as e:
#         print(f"Database error: {e}")
#         return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500
    
#     finally:
#         if cursor:
#             cursor.close()
#         if connection:
#             connection.close()


@app.route('/update_slot_for_exit/<rfid>', methods=['POST'])
def update_slot_for_exit(rfid):
    connection = None
    cursor = None
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Step 1: Check if the RFID exists in the users table and fetch the assignedslot and name
            cursor.execute("SELECT assignedslot, name FROM users WHERE rfid = %s LIMIT 1", (rfid,))
            user = cursor.fetchone()

            if user:
                assignedslot, extracted_name = user
                
                # Step 2: Check if the assignedslot column exists in the stores table
                cursor.execute("SHOW COLUMNS FROM stores")
                store_columns = [column[0] for column in cursor.fetchall()]

                if assignedslot not in store_columns:
                    return jsonify({"error": f"'{assignedslot}' column does not exist in the stores table."}), 400

                # Step 3: Fetch the current value of the assignedslot in the stores table
                cursor.execute(f"SELECT {assignedslot} FROM stores WHERE unique_id = '12345' LIMIT 1")
                store_value = cursor.fetchone()

                if store_value:
                    if store_value[0] != 'available':
                        # Step 4: Update the slot value to 'available' because the user is exiting
                        cursor.execute(f"UPDATE stores SET {assignedslot} = 'available' WHERE unique_id = '12345'")

                        # Step 5: Add parking history
                        insert_sql = """
                        INSERT INTO parking_history (name, role, status, type, info, slotname)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        name = extracted_name
                        role = "user"
                        status = "inactive"
                        type = "rfid"
                        info = "Exit recorded – Slot cleared."
                        slotname = assignedslot

                        cursor.execute(insert_sql, (name, role, status, type, info, slotname))

                        # Commit all changes
                        connection.commit()

                        return jsonify({"message": f"{assignedslot} successfully updated to 'available' and exit recorded."}), 200
                    else:
                        return jsonify({"error": f"{assignedslot} is already marked as 'available', cannot update."}), 400
                else:
                    return jsonify({"error": f"No data found for column '{assignedslot}' in the stores table."}), 404
            else:
                return jsonify({"error": "RFID not found in users table."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/assign_slot_for_entry/<rfid>', methods=['POST'])
def assign_slot_for_entry(rfid):
    connection = None
    cursor = None
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Step 1: Check if the RFID exists in the users table and fetch the assignedslot
            cursor.execute("SELECT assignedslot FROM users WHERE rfid = %s LIMIT 1", (rfid,))
            user = cursor.fetchone()

            if user:
                assignedslot = user[0]
                
                # Step 2: Check if the assignedslot column exists in the stores table
                cursor.execute("SHOW COLUMNS FROM stores")
                store_columns = [column[0] for column in cursor.fetchall()]

                if assignedslot not in store_columns:
                    return jsonify({"error": f"'{assignedslot}' column does not exist in the stores table."}), 400

                # Step 3: Check if the slot is available, then update it to 'taken'
                cursor.execute(f"SELECT {assignedslot} FROM stores WHERE unique_id = '12345' LIMIT 1")
                store_value = cursor.fetchone()

                if store_value:
                    if store_value[0] == 'available':
                        # Step 4: Update the slot value to 'taken'
                        cursor.execute(f"UPDATE stores SET {assignedslot} = 'taken' WHERE unique_id = '12345'")
                        connection.commit()  # Commit the changes using the connection object
                        return jsonify({"message": f"{assignedslot} successfully updated to 'taken'."}), 200
                    else:
                        return jsonify({"error": f"{assignedslot} is already marked as '{store_value[0]}', cannot update."}), 400
                else:
                    return jsonify({"error": f"No data found for column '{assignedslot}' in the stores table."}), 404
            else:
                return jsonify({"error": "RFID not found in users table."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/assign_slot_for_exit/<rfid>', methods=['POST'])
def assign_slot_for_exit(rfid):
    connection = None
    cursor = None
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Step 1: Check if the RFID exists in the users table and fetch the assignedslot
            cursor.execute("SELECT assignedslot FROM users WHERE rfid = %s LIMIT 1", (rfid,))
            user = cursor.fetchone()

            if user:
                assignedslot = user[0]
                
                # Step 2: Check if the assignedslot column exists in the stores table
                cursor.execute("SHOW COLUMNS FROM stores")
                store_columns = [column[0] for column in cursor.fetchall()]

                if assignedslot not in store_columns:
                    return jsonify({"error": f"'{assignedslot}' column does not exist in the stores table."}), 400

                # Step 3: Now, using the hardcoded unique_id ('12345'), fetch the current value from the stores table
                cursor.execute(f"SELECT {assignedslot} FROM stores WHERE unique_id = '12345' LIMIT 1")
                store_value = cursor.fetchone()

                if store_value:
                    if store_value[0] == 'taken':
                        # Step 4: Update the slot value to 'available' because the user is exiting
                        cursor.execute(f"UPDATE stores SET {assignedslot} = 'available' WHERE unique_id = '12345'")
                        connection.commit()  # Commit the changes to the database
                        return jsonify({"message": f"{assignedslot} successfully updated to 'available'."}), 200
                    else:
                        return jsonify({"error": f"{assignedslot} is already marked as '{store_value[0]}', cannot update."}), 400
                else:
                    return jsonify({"error": f"No data found for column '{assignedslot}' in the stores table."}), 404
            else:
                return jsonify({"error": "RFID not found in users table."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

## show the all the records of table 'users'
@app.route('/users', methods=['GET'])
def get_users():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()
        
        if cursor:
            # Execute the SQL query to fetch all users from the 'users' table
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            if not users:
                return jsonify({"message": "No users found."}), 404
            
            # Prepare the list to return in JSON format
            users_list = []
            for user in users:
                # Assuming your table columns are id, name, password_hash, role, email, status, token, rfid, assignedslot, timestamp
                users_list.append({
                    "id": user[0],
                    "name": user[1],
                    "password_hash": user[2],
                    "role": user[3],
                    "email": user[4],
                    "status": user[5],
                    "token": user[6],
                    "rfid": user[7],  # assuming the column exists
                    "assignedslot": user[8],  # assuming the column exists
                    "timestamp": user[9]
                })
            
            # Close the cursor
            cursor.close()
            
            # Return the users as a JSON response
            return jsonify({"users": users_list}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

## adding the new user
@app.route('/users/add', methods=['POST'])
def add_user():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the required fields
        if "name" not in data or "password_hash" not in data or "email" not in data or "rfid" not in data or "assignedslot" not in data:
            return jsonify({"error": "Fields 'name', 'password_hash', 'email', 'rfid', and 'assignedslot' are required."}), 400
        
        # Add validation for the 'role' field (if required)
        role = data.get("role", "")  # Default to empty string if not provided

        # Validate role if necessary, for example, checking if it’s one of a list of valid roles
        valid_roles = ["admin", "user", "guest"]  # Example of valid roles
        if role and role not in valid_roles:
            return jsonify({"error": f"Invalid role. Valid roles are {', '.join(valid_roles)}."}), 400
        
        name = data["name"]
        password_hash = data["password_hash"]
        email = data["email"]
        rfid = data["rfid"]
        assignedslot = data["assignedslot"]

        # Get a database cursor
        # cursor = get_cursor()

        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the user with the same name already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (name,))
            user_exists = cursor.fetchone()[0]
            
            if user_exists:
                cursor.close()
                return jsonify({"error": f"User with name '{name}' already exists."}), 400

            # Prepare the SQL query to insert a new user into the 'users' table
            insert_sql = """
            INSERT INTO users (name, password_hash, role, email, status, token, rfid, assignedslot, timestamp)
            VALUES (%s, %s, %s, %s, '', '', %s, %s, NOW());
            """
            
            # Execute the insert query, including the assignedslot if it's provided
            cursor.execute(insert_sql, (name, password_hash, role, email, rfid, assignedslot))
            
            # Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "User added successfully."}), 201
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/users/update_assignedslot', methods=['PUT'])
def update_assignedslot():
    try:
        # Get data from request
        data = request.get_json()
        name = data.get("name")
        assignedslot = data.get("assignedslot")
        
        if not name or not assignedslot:
            return jsonify({"error": "Both 'name' and 'assignedslot' must be provided"}), 400
        
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()
        
        if cursor:
            # Execute the SQL query to update the assignedslot based on the user's name
            cursor.execute("UPDATE users SET assignedslot = %s WHERE name = %s", (assignedslot, name))
            
            # Commit the transaction
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({"error": "No user found with the given name"}), 404
            
            # Close the cursor
            cursor.close()
            
            return jsonify({"message": "Assigned slot updated successfully"}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return jsonify({"error": "MySQL database operation failed. Please check the database connection."}), 500

@app.route('/users/update_rfid', methods=['PUT'])
def update_rfid():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the required fields
        if "name" not in data or "rfid" not in data:
            return jsonify({"error": "Fields 'name' and 'rfid' are required."}), 400
        
        name = data["name"]
        rfid = data["rfid"]

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the user with the provided name exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (name,))
            user_exists = cursor.fetchone()[0]
            
            if not user_exists:
                cursor.close()
                return jsonify({"error": f"User with name '{name}' does not exist."}), 404

            # Prepare the SQL query to update the RFID for the user
            update_sql = """
            UPDATE users
            SET rfid = %s
            WHERE name = %s;
            """
            
            # Execute the update query
            cursor.execute(update_sql, (rfid, name))
            
            # Commit the changes to the database
            connection.commit()
            cursor.close()
            
            return jsonify({"message": f"RFID for user '{name}' updated successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)


## name and password hash validation
@app.route('/users/validate', methods=['POST'])
def validate_user():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the required fields
        if "name" not in data or "password_hash" not in data:
            return jsonify({"error": "Both 'name' and 'password_hash' are required fields."}), 400
        
        name = data["name"]
        password_hash = data["password_hash"]
        
        # # Get a database cursor
        # cursor = get_cursor()

        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Check if the user exists with the provided name
            cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
            user = cursor.fetchone()
            
            if user:
                # User exists, check if the password_hash matches
                stored_password_hash = user[2]  # Assuming password_hash is in the 3rd column
                role = user[3]  # Assuming role is in the 4th column
                
                if password_hash == stored_password_hash:
                    cursor.close()
                    return jsonify({
                        "message": "Match",
                        "role": role
                    }), 200
                else:
                    cursor.close()
                    return jsonify({"error": "Password does not match."}), 400
            else:
                cursor.close()
                return jsonify({"error": "User not found."}), 404
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/users/validate-email', methods=['POST'])
def validate_email():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the required fields
        if "email" not in data or "password_hash" not in data:
            return jsonify({"error": "Both 'email' and 'password_hash' are required fields."}), 400
        
        email = data["email"]
        password_hash = data["password_hash"]
        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the user exists with the provided email
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                # User exists, check if the password_hash matches
                stored_password_hash = user[2]  # Assuming password_hash is in the 3rd column
                role = user[3]  # Assuming role is in the 4th column
                
                if password_hash == stored_password_hash:
                    cursor.close()
                    return jsonify({
                        "message": "Match",
                        "role": role
                    }), 200
                else:
                    cursor.close()
                    return jsonify({"error": "Password does not match."}), 400
            else:
                cursor.close()
                return jsonify({"error": "User not found."}), 404
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)


## update password_hash by name
@app.route('/users/update-password/', methods=['PUT'])
def update_password():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the required fields
        if "name" not in data or "password_hash" not in data:
            return jsonify({"error": "Both 'name' and 'password_hash' are required fields."}), 400
        
        name = data["name"]
        new_password_hash = data["password_hash"]
        
        # # Get a database cursor
        # cursor = get_cursor()

        
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the user exists with the provided name
            cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
            user = cursor.fetchone()
            
            if user:
                # Prepare the SQL query to update the password_hash for the user
                update_sql = "UPDATE users SET password_hash = %s WHERE name = %s"
                
                # Execute the update query
                cursor.execute(update_sql, (new_password_hash, name))
                
                # Commit the changes to the database
                db_connection.commit()
                cursor.close()
                
                return jsonify({"message": "Password updated successfully."}), 200
            else:
                cursor.close()
                return jsonify({"error": "User not found."}), 404
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## update user by name
@app.route('/users/delete/', methods=['DELETE'])
def delete_user():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Validate the required field
        if "name" not in data:
            return jsonify({"error": "'name' is a required field."}), 400
        
        name = data["name"]
        
        # Get a database cursor
        # cursor = get_cursor()


        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the user exists with the provided name
            cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
            user = cursor.fetchone()
            
            if user:
                # Prepare the SQL query to delete the user by name
                delete_sql = "DELETE FROM users WHERE name = %s"
                
                # Execute the delete query
                cursor.execute(delete_sql, (name,))
                
                # Commit the changes to the database
                db_connection.commit()
                cursor.close()
                
                return jsonify({"message": f"User '{name}' deleted successfully."}), 200
            else:
                cursor.close()
                return jsonify({"error": "User not found."}), 404
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## show the all the records of table 'users'
@app.route('/admin', methods=['GET'])
def get_users_admin():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        # cursor = get_cursor()


        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()
        
        if cursor:
            # Execute the SQL query to fetch all users from the 'users' table
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            # Prepare the list to return in JSON format
            users_list = []
            for user in users:
                # Convert each user to a dictionary (assuming your table has id, name, etc. columns)
                users_list.append({
                    "id": user[0],
                    "name": user[1],
                    "password_hash": user[2],
                    "role": user[3],
                    "email": user[4],
                    "status": user[5],
                    "token": user[6],
                    "timestamp": user[7]
                })
            
            # Close the cursor
            cursor.close()
            
            # Return the users as a JSON response
            return jsonify({"users": users_list}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)


## adding the new admin user
@app.route('/admin/add', methods=['POST'])
def add_admin_user():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the data from the request
        data = request.get_json()
        
        # Ensure all required fields are provided
        if not all(field in data for field in ["name", "password_hash", "email"]):
            return jsonify({"error": "Missing required fields: 'name', 'password_hash', or 'email'"}), 400
        
        name = data["name"]
        password_hash = data["password_hash"]
        email = data["email"]

        # Generate a unique token 
        token = generate_random_string()
        
        # Set the role and status
        role = "admin"
        status = "inactive"
        
        # Get a database cursor
        # cursor = get_cursor()



        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()
        
        if cursor:
            # SQL to insert the new record (using NOW() for timestamp)
            insert_user_sql = """
            INSERT INTO users (name, password_hash, role, email, status, token, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, NOW());
            """
            
            # Execute the insert query with the data
            cursor.execute(insert_user_sql, (name, password_hash, role, email, status, token))
            
            # Commit the transaction
            db_connection.commit()
            cursor.close()
            
            # Return a response with the added details
            return jsonify({
                "message": "Admin User added successfully",
                "status": "ok",
                "role": "admin",
                "token": token
            }), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## validate the admin user
@app.route('/admin/login', methods=['POST'])
def admin_login():
    try:
        # Get the data from the request
        data = request.get_json()
        
        # Ensure that the required fields are in the request
        if not all(field in data for field in ["name", "password_hash"]):
            return jsonify({"error": "Missing required fields: 'name' or 'password_hash'"}), 400
        
        name = data["name"]
        password_hash = data["password_hash"]
        
        # Get a database cursor
        # cursor = get_cursor()



        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        
        if cursor:
            # SQL query to find the first user with the given name, password_hash, and role "admin"
            select_user_sql = """
            SELECT id, role, timestamp FROM users
            WHERE name = %s AND password_hash = %s AND role = 'admin'
            LIMIT 1;
            """
            
            # Execute the query with the provided name and password_hash
            cursor.execute(select_user_sql, (name, password_hash))
            user = cursor.fetchone()
            
            if user:
                # User found and role is admin
                user_id, role, timestamp = user
                
                # Return a success response with the required details
                return jsonify({
                    "message": "Login successful",
                    "status": "ok",
                    "role": role,
                    "timestamp": timestamp.isoformat()  # Assuming timestamp is a datetime object
                }), 200
            else:
                return jsonify({"error": "Invalid credentials or user is not an admin"}), 401
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## delete the admin user
@app.route('/admin/delete', methods=['DELETE'])
def admin_delete():
    try:
        # Get the data from the request
        data = request.get_json()
        
        # Ensure that the required fields are in the request
        if not all(field in data for field in ["name", "password_hash"]):
            return jsonify({"error": "Missing required fields: 'name' or 'password_hash'"}), 400
        
        name = data["name"]
        password_hash = data["password_hash"]
        
        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()
        
        if cursor:
            # SQL query to check for a user with the given name, password_hash, and role "admin"
            select_user_sql = """
            SELECT id FROM users
            WHERE name = %s AND password_hash = %s AND role = 'admin'
            LIMIT 1;
            """
            
            # Execute the query with the provided name and password_hash
            cursor.execute(select_user_sql, (name, password_hash))
            user = cursor.fetchone()
            
            if user:
                # If the user exists with role "admin", delete the record
                delete_user_sql = "DELETE FROM users WHERE id = %s"
                cursor.execute(delete_user_sql, (user[0],))
                
                # Commit the transaction
                db_connection.commit()
                cursor.close()
                
                # Return a success message
                return jsonify({
                    "message": "Admin user deleted successfully",
                    "status": "ok"
                }), 200
            else:
                return jsonify({"error": "User not found or not an admin"}), 404
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## update the admin user
@app.route('/admin/update', methods=['PUT'])
def admin_update_profile():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'name', 'full_name', and 'phone_number' are provided
        if 'name' not in data or 'full_name' not in data or 'phone_number' not in data:
            return jsonify({"error": "'name', 'full_name', and 'phone_number' are required to update a profile."}), 400

        # Extract name, full_name, and phone_number from the data
        name = data["name"]
        full_name = data["full_name"]
        phone_number = data["phone_number"]

        # Check if the 'profile' table exists
        # cursor = get_cursor()


        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # First, check if the profile exists and if the role is 'admin'
            cursor.execute("SELECT role FROM profile WHERE name = %s", (name,))
            result = cursor.fetchone()

            if result is None:
                return jsonify({"error": "Profile not found."}), 404

            # Check if the role of the profile is 'admin'
            role = result[0]
            if role != "admin":
                return jsonify({"error": "Only profiles with 'admin' role can be updated."}), 403

            # SQL to update the full_name and phone_number fields
            update_sql = """
            UPDATE profile
            SET 
                full_name = %s,
                phone_number = %s
            WHERE name = %s
            """

            # Execute the update query
            cursor.execute(update_sql, (full_name, phone_number, name))

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Profile updated successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## show all admin user details
@app.route('/contact', methods=['GET'])
def get_admin_profiles_contact():
    try:
        # Check if the 'profile' table exists
        # cursor = get_cursor()


        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Query to fetch all admin profiles from the 'profile' table
            cursor.execute("""
                SELECT id, name, full_name, id_number, plate_number, vehicle_type, vehicle_model, 
                       role, phone_number, image_link, timestamp 
                FROM profile WHERE role = 'admin'
            """)
            profiles = cursor.fetchall()

            if profiles:
                # If profiles are found, return them as JSON
                profile_list = []
                for profile in profiles:
                    profile_data = {
                        "id": profile[0],
                        "name": profile[1],
                        "full_name": profile[2],
                        "id_number": profile[3],
                        "plate_number": profile[4],
                        "vehicle_type": profile[5],
                        "vehicle_model": profile[6],
                        "role": profile[7],
                        "phone_number": profile[8],
                        "image_link": profile[9],
                        "timestamp": profile[10]
                    }
                    profile_list.append(profile_data)

                cursor.close()
                return jsonify(profile_list), 200
            else:
                cursor.close()
                return jsonify({"message": "No admin profiles found."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## update value of a "slot column" by uniqueid and slot-name-column
@app.route('/stores/update-slot/', methods=['POST'])
def update_store_slot():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get the JSON data from the request
        data = request.get_json()

        # Check if the required fields are in the request body
        if "unique_id" not in data or "slot" not in data or "new_value" not in data:
            return jsonify({"error": "'unique_id', 'slot', and 'new_value' are required in the request body."}), 400
        
        unique_id = data["unique_id"]
        slot = data["slot"]
        new_value = data["new_value"]

        # Validate if the slot name is valid (it should be one of the 'slot1' to 'slot16')
        # valid_slots = [f"slot{i}" for i in range(1, 17)]
        valid_slots = [f"slot{i}" for i in range(1, 201)]
        if slot not in valid_slots:
            return jsonify({"error": f"Invalid slot name. Valid slots are: {', '.join(valid_slots)}."}), 400
        
        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Check if the store with the given unique_id exists
            cursor.execute("SELECT COUNT(*) FROM stores WHERE unique_id = %s", (unique_id,))
            store_exists = cursor.fetchone()[0]

            if not store_exists:
                cursor.close()
                return jsonify({"error": f"Store with unique_id '{unique_id}' does not exist."}), 404

            # Prepare the SQL query to update the slot column
            update_sql = f"""
            UPDATE stores
            SET {slot} = %s
            WHERE unique_id = %s;
            """

            # Execute the update query
            cursor.execute(update_sql, (new_value, unique_id))

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": f"Successfully updated {slot} for store with unique_id '{unique_id}'."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## show the all the records of table 'stores'
@app.route('/stores', methods=['GET'])
def get_stores():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Query all records from the stores table
            cursor.execute("SELECT * FROM stores")
            rows = cursor.fetchall()

            if rows:
                # Prepare the list of store records in a dictionary format
                stores_data = []
                columns = [desc[0] for desc in cursor.description]  # Get column names

                for row in rows:
                    store = dict(zip(columns, row))
                    stores_data.append(store)

                # Close cursor and return the data
                cursor.close()
                return jsonify(stores_data), 200
            else:
                cursor.close()
                return jsonify({"message": "No records found in the stores table."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/stores/add', methods=['POST'])
def add_store_slot_column():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'unique_id' is provided
        if "unique_id" not in data:
            return jsonify({"error": "'unique_id' is required."}), 400

        unique_id = data["unique_id"]

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the store with the provided unique_id exists
            cursor.execute("SELECT * FROM stores WHERE unique_id = %s", (unique_id,))
            store = cursor.fetchone()

            if not store:
                cursor.close()
                return jsonify({"error": f"Store with unique_id '{unique_id}' not found."}), 404

            # Find the next available slot (next column like slot17, slot18, etc.)
            # Get the column names for the stores table to find the last slot
            cursor.execute("SHOW COLUMNS FROM stores")
            columns = cursor.fetchall()

            # Extract the column names
            column_names = [column[0] for column in columns]

            # Find the last slot (slotX) to determine the next available slot
            slot_columns = [col for col in column_names if col.startswith('slot')]
            slot_numbers = [int(col.replace('slot', '')) for col in slot_columns]
            next_slot_number = max(slot_numbers, default=0) + 1  # Next available slot number

            # Add a new column for the new slot
            new_column_name = f"slot{next_slot_number}"
            add_column_sql = f"ALTER TABLE stores ADD COLUMN {new_column_name} TEXT"
            cursor.execute(add_column_sql)

            # Commit the changes
            db_connection.commit()

            cursor.close()
            return jsonify({"message": f"New column '{new_column_name}' added to the 'stores' table."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/stores/delete-column', methods=['DELETE'])
def delete_store_column():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'unique_id' is provided
        if "unique_id" not in data:
            return jsonify({"error": "'unique_id' is required."}), 400

        unique_id = data["unique_id"]

        # Validate that 'column_name' is provided
        if "column_name" not in data:
            return jsonify({"error": "'column_name' is required."}), 400

        column_name = data["column_name"]

        # Ensure that 'unique_id' and 'slot1' cannot be deleted
        if column_name in ["unique_id", "slot1"]:
            return jsonify({"error": "'unique_id' and 'slot1' cannot be deleted."}), 400

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Check if the store with the provided unique_id exists
            cursor.execute("SELECT * FROM stores WHERE unique_id = %s", (unique_id,))
            store = cursor.fetchone()

            if not store:
                cursor.close()
                return jsonify({"error": f"Store with unique_id '{unique_id}' not found."}), 404

            # Check if the column exists in the stores table
            cursor.execute("SHOW COLUMNS FROM stores")
            columns = cursor.fetchall()

            column_names = [column[0] for column in columns]

            if column_name not in column_names:
                cursor.close()
                return jsonify({"error": f"Column '{column_name}' does not exist in the stores table."}), 404

            # Drop the specified column
            drop_column_sql = f"ALTER TABLE stores DROP COLUMN {column_name}"
            cursor.execute(drop_column_sql)

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": f"Column '{column_name}' has been deleted from the 'stores' table."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

# ## adding the new profile
# @app.route('/profile/add', methods=['POST'])
# def insert_profile():
#     try:
#         # Get the data from the request body
#         data = request.get_json()

#         # Validate the required fields
#         required_fields = ["name", "full_name", "id_number", "plate_number", "vehicle_type", "vehicle_model"]
#         for field in required_fields:
#             if field not in data:
#                 return jsonify({"error": f"'{field}' is required."}), 400

#         name = data["name"]
#         full_name = data["full_name"]

#         # Check if the 'profile' table exists
#         # cursor = get_cursor()

#         # Get a database connection and cursor
#         connection = get_connection()  # Get the MySQL connection
#         if connection is None:
#             return jsonify({"error": "Failed to connect to the database"}), 500
        
#         cursor = connection.cursor()


#         if cursor:
#             # Check if the given 'name' or 'full_name' already exists in the profile table
#             cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s OR full_name = %s", (name, full_name))
#             duplicate_check = cursor.fetchone()[0]

#             if duplicate_check:
#                 cursor.close()
#                 return jsonify({"error": "Profile with this 'name' or 'full_name' already exists."}), 400

#             # Insert the new record into the profile table
#             insert_sql = """
#             INSERT INTO profile (name, full_name, id_number, plate_number, vehicle_type, vehicle_model)
#             VALUES (%s, %s, %s, %s, %s, %s)
#             """
#             cursor.execute(insert_sql, (name, full_name, data["id_number"], data["plate_number"], data["vehicle_type"], data["vehicle_model"]))

#             # Commit the changes to the database
#             db_connection.commit()
#             cursor.close()

#             return jsonify({"message": "Profile added successfully."}), 200

#         else:
#             return jsonify({"error": "Database connection not available"}), 500

#     except mysql.connector.Error as e:
#         return handle_mysql_error(e)

## adding the new profile
@app.route('/profile/add', methods=['POST'])
def insert_profile():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate the required fields
        required_fields = ["name", "full_name", "id_number", "plate_number", "vehicle_type", "vehicle_model"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required."}), 400

        name = data["name"]
        full_name = data["full_name"]
        id_number = data["id_number"]
        plate_number = data["plate_number"]
        vehicle_type = data["vehicle_type"]
        vehicle_model = data["vehicle_model"]
        image_link = data.get("image_link", None)  # Optional field

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the given 'name' or 'full_name' already exists in the profile table
            cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s OR full_name = %s", (name, full_name))
            duplicate_check = cursor.fetchone()[0]

            if duplicate_check:
                cursor.close()
                return jsonify({"error": "Profile with this 'name' or 'full_name' already exists."}), 400

            # Insert the new record into the profile table
            insert_sql = """
            INSERT INTO profile (name, full_name, id_number, plate_number, vehicle_type, vehicle_model, image_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                name, full_name, id_number, plate_number, vehicle_type, vehicle_model, image_link
            ))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Profile added successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


## updating records from profile
@app.route('/profile/update', methods=['POST'])
def update_profile():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'name' is provided (we're only using 'name' for this update)
        if 'name' not in data:
            return jsonify({"error": "'name' is required to update a profile."}), 400

        # Extract name and full_name from the data
        name = data["name"]
        full_name = data.get("full_name")  # full_name is optional

        # Validate other fields that are allowed to be updated (fields can be optional)
        fields_to_update = ["id_number", "plate_number", "vehicle_type", "vehicle_model", "role", "phone_number", "image_link"]
        for field in fields_to_update:
            if field in data and data[field] == "":
                return jsonify({"error": f"'{field}' cannot be empty."}), 400

        # Check if the 'profile' table exists
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # SQL to update the profile fields
            update_sql = """
            UPDATE profile
            SET 
                id_number = %s, 
                plate_number = %s, 
                vehicle_type = %s, 
                vehicle_model = %s,
                role = %s,
                phone_number = %s,
                image_link = %s
            """
            
            # If full_name is provided, append it to the SQL and add it to the parameters
            if full_name:
                update_sql += ", full_name = %s"
            
            # Add WHERE clause to match the profile by name
            update_sql += " WHERE name = %s"

            # Prepare parameters for the query
            params = (
                data.get("id_number", ""),
                data.get("plate_number", ""),
                data.get("vehicle_type", ""),
                data.get("vehicle_model", ""),
                data.get("role", ""),
                data.get("phone_number", ""),
                data.get("image_link", ""),
            )

            # Include full_name in the parameters if it exists
            if full_name:
                params += (full_name,)

            # Add the name at the end of the parameters (for WHERE condition)
            params += (name,)

            # Execute the update query with all the updated values
            cursor.execute(update_sql, params)

            # Commit the changes
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Profile updated successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## show the records by name from profile table
@app.route('/profile/<name>', methods=['GET'])
def get_profile_by_name(name):
    try:
        # Check if the 'profile' table exists
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Query the profile table to find the profile by name, including the new fields
            cursor.execute("""
                SELECT id, name, full_name, id_number, plate_number, vehicle_type, vehicle_model, 
                       role, phone_number, image_link, timestamp 
                FROM profile WHERE name = %s
            """, (name,))
            profile = cursor.fetchone()

            if profile:
                # If the profile is found, return it as JSON
                profile_data = {
                    "id": profile[0],
                    "name": profile[1],
                    "full_name": profile[2],
                    "id_number": profile[3],
                    "plate_number": profile[4],
                    "vehicle_type": profile[5],
                    "vehicle_model": profile[6],
                    "role": profile[7],  
                    "phone_number": profile[8], 
                    "image_link": profile[9],
                    "timestamp": profile[10]
                }

                cursor.close()
                return jsonify(profile_data), 200
            else:
                cursor.close()
                return jsonify({"error": f"Profile with name '{name}' not found."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## show all the records from profile table
@app.route('/profile', methods=['GET'])
def get_all_profiles():
    try:
        # Check if the 'profile' table exists
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Query to fetch all profiles from the 'profile' table, including the new fields
            cursor.execute("""
                SELECT id, name, full_name, id_number, plate_number, vehicle_type, vehicle_model, 
                       role, phone_number, image_link, timestamp 
                FROM profile
            """)
            profiles = cursor.fetchall()

            if profiles:
                # If profiles are found, return them as JSON
                profile_list = []
                for profile in profiles:
                    profile_data = {
                        "id": profile[0],
                        "name": profile[1],
                        "full_name": profile[2],
                        "id_number": profile[3],
                        "plate_number": profile[4],
                        "vehicle_type": profile[5],
                        "vehicle_model": profile[6],
                        "role": profile[7],  
                        "phone_number": profile[8], 
                        "image_link": profile[9], 
                        "timestamp": profile[10]
                    }
                    profile_list.append(profile_data)

                cursor.close()
                return jsonify(profile_list), 200
            else:
                cursor.close()
                return jsonify({"message": "No profiles found."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## delete records by name from profile table
@app.route('/profile/delete', methods=['DELETE'])
def delete_profile():
    try:
        # Get the data from the request query parameters
        name = request.args.get('name')

        if not name:
            return jsonify({"error": "'name' is required to delete a profile."}), 400

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Check if the profile with the given name exists
            cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s", (name,))
            profile_exists = cursor.fetchone()[0]

            if profile_exists:
                # Delete the profile by name
                delete_sql = "DELETE FROM profile WHERE name = %s"
                cursor.execute(delete_sql, (name,))

                connection.commit()
                cursor.close()

                return jsonify({"message": "Profile deleted successfully."}), 200
            else:
                cursor.close()
                return jsonify({"error": "Profile not found."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations', methods=['GET'])
def get_violations():
    try:
        # Get the query parameters
        sort = request.args.get('sort', default=None, type=str)
        status = request.args.get('status', default=None, type=str)
        limit = request.args.get('limit', default=None, type=str)

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Start building the SQL query
            query = "SELECT * FROM violations"
            conditions = []
            order_by = None
            limit_clause = None

            # Handle the sorting
            if sort == "latest":
                order_by = "ORDER BY timestamp DESC"
            elif sort == "old":
                order_by = "ORDER BY timestamp ASC"

            # Handle the status filtering
            if status:
                if status in ["active", "new"]:
                    conditions.append(f"status = '{status}'")

            # Handle the limit
            if limit:
                if limit == "all":
                    limit_clause = ""
                elif limit.isdigit() and int(limit) > 0:
                    limit_clause = f"LIMIT {int(limit)}"
                else:
                    limit_clause = "LIMIT 10"  # Default to 10 if an invalid limit is given

            # Combine conditions and order by clauses
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Add order by and limit clauses if they exist
            if order_by:
                query += " " + order_by
            if limit_clause:
                query += " " + limit_clause

            # Execute the query
            cursor.execute(query)
            violations = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # If no violations found, return an empty list
            if not violations:
                return jsonify({"message": "No violations found."}), 200

            # Return the result as JSON
            return jsonify(violations), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations-content', methods=['GET'])
def violations_content():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # SQL to retrieve all data from the 'violations' table
            cursor.execute("SELECT * FROM violations")
            violations = cursor.fetchall()

            # If no data is found in the 'violations' table
            if not violations:
                cursor.close()
                return jsonify({"message": "No violations found."}), 200

            # Format the data as a list of dictionaries
            violation_data = []
            for violation in violations:
                violation_data.append({
                    "id": violation[0],
                    "name": violation[1],
                    "role": violation[2],
                    "status": violation[3],
                    "type": violation[4],
                    "info": violation[5],
                    "timestamp": violation[6].strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as a string
                })

            # Close the cursor
            cursor.close()

            return jsonify({"violations": violation_data}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/all', methods=['GET'])
def get_all_violations():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # SQL query to select all records from the 'violations' table
            cursor.execute("SELECT * FROM violations")
            violations = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # If no violations found, return a message indicating so
            if not violations:
                return jsonify({"message": "No violations found."}), 200

            # Return the result as JSON
            return jsonify(violations), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/add', methods=['POST'])
def add_violation():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Validate that required fields are provided
        required_fields = ["name", "role", "status", "type", "info"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required to add a violation."}), 400

        # Extract values from the request body
        name = data["name"]
        role = data["role"]
        status = data["status"]
        violation_type = data["type"]
        info = data["info"]

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Check if the violation name already exists
            cursor.execute("SELECT COUNT(*) FROM violations WHERE name = %s", (name,))
            name_exists = cursor.fetchone()[0]

            if name_exists:
                return jsonify({"error": "Violation with this name already exists."}), 400

            # SQL to insert the new violation record (MySQL will handle the timestamp)
            insert_sql = """
            INSERT INTO violations (name, role, status, type, info)
            VALUES (%s, %s, %s, %s, %s);
            """

            # Execute the insertion
            cursor.execute(insert_sql, (name, role, status, violation_type, info))

            # Commit the changes to the database
            connection.commit()
            cursor.close()

            return jsonify({"message": "Violation record added successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/delete', methods=['DELETE'])
def delete_violations():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that the 'name' field is provided
        if "name" not in data:
            return jsonify({"error": "'name' is required."}), 400

        name = data["name"]
        status = data.get("status")  # Status is optional

        # Check if the 'violations' table exists
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Build the delete query
            if status:
                # If 'status' is provided, delete violations where both 'name' and 'status' match
                delete_sql = "DELETE FROM violations WHERE name = %s AND status = %s"
                cursor.execute(delete_sql, (name, status))
            else:
                # If 'status' is not provided, delete violations where only 'name' matches
                delete_sql = "DELETE FROM violations WHERE name = %s"
                cursor.execute(delete_sql, (name,))

            # Commit the changes to the database
            db_connection.commit()

            # Get the number of rows affected
            rows_affected = cursor.rowcount
            cursor.close()

            if rows_affected > 0:
                return jsonify({"message": f"{rows_affected} violation(s) deleted successfully."}), 200
            else:
                return jsonify({"message": "No violations found matching the criteria."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/<name>', methods=['GET'])
def get_violations_by_name(name):
    try:
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Query the violations table to find the violations by name, ordered by timestamp (latest to oldest)
            cursor.execute("""
                SELECT id, name, role, status, type, info, timestamp 
                FROM violations 
                WHERE name = %s
                ORDER BY timestamp DESC
            """, (name,))
            violations = cursor.fetchall()

            if violations:
                # Prepare the list of violations with the correct columns
                violation_data = []
                for violation in violations:
                    violation_data.append({
                        "id": violation[0],
                        "name": violation[1],
                        "role": violation[2],
                        "status": violation[3],
                        "type": violation[4],
                        "info": violation[5],
                        "timestamp": violation[6].strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as a string
                    })

                cursor.close()
                return jsonify(violation_data), 200
            else:
                cursor.close()
                return jsonify({"error": f"No violations found for name '{name}'."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/delete/<int:violation_id>', methods=['DELETE'])
def delete_violation_by_id(violation_id):
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Delete the violation with the specified ID
            delete_sql = "DELETE FROM violations WHERE id = %s"
            cursor.execute(delete_sql, (violation_id,))

            # Commit the changes
            connection.commit()

            rows_affected = cursor.rowcount
            cursor.close()

            if rows_affected > 0:
                return jsonify({"message": f"Violation with ID {violation_id} deleted successfully."}), 200
            else:
                return jsonify({"message": f"No violation found with ID {violation_id}."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/violations/update-status/<int:violation_id>', methods=['PUT'])
def update_violation_status(violation_id):
    try:
        # Parse the request data
        data = request.get_json()
        new_status = data.get("status")

        # Validate the input
        if not new_status:
            return jsonify({"error": "'status' field is required."}), 400

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Update the status for the given ID
            update_sql = "UPDATE violations SET status = %s WHERE id = %s"
            cursor.execute(update_sql, (new_status, violation_id))

            connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()

            if rows_affected > 0:
                return jsonify({"message": f"Status for violation ID {violation_id} updated to '{new_status}'."}), 200
            else:
                return jsonify({"message": f"No violation found with ID {violation_id}."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/violations/rfid/add', methods=['POST'])
def add_violation_and_update_rfid():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Validate required fields
        required_fields = ["name", "role", "status", "type", "info"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required to add a violation."}), 400

        name = data["name"]
        role = data["role"]
        status = data["status"]
        violation_type = data["type"]
        info = data["info"]

        # Get DB connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Check if the violation name already exists
            cursor.execute("SELECT COUNT(*) FROM violations WHERE name = %s", (name,))
            name_exists = cursor.fetchone()[0]

            if name_exists:
                return jsonify({"error": "Violation with this name already exists."}), 400

            # Insert new violation
            insert_sql = """
            INSERT INTO violations (name, role, status, type, info)
            VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(insert_sql, (name, role, status, violation_type, info))

            # Check for matching user by name
            cursor.execute("SELECT rfid FROM users WHERE name = %s", (name,))
            user = cursor.fetchone()

            if user:
                current_rfid = user[0] or ""
                updated_rfid = f"{current_rfid}-violate"

                # Update the user's RFID value
                update_sql = "UPDATE users SET rfid = %s WHERE name = %s"
                cursor.execute(update_sql, (updated_rfid, name))

            # Commit changes and close cursor
            connection.commit()
            cursor.close()

            return jsonify({"message": "Violation added and RFID updated (if user found)."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/violations/rfid/resolve/byid', methods=['PUT'])
def resolve_violation_and_update_rfid_by_id():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Validate that 'id' field is provided
        if "id" not in data:
            return jsonify({"error": "'id' field is required."}), 400
        
        violation_id = data["id"]

        # Get DB connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Update the violation status to "resolved"
            update_sql = "UPDATE violations SET status = 'resolved' WHERE id = %s"
            cursor.execute(update_sql, (violation_id,))

            # Get the name from the updated violation record
            cursor.execute("SELECT name FROM violations WHERE id = %s", (violation_id,))
            violation = cursor.fetchone()

            if violation:
                name = violation[0]

                # Check if user exists in the 'users' table
                cursor.execute("SELECT rfid FROM users WHERE name = %s", (name,))
                user = cursor.fetchone()

                if user:
                    current_rfid = user[0] or ""
                    # Remove the '-violate' suffix if it exists
                    if current_rfid.endswith("-violate"):
                        updated_rfid = current_rfid[:-8]  # Remove the '-violate' suffix
                        
                        # Update the user's RFID value
                        update_rfid_sql = "UPDATE users SET rfid = %s WHERE name = %s"
                        cursor.execute(update_rfid_sql, (updated_rfid, name))

            # Commit changes and close cursor
            connection.commit()
            cursor.close()

            return jsonify({"message": f"Violation with ID {violation_id} resolved and RFID updated (if user found)."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/rfid/resolve/byname', methods=['PUT'])
def resolve_violation_and_update_rfid_by_name():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Validate that 'name' field is provided
        if "name" not in data:
            return jsonify({"error": "'name' field is required."}), 400
        
        violation_name = data["name"]

        # Get DB connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Update the violation status to "resolved" by name
            update_sql = "UPDATE violations SET status = 'resolved' WHERE name = %s"
            cursor.execute(update_sql, (violation_name,))

            # Get the name from the updated violation record
            cursor.execute("SELECT name FROM violations WHERE name = %s", (violation_name,))
            violation = cursor.fetchone()

            if violation:
                name = violation[0]

                # Check if user exists in the 'users' table
                cursor.execute("SELECT rfid FROM users WHERE name = %s", (name,))
                user = cursor.fetchone()

                if user:
                    current_rfid = user[0] or ""
                    # Remove the '-violate' suffix if it exists
                    if current_rfid.endswith("-violate"):
                        updated_rfid = current_rfid[:-8]  # Remove the '-violate' suffix
                        
                        # Update the user's RFID value
                        update_rfid_sql = "UPDATE users SET rfid = %s WHERE name = %s"
                        cursor.execute(update_rfid_sql, (updated_rfid, name))

            # Commit changes and close cursor
            connection.commit()
            cursor.close()

            return jsonify({"message": f"Violation with name '{violation_name}' resolved and RFID updated (if user found)."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/violations/exclude-resolved', methods=['GET'])
def get_violations_excluding_resolved():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # SQL query to get all violations excluding those with status 'resolved'
            cursor.execute("SELECT * FROM violations WHERE status != 'resolved'")
            violations = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # If no violations found, return an empty list
            if not violations:
                return jsonify({"message": "No unresolved violations found."}), 200

            # Return the result as JSON
            return jsonify(violations), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/notifications', methods=['GET'])
def get_notifications():
    try:
        # Get the query parameters
        sort = request.args.get('sort', default=None, type=str)
        status = request.args.get('status', default=None, type=str)
        limit = request.args.get('limit', default=None, type=str)

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Start building the SQL query
            query = "SELECT * FROM notifications"
            conditions = []
            order_by = None
            limit_clause = None

            # Handle the sorting
            if sort == "latest":
                order_by = "ORDER BY timestamp DESC"
            elif sort == "old":
                order_by = "ORDER BY timestamp ASC"

            # Handle the status filtering
            if status:
                if status in ["active", "new"]:
                    conditions.append(f"status = '{status}'")

            # Handle the limit
            if limit:
                if limit == "all":
                    limit_clause = ""
                elif limit.isdigit() and int(limit) > 0:
                    limit_clause = f"LIMIT {int(limit)}"
                else:
                    limit_clause = "LIMIT 10"  # Default to 10 if an invalid limit is given

            # Combine conditions and order by clauses
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Add order by and limit clauses if they exist
            if order_by:
                query += " " + order_by
            if limit_clause:
                query += " " + limit_clause

            # Execute the query
            cursor.execute(query)
            notifications = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # If no notifications found, return an empty list
            if not notifications:
                return jsonify({"message": "No notifications found."}), 200

            # Return the result as JSON
            return jsonify(notifications), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/notifications/add', methods=['POST'])
def add_notification():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate the required fields in the request body
        required_fields = ["uniqueId", "role", "status", "message"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required."}), 400

        # Extract the fields from the request data
        uniqueId = data["uniqueId"]
        role = data["role"]
        status = data["status"]
        message = data["message"]

        # Ensure that the status is either 'active' or 'new'
        if status not in ["active", "new"]:
            return jsonify({"error": "'status' must be either 'active' or 'new'."}), 400

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # SQL to insert a new record into the notifications table
            insert_sql = """
            INSERT INTO notifications (uniqueId, role, status, message)
            VALUES (%s, %s, %s, %s)
            """

            # Execute the insert query
            cursor.execute(insert_sql, (uniqueId, role, status, message))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Notification added successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/notifications/delete/<name>', methods=['DELETE'])
def delete_notifications_by_name(name):
    try:
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # SQL query to delete all notifications for the given name (uniqueId)
            cursor.execute("""
                DELETE FROM notifications 
                WHERE uniqueId = %s
            """, (name,))

            # Commit the changes to the database
            connection.commit()

            # Check how many records were deleted
            if cursor.rowcount > 0:
                cursor.close()
                return jsonify({"message": f"All notifications for '{name}' deleted successfully."}), 200
            else:
                cursor.close()
                return jsonify({"message": f"No notifications found for '{name}' to delete."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/notifications/all', methods=['GET'])
def get_all_notifications():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # SQL query to select all records from the 'notifications' table
            cursor.execute("SELECT * FROM notifications")
            notifications = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # If no notifications found, return a message indicating so
            if not notifications:
                return jsonify({"message": "No notifications found."}), 200

            # Return the result as JSON
            return jsonify(notifications), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/notifications/<name>', methods=['GET'])
def get_notifications_by_name(name):
    try:
        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Query the notifications table to find notifications by uniqueId (name), ordered by timestamp (latest to oldest)
            cursor.execute("""
                SELECT id, uniqueId, role, status, message, timestamp 
                FROM notifications 
                WHERE uniqueId = %s
                ORDER BY timestamp DESC
            """, (name,))
            notifications = cursor.fetchall()

            if notifications:
                # Prepare the list of notifications
                notification_data = []
                for notification in notifications:
                    notification_data.append({
                        "id": notification[0],
                        "uniqueId": notification[1],
                        "role": notification[2],
                        "status": notification[3],
                        "message": notification[4],
                        "timestamp": notification[5].strftime('%a, %d %b %Y %H:%M:%S GMT')  # Format timestamp as in your example
                    })

                cursor.close()
                return jsonify(notification_data), 200
            else:
                cursor.close()
                return jsonify({"error": f"No notifications found for '{name}'."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/parking-history', methods=['GET'])
def get_parking_history():
    try:
        # Get the query parameters
        sort = request.args.get('sort', default=None, type=str)
        status = request.args.get('status', default=None, type=str)
        limit = request.args.get('limit', default=None, type=str)

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Start building the SQL query
            query = "SELECT * FROM parking_history"
            conditions = []
            order_by = None
            limit_clause = None

            # Handle the sorting
            if sort == "latest":
                order_by = "ORDER BY timestamp DESC"
            elif sort == "old":
                order_by = "ORDER BY timestamp ASC"

            # Handle the status filtering
            if status:
                if status in ["active", "completed", "pending"]:  # Adjust status values based on your needs
                    conditions.append(f"status = '{status}'")

            # Handle the limit
            if limit:
                if limit == "all":
                    limit_clause = ""
                elif limit.isdigit() and int(limit) > 0:
                    limit_clause = f"LIMIT {int(limit)}"
                else:
                    limit_clause = "LIMIT 10"  # Default to 10 if an invalid limit is given

            # Combine conditions and order by clauses
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # Add order by and limit clauses if they exist
            if order_by:
                query += " " + order_by
            if limit_clause:
                query += " " + limit_clause

            # Execute the query
            cursor.execute(query)
            parking_history = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # If no parking history found, return an empty list
            if not parking_history:
                return jsonify({"message": "No parking history found."}), 200

            # Format the data as a list of dictionaries
            history_data = []
            for record in parking_history:
                history_data.append({
                    "id": record[0],
                    "name": record[1],
                    "role": record[2],
                    "status": record[3],
                    "type": record[4],
                    "info": record[5],
                    "slotname": record[6],
                    "timestamp": record[7].strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp as a string
                })

            # Return the result as JSON
            return jsonify(history_data), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

## show all the records of the 'parking_history' table
@app.route('/parking-history-content', methods=['GET'])
def get_parking_history_content():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        
        if cursor:
            # Execute the SQL query to fetch all records from the 'parking_history' table
            cursor.execute("SELECT * FROM parking_history")
            records = cursor.fetchall()
            
            # Prepare the list to return in JSON format
            parking_history_list = []
            for record in records:
                # Convert each record to a dictionary (adjust the keys as per your table structure)
                parking_history_list.append({
                    "id": record[0],
                    "name": record[1],
                    "role": record[2],
                    "status": record[3],
                    "type": record[4],
                    "info": record[5],
                    "slotname": record[6],
                    "timestamp": record[7]
                })
            
            # Close the cursor
            cursor.close()
            
            # Return the records as a JSON response
            return jsonify({"parking_history": parking_history_list}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/parking-history/add', methods=['POST'])
def add_parking_history():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500


        # Validate the required fields
        required_fields = ["name", "role", "status", "type", "info", "slotname"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required."}), 400

        name = data["name"]
        role = data["role"]
        status = data["status"]
        type = data["type"]
        info = data["info"]
        slotname = data["slotname"]

        # Check if the 'parking_history' table exists
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()


        if cursor:
            # Insert the new record into the parking_history table
            insert_sql = """
            INSERT INTO parking_history (name, role, status, type, info, slotname)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (name, role, status, type, info, slotname))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Parking history added successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/parking-history/<name>', methods=['GET'])
def get_parking_history_by_name(name):
    try:

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Check if the 'parking_history' table exists
        # cursor = get_cursor()

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Query the parking_history table to find records by name, ordered by timestamp (latest to oldest)
            cursor.execute("""
                SELECT id, name, role, status, type, info, slotname, timestamp 
                FROM parking_history 
                WHERE name = %s 
                ORDER BY timestamp DESC
            """, (name,))
            parking_history = cursor.fetchall()

            if parking_history:
                # If records are found, return them as JSON
                history_data = []
                for record in parking_history:
                    history_data.append({
                        "id": record[0],
                        "name": record[1],
                        "role": record[2],
                        "status": record[3],
                        "type": record[4],
                        "info": record[5],
                        "slotname": record[6],
                        "timestamp": record[7].strftime('%Y-%m-%d %H:%M:%S')  # Format timestamp
                    })

                cursor.close()
                return jsonify(history_data), 200
            else:
                cursor.close()
                return jsonify({"error": f"No parking history records found for '{name}'."}), 404
        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/parking-history/delete-all', methods=['DELETE'])
def delete_all_parking_history():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Execute delete query
            cursor.execute("DELETE FROM parking_history")
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "All parking history records deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/parking-history/delete/<name>', methods=['DELETE'])
def delete_parking_history_by_name(name):
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Delete all records with the specified name
            cursor.execute("DELETE FROM parking_history WHERE name = %s", (name,))
            db_connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                return jsonify({"message": f"All records for '{name}' deleted successfully."}), 200
            else:
                return jsonify({"message": f"No records found for '{name}'."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/parking-history/delete/id/<int:id>', methods=['DELETE'])
def delete_parking_history_by_id(id):
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Delete the record with the specified id
            cursor.execute("DELETE FROM parking_history WHERE id = %s", (id,))
            db_connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                return jsonify({"message": f"Record with id {id} deleted successfully."}), 200
            else:
                return jsonify({"message": f"No record found with id {id}."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/parking-history/delete/status/<status>', methods=['DELETE'])
def delete_parking_history_by_status(status):
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Delete records matching the given status
            cursor.execute("DELETE FROM parking_history WHERE status = %s", (status,))
            db_connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()

            if affected_rows > 0:
                return jsonify({"message": f"All records with status '{status}' deleted successfully."}), 200
            else:
                return jsonify({"message": f"No records found with status '{status}'."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/messages/all', methods=['GET'])
def get_all_messages():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor(dictionary=True)  # dictionary=True for JSON-style records

        if cursor:
            # SQL query to select all records from the 'message' table
            cursor.execute("SELECT * FROM message")
            messages = cursor.fetchall()

            cursor.close()

            if not messages:
                return jsonify({"message": "No messages found."}), 200

            return jsonify(messages), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/messages/<name>', methods=['GET'])
def get_messages_by_name(name):
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Query the message table to find records by name, ordered by timestamp (latest to oldest)
            cursor.execute("""
                SELECT id, name, status, type, `group`, sender, receiver, message, timestamp
                FROM message
                WHERE name = %s
                ORDER BY timestamp DESC
            """, (name,))
            message_records = cursor.fetchall()

            if message_records:
                # Format and return results
                message_data = []
                for record in message_records:
                    message_data.append({
                        "id": record[0],
                        "name": record[1],
                        "status": record[2],
                        "type": record[3],
                        "group": record[4],
                        "sender": record[5],
                        "receiver": record[6],
                        "message": record[7],
                        "timestamp": record[8]  # No formatting
                    })

                cursor.close()
                return jsonify(message_data), 200
            else:
                cursor.close()
                return jsonify({"error": f"No messages found for '{name}'."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/messages/add', methods=['POST'])
def add_message():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500

        # Validate the required fields
        required_fields = ["name", "status", "type", "group", "sender", "receiver", "message"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required."}), 400

        name = data["name"]
        status = data["status"]
        type = data["type"]
        group = data["group"]
        sender = data["sender"]
        receiver = data["receiver"]
        message_text = data["message"]

        # Get a database connection and cursor
        connection = get_connection()
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # Insert the new message record into the message table
            insert_sql = """
            INSERT INTO message (name, status, type, `group`, sender, receiver, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (name, status, type, group, sender, receiver, message_text))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Message added successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/message/update', methods=['PUT'])
def update_message():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'name' and 'id' are provided
        if 'name' not in data or 'id' not in data:
            return jsonify({"error": "'name' and 'id' are required to update a message."}), 400

        # Extract the fields from the data
        name = data["name"]
        message_id = data["id"]

        # Validate other fields that can be updated (fields can be optional)
        fields_to_update = ["status", "type", "group", "sender", "receiver", "message"]
        for field in fields_to_update:
            if field in data and data[field] == "":
                return jsonify({"error": f"'{field}' cannot be empty."}), 400

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # Build the update SQL query
            update_sql = """
            UPDATE message
            SET 
                status = %s, 
                type = %s, 
                `group` = %s, 
                sender = %s,
                receiver = %s,
                message = %s
            WHERE id = %s AND name = %s
            """
            
            # Prepare parameters for the query
            params = (
                data.get("status", ""),
                data.get("type", ""),
                data.get("group", ""),
                data.get("sender", ""),
                data.get("receiver", ""),
                data.get("message", ""),
                message_id,
                name
            )

            # Execute the update query
            cursor.execute(update_sql, params)

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Message updated successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/message/delete', methods=['DELETE'])
def delete_message():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'name' and 'id' are provided
        if 'name' not in data or 'id' not in data:
            return jsonify({"error": "'name' and 'id' are required to delete a message."}), 400

        # Extract name and id from the data
        name = data["name"]
        message_id = data["id"]

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500
        
        cursor = connection.cursor()

        if cursor:
            # SQL to delete the message record by name and id
            delete_sql = "DELETE FROM message WHERE id = %s AND name = %s"

            # Execute the delete query
            cursor.execute(delete_sql, (message_id, name))

            # Check if any rows were affected (i.e., record exists and was deleted)
            if cursor.rowcount == 0:
                return jsonify({"error": "Message not found for the given name and id."}), 404

            # Commit the changes to the database
            connection.commit()
            cursor.close()

            return jsonify({"message": "Message deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)

@app.route('/message/delete-by-name', methods=['DELETE'])
def delete_messages_by_name():
    try:
        # Get the data from the request body
        data = request.get_json()

        # Validate that 'name' is provided
        if 'name' not in data:
            return jsonify({"error": "'name' is required to delete messages."}), 400

        name = data["name"]

        # Get a database connection and cursor
        connection = get_connection()  # Get the MySQL connection
        if connection is None:
            return jsonify({"error": "Failed to connect to the database"}), 500

        cursor = connection.cursor()

        if cursor:
            # SQL to delete all messages by name
            delete_sql = "DELETE FROM message WHERE name = %s"
            cursor.execute(delete_sql, (name,))

            if cursor.rowcount == 0:
                return jsonify({"message": f"No messages found for name '{name}'."}), 200

            # Commit the changes to the database
            connection.commit()
            cursor.close()

            return jsonify({"message": f"All messages for '{name}' deleted successfully."}), 200

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


# Route to reconnect to MySQL
@app.route('/reconnect-mysql', methods=['GET'])
def reconnect_mysql():
    if reconnect_to_mysql():
        return jsonify({"message": "Reconnected to MySQL successfully!"}), 200
    else:
        return jsonify({"error": "Failed to reconnect to MySQL."}), 500


# Check if the file "dev" exists
if not os.path.exists('dev'):
    # Execute this route if "dev" is not present and MySQL is available
    @app.route('/', methods=['GET'])
    def index():
        if is_mysql_available():
            return jsonify({
                "message": {
                    "status": "ok",
                    "developer": "kayven",
                    "email": "yvendee2020@gmail.com"
                }
            })
        else:
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
else:
    # Execute this route if "dev" exists
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({"message": "Welcome to the appfinity API"})

if __name__ == '__main__':
    app.run(debug=True)
