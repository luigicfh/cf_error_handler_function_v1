from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import functions_framework
import os

ENV_VAR_MSG = "Specified environment variable is not set."
METHOD_NOT_ALLOWED_MSG = "Method not allowed"
METHOD_NOT_ALLOWED = 405


@functions_framework.http
def error_handler(request):

    if request.method != "POST":
        METHOD_NOT_ALLOWED_MSG, METHOD_NOT_ALLOWED

    request_json = request.get_json()
    sender = os.environ.get('USER', ENV_VAR_MSG)
    password = os.environ.get('PASSWORD', ENV_VAR_MSG)
    recipients = request.args['recipients'].split(",")

    message = MIMEMultipart("alternative")
    message['Subject'] = f"AT Central Alerts - Error Job ID {request_json['job']['id']}"
    message['From'] = sender
    message['To'] = recipients

    body = f"""
        Hi there,\n\n
        The following service has returned an error, please review the details below:\n\n
        Job ID: {request_json['job']['id']}\n
        Service: {request_json['job']['service_instance']['name']}\n
        Error: {request['error']}\n\n
        Best,\n
        AT Central
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
