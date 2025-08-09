# datacreation.py
# This script sets up the necessary database and tables for the loan prediction application.
import pymysql

def create_database():
    """Creates the database if it doesn't already exist."""
    try:
        connection = pymysql.connect(host="localhost", user="root", password="")
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS loan_prediction_system")
        print("Database 'loan_prediction_system' created or already exists.")
        connection.close()
    except pymysql.err.OperationalError as e:
        print(f"Error connecting to MySQL: {e}")
        print("Please ensure your MySQL server (like XAMPP) is running.")

def create_tables():
    """Creates the tables for user data, admin data, and predictions."""
    try:
        connection = pymysql.connect(host="localhost", user="root", password="", database="loan_prediction_system")
        cursor = connection.cursor()

        # Table for user sign-in information
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS USER_DATA ( 
                USER_ID VARCHAR(100) NOT NULL PRIMARY KEY,
                EMAILADDRESS VARCHAR(100) NOT NULL,
                MOBILE_NUMBER VARCHAR(100) NOT NULL,
                FULL_NAME VARCHAR(100) NOT NULL,
                PASSWORD VARCHAR(50) NOT NULL
            );
        """)
        print("Table 'USER_DATA' created or already exists.")

        # Table for storing prediction results with new features
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction (
                ID INT AUTO_INCREMENT PRIMARY KEY,
                First_Name VARCHAR(50),
                Last_Name VARCHAR(50),
                Gender INT,
                Martial_Status INT,
                Number_of_dependents INT,
                Education INT,
                Employment_status INT,
                Property_Area INT,
                Credit_History FLOAT,
                CIBIL_Score INT,
                Income FLOAT,
                Co_Applicant_Income FLOAT,
                Loan_Amount FLOAT,
                Loan_Duration FLOAT,
                prediction VARCHAR(20),
                Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Table 'prediction' created or already exists.")
        
        # Table for admin login
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_data (
                ADMIN_ID VARCHAR(50) NOT NULL PRIMARY KEY,
                PASSWORD VARCHAR(50) NOT NULL
            );
        """)
        print("Table 'admin_data' created or already exists.")

        # Insert a default admin if one doesn't exist
        cursor.execute("SELECT * FROM admin_data WHERE ADMIN_ID = 'admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO admin_data (ADMIN_ID, PASSWORD) VALUES ('admin', 'admin123')")
            connection.commit()
            print("Default admin user ('admin'/'admin123') created.")

        connection.close()
    except pymysql.err.OperationalError as e:
        print(f"Error connecting to database 'loan_prediction_system': {e}")
        print("Please run create_database() first.")

if __name__ == '__main__':
    print("Setting up the database...")
    create_database()
    create_tables()
    print("\nDatabase setup complete!")
    print("You can now run 'main.py' to start the application.")
