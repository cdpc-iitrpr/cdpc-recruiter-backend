﻿# cdpc-recruiter-backend

## Installation

### Setup Virtual Environment
- If virtualenv is not installed then install it with pip
```
python -m virtualenv env -p python3.8.5
./env/scripts/activate
pip install -r requirements.txt
```
Note: Make sure python3.8.5 is installed in your system

### Setup Environment Variables
- Create a .env file in the root directory of the project
- Add the following variables to the .env file
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_USE_TLS=True
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_HOST_USER=<email@outlook.com>
EMAIL_HOST_PASSWORD=<password>
SECRET_KEY=test
POSTGRES_DB=<database_name>
POSTGRES_USER=<username>
POSTGRES_PASSWORD=<postgres_password>
```
Note: Replace the values enclosed in angle brackets of the variables with your own values. 

You can ignore the below instruction, These instruction are for using gmail as smtp server.
If you are using gmail then replace the values with the following
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=email@gmail.com
EMAIL_HOST_PASSWORD=password
SECRET_KEY=test
POSTGRES_DB=portal
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
```
Note: To use gmail to send otp, you need to generate app password in google settings to bypass 2 step verification

### Setup Database
- As of now, we are using postgres ( psql ) as our database.

### Start the server
- Run the following commands
```
python manage.py makemigrations
python manage.py migrate
```
- This will create all the tables in the database
- Now run the following command to start the server
```
python manage.py runserver
```
