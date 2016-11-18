import requests
import json
import sys

token = ""
server = ""

def getClinicalDataCollections():
    global token, server,server
    r = requests.get(url = server + 'dcbia/clinical/collections',
                     headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getClinicalDataCollection(id):
    global token, server
    r = requests.get(url = server + 'dcbia/clinical/collection/' + str(id),
                     headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def createClinicalDataCollection(data):
    global token, server
    r = requests.post(url = server + 'dcbia/clinical/collection', data=data,
                                 headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def updateClinicalDataCollection(data):
    global token, server
    r = requests.put(url = server + 'dcbia/clinical/collection', data=data,
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def deleteClinicalDataCollection(id):
    global token, server
    r = requests.delete(url = server + 'dcbia/clinical/collection/' + str(id),
                           headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getAllClinicalData():
    global token, server
    r = requests.get(url = server + 'dcbia/clinical/collection/data',
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getClinicalData(id):
    global token, server
    r = requests.get(url = server + 'dcbia/clinical/collection/data/' + str(id),
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def createClinicalData(data):
    global token, server
    r = requests.post(url = server + 'dcbia/clinical/data', data=data,
                         headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def updateClinicalData(data):
    global token, server
    r = requests.put(url = server + 'dcbia/clinical/data', data=data,
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def deleteClinicalData(id):
    global token, server
    r = requests.delete(url = server + 'dcbia/clinical/data/' + str(id),
                           headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getMorphologicalDataCollections():
    global token, server
    r = requests.get(url = server + 'dcbia/morphological/collections',
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getMorphologicalDataCollection(id):
    global token, server
    r = requests.get(url = server + 'dcbia/morphological/collection/' + str(id),
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def createMorphologicalDataCollection(data):
    global token, server
    r = requests.post(url = server + 'dcbia/morphological/collection', data=data,
                         headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def updateMorphologicalDataCollection(data):
    global token, server
    r = requests.put(url = server + 'dcbia/morphological/collection', data=data,
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def deleteMorphologicalDataCollection(id):
    global token, server
    r = requests.delete(url = server + 'dcbia/morphological/collection/' + str(id),
                           headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getAllMorphologicalData():
    global token, server
    r = requests.get(url = server + 'dcbia/morphological/collection/data',
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getMorphologicalData(id):
    global token, server
    r = requests.get(url = server + 'dcbia/morphological/collection/data/' + str(id),
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def createMorphologicalData(data):
    global token, server
    r = requests.post(url = server + 'dcbia/morphological/data', data=data,
                         headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def addAttachment(id, filename, data):
    global token, server
    r = requests.put(url = server + 'dcbia/' + str(id) + '/' + str(filename), data=data,
                        headers={
                            'Authorization': 'Bearer ' + token,
                            'Content-Type': 'application/octet-stream'
                        },verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getAttachment(id, filename, responseType):
    global token, server
    r = requests.get(url=server + 'dcbia/' + str(id) + '/' + str(filename),
                     headers={
                         'Authorization': 'Bearer ' + token,
                         'responseType': responseType,
                         'Content-Type': 'application/octet-stream'
                     },
                     stream=True,verify=False)
    return r


def updateMorphologicalData(data):
    global token, server
    r = requests.put(url = server + 'dcbia/morphological/data', data=data,
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def deleteMorphologicalData(id):
    global token, server
    r = requests.delete(url = server + 'dcbia/morphological/data/' + str(id),
                           headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def getMorphologicalDataByPatientId(id):
    global token, server
    r = requests.get(url = server + 'dcbia/morphological/data/patientId/' + str(id),
                        headers={'Authorization': 'Bearer ' + token},verify=False)
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])
            return -1


def connect(email, password):
    global token, server
    payload = {'email': email, 'password': password}

    # Check if the email/password are ok
    try:
        response = requests.post(url = server + 'auth/login', data=json.dumps(payload),
                                 headers={'alg': 'HS256', 'typ': 'JWT'},verify=False)
        token = response.json()['token']
        return token,""
    except KeyError:
        return -1,"Wrong email or password !"
    except requests.exceptions.MissingSchema as e:
        return -1,"Invalid server URL !"



def disconnect():
    global token, server
    token = ''
    server = ''

def getUserScope():
    r = requests.get(url = server + 'auth/user',
                        headers={'Authorization': 'Bearer ' + token}, verify=False)
    return r.json()["scope"]

def getUserEmail():
    r = requests.get(url=server + 'auth/user',
                     headers={'Authorization': 'Bearer ' + token}, verify=False)
    return r.json()["email"]

def setServer(serverParam,serverFilePath):
    global server
    server = serverParam
    file = open(serverFilePath, 'w+')
    file.write(server)
    file.close()

def getServer(serverFilePath):
    global server
    file = open(serverFilePath, 'r')
    first_line = file.readline()
    server = first_line
    file.close()