# ACUP
Alcuin C'est Une Passoire

It was made to sync all the grades from a list of IDs on alcuin.

A light version is available on another branch, it doesn't have any print or discord messaging, you can do a mix of both if you want

# Setup

Install MySQL and use the commands in the createDB file to create the right structure.

It will also create the user and give it it's privileges you can change the user name and password before using the commands.

Install Python3 and download the repo with the git command line or just with the download button.

Go in the folder and install the requirements.

For Linux/Mac:
```
python3 -m pip install -r requirements.txt
```

For Windows:
```
pip -r requirements.txt
```

Change the main.py to fill all the different variables
```
SERVER = "localhost" <-- The address of your database
USER = "" <-- The user with create update and select prevelegies of your DB
PASSWORD = "" <-- The password of your DB
DATABASE = "" <-- The name of your DB
LOGIN="" <-- Your Alcuin login 
PASS=""  <--  Your alcuin password
TOKEN = {'authorization': ''} <-- The token of your discord user or bot
channel=('') <-- The url of the POST request when you send a message to a channel on discord
Elevesclasse = [] <-- List of the student's IDs that you went to get in the retrieveNotes function
```

# Utilisation:

If you don't pass any arguments it will retrive the grades of the students in the list.

Without any students in the list it will not work, you first have to use the Matiere function to fill the DB with your courses names and coeff :

Linux/Mac:
```
python3 main.py Matiere
```
Windows:
```
py main.py Matiere
```
When it's done you can check your DB to see that the courses are ok.
Then you will need to know around wich number your ID and the ones of your class mates have been created.
Add a print(usrId) after the declaration of the variable.
Then use the Noms function to scan around that number :

Linux/Mac:
```
python3 main.py Noms -debut 56000 -fin 57000
```
Windows:
```
py main.py Noms -debut 56000 -fin 57000
```
Then use the list of your class to get the corresponding IDs and fill the Elevesclasse variable with all the IDs.
Use a SELECT * FROM Noms; to see all the names.

Finally you can execute the programm and it will fill the Notes table and notify your group on discord when new grades drop.

# Automation
For Linux/Mac, you can create a crontab like this:
```
0 7,8,9,10,11,12,13,14,15,16,17,18 * * * /home/pi/alcuin/main.py
```
Pour Windows:
Search for Task Scheduler on the internet to see how to launch the main.py every hour.

# Thanks
Thanks to [@lyghtnox](https://github.com/lyghtnox)  for his PACEPO software that helped me getting started.

