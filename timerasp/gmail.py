#!/usr/bin/env python
'''
http://stackoverflow.com/questions/11445523/python-smtplib-is-sending-mail-via-gmail-using-oauth2-possible

https://console.developers.google.com/project
export client_id=xxx.apps.googleusercontent.com
export client_secret=
export refresh_token=
# python gmail_oauth2.py --generate_oauth2_token --client_id=$client_id --client_secret=$client_secret
# python gmail_oauth2.py --client_id=$client_id --client_secret=$client_secret --refresh_token=$refresh_token


# python gmail_oauth2.py --generate_oauth2_string --access_token=xxx --user=xxx@gmail.com
# python gmail_oauth2.py --test_smtp_authentication --access_token=xxx --user=xxx@gmail.com
# python gmail_oauth2.py --client_id=xxx.apps.googleusercontent.com --client_secret=xxx --refresh_token=xxx

'''
import time
import xoauth
import base64
import socket
import smtplib
import calendar
import gmail_oauth2
from pymendez import auth
from datetime import datetime




TEMPLATE = '''To:{address}
From: {email}
Subject:{subject}

{message}

{info}

'''

def setup_email():
    email, address, client_id, client_secret, refresh_token = auth('gmail', ['email', 'address', 'client_id', 'client_secret', 'refresh_token'])
    scope = 'https://mail.google.com/'
    print 'To authorize token, visit this url and follow the directions:'
    print '  %s' % gmail_oauth2.GeneratePermissionUrl(client_id, scope)
    authorization_code = raw_input('Enter verification code: ').strip()
    response = gmail_oauth2.AuthorizeTokens(client_id, client_secret, authorization_code)
    print 'Refresh Token: %s' % response['refresh_token']
    print 'Access Token: %s' % response['access_token']
    print 'Access Token Expiration Seconds: %s' % response['expires_in']
    


def send_email(subject, message, addinfo=True):
    email, address, client_id, client_secret, refresh_token = auth('gmail', ['email', 'address', 'client_id', 'client_secret', 'refresh_token'])
    
    response = gmail_oauth2.RefreshToken(client_id, client_secret, refresh_token)
    access_token = response['access_token']
    auth_string = gmail_oauth2.GenerateOAuth2String(email, access_token, base64_encode=False)
    
    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    # smtp_conn.set_debuglevel(True)
    smtp_conn.ehlo()
    smtp_conn.starttls()
    smtp_conn.ehlo()
    smtp_conn.docmd('AUTH', 'XOAUTH2 ' + base64.b64encode(auth_string))
    
    
    if addinfo:
        info = '{} : {} : {}'.format(socket.gethostname(), calendar.timegm(time.gmtime()), datetime.now())
    else:
        info = ''
        
    msg = TEMPLATE.format(address=address, email=email, subject=subject, message=message, info=info)
    smtp_conn.sendmail(email, address, msg)
    





def send_email_xoauth(subject, message, addinfo=True):
    '''Broken!'''
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
    # setup_email()
    send_email('email test', 'body')