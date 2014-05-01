import requests
import pyping
import smtplib
import time
import subprocess
from datetime import datetime

# Set These Variables

# Name of Webserver running the site
server = 'server.local.domain'

# URL of Page to Monitor
site = 'http://site.com/default.asp'

# Address Alerts are sent from
sender = 'alerts@local.domain'

# Mail Exceptions to
exception_recipient = 'admin@site.com'

# Alert recipient
recipient = 'group@site.com'

# SMTP Server to send mail through
smpt_serv = 'mail.local.domain'

# Log Location, use forward slashes instead of backslashes
log_file = 'c:/sitechecker/log.txt'

# Line to search for on site to verify the correct page is being displayed
# if you aren't sure, visit the page in a browser, open source and copy some text
web_string = '<header>Website</header>'



def email_error(error):
    message = """From: %s
To: %s
Subject: Site Checker Exception

The Website Checker threw an exception at %s

""" % (sender, exception_recipient, error)
    send_email(sender, recipient, message, smtp_serv)

def email_alert(pingresult, stopresult, startresult, resolved):
    message = """From: %s
To: %s
Subject: Site Checker Alert

%s IIS has failed 3 times to properly display the correct webpage.

%s

    %s

    %s

%s
""" % (sender, recipient, server, pingserver, stopresult, startresult, resolved)
    send_email(sender, recipient, message, smtp_serv)

def log_event(event):
    log = open(log_file, 'a')
    log.write(str(datetime.now()) + ': ' + event + '\n')
    log.close

def ping(address):
    try:
        r = pyping.ping(address)
    except:
        email_error('Pinging Server')
        log_event('Exception Pinging Server')
        die()

    return not r.ret_code

def check_site():
    try:
        r = s.get(site)
    except requests.exceptions.RequestException:
        return False    
    
    return r and web_string in r.content

def restart_iis():
    try:
        result = subprocess.check_output('iisreset ' + server, bufsize = -1)
    except:
        email_error('Restarting IIS')
        log_event('Exception Restarting IIS')

        stop = False
        start = False
        command_except = True

        return stop, start, command_except        

    if result.find('Internet services successfully stopped') > -1:
        stop = True
    else:
        stop = False
        command_except = False 

    if result.find('Internet services successfully restarted') > -1:
        start = True
        command_except = False
    else:
        start = False 
        command_except = False

    return stop, start, command_except

def die():
    log_event('Stopping Monitor')
    exit()

def send_email(sender, recipient, message, smtp_serv):
    smtpObj = smtplib.SMTP(smtp_serv, 25)
    smtpObj.sendmail(sender, recipient, message)


log_event('Monitor Started')

s = requests.session()

while True:
    pingserver = ''
    stopresult = ''
    startresult = ''
    resolved = ''
    command_except = ''

    time.sleep(60)
    
    for _ in range(3):
        if check_site():
            break
            
        time.sleep(10)

    else:
        log_event('Site failed to return correct page 3 times')

        if not ping(server):
            pingserver = 'The server is not responding to pings. No further action will be taken.'
            email_alert(pingserver, stopresult, startresult, resolved)
            log_event(pingserver)
            time.sleep(1800)
            continue

        pingserver = 'The server is responding to pings.\nAttempting to stop and restart IIS...'
        log_event('The server is responding to pings')
        
        stop_command, start_command, command_except = restart_iis()

        if command_except:
            # Exception trying to run command
            time.sleep(600)
            continue

        elif stop_command and start_command:
            # Restart succesful
            stopresult = 'IIS has successfully stopped'
            startresult = 'IIS has successfully started'
            log_event(stopresult)
            log_event(startresult)

        elif stop_command is True and start_command is False:
            # Stopped and didn't come back up
            stopresult = 'IIS has successfully stopped'
            startresult = 'IIS was unable to start and is down'
            log_event(stopresult)
            log_event(startresult)

        elif stop_command is False:
            # Failed to stop
            stopresult = 'IIS was unable to stop.'
            log_event(stopresult)

        # See if the site is back online
        if not check_site():
            resolved = 'The site is still down. No further action will be taken.'
            log_event(resolved)
            email_alert(pingserver, stopresult, startresult, resolved)
            time.sleep(1800)
        else:
            resolved = 'The site is back up.'
            log_event(resolved)
            email_alert(pingserver, stopresult, startresult, resolved)
