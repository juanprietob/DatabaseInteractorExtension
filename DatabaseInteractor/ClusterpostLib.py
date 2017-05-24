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
        self.user = None

    def setServerUrl(self, server):
        self.server = server

    def setVerifyHttps(self, verify):
        self.verify = verify


    def getUser(self):
        if(self.user == None):

            r = requests.get(url=self.server + "/auth/user",
                auth=self.auth,
                verify=False)

            self.user = r.json()
        return self.user

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

    def getJobs(self, executable=None, jobstatus=None, email=None):

        payload={}

        if(executable):
            payload["executable"] = executable

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

    def createAndSubmitJob(self, job, files):
        res = self.createJob(job)
        
        jobid = res["id"]

        for file in files:
            self.addAttachment(jobid, file)

        return self.executeJob(jobid)

    def getJobsDone(self, outdir):
        res = self.getJobs(jobstatus="DONE")
        for job in res:
            outputs = job["outputs"]

            jobname = job["_id"]
            
            key = "name"

            if(key in job):
                jobname = job["name"]

            outputdir = os.path.join(outdir, jobname)
            
            if(not os.path.exists(outputdir)):
                os.mkdir(outputdir)

            for output in outputs:
                if(output["type"] == "file"):
                    self.getAttachment(job["_id"], output["name"], os.path.join(outputdir, output["name"]), "blob")

    def updateJobStatus(self, jobid, status):
        res = self.getJob(jobid)
        res["jobstatus"] = {
            "status": status
        }
        r = requests.put(url=self.server + "/dataprovider",
            auth=self.auth,
            verify=self.verify,
            data=json.dumps(res))

        return r.json()


class JWTAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
    # Implement my authentication
        r.headers['Authorization'] = 'Bearer ' + self.token
        return r
