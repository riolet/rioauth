[![Build Status](https://jenkins-rioauth.hotbed.io/buildStatus/icon?job=rioauth-provider)](https://jenkins-rioauth.hotbed.io/job/rioauth-provider)

# oauth for webpy

This comes with two example programs, provider and consumer.

## Provider
This is the authentication server that holds and verifies the credentials of the user against applications.

## Consumer
This is an example of the web application, or "client".

## Running the example
TODO: simplify.

Set up app.local and auth.local as aliases for localhost in /etc/host

0. Some libraries may be required. see other_reqs.txt for ubuntu instructions
1. set up your virtual environment
1. install python libraries: `pip install -r requirements.txt`
1. create some localhost certificates for consumer and provider
1. navigate to /provider and run `python test_db_data.py` to install some data
1. run provider/server.py on 8081 and log in to check app id and secret
1. set up consumer/app.cfg with id and secret
1. run consumer/server.py on 8080 while the provider is running and try to log in.
