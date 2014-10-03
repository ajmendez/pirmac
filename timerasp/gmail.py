#!/usr/bin/env python
'''
http://stackoverflow.com/questions/11445523/python-smtplib-is-sending-mail-via-gmail-using-oauth2-possible

'''
import time
import smtplib
import xoauth
from pymendez import auth

TEMPLATE = '''To:{address}
From: {email}
Subject:Notification of Time-lapse

{note}

'''

def send_email(note):
    email, address, oauth_token, oauth_token_secret = auth('gmail', ['email','address', 'oauth_token', 'oauth_token_secret'])

    consumer = xoauth.OAuthEntity('anonymous', 'anonymous')
    access_token = xoauth.OAuthEntity(oauth_token, oauth_token_secret)

    xoauth_string = xoauth.GenerateXOauthString(consumer, access_token, email, 'smtp', email, 
                        str(xoauth.random.randrange(2**64 - 1)), str(int(time.time())))

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo()
    smtp_conn.starttls()
    smtp_conn.ehlo()
    smtp_conn.docmd('AUTH', 'XOAUTH ' + xoauth.base64.b64encode(xoauth_string))

    msg = TEMPLATE.format(address=address, email=email, note=note)
    smtp_conn.sendmail(email, address, msg)
    


if __name__ == '__main__':
    send_email('gmail.py test')