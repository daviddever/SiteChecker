SiteChecker
===========

Simple monitoring script for a site running on IIS on Windows Server 2003


This script will check a website for a speciffic string (as opposed to an asp error) in the hosted page once a minute. If the string is not returned the script will check 3 more times, then attempt to ping the server to determine if the server is up. If the server is up it will send the iisreset command to restart the site and check if it is back up after the restart and send an alert email with the actions taken and the results. If the site is not up the script will wait 30 mins before beginning to check again.

This script was written to deal with a webapp we had in production that would often end up throwing an asp error to overcome a shortcoming of our existing monitoring solution which only notified us when the webserver was down but not if the page was displaying an error.


Requirements
============

Website running on Windows Server 2003
Script needs to run on a windows server with an account with admin permissions on the webserver
Python 2.7
Requests: http://docs.python-requests.org
Pyping: pypi.python.org/pypi/pyping


Installation
============

1. Install the dependencies and clone the repo
::
    pip install requests
    pip install pyping
    git clone https://github.com/daviddever/SiteChecker.git

2. Edit the variables at the top of sitechecker.py for your environment

3. Run sitechecker.py or optionally add a scheduled task to run the script on startup
