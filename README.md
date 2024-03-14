# QC_SoftTest

# Simple Webbapp using HTML/CSS + Flask For Medical Cost Prediction in USA
This app is designed for Medical Cost prediction in four biggest region in USA.

To setup and run the app. Please refer to following steps.

## To setup the app:

Ensure your device have "pip" installed. Otherwise, please refer to this link and install the pip package first:
https://phoenixnap.com/kb/install-pip-windows

First, open your cmd or console, cd to the QC_SoftTest folder, then run these command lines:

* Some devices won't start installing setuptools automatically. Hence run this command first.
* 
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
