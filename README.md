| Component  | Build Status  | Demo  |
| ---  | ---  | ---  |
| Provider  | [![Build Status](https://jenkins-rioauth.hotbed.io/buildStatus/icon?job=rioauth-provider)](https://jenkins-rioauth.hotbed.io/job/rioauth-provider)  | https://provider-rioauth.hotbed.io  |

# RioAuth

RioAuth is an authentication server written in python, implementing of the oauth2 protocol 
using web.py and sqlite. In addition to providing registration capabilities, 
it can delegate to GitHub or Google to authenticate your email address.  RioAuth can be viewed
 in a demo format on our [hotbed server](https://provider-rioauth.hotbed.io).

  
## Motivation

RioAuth was built during the development of another application called 
[SAM](https://github.com/riolet/rioauth). SAM needed an 
authentication service but nothing fancy. All we needed was to have the user verify their 
email address, so that we could connect them to their information. Our online version of 
[SAM](https://samapper.com) is now running using this as an authentication service.


## Repository

The RioAuth repository includes two modules, Provider and Consumer. Provider is an example 
webserver that manages login and registration. Consumer is an sample webserver that connects
to Provider to validate the user. Consumer would be your main website that RioAuth was serving


## Usage

The provider application is configured through environment variables.  See the file 
provider/default.cfg for details on format and values. 
Take particular note to provide SMTP settings and not the admin user and password.
 
Once the server is running, you must add your application in the admin control panel. 

For the sample consumer, just edit the default.cfg file.

## Deployment

For deploying a web.py server, see the Deployment section of [webpy.org cookbook](http://webpy.org/cookbook/). 