DatabaseInteractor
==================

##What is it?

This extension contains multiple panels that allow the user to manage data from a web database. The data displayed in this extension dynamically reacts with user local folders and online database. The user should login with the same credentials as the server entered as input. That means the user will have exactly the same scope as on the website. Some functionality are restricted to administrators, like creating new patients.
Main functionality are:
- Retrieve data using the patient Id or the patient Id and a date
- Download one or multiple attachments from online database
- Upload data stored in a local folder to the database
- Manage database architecture

This extensions uses **requests** library for python (*http://docs.python-requests.org/en/master/*) that ease doing http requests.

##License

See License.txt for information on using and contributing.

##Source code

Find the source code on [Github](https://github.com/DCBIA-OrthoLab/DatabaseInteractorExtension).