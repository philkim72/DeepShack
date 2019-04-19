import json
import os
import random
import smtplib


def email_handler(event, context):
    subject = "Shack Alert"

    event_message = json.loads(event['Records'][0]['Sns']['Message'])
    pred = event_message['prediction']
    fileneme = event_message['filename']
    body = f"{fileneme} was scraped\nPredicted value is {pred}"
    message = f"Subject: {subject}\n\n{body}"

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(os.environ['gmail_username'], os.environ['gmail_password'])
    s.sendmail("from@gmail.com", "ikkeiitoku@gmail.com", message)
    s.quit()
