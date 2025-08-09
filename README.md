# Enhanced Loan Eligibility Prediction System

This project is an upgraded version of a simple bank loan eligibility prediction system. It features a more robust machine learning model, a modern web interface, and enhanced features like CIBIL score integration to provide more accurate predictions.

## Features

-   **Accurate Predictions**: Utilizes a `RandomForestClassifier` model, which offers higher accuracy than simpler models like Decision Trees or Logistic Regression.
-   **Advanced Feature Engineering**:
    -   **CIBIL Score**: Incorporates a CIBIL score, a critical factor in real-world loan assessment.
    -   **Derived Features**: Creates new features like Total Income, Loan-to-Income Ratio, and an EMI-like feature to provide more context to the model.
-   **Modern Web Interface**: A clean, responsive user interface built with **Flask** and **Tailwind CSS** for a better user experience.
-   **User and Admin Portals**: Separate login and dashboard functionalities for regular users and administrators.
-   **Database Integration**: User data and prediction results are stored in a **MySQL** database.

## Tech Stack

-   **Backend**: Python, Flask
-   **Machine Learning**: Scikit-learn, Pandas, NumPy
-   **Database**: MySQL (via PyMySQL)
-   **Frontend**: HTML, Tailwind CSS
-   **Development**: Jupyter Notebook

---

## Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites

-   Python 3.7+
-   Anaconda or another virtual environment manager (recommended)
-   XAMPP or any other MySQL server

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd enhanced-loan-eligibility
3. Create a Virtual EnvironmentIt's highly recommended to use a virtual environment to manage dependencies.# Create the environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
4. Install DependenciesInstall all the required Python packages using the requirements.txt file.pip install -r requirements.txt
5. Set Up the DatabaseStart your MySQL server (e.g., start Apache and MySQL in the XAMPP Control Panel).Run the datacreation.py script to automatically create the database (loan_prediction_system) and the necessary tables (user_data, admin_data, prediction).python datacreation.py
This will also create a default admin user with the credentials:Admin ID: adminPassword: admin1236. Train the Model (Optional)A pre-trained model (loan_eligibility_model.pkl) and scaler (scaler.pkl) are already included in the /model directory. If you wish to retrain the model with new data or different parameters, run the model_training.ipynb Jupyter notebook.How to Run the ApplicationOnce the setup is complete, you can start the Flask web server.flask run
Or simply:python main.py
Open your web browser and navigate to http://127.0.0.1:5000.You can sign up for a new user account or log in if you already have one.To access the admin panel, navigate to http://127.0.0.1:5000/adminlogin and use the default admin credentials.Project Structure.
├── model/
│   ├── loan_eligibility_model.pkl  # The trained RandomForest model
│   └── scaler.pkl                  # The StandardScaler object
├── templates/
│   ├── index.html                  # User login/signup page
│   ├── home.html                   # Main prediction form
│   ├── result.html                 # Prediction result display
│   ├── admin.html                  # Admin dashboard
│   └── adminlogin.html             # Admin login page
├── data/
│   └── train.csv                   # Training data used for the model
├── datacreation.py                 # Script to set up the MySQL database
├── main.py                         # The main Flask application file
├── model_training.ipynb            # Jupyter notebook for model training
├── requirements.txt                # Python dependencies
└── README.md                       # This file
