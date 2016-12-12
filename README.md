DatabaseInteractor
==================

##What is it?

This extension contains multiple panels that allow the user to manage data from a CouchDB database stored on a server. It has been developed to work with this [website](https://ec2-52-42-49-63.us-west-2.compute.amazonaws.com:8180/DCBIA-OrthoLab/public/), so the user will need to have an account on the website. 
The data currently stored on this website is for a pilot study which needs to federate biological, morphological and clinical data. At the end of the development of the website, this should be available for other projects. 
For more information about the website status, contact *juanprietob@gmail.com*. The data displayed in this extension dynamically reacts with user local folders and online database. The user should login with the same credentials as the server entered as input. That means the user will have exactly the same scope as on the website. Some functionalities are restricted to administrators, like creating new patients.

Main functionalities are:
- Retrieve data using the patient Id or the patient Id and a date
- Download one or multiple attachments from online database
- Upload data stored in a local folder to the database
- Manage database architecture

##Technologies used
This extensions uses **requests** library for python (*http://docs.python-requests.org/en/master/*) that ease doing http requests.
For more information about the website linked to this project, visit [Github](https://github.com/NIRALUser/shiny-tooth).

##License

See License.txt for information on using and contributing.

##Source code

Find the source code on [Github](https://github.com/DCBIA-OrthoLab/DatabaseInteractorExtension).
