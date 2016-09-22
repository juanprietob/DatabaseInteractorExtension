import requests
import json
import sys

token = ""

def getClinicalDataCollections():
    global token
    r = requests.get(url='http://localhost:8180/dcbia/clinical/collections',
                     headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print(r.json()['message'])


def getClinicalDataCollection(id):
    global token
    r = requests.get(url='http://localhost:8180/dcbia/clinical/collection/' + str(id),
                     headers={'Authorization': 'Bearer ' + token})
    if "error" in r.json():
        sys.exit("Collection " + str(id) + " " + r.json()['error'])
    else:
        return r


def createClinicalDataCollection(data):
    global token
    r = requests.post(url='http://localhost:8180/dcbia/clinical/collection', data=data,
                                 headers={'Authorization': 'Bearer ' + token})
    if "error" in r.json():
        sys.exit(r.json()['message'])
    else:
        return r


def updateClinicalDataCollection(data):
    global token
    r = requests.put(url='http://localhost:8180/dcbia/clinical/collection', data=data,
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def deleteClinicalDataCollection(id):
    global token
    r = requests.delete(url='http://localhost:8180/dcbia/clinical/collection/' + str(id),
                           headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getAllClinicalData():
    global token
    r = requests.get(url='http://localhost:8180/dcbia/clinical/collection/data',
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getClinicalData(id):
    global token
    r = requests.get(url='http://localhost:8180/dcbia/clinical/collection/data/' + str(id),
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def createClinicalData(data):
    global token
    r = requests.post(url='http://localhost:8180/dcbia/clinical/data', data=data,
                         headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def updateClinicalData(data):
    global token
    r = requests.put(url='http://localhost:8180/dcbia/clinical/data', data=data,
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def deleteClinicalData(id):
    global token
    r = requests.delete(url='http://localhost:8180/dcbia/clinical/data/' + str(id),
                           headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getMorphologicalDataCollections():
    global token
    r = requests.get(url='http://localhost:8180/dcbia/morphological/collections',
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getMorphologicalDataCollection(id):
    global token
    r = requests.get(url='http://localhost:8180/dcbia/morphological/collection/' + str(id),
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def createMorphologicalDataCollection(data):
    global token
    r = requests.post(url='http://localhost:8180/dcbia/morphological/collection', data=data,
                         headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def updateMorphologicalDataCollection(data):
    global token
    r = requests.put(url='http://localhost:8180/dcbia/morphological/collection', data=data,
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            print r.json()['message']


def deleteMorphologicalDataCollection(id):
    global token
    r = requests.delete(url='http://localhost:8180/dcbia/morphological/collection/' + str(id),
                           headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getAllMorphologicalData():
    global token
    r = requests.get(url='http://localhost:8180/dcbia/morphological/collection/data',
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getMorphologicalData(id):
    global token
    r = requests.get(url='http://localhost:8180/dcbia/morphological/collection/data/' + str(id),
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def createMorphologicalData(data):
    global token
    r = requests.post(url='http://localhost:8180/dcbia/morphological/data', data=data,
                         headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def addAttachement(id, filename, data):
    global token
    r = requests.put(url='http://localhost:8180/dcbia/' + str(id) + '/' + str(filename), data=data,
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getAttachement(id, filename, responseType):
    global token
    r = requests.get(url='http://localhost:8180/dcbia/' + str(id) + '/' + str(filename),
                        headers={'Authorization': 'Bearer ' + token})
    return r
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def updateMorphologicalData(data):
    global token
    r = requests.put(url='http://localhost:8180/dcbia/morphological/data', data=data,
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def deleteMorphologicalData(id):
    global token
    r = requests.delete(url='http://localhost:8180/dcbia/morphological/data/' + str(id),
                           headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def getMorphologicalDataByPatientId(id):
    global token
    r = requests.get(url='http://localhost:8180/dcbia/morphological/data/patientId/' + str(id),
                        headers={'Authorization': 'Bearer ' + token})
    if "error" not in r.json():
        return r
    else:
        if 'message' in r.json():
            sys.exit(r.json()['message'])


def connect(email, password):
    global token
    payload = {'email': email, 'password': password}

    # Check if the email/password are ok
    try:
        response = requests.post(url='http://localhost:8180/auth/login', data=json.dumps(payload),
                                 headers={'alg': 'HS256', 'typ': 'JWT'})
        token = response.json()['token']
        return token
    except KeyError:
        print ("Wrong email or password !")
        return -1


def disconnect():
    global token
    token = ''
