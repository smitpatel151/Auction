from flask_mail import Message
from app import app,mail
from flask import render_template
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

#mail chimp

def send_password_reset_email(user,bid=""):
    print("bid = ",bid)
    if bid == "":
        token = user.get_reset_password_token()
        send_email('[Online Auction] Reset Your Password',
                   sender=app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('email/reset_password.txt',user=user, token=token),
                   html_body=render_template('email/reset_password.html',user=user, token=token)
                   )
    else:
        send_email('[Online Auction] New product',
                   sender=app.config['ADMINS'][0],
                   recipients=[user.email],
                   text_body=render_template('email/new_bid.txt', user=user,product = bid.bidder),
                   html_body=render_template('email/new_bid.html', user=user,product = bid.bidder)
                   )