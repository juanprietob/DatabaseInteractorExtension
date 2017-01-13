import os,sys
#sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'requests/'))
import requests
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

import json

class ClusterpostLib():
    def __init__(self, parent=None):
        if parent:
            parent.title = " "
        self.server = ""
        self.verify = False
        self.auth = {}

    def setServerUrl(self, server):
        self.server = server

    def setVerifyHttps(self, verify):
        serlf.verify = verify

    def createUser(self):
        r = requests.get(url=self.server + "/auth/user",
                         headers={'Authorization': 'Bearer ' + self.token}, verify=False)
        if "error" not in r.json():
            return r
        else:
            if 'message' in r.json():
                print(r.json()['message'])
                return -1

    def userLogin(self, user):
        
        r = requests.post(url=self.server + "/auth/login",
            json=user,
            verify=self.verify)

        self.auth = JWTAuth(r.json()["token"])

    def setToken(self, token):
        self.auth = JWTAuth(token)
        

    def getExecutionServers(self):
        r = requests.get(url=self.server + "/executionserver",
            auth=self.auth,
            verify=self.verify)

        return r.json()


    def createJob(self, job):
        r = requests.post(url=self.server + "/dataprovider",
            auth=self.auth,
            verify=self.verify,
            json=job)

        return r.json()

    def addAttachment(self, jobid, filename):
        
        basefn = os.path.basename(filename)
        data = open(filename, 'rb')

        r = requests.put(url=self.server + "/dataprovider/" + jobid + "/" + basefn,
            auth=self.auth,
            verify=self.verify,
            headers={"Content-Type": "application/octet-stream"},
            data=data)

        data.close()

        return r.json()

    def getAttachment(self, jobid, name, filename="", responseType=None):

        stream=filename!=""

        r = requests.get(url=self.server + "/dataprovider/" + jobid + "/" + name,
            auth=self.auth,
            verify=self.verify,
            stream=stream,
            headers={
                'responseType': responseType,
                'Content-Type': 'application/octet-stream'
            })

        if(stream):
            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=2048):
                    fd.write(chunk)

        return r

    def executeJob(self, jobid, force=False):
        r = requests.post(url=self.server + "/executionserver/" + jobid,
            auth=self.auth,
            verify=self.verify,
            json={"force":force})

        return r.json()

    def getJobs(self, executable, jobstatus=None, email=None):

        payload={
            "executable": executable
        }

        if(jobstatus):
            payload["jobstatus"] = jobstatus

        if(email):
            payload["email"] = email

        r = requests.get(url=self.server + "/dataprovider/user",
            auth=self.auth,
            verify=self.verify,
            params=payload)

        return r.json()

    def getJob(self, id):
        r = requests.get(url=self.server + "/dataprovider/" + id,
            auth=self.auth,
            verify=self.verify)

        return r.json()


class JWTAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
    # Implement my authentication
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r
