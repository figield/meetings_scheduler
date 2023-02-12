
## Solution description

1. Why Django?

- It's easy to write commands like `loaddata` or `fetchdata`, so it's easy to access Django ORM ie database data.
- Because I'm working in a Django project and I can start right away.
- There is a good project structure inherited from django.
- The Django ORM works pretty well.

2. Project structure

- management - directory to store new Django commands.
- free - application module - here is the logic and tests.
- freebusy - project module which inclued main urls dispatcher file and project settings.
- `lime` - SQLite3 file database.
- freebusy.txt - input data file, already pre-downloaded. You can overwrite with fetchdata.

```commandline
.
├── free
│   ├── management
│   │   ├── commands
│   │   │   ├── fetchdata.py
│   │   │   ├── __init__.py
│   │   │   └── loaddata.py
│   │   └── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── serializers.py
│   ├── tests
│   ├── utils
│   └── views.py
├── freebusy
│   ├── settings.py
│   └── urls.py
├── freebusy.txt
├── lime
└── pytest.ini

```

2. How the `python3 manage.py loaddata` command is working?

The file is read line by line. It can be very large, so this method allows you to minimize memory consumption.
The file goes through twice. Collect employee data first. If you meet the same person, the update is not performed (this is a matter of choice).
The second round is to collect data on employee meetings.
To store meeting data in the database, the following requirements must be met:

- The employee must exist,
- Meeting start time is smaller than meeting end time,
- Row format is correct - number of data segments is correct - ex. There is Employee name,
- The data row does not contain any consistency errors - ex. Time format is correct, no `PM` or `AM` is cut,
- If an appointment is assigned to the same employee and at the same time, the appointment is not treated as new (it is not saved or updated).
- Empty line is treated as an error.

```commandline
979:ERROR:TRASH:
4233:ERROR:TRASH:
7067:ERROR:employee VALIDATION:320426673944415970493216791331086532677;
8008:ERROR:TRASH:
7062:ERROR:START >= END:132170847144391420901310654714918986833;1/1/2015 2:00:00 PM;1/1/2015 9:00:00 AM;2E77E3ACE...
```

3. Choosen one-to-many relation instead many-to-many

Mainly due to the efficiency of the `loaddata` command. Also the current approach makes coding simple.
It is not important to know if the employees meeting is common.

### What else could be added or improved?

- Performance and command tests would be good to have.
- Better project description.
- Handle office time with minutes precision, ex. 7:30 - 17:30.
- I also played with class method deorators, the solution is a bit over-engineered, but... I couldn't resist.
