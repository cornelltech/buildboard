# Buildboard

[buildboard.cornelltech.io](https://buildboard.cornelltech.io)

Buildboard is a tool to showcase what studio students are working on. The objective is to encourage engagement between students, practitioners and other members of Cornell Tech community.  

### Design

At the core is a django app, that handles most functionality like authentication, authorization, database, forms and views. The django app has nginx as the frontend server to manage traffic. Postgres is the database of choice with Django's ORM managine schema changes. LetsEncrypt is used to manage ssl certifications.

Docker is used to containarize the services. Django App, Nginx, Postgres and LetsEncrypt are all seperate service hosted on different containers. Docker compose is used to orchestrate service dependencies and networking. 

The docker VM is itself hosted on an AWS EC2 instance accessible through [Foundry](http://cornelltech.io) AWS account. Also the different credentials are stored there. 

### Develop

The development environment takes advantage of modularity of services to run only django app and a postgres service locally. The configuration is stored in [buildboard/docker-compose-dev.yml](https://github.com/cornelltech/buildboard/blob/master/docker-compose-dev.yml)

### Deploy


### Issues

### Future Work
