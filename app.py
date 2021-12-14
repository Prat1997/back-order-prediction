# importing required packages

from flask import Flask, render_template, request, abort
import boto3
import json
import pickle
import datetime
import sklearn
import numpy as np
import logging
import pymongo

# configuring logging method
logging.basicConfig(filename='info.txt',
                    level=logging.INFO,
                    filemode='a',
                    format='%(asctime)s %(levelname)s-%(message)s',
                    datefmt='%Y-%m-%d %H:%M-%S')

# Load the decision tree model
model = pickle.load(open('Tuned_DT_Back_order.pkl', 'rb'))

app = Flask(__name__)


# route for 404 error handler
@app.errorhandler(404)
def page_not_found(error):
    logging.error("Page not found: %s", (request.path))
    return render_template('404.html', title='404 Error', msg=request.path)


# route for 403 error handler
@app.errorhandler(405)
def page_not_found(error):
    logging.error("Method is not allowed: %s", (request.path))
    return render_template('405.html', title='405 Error', msg=request.path)


# route for 500 error handler
@app.errorhandler(500)
def internal_server_error(error):
    logging.error('Server Error: %s' % error)
    return render_template('500.html', title='500 Error', msg=error)


# route for main page
@app.route('/')
def index():
    try:
        logging.info("someone is accessing index.html!!!")
        return render_template("index.html")
    except Exception as e:
        logging.critical("Cannot able to access index.html...! ")
        return render_template("new_error.html")


# route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    global collection, national_inv, Lead_time, Sales1month, piecespastdue, perf_6_month_avg, localboqty, deck_risk, oe_constraint, stopautobuy, ppap_risk, rev_stop3, result, client
    # global national_inv, Sales1month
    try:
        if request.method == 'POST':
            national_inv = request.form["national_inv"]
            Lead_time = request.form["Lead_time"]
            Sales1month = request.form["Sales1month"]
            piecespastdue = request.form["piecespastdue"]
            perf_6_month_avg = request.form["perf_6_month_avg"]
            localboqty = request.form["localboqty"]
            deck_risk = request.form["deck_risk"]
            oe_constraint = request.form["oe_constraint"]
            stopautobuy = request.form["stopautobuy"]
            ppap_risk = request.form["ppap_risk"]
            rev_stop3 = request.form["rev_stop"]

            logging.info("Successfully retrieved information from user...! ")
            print(national_inv)
            print(Lead_time)
            print(Sales1month)
            print(piecespastdue)
            print(perf_6_month_avg)
            print(localboqty)
            print(deck_risk)
            print(oe_constraint)
            print(stopautobuy)
            print(ppap_risk)
            print(rev_stop3)

            data = [[national_inv, Lead_time, Sales1month, piecespastdue, perf_6_month_avg, localboqty, deck_risk,
                     oe_constraint, stopautobuy, ppap_risk, rev_stop3]]

            product_no = national_inv
            print(product_no)
            prediction = model.predict(data)
            my_prediction = int(prediction)
            print("prediction: ", my_prediction)
            if my_prediction == 0:
                result = "No"
                print(result)
            else:
                result = "Yes"
                print(result)

            logging.info("Successfully predicted")

    except Exception as e:
        logging.critical("Found Exception in route /predict: ")
        return render_template("new_error.html")




    # try:

    # creating date time for inserting data
    date_time = datetime.datetime.now()
    time = date_time.strftime('%A %d-%m-%Y, %H:%M:%S')
    date = (str(time))
    print(date)
    print(type(date))

    ACCESS_KEY_ID = 'AKIA2U5J5V6SNVNOWFRL'
    print(ACCESS_KEY_ID)
    ACCESS_SECRET_KEY = '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'
    print(ACCESS_SECRET_KEY)

    def put_data(a, b, c, d, e, f, g, h, i, j, k, l, m, dynamodb=None):
        if not dynamodb:
            dynamodb = boto3.resource('dynamodb',
                                        aws_access_key_id=ACCESS_KEY_ID,
                                        aws_secret_access_key=ACCESS_SECRET_KEY
                                        )
            print(dynamodb)

        table = dynamodb.Table('user_data')
        print(table)
        response = table.put_item(
            Item={
                'national_inv': a,
                'Lead_time': b,
                'Sales1month': c,
                'piecespastdue': d,
                'perf_6_month_avg': e,
                'localboqty': f,
                'deck_risk': g,
                'oe_constraint': h,
                'stopautobuy': i,
                'ppap_risk': j,
                'rev_stop3': k,
                'date': l,
                'predict': m
            }
        )
        # print(response)
        return response
        

    put_data(national_inv, Lead_time, Sales1month, piecespastdue, perf_6_month_avg, localboqty, deck_risk,
                oe_constraint, stopautobuy, ppap_risk, rev_stop3, date, result)
    # print(result)
    print("Put Item succeeded:")
# logging.info("successfully inserted data into dynamo db") 

# except Exception as e:
    # logging.warning("found error in inserting data")
    # print("error in insertion")

# logging.info("successfully predicted")
    return render_template('result.html', predict=result, product_no=product_no)


if __name__ == "__main__":
    app.run(host="localhost", port=8008, debug=True)