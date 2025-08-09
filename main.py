# main.py
# Import necessary libraries
import pymysql.connections
from flask import Flask, render_template, request, redirect, session
import os
import pickle
import hashlib
import numpy as np
import pandas as pd

# Initialize the Flask application
app = Flask(__name__)

# Load the trained machine learning model and scaler
try:
    model = pickle.load(open('model/loan_eligibility_model.pkl', 'rb'))
    scaler = pickle.load(open('model/scaler.pkl', 'rb'))
except FileNotFoundError:
    print("Error: Model or scaler file not found. Please run model_training.ipynb first.")
    model = None
    scaler = None

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Database connection setup
try:
    connection = pymysql.connect(host="localhost", user="root", password="", database="loan_prediction_system")
    cursor = connection.cursor()
except pymysql.err.OperationalError as e:
    print(f"Database connection failed: {e}")
    connection = None
    cursor = None

# --- User and Admin Authentication Routes ---

@app.route('/')
def login():
    """Renders the user login page."""
    return render_template('index.html', show_login=True)

@app.route('/signup_page')
def signup_page():
    """Renders the user signup page."""
    return render_template('index.html', show_signup=True)

@app.route('/adminlogin')
def adminlogin():
    """Renders the admin login page."""
    return render_template('adminlogin.html')

@app.route('/login_validation', methods=["POST"])
def login_validation():
    """Validates user login credentials."""
    if not cursor:
        return "Database connection not available."
    userid = request.form.get('userid')
    password = request.form.get('password')
    
    val = (userid,)
    val_sql = 'SELECT * FROM user_data WHERE USER_ID = %s'
    cursor.execute(val_sql, val)
    user_data = cursor.fetchall()
    
    if user_data:
        user_record = list(user_data[0])
        md5 = hashlib.md5(str(password).encode('utf-8'))
        if str(md5.hexdigest()) == user_record[-1]:
            session['userid'] = user_record[0]
            return redirect('/home')
    
    return render_template('index.html', show_login=True, prediction_text="Invalid username or password.")

@app.route('/add_user', methods=['POST'])
def add_user():
    """Handles new user registration."""
    if not cursor:
        return "Database connection not available."
    # --- (Existing user creation logic remains the same) ---
    userid = request.form.get('userid')
    email = request.form.get('email')
    mobile_number = request.form.get('mobile_number')
    fullname = request.form.get('fullname')
    password = request.form.get('password')
    con_password = request.form.get('con_password')

    if password != con_password:
        return render_template('index.html', show_signup=True, prediction_text="Passwords do not match.")

    md5 = hashlib.md5(str(password).encode('utf-8'))
    password_hash = md5.hexdigest()
    
    val = (userid, email, mobile_number, fullname, password_hash)
    insert_sql = "INSERT INTO user_data (USER_ID, EMAILADDRESS, MOBILE_NUMBER, FULL_NAME, PASSWORD) VALUES (%s, %s, %s, %s, %s)"
    
    try:
        cursor.execute(insert_sql, val)
        connection.commit()
        return redirect('/')
    except pymysql.err.IntegrityError:
        return render_template('index.html', show_signup=True, prediction_text="Username already exists.")


@app.route('/admin_validation', methods=["POST"])
def admin_validation():
    """Validates admin login credentials."""
    if not cursor:
        return "Database connection not available."
    admin_id = request.form.get('auserid')
    password = request.form.get('apassword')
    
    val = (admin_id,)
    val_sql = "SELECT * FROM admin_data WHERE ADMIN_ID=%s;"
    cursor.execute(val_sql, val)
    admin_data = cursor.fetchall()

    if admin_data and password == admin_data[0][1]: # Assuming password is in plain text for admin
        session['ADMIN_ID'] = admin_data[0][0]
        return redirect('/admin')
    else:
        return render_template('adminlogin.html', error="Invalid admin credentials.")

# --- Core Application Routes ---

@app.route('/home')
def home():
    """Renders the main prediction form page if the user is logged in."""
    if 'userid' in session:
        return render_template('home.html')
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    """Logs the user out."""
    session.pop('userid', None)
    return redirect('/')
    
@app.route('/admin_logout')
def admin_logout():
    """Logs the admin out."""
    session.pop('ADMIN_ID', None)
    return redirect('/adminlogin')

