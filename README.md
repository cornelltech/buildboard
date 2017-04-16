# Buildboard

Buildboard is a tool to showcase what studio students are working on. The objective is to encourage engagement between students, practitioners and other members of Cornell Tech community.  

# Design

## TLDR;
At the core is a django app, that handles most functionality from authentication, authorization to forms and views. The django app has nginx as the frontend server to manage traffic. Postgres is the database of choice with Django's ORM managine schema changes. LetsEncrypt is used to manage ssl certifications.


Production = django + postgres + nginx + letsencrypt
Letsencrypt needs a server with a domain name to work.

Dev = django + postgres

Credentials are stored on AWS Foundry S3 account accesible. It works out of the box from AWS.



# Develop


# Deploy

