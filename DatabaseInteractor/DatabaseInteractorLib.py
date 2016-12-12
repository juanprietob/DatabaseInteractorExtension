import os,sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'requests/'))
import requests
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import json


class DatabaseInteractorLib():
    def __init__(self, parent=None):
        if parent:
            parent.title = " "
        self.token = ""
        self.server = ""

    def getClinicalDataCollections(self):
        r = requests.get(url=self.server + 'dcbia/clinical/collections',
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getClinicalDataCollection(self, id):

        r = requests.get(url=self.server + 'dcbia/clinical/collection/' + str(id),
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def createClinicalDataCollection(self, data):

        r = requests.post(url=self.server + 'dcbia/clinical/collection', data=data,
                          headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def updateClinicalDataCollection(self, data):

        r = requests.put(url=self.server + 'dcbia/clinical/collection', data=data,
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def deleteClinicalDataCollection(self, id):

        r = requests.delete(url=self.server + 'dcbia/clinical/collection/' + str(id),
                            headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getAllClinicalData(self):

        r = requests.get(url=self.server + 'dcbia/clinical/collection/data',
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getClinicalData(self, id):

        r = requests.get(url=self.server + 'dcbia/clinical/collection/data/' + str(id),
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def createClinicalData(self, data):

        r = requests.post(url=self.server + 'dcbia/clinical/data', data=data,
                          headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def updateClinicalData(self, data):

        r = requests.put(url=self.server + 'dcbia/clinical/data', data=data,
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def deleteClinicalData(self, id):

        r = requests.delete(url=self.server + 'dcbia/clinical/data/' + str(id),
                            headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getMorphologicalDataCollections(self):

        r = requests.get(url=self.server + 'dcbia/morphological/collections',
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getMorphologicalDataCollection(self, id):

        r = requests.get(url=self.server + 'dcbia/morphological/collection/' + str(id),
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def createMorphologicalDataCollection(self, data):

        r = requests.post(url=self.server + 'dcbia/morphological/collection', data=data,
                          headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def updateMorphologicalDataCollection(self, data):

        r = requests.put(url=self.server + 'dcbia/morphological/collection', data=data,
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def deleteMorphologicalDataCollection(self, id):

        r = requests.delete(url=self.server + 'dcbia/morphological/collection/' + str(id),
                            headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getAllMorphologicalData(self):

        r = requests.get(url=self.server + 'dcbia/morphological/collection/data',
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getMorphologicalData(self, id):

        r = requests.get(url=self.server + 'dcbia/morphological/collection/data/' + str(id),
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def createMorphologicalData(self, data):

        r = requests.post(url=self.server + 'dcbia/morphological/data', data=data,
                          headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def addAttachment(self, id, filename, data):

        r = requests.put(url=self.server + 'dcbia/' + str(id) + '/' + str(filename), data=data,
                         headers={
                             'Authorization': 'Bearer ' + self.token,
                             'Content-Type': 'application/octet-stream'
                         }, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getAttachment(self, id, filename, responseType):

        r = requests.get(url=self.server + 'dcbia/' + str(id) + '/' + str(filename),
                         headers={
                             'Authorization': 'Bearer ' + self.token,
                             'responseType': responseType,
                             'Content-Type': 'application/octet-stream'
                         },
                         stream=True, verify=False)
        return r

    def updateMorphologicalData(self, data):

        r = requests.put(url=self.server + 'dcbia/morphological/data', data=data,
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def deleteMorphologicalData(self, id):

        r = requests.delete(url=self.server + 'dcbia/morphological/data/' + str(id),
                            headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def getMorphologicalDataByPatientId(self, id):

        r = requests.get(url=self.server + 'dcbia/morphological/data/patientId/' + str(id),
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def connect(self, email, password):

        payload = {'email': email, 'password': password}

        # Check if the email/password are ok
        try:
            response = requests.post(url=self.server + 'auth/login', data=json.dumps(payload),
                                     headers={'alg': 'HS256', 'typ': 'JWT'}, verify=False)
            self.token = response.json()['token']
            return self.token, ""
        except KeyError:
            return -1, "Wrong email or password !"
        except requests.exceptions.MissingSchema as e:
            return -1, "Invalid server URL !"

    def disconnect(self):

        self.token = ''
        self.server = ''

    def getUserScope(self):
        r = requests.get(url=self.server + 'auth/user',
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        return r.json()["scope"]

    def getUserEmail(self):
        r = requests.get(url=self.server + 'auth/user',
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        return r.json()["email"]

    def setServer(self, serverParam, serverFilePath):
        self.server = serverParam
        file = open(serverFilePath, 'w+')
        file.write(self.server)
        file.close()

    def getServer(self, serverFilePath):
        file = open(serverFilePath, 'r')
        first_line = file.readline()
        self.server = first_line
        file.close()
