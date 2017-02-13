Provisioning a new site
=======================

## Required packages:

*nginx
*Python 3
*Git
*pip
*virtualenv

e.g.,, on Ubuntu:
	
	sudo apt-get install nginx git python3 python3-pip
	sudo pip3 install virtualenv

## Nginx Virtual Host Config

* see nginx.template.conf
* replace SITENAME with, e.g., my-domain.staging.us

## Upstart Job (replace with systemd)

* see gunicorn-upstart.template.conf
* replace SITENAME with, e.g., my-domain.staging.us


## Folder structure:
Assume we have a user account at /home/username

/home/username
|___sites
    |____SITENAME
    	 |--database
	 |--source
	 |--static
	 |--virtualenv
	 
