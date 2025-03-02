from flask import Flask, jsonify, request
# from dotenv import load_dotenv
import mysql.connector
from datetime import datetime
import os
from swagger.swaggerui import setup_swagger

app = Flask(__name__)
app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

# Set up Swagger
setup_swagger(app)

# Load environment variables from .env file
# load_dotenv()

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
        print(f"Error connecting to MySQL: {e}")
        db_connection = None
else:
    print("MYSQL_DETAILS environment variable is not set.")
    db_connection = None


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

@app.route('/delete-table-datawatch/', methods=['GET'])
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


# List of users to insert 
users_db = [
    {
        "name": "testuser",
        "password_hash": "12345",
        "role": "admin", 
        "email": "-",
        "token": "-",
    },
    {
        "name": "guestuser",
        "password_hash": "12345",
        "role": "guest", 
        "email": "-",
        "token": "-",
    }
]

@app.route('/insert-data-to-users', methods=['GET'])
def insert_users():
    try:

        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()
        
        if cursor:
            # Prepare the SQL statement to insert data into 'users' table
            insert_sql = """
            INSERT INTO users (name, password_hash, role, email, token, timestamp)
            VALUES (%s, %s, %s, %s, %s, NOW());
            """
            
            # Iterate over users_db to insert users one by one
            for user in users_db:
                # Check if the user with the same name already exists
                cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (user['name'],))
                user_exists = cursor.fetchone()[0]
                
                if user_exists:
                    return jsonify({"error": f"User with name '{user['name']}' already exists."}), 400
                
                # Execute the insert query for the user if the name doesn't exist
                cursor.execute(insert_sql, (user['name'], user['password_hash'], user['role'], user['email'], user['token']))
            
            # Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "Users inserted successfully."}), 200
        
        else:
            return jsonify({"error": "Database connection not available"}), 500
    
    except mysql.connector.Error as e:
        return handle_mysql_error(e)


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

## insert the initial records for stores
@app.route('/insert-data-to-stores', methods=['GET'])
def insert_stores():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        

        # Get a database cursor
        cursor = get_cursor()

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


profile_db = [
    {
        "name": "testuser",
        "full_name": "Test User",
        "id_number": "TUPM-21-25344",
        "plate_number": "453QUM",
        "vehicle_type": "MOTORCYCLE",
        "vehicle_model": "HONDA CLICK"
    },
    # Add more records here if needed
]

