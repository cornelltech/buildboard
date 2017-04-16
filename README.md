# Buildboard

[buildboard.cornelltech.io](https://buildboard.cornelltech.io)

Buildboard is a tool to showcase what studio students are working on. The objective is to encourage engagement between students, practitioners and other members of Cornell Tech community.  

# Design

At the core is a django app, that handles most functionality from authentication, authorization to forms and views. The django app has nginx as the frontend server to manage traffic. Postgres is the database of choice with Django's ORM managine schema changes. LetsEncrypt is used to manage ssl certifications.

Docker is used to containarize the services. Django App, Nginx, Postgres and LetsEncrypt are all seperate service hosted on different containers. Docker compose is used to orchestrate service dependencies and networking. 

Credentials are stored on AWS Foundry S3 account accesible. It works out of the box from AWS.


# Develop

The

# Deploy


# Issues