@app.route('/admin')
def admin():
    """Displays all predictions for the admin."""
    if not cursor:
        return "Database connection not available."
    if 'ADMIN_ID' in session:
        query = "SELECT * FROM prediction;"
        cursor.execute(query)
        predictions = cursor.fetchall()
        return render_template('admin.html', value=predictions)
    else:
        return redirect('/adminlogin')

@app.route('/predict', methods=['POST'])
def predict():
    """Handles the loan prediction logic."""
    if 'userid' not in session:
        return redirect('/')
    if not model or not scaler or not cursor:
        return render_template('home.html', prediction_text="Prediction service is currently unavailable.")

    try:
        # --- 1. Get User Input from Form ---
        fn = request.form['first_name']
        ln = request.form['last_name']
        
        # Convert form values to appropriate types
        gender = int(request.form['gender'])
        married = int(request.form['married'])
        dependents = int(request.form['dependents'])
        education = int(request.form['education'])
        self_employed = int(request.form['self_employed'])
        property_area = int(request.form['property_area'])
        credit_history = float(request.form['credit_history'])
        cibil_score = int(request.form['cibil_score'])
        
        applicant_income = float(request.form['applicant_income'])
        coapplicant_income = float(request.form['coapplicant_income'])
        loan_amount = float(request.form['loan_amount'])
        loan_amount_term = float(request.form['loan_amount_term'])

        # --- 2. Engineer Features (must match the notebook) ---
        total_income = applicant_income + coapplicant_income
        loan_to_income_ratio = loan_amount / total_income if total_income > 0 else 0
        emi_feature = loan_amount / loan_amount_term if loan_amount_term > 0 else 0
        
        applicant_income_log = np.log(applicant_income + 1)
        coapplicant_income_log = np.log(coapplicant_income + 1)
        loan_amount_log = np.log(loan_amount + 1)
        total_income_log = np.log(total_income + 1)

        # --- 3. Create DataFrame for Prediction (must match notebook columns) ---
        # The order of columns is critical and must be the same as the training data
        input_data = pd.DataFrame({
            'Loan_Amount_Term': [loan_amount_term],
            'Credit_History': [credit_history],
            'CIBIL_Score': [cibil_score],
            'Loan_to_Income_Ratio': [loan_to_income_ratio],
            'EMI_feature': [emi_feature],
            'ApplicantIncome_log': [applicant_income_log],
            'CoapplicantIncome_log': [coapplicant_income_log],
            'LoanAmount_log': [loan_amount_log],
            'Total_Income_log': [total_income_log],
            'Gender_Male': [1 if gender == 1 else 0],
            'Married_Yes': [1 if married == 1 else 0],
            'Dependents_1': [1 if dependents == 1 else 0],
            'Dependents_2': [1 if dependents == 2 else 0],
            'Dependents_3+': [1 if dependents == 3 else 0],
            'Education_Not Graduate': [1 if education == 1 else 0],
            'Self_Employed_Yes': [1 if self_employed == 1 else 0],
            'Property_Area_Semiurban': [1 if property_area == 1 else 0],
            'Property_Area_Urban': [1 if property_area == 2 else 0]
        })

        # --- 4. Scale the Input and Predict ---
        input_scaled = scaler.transform(input_data)
        prediction = model.predict(input_scaled)
        prediction_proba = model.predict_proba(input_scaled)

        # --- 5. Format Output and Save to DB ---
        result_text = "Approved" if prediction[0] == 1 else "Not Approved"
        confidence = prediction_proba[0][prediction[0]] * 100

        # Save prediction to the database
        resp_data = (
            fn, ln, gender, married, dependents, education, self_employed, 
            property_area, credit_history, cibil_score, applicant_income, 
            coapplicant_income, loan_amount, loan_amount_term, result_text
        )
        resp_query = """
            INSERT INTO prediction (First_Name, Last_Name, Gender, Martial_Status, Number_of_dependents, 
            Education, Employment_status, Property_Area, Credit_History, CIBIL_Score, Income, 
            Co_Applicant_Income, Loan_Amount, Loan_Duration, prediction) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(resp_query, resp_data)
        connection.commit()

        # Render the result page
        return render_template('result.html', 
                               prediction_text=result_text, 
                               confidence_text=f"{confidence:.2f}%",
                               user_name=f"{fn} {ln}")

    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return render_template('home.html', prediction_text="An error occurred. Please check your inputs and try again.")

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