## insert the initial records for profile
@app.route('/insert-data-to-profile', methods=['GET'])
def bulk_insert_profiles():
    try:
        # Check if the 'profile' table exists
        cursor = get_cursor()

        if cursor:
            # Iterate over the profile_db list to insert each record into the profile table
            for profile in profile_db:
                name = profile["name"]
                full_name = profile["full_name"]
                id_number = profile["id_number"]
                plate_number = profile["plate_number"]
                vehicle_type = profile["vehicle_type"]
                vehicle_model = profile["vehicle_model"]

                # Check if the profile already exists based on 'name' or 'full_name'
                cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s OR full_name = %s", (name, full_name))
                profile_exists = cursor.fetchone()[0]

                if profile_exists:
                    continue  # Skip the current record if it already exists

                # Insert new profile record into the 'profile' table
                insert_sql = """
                INSERT INTO profile (name, full_name, id_number, plate_number, vehicle_type, vehicle_model)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (name, full_name, id_number, plate_number, vehicle_type, vehicle_model))

            # Commit the changes to the database
            db_connection.commit()
            cursor.close()

            return jsonify({"message": "Profiles inserted successfully."}), 200

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

## show the all the records of table 'users'
@app.route('/users', methods=['GET'])
def get_users():
    try:
        # Check if MySQL is available
        if not is_mysql_available():
            return jsonify({"error": "MySQL database not responding, please check the database service"}), 500
        
        # Get a database cursor
        cursor = get_cursor()
        
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
        if "name" not in data or "password_hash" not in data:
            return jsonify({"error": "Both 'name' and 'password_hash' are required fields."}), 400
        
        # Add validation for the 'role' field (if required)
        role = data.get("role", "")  # Default to empty string if not provided

        # Validate role if necessary, for example, checking if it’s one of a list of valid roles
        valid_roles = ["admin", "user", "guest"]  # Example of valid roles
        if role and role not in valid_roles:
            return jsonify({"error": f"Invalid role. Valid roles are {', '.join(valid_roles)}."}), 400
        
        name = data["name"]
        password_hash = data["password_hash"]
        
        # Get a database cursor
        cursor = get_cursor()

        if cursor:
            # Check if the user with the same name already exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (name,))
            user_exists = cursor.fetchone()[0]
            
            if user_exists:
                cursor.close()
                return jsonify({"error": f"User with name '{name}' already exists."}), 400

            # Prepare the SQL query to insert a new user into the 'users' table
            insert_sql = """
            INSERT INTO users (name, password_hash, role, email, status, token, timestamp)
            VALUES (%s, %s, %s, '', '', '', NOW());
            """
            
            # Execute the insert query, including the role
            cursor.execute(insert_sql, (name, password_hash, role))
            
            # Commit the changes to the database
            db_connection.commit()
            cursor.close()
            
            return jsonify({"message": "User added successfully."}), 201
        
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
        
        # Get a database cursor
        cursor = get_cursor()

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
        
        # Get a database cursor
        cursor = get_cursor()

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
        cursor = get_cursor()

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
        valid_slots = [f"slot{i}" for i in range(1, 17)]
        if slot not in valid_slots:
            return jsonify({"error": f"Invalid slot name. Valid slots are: {', '.join(valid_slots)}."}), 400
        
        # Get a database cursor
        cursor = get_cursor()

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
        cursor = get_cursor()

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

        # Check if the 'profile' table exists
        cursor = get_cursor()

        if cursor:
            # Check if the given 'name' or 'full_name' already exists in the profile table
            cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s OR full_name = %s", (name, full_name))
            duplicate_check = cursor.fetchone()[0]

            if duplicate_check:
                cursor.close()
                return jsonify({"error": "Profile with this 'name' or 'full_name' already exists."}), 400

            # Insert the new record into the profile table
            insert_sql = """
            INSERT INTO profile (name, full_name, id_number, plate_number, vehicle_type, vehicle_model)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (name, full_name, data["id_number"], data["plate_number"], data["vehicle_type"], data["vehicle_model"]))

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
        fields_to_update = ["id_number", "plate_number", "vehicle_type", "vehicle_model"]
        for field in fields_to_update:
            if field in data and data[field] == "":
                return jsonify({"error": f"'{field}' cannot be empty."}), 400

        # Check if the 'profile' table exists
        cursor = get_cursor()

        if cursor:
            # Prepare the condition to search by 'name'
            condition = "name = %s"
            param = (name,)

            # Check if the profile exists based on the 'name'
            cursor.execute("SELECT COUNT(*) FROM profile WHERE " + condition, param)
            profile_exists = cursor.fetchone()[0]

            if not profile_exists:
                cursor.close()
                return jsonify({"error": f"Profile with name '{name}' does not exist."}), 404

            # SQL to update the profile fields, including full_name
            update_sql = """
            UPDATE profile
            SET 
                id_number = %s, 
                plate_number = %s, 
                vehicle_type = %s, 
                vehicle_model = %s,
                full_name = %s
            WHERE name = %s
            """
            
            # Execute the update query with all the updated values
            cursor.execute(update_sql, (
                data.get("id_number", ""),
                data.get("plate_number", ""),
                data.get("vehicle_type", ""),
                data.get("vehicle_model", ""),
                full_name if full_name else "",  # Only update full_name if provided
                name
            ))

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
        cursor = get_cursor()

        if cursor:
            # Query the profile table to find the profile by name
            cursor.execute("SELECT id, name, full_name, id_number, plate_number, vehicle_type, vehicle_model, timestamp FROM profile WHERE name = %s", (name,))
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
                    "timestamp": profile[7]
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
        cursor = get_cursor()

        if cursor:
            # Query to fetch all profiles from the 'profile' table
            cursor.execute("SELECT id, name, full_name, id_number, plate_number, vehicle_type, vehicle_model, timestamp FROM profile")
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
                        "timestamp": profile[7]
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

## delete records by name or fullname from profile table
@app.route('/profile/delete', methods=['DELETE'])
def delete_profile():
    try:
        # Get the data from the request query parameters
        data = request.args
        name = data.get('name')
        full_name = data.get('full_name')

        if not name and not full_name:
            return jsonify({"error": "'name' or 'full_name' is required to delete a profile."}), 400

        # Check if the 'profile' table exists
        cursor = get_cursor()

        if cursor:
            # Determine which column to use for deletion: 'name' or 'full_name'
            if name:
                cursor.execute("SELECT COUNT(*) FROM profile WHERE name = %s", (name,))
            else:
                cursor.execute("SELECT COUNT(*) FROM profile WHERE full_name = %s", (full_name,))

            profile_exists = cursor.fetchone()[0]

            if profile_exists:
                # Delete the profile based on the available identifier (name or full_name)
                if name:
                    delete_sql = "DELETE FROM profile WHERE name = %s"
                    cursor.execute(delete_sql, (name,))
                else:
                    delete_sql = "DELETE FROM profile WHERE full_name = %s"
                    cursor.execute(delete_sql, (full_name,))

                db_connection.commit()
                cursor.close()

                return jsonify({"message": "Profile deleted successfully."}), 200
            else:
                cursor.close()
                return jsonify({"error": "Profile not found."}), 404

        else:
            return jsonify({"error": "Database connection not available"}), 500

    except mysql.connector.Error as e:
        return handle_mysql_error(e)


@app.route('/', methods=['GET'])
def index():
    if is_mysql_available():
        return jsonify({"message": "Welcome to the appfinity API"})
    else:
        return jsonify({"error": "MySQL database not responding, please check the database service"}), 500


# @app.route('/', methods=['GET'])
# def index():
#     return jsonify({"message": "Welcome to the appfinity API"})

if __name__ == '__main__':
    app.run(debug=True)
