from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import functions_framework
import os
import json

ENV_VAR_MSG = "Specified environment variable is not set."
METHOD_NOT_ALLOWED_MSG = "Method not allowed"
METHOD_NOT_ALLOWED = 405


@functions_framework.http
def error_handler(request):

    if request.method != "POST":
        METHOD_NOT_ALLOWED_MSG, METHOD_NOT_ALLOWED

    request_json = request.get_json()
    sender = os.environ.get('SENDER', ENV_VAR_MSG)
    password = os.environ.get('PASSWORD', ENV_VAR_MSG)
    recipients = request.args['recipients'].split(",")

    message = MIMEMultipart("alternative")
    message['Subject'] = f"AT Central Alerts - Error Job ID {request_json['job']['id']}"
    message['From'] = sender
    message['To'] = ",".join(recipients)

    body = f"""
        Job ID: {request_json['job']['id']}<br>
        <hr>
        Service: {request_json['job']['service_instance']['name']}<br>
        Error: {request_json['error']}<br>
        Job: <pre>{json.dumps(request_json['job'])}</pre>
    """

    text = body
    html = body

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.sendmail(
            sender, recipients, message.as_string()
        )

    return "OK"
