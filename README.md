# QC_SoftTest

# Simple Webbapp using HTML/CSS + Flask For Medical Cost Prediction in USA
# SQL SERVER powered for database
This app is designed for Medical Cost prediction in four biggest regions in USA.

To setup and run the app. Please refer to following steps.

## To setup the app:

Ensure your device have "pip" installed. Otherwise, please refer to this link and install the pip package:
https://phoenixnap.com/kb/install-pip-windows

First, open your cmd or console, cd to the QC_SoftTest folder, then run these command lines:

* Some devices won't start installing setuptools automatically. Hence run this command first.

```bash
pip install setuptools
```

Then run this:

```bash
pip install -r requirements.txt
```

To have database attached. First, please run the given .sql file to create database and its corresponding tables.
If you are authorizing your database as window authentication, then UserID and Password for connection are unnecessary.
For more information, please refer to app.py

To run the app:

```bash
python run app.py
```
If the above command line not work, then run this instead:

```bash
python app.py
```

* It would be nice if you can use your virtual environment to host the webapp independently.
All steps are the same as mentioned above.

TODO List (it isn't completed, other features may added or changed.)
* <s>Attach to database</s>
* <s>Feature 1: A function that counts total uses of webbapp in real-time. The output should expect related things to display in frontend.</s>
* <s>Feature 2: A function that displays a graph for monitoringtotal uses over time. The output should expect a graph displayed in frontend.</s>
* Feature 3: A function that collects information of provided users and stores to database.
* Feature 4: A function for user to login.
