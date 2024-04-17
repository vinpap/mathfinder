"""
This script monitors all the models registered in Mathfinder's database.

It is intended to be run every day, using the CSV files stored 
in the 'autotest' folder to test the models and make sure their performance 
is still within a reasonable range away from the performance obtained with
the first version of the model.
"""
import os
import json
import logging
from datetime import date, datetime
import smtplib
from email.mime.text import MIMEText

import mysql.connector
import mlflow
import pandas as pd
from sklearn.metrics import mean_absolute_error



def setup_logging():
    """
    Sets up everything required in order to log enable logging in a .log file.

    Logs are located in the 'logs' subfolder.
    """
    if not (os.path.exists("./logs") and os.path.isdir("./logs")):
        os.mkdir("./logs")

    # Setting up logging
    now = datetime.now()
    filename = now.strftime("%Y_%m_%d_%H_%M_%S.log")
    logging.basicConfig(filename=os.path.join("./logs", filename), level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s')
    

    

def testing_is_necessary(last_testing_date, test_frequency: int) -> bool:
    """
    Decides if a test should be performed based on the date of the last date.
    """
    today = date(2024, 6, 16)
    #today = date.today()
    days_elapsed = today - last_testing_date

    if days_elapsed.days > test_frequency:
        return True
    return False

def update_testing_date(model_name: str):
    """
    Update the last testing date in the database.
    """

    logging.debug(f"Updated last training date for model {model_name}")
    with mysql.connector.connect(
        host="localhost",
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PWD"],
        database="mathfinder"
    ) as db:
        with db.cursor() as c:
            today = date.today()
            query = f"""UPDATE Models SET last_testing_date="{today.strftime('%Y-%m-%d')}" WHERE name="{model_name}";"""
            c.execute(query)
            db.commit()

def get_test_data(model_name: str) -> tuple:
    """
    Retrieves, loads and returns the test data for a specific model.

    Returns a tuple (X, y, filename) if the data was found, False otherwise.
    """

    # First we retrieve the name of each feature and target values so we know ehat columns we should use in the CSV
    client = mlflow.MlflowClient()
    model_versions = client.search_model_versions(f"name='{model_name}'")
    last_version = model_versions[0].version
    model_uri = client.get_model_version_download_uri(model_name, last_version)
    model_info = mlflow.models.get_model_info(model_uri)
    schema = model_info._signature_dict

    feature_names = []
    target_names = []
    feature_data_json = json.loads(schema["inputs"])
    target_data_json = json.loads(schema["outputs"])
    for feature in feature_data_json:
        feature_names.append(feature["name"])
    for target in target_data_json:
        target_names.append(target["name"])
    
    # Loading the oldest CSV in the test data folder
    oldest_csv_file_name = None
    oldest_modification_time= None
    
    subdir = os.path.join("./autotest", model_name)
    for filename in os.listdir(subdir):
        if not filename.endswith(".csv"):
            continue
        modification_time = os.path.getmtime(os.path.join(subdir, filename))
        if not oldest_modification_time:
            oldest_modification_time = modification_time
            oldest_csv_file_name = filename
        elif modification_time < oldest_modification_time:
            oldest_modification_time = modification_time
            oldest_csv_file_name = filename
    
    if not oldest_csv_file_name:
        return False
    
    test_csv = pd.read_csv(os.path.join(subdir, oldest_csv_file_name))
    
    try:
        X = test_csv[feature_names]
        y = test_csv[target_names]
        return X, y, oldest_csv_file_name
    
    except KeyError:
        print(f"ERROR: Could not find columns {feature_names}, {target_names} in {oldest_csv_file_name}.")
        return False

def load_model(model_name: str):
    """
    Loads the last version of the mode lreferenced by model_name.
    """

    client = mlflow.MlflowClient()
    model_versions = client.search_model_versions(f"name='{model_name}'")
    last_version = model_versions[0].version
    model_uri = client.get_model_version_download_uri(name=model_name, version=last_version)
    # Reconstituting the model local path
    splitted_uri = model_uri.split("/")[1:]
    model_uri = "mlartifacts/" + "/".join(splitted_uri)
    model = mlflow.pyfunc.load_model(model_uri)
    return model

def get_original_metrics(model_name: str) -> float:
    """
    Retrieves and returns the Mean Absolute Error of the model's first run.
    """
    client = mlflow.tracking.MlflowClient()
    experiment = client.get_experiment_by_name(f"/{model_name}")
    runs = client.search_runs(experiment.experiment_id, order_by=["end_time"])
    first_run = runs[0].data.to_dictionary()
    return first_run["metrics"]["mean absolute error"]

def give_report(title: str, report: str, email: str):
    """
    Conveys the test report to the user.
    """
    print(f"Report given to {email}:")
    print(report)

    #TODO: enlever 'smtp.gmail.com' du code, utiliser la variable d'environnement à la place
    # Some environment variables need to be set, depending on the SMTP server you use
    subject = title
    body = report
    sender = os.environ["SMTP_LOGIN"]
    recipients = [email]
    password = os.environ["SMTP_PWD"]
    smtp_server = os.environ["SMTP_SERVER"]

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail("papelardvincent@gmail.com", recipients, msg.as_string())
    print("Message sent!")


if __name__ == "__main__":

    setup_logging()
    logging.info("Starting the monitoring script")

    mlflow.set_tracking_uri(uri="http://127.0.0.1:8080")

    
    with mysql.connector.connect(
        host="localhost",
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PWD"],
        database="mathfinder"
    ) as db:
        
        logging.info("Established connection with the database")
        with db.cursor() as c:
            
            query = """SELECT * FROM Models;"""
            c.execute(query)
            models = c.fetchall()
            logging.info("Retrieved models list")
            for model in models:
                model_name = model[0]
                email = model[1]
                logging.debug(f"Processing model {model_name}")
                if testing_is_necessary(last_testing_date=model[3], test_frequency=model[2]):
                    
                    report = "" # Stores the report that will be conveyed to the user
                    test_data = get_test_data(model_name)
                    if not test_data:
                        logging.info(f"Model {model_name} should be tested but test data could not be loaded. This means they are either missing or do not follow the right formatting.")
                        title = "Mathfinder did not find your test data"
                        report = f"""Mathfinder tried to test your model {model_name} to ensure it still retains good performance, but no testing data was found. Please ensure that:\n- there is at least one CSV file that contains test data in the 'autotest/<your model name> folder, in Mathfinder's directory\n- this CSV file contains one column for each input data used in your model, and one for each target value. The column names must be the same as those of the data used to train the model."""
                    else:
                        logging.debug(f"Test data loaded for model {model_name}")
                        model = load_model(model_name)
                        X_test = test_data[0]
                        y_test = test_data[1]
                        filename = test_data[2]
                        y_pred = model.predict(X_test)
                        mae = mean_absolute_error(y_test, y_pred)
                    
                        subdir = os.path.join("./autotest", model_name)
                        os.remove(os.path.join(subdir, filename))

                        original_mae = get_original_metrics(model_name)

                        
                        
                        if mae < 1.05 * original_mae:
                            logging.info(f"MAE computed for model {model_name}: {mae}. Original MAE: {original_mae}. Performance metrics are still acceptable")
                            title = "Your model passed the test"
                            report = f"""Congratulations, your model {model_name} is doing well!\nMathfinder tested your model automatically using the testing data your provided, and its performance is still good."""
                                
                        else:
                            logging.info(f"MAE computed for model {model_name}: {mae}. Original MAE: {original_mae}. Error metrics are above the acceptability threshold, the model must be retrained")
                            title = "Your model failed the test"
                            report = f"""Your model {model_name} needs to be retrained!\nMathfinder tested your model automatically using the testing data your provided, and its performance metrics went down. Please retrain your model using recent data whenever you have the chance."""
                                
                        report += "\n"
                        report += f"Original mean absolute error (MAE): {original_mae}\n"
                        report += f"MAE with the latest test: {mae}\n"
                        report += "Acceptability threshold: 105% of the original MAE"
                    
                    logging.info(f"Sending report to the email address registered for model {model_name}")
                    give_report(title, report, email)
                    update_testing_date(model_name)
                    
            


