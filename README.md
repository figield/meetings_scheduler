# Project Installation 

## Virtual environament and libraries

Install Python and the tool for installing Python packages - pip:
```commandline
sudo apt-get install -y python3
sudo apt-get install -y python3-pip python3-dev python3-venv
```

Install virtualenv using pip3:
```commandline
pip3 install virtualenv
```

Create a virtual environment with virtualenv:
```commandline
virtualenv venv
```
OR 

Create a virtual environment with Python:
```commandline
python3 -m venv venv
```

Activate a virtual environment:
```commandline
source venv/bin/activate
```

Install libraries into the virtual environment
```commandline
pip install -r requirements.txt
```

## The quickest START

Project already has initialized `sqlite3` database with loaded data. 
Just run tests to check if code is working.

```commandline
pytest
```

Run the application to play with it.

```commandline
python3 manage.py runserver
```

Run curl command to get some results.
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"duration":"90","earliest_start":"2/14/2015 8:00:00 AM","latest_start":"2/15/2015 4:00:00 PM","office_hours":"8-17","employee_ids":"276908764613820584354290536660008166629,48639959687376052586683994275030460621"}' \
  http://127.0.0.1:8000/api/free/
```

## Quick START

Copy paste commands:
```commandline
rm lime
python3 manage.py migrate
python3 manage.py loaddata
pytest
```

## Step by step

## Database configuration.

Project is starting automatically with sqlite3. It is possible to run it with PostgreSQL or any other compatible with Django database.

### Connecting to PostgreSQL

Create database ex. `lime`. With your custom credentials.

Once created you can remove it and create if you need:

```commandline
dropdb lime 
createdb lime
```
In the Django settings.py there is the following example how to setup connection to POstgreSQL database:

```python
DATABASES = {
    'default': {
        'HOST': '127.0.0.1',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lime',
        'USER': 'lime',
        'PASSWORD': 'lime',
    }
}
```

### Connecting to SQLite3

SQLite3 database is default database, already configured in settings.py.
Project also includes initialized database in `lime` file.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lime',
    }
}
```

## Run project

If database is empty, the first step is running django migrations to create tables:

```commandline
python3 manage.py migrate
```

Fetch data from the remote server (optional - since there is already prepared file: `freebusy.txt`)

```commandline
python3 manage.py fetchdata
```

Add `--help` to check command usage.

Load data to database (optional if SQLite is used).
The command lasts almost 2 minutes. It is quite slow as data integrity is checked.

```commandline
python3 manage.py loaddata
```
Add `--help` to check command usage.

Command output to terminal (for reference only):

```commandline
...
10077:Marquerite Romero: 2015-02-10 14:30:00 - 2015-02-10 15:00:00
10078:Lorraine Phillips: 2015-03-02 08:00:00 - 2015-03-02 08:30:00
Data loaded in 0:01:44.330360
143 lines with employee data
10078 lines with meetings data
```
 
Loading data to PostgreSQL database is twice faster:

```commandline
...
10077:Marquerite Romero: 2015-02-10 14:30:00 - 2015-02-10 15:00:00
10078:Lorraine Phillips: 2015-03-02 08:00:00 - 2015-03-02 08:30:00
Data loaded in 0:00:56.803654
143 lines with employee data
10078 lines with meetings data
```

If there is no tables created in database, the following error will be shown:

```commandline
python3 manage.py loaddata
...
[handle_employee_data] no such table: free_employee
...
```

Run tests to check if the code is working:

```commandline
pytest
```

Desired output from running tests:
```commandline
============================== test session starts ===============================
platform linux -- Python 3.8.10, pytest-5.4.2, py-1.11.0, pluggy-0.13.1
django: settings: freebusy.settings (from ini)
rootdir: /home/dawidfigiel/projects/lime, inifile: pytest.ini
plugins: Faker-4.1.0, django-3.9.0
collected 26 items                                                               

free/tests/component_tests.py .                                            [  3%]
free/tests/e2e_tests.py ...........                                        [ 46%]
free/tests/component_tests.py ............                                 [ 92%]
free/tests/unit_tests.py ..                                                [100%]

=============================== 26 passed in 0.25s ===============================
```

Optional step (if you want to play with Django admin):

```commandline
python3 manage.py createsuperuser
```

## Run Django development server 


```commandline
python3 manage.py runserver
```

### Manual testing

Example of the request data. 
Can be copied for the POST methed on  page (Django feature): `http://127.0.0.1:8000/api/free/`:

```
{
"duration": "90",
"earliest_start": "2/14/2015 8:00:00 AM",
"latest_start": "2/15/2015 4:00:00 PM",
"office_hours": "8-17",
"employee_ids": "276908764613820584354290536660008166629,48639959687376052586683994275030460621"
}
```

Data taken into analysis (taken from the file):

```
276908764613820584354290536660008166629;2/14/2015 9:00:00 AM;2/14/2015 12:00:00 PM;
276908764613820584354290536660008166629;2/14/2015 1:00:00 PM;2/14/2015 2:00:00 PM;
276908764613820584354290536660008166629;2/14/2015 7:00:00 AM;2/14/2015 8:00:00 AM;

48639959687376052586683994275030460621;2/15/2015 10:00:00 AM;2/15/2015 12:00:00 PM;
48639959687376052586683994275030460621;2/15/2015 7:00:00 AM;2/15/2015 7:30:00 AM;
48639959687376052586683994275030460621;2/15/2015 12:30:00 PM;2/15/2015 3:00:00 PM;
```

### Using GET method with `curl` command:

```
curl 'http://127.0.0.1:8000/api/free/?employee_ids=276908764613820584354290536660008166629,48639959687376052586683994275030460621&duration=90&earliest_start=2/14/2015+8:00:00+AM&latest_start=2/15/2015+4:00:00+PM&office_hours=8-17' -H "Accept: application/json"
```

### Using POST method:

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"duration":"90","earliest_start":"2/14/2015 8:00:00 AM","latest_start":"2/15/2015 4:00:00 PM","office_hours":"8-17","employee_ids":"276908764613820584354290536660008166629,48639959687376052586683994275030460621"}' \
  http://127.0.0.1:8000/api/free/
```
#### Response:

Command output:
```
{"freetimes":["2/14/2015 2:00:00 PM","2/14/2015 2:30:00 PM","2/14/2015 3:00:00 PM","2/14/2015 3:30:00 PM","2/15/2015 8:00:00 AM","2/15/2015 8:30:00 AM","2/15/2015 3:00:00 PM","2/15/2015 3:30:00 PM"]}
```

Browser on Django page:
```
HTTP 200 OK
Allow: GET, POST, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "freetimes": [
        "2/14/2015 2:00:00 PM",
        "2/14/2015 2:30:00 PM",
        "2/14/2015 3:00:00 PM",
        "2/14/2015 3:30:00 PM",
        "2/15/2015 8:00:00 AM",
        "2/15/2015 8:30:00 AM",
        "2/15/2015 3:00:00 PM",
        "2/15/2015 3:30:00 PM"
    ]
}
```

Have fun!
