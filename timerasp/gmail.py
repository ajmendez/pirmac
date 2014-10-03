#!/usr/bin/env python
'''
http://stackoverflow.com/questions/11445523/python-smtplib-is-sending-mail-via-gmail-using-oauth2-possible

'''
import time
import xoauth
import socket
import smtplib
import calendar
from pymendez import auth
from datetime import datetime


TEMPLATE = '''To:{address}
From: {email}
Subject:{subject}

{message}

{info}

'''

def send_email(subject, message, addinfo=True):
    email, address, oauth_token, oauth_token_secret = auth('gmail', ['email','address', 'oauth_token', 'oauth_token_secret'])

    consumer = xoauth.OAuthEntity('anonymous', 'anonymous')
    access_token = xoauth.OAuthEntity(oauth_token, oauth_token_secret)

    xoauth_string = xoauth.GenerateXOauthString(consumer, access_token, email, 'smtp', email, 
                        str(xoauth.random.randrange(2**64 - 1)), str(int(time.time())))

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    # smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo()
    smtp_conn.starttls()
    smtp_conn.ehlo()
    smtp_conn.docmd('AUTH', 'XOAUTH ' + xoauth.base64.b64encode(xoauth_string))
    
    if addinfo:
        info = '{} : {} : {}'.format(socket.gethostname(), calendar.timegm(time.gmtime()), datetime.now())
    else:
        info = ''
        
    msg = TEMPLATE.format(address=address, email=email, subject=subject, message=message, info=info)
    smtp_conn.sendmail(email, address, msg)
    


if __name__ == '__main__':
    send_email('email test', 'body')