import os, sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import myLib
import json


#
# DatabaseInteractor
#

class DatabaseInteractor(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Database Interactor"
        self.parent.categories = ["Developement"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Clement Mirabel (University of Michigan)"]
        self.parent.helpText = """
    To be completed.
    """
        self.parent.acknowledgementText = """
    To be completed.
"""


#
# DatabaseInteractorWidget
#

class DatabaseInteractorWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # ---------------------------------------------------------------- #
        # ------------------------ Global variables ---------------------- #
        # ---------------------------------------------------------------- #

        self.connected = False
        self.collections = dict()
        self.morphologicalData = dict()
        self.tokenFilePath = slicer.app.temporaryPath + '/user.slicer_token'
        self.serverFilePath = slicer.app.temporaryPath + '/user.slicer_server'
        self.moduleName = 'DatabaseInteractor'
        scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)

        # ---------------------------------------------------------------- #
        # ---------------- Definition of the UI interface ---------------- #
        # ---------------------------------------------------------------- #

        # --------------------------------------------------- #
        # --- Definition of connection collapsible button --- #
        # --------------------------------------------------- #
        # Collapsible button
        self.connectionCollapsibleButton = ctk.ctkCollapsibleButton()
        self.connectionCollapsibleButton.text = "Authentication"
        self.layout.addWidget(self.connectionCollapsibleButton)
        self.connectionVBoxLayout = qt.QVBoxLayout(self.connectionCollapsibleButton)

        # - GroupBox containing Server, Email and Password Inputs - #
        self.connectionGroupBox = qt.QGroupBox("Login")
        self.connectionGroupBoxLayout = qt.QFormLayout(self.connectionGroupBox)
        self.connectionVBoxLayout.addWidget(self.connectionGroupBox)

        # Server input
        self.serverInput = qt.QLineEdit()
        self.serverInput.text = 'http://localhost:8180/'
        self.connectionGroupBoxLayout.addRow("Server address: ", self.serverInput)

        # Email input
        self.emailInput = qt.QLineEdit()
        self.emailInput.text = ''
        self.connectionGroupBoxLayout.addRow("Email address: ", self.emailInput)

        # Password input
        self.passwordInput = qt.QLineEdit()
        self.passwordInput.text = ''
        self.passwordInput.setEchoMode(qt.QLineEdit.Password)
        self.connectionGroupBoxLayout.addRow("Password: ", self.passwordInput)

        # Error Login Label
        self.errorLoginText = qt.QLabel()
        self.errorLoginText.setStyleSheet("color: rgb(255, 0, 0);")
        self.connectionGroupBoxLayout.addWidget(self.errorLoginText)
        self.errorLoginText.hide()

        # Connection Button
        self.connectionButton = qt.QPushButton("Connect")
        self.connectionButton.toolTip = "Connect to the server."
        self.connectionButton.enabled = False
        self.connectionVBoxLayout.addWidget(self.connectionButton)

        # Disconnection Button
        self.disconnectionButton = qt.QPushButton("Disconnect")
        self.disconnectionButton.toolTip = "Disconnect to the server."
        self.connectionVBoxLayout.addWidget(self.disconnectionButton)
        self.disconnectionButton.hide()

        # ------------------------------------------------- #
        # --- Definition of download collapsible button --- #
        # ------------------------------------------------- #
        # Collapsible button
        self.downloadCollapsibleButton = ctk.ctkCollapsibleButton()
        self.downloadCollapsibleButton.text = "Download data"
        self.layout.addWidget(self.downloadCollapsibleButton, 0)
        self.downloadFormLayout = qt.QFormLayout(self.downloadCollapsibleButton)
        self.downloadCollapsibleButton.hide()

        # Query type selector groupBox
        self.queryTypeGroupBox = qt.QGroupBox("Find data with:")
        self.queryTypeGroupBoxLayout = qt.QHBoxLayout(self.queryTypeGroupBox)

        # RadioButtons choices
        self.downloadRadioButtonPatientOnly = qt.QRadioButton("PatientId only")
        self.downloadRadioButtonPatientOnly.setChecked(True)
        self.downloadRadioButtonPatientDate = qt.QRadioButton("PatientId and date")
        self.queryTypeGroupBoxLayout.addWidget(self.downloadRadioButtonPatientOnly)
        self.queryTypeGroupBoxLayout.addWidget(self.downloadRadioButtonPatientDate)
        self.downloadFormLayout.addRow(self.queryTypeGroupBox)

        # Directory Button
        self.downloadFilepathSelector = ctk.ctkDirectoryButton()
        self.downloadFilepathSelector.toolTip = "Choose a path to save the model."
        self.downloadFormLayout.addRow(qt.QLabel("Choose a destination: "), self.downloadFilepathSelector)

        # Collection Selector
        self.downloadCollectionSelector = qt.QComboBox()
        self.downloadCollectionSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose a collection: ", self.downloadCollectionSelector)

        # Download entire collection Button
        self.downloadCollectionButton = qt.QPushButton("Download the entire collection")
        self.downloadCollectionButton.toolTip = "Download the whole collection in a folder."
        self.downloadFormLayout.addWidget(self.downloadCollectionButton)
        self.downloadCollectionButton.enabled = False

        # Patient Selector
        self.downloadPatientSelector = qt.QComboBox()
        self.downloadPatientSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose a patient: ", self.downloadPatientSelector)
        self.downloadPatientSelector.setDuplicatesEnabled(True)

        # Date Selector
        self.downloadDate = qt.QCalendarWidget()
        self.downloadDate.setStyleSheet(
            "QCalendarWidget QWidget#qt_calendar_navigationbar{background-color:rgb(200,200,200);}"
            "QCalendarWidget QWidget#qt_calendar_nextmonth{"
            "qproperty-icon: url(" + scriptedModulesPath + "/Resources/Icons/ArrowRight.png);"
            "qproperty-iconSize: 10px;width:20px;}"
            "QCalendarWidget QWidget#qt_calendar_prevmonth{"
            "qproperty-icon: url(" + scriptedModulesPath + "/Resources/Icons/ArrowLeft.png);"
            "qproperty-iconSize: 10px;width:20px;}"
            "QCalendarWidget QToolButton{height:25px;width:90px;color:black;icon-size:25px,25px;"
            "background-color:rgb(200,200,200);}"
            "QCalendarWidget QMenu{width:125px;background-color:rgb(200,200,200);}"
            "QCalendarWidget QSpinBox{width:65px;background-color:rgb(200,200,200);"
            "selection-background-color:rgb(200,200,200);selection-color:black;}"
            "QCalendarWidget QWidget{alternate-background-color:rgb(225,225,225);}"
            "QCalendarWidget QAbstractItemView:enabled{color:rgb(100,100,100);"
            "selection-background-color:rgb(200,200,200);selection-color:white;}"
            "QCalendarWidget QAbstractItemView:disabled {color: rgb(200, 200, 200);}")
        self.downloadDateLabel = qt.QLabel("Choose a date: ")
        self.downloadFormLayout.addRow(self.downloadDateLabel, self.downloadDate)
        self.downloadDateLabel.hide()
        self.downloadDate.hide()

        # Attachment selector
        self.downloadAttachmentSelector = qt.QComboBox()
        self.downloadAttachmentSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose an attachment: ", self.downloadAttachmentSelector)

        # Error download Label
        self.downloadErrorText = qt.QLabel("No file found for this date !")
        self.downloadErrorText.setStyleSheet("color: rgb(255, 0, 0);")
        self.downloadFormLayout.addWidget(self.downloadErrorText)
        self.downloadErrorText.hide()

        # Download Button
        self.downloadButton = qt.QPushButton("Download selected attachment")
        self.downloadButton.toolTip = "Download patient data."
        self.downloadFormLayout.addRow(self.downloadButton)
        self.downloadButton.enabled = False

        # ----------------------------------------------- #
        # --- Definition of upload collapsible button --- #
        # ----------------------------------------------- #
        # Collapsible button
        self.uploadCollapsibleButton = ctk.ctkCollapsibleButton()
        self.uploadCollapsibleButton.text = "Upload data"
        self.layout.addWidget(self.uploadCollapsibleButton, 0)
        self.uploadFormLayout = qt.QFormLayout(self.uploadCollapsibleButton)
        self.uploadCollapsibleButton.hide()

        # Directory Button
        self.uploadFilepathSelector = ctk.ctkDirectoryButton()
        self.uploadFilepathSelector.toolTip = "Choose the path to the folder where you saved patient files."
        self.uploadFormLayout.addRow(qt.QLabel("Choose collection folder: "), self.uploadFilepathSelector)

        # ListView of the differences between local folder and online database
        self.uploadListView = qt.QListWidget()
        self.uploadFormLayout.addRow("Modified files: ", self.uploadListView)

        # Volume selector
        # self.modelSelector = slicer.qMRMLNodeComboBox()
        # self.modelSelector.nodeTypes = (("vtkMRMLModelNode"), "")
        # self.modelSelector.addEnabled = False
        # self.modelSelector.removeEnabled = False
        # self.modelSelector.setMRMLScene(slicer.mrmlScene)
        # self.uploadFormLayout.addRow("Choose a model: ", self.modelSelector)

        # Upload Button
        self.uploadButton = qt.QPushButton("Upload")
        self.uploadButton.toolTip = "Upload patient data."
        self.uploadFormLayout.addRow(self.uploadButton)
        self.uploadButton.enabled = False

        # ----------------------------------------------- #
        # - Definition of management collapsible button - #
        # ----------------------------------------------- #
        # Collapsible button
        self.managementCollapsibleButton = ctk.ctkCollapsibleButton()
        self.managementCollapsibleButton.text = "Management"
        self.layout.addWidget(self.managementCollapsibleButton, 0)
        self.managementFormLayout = qt.QFormLayout(self.managementCollapsibleButton)
        self.managementCollapsibleButton.hide()

        # Creation type selector groupBox
        self.creationTypeGroupBox = qt.QGroupBox("Action wanted:")
        self.creationTypeGroupBoxLayout = qt.QHBoxLayout(self.creationTypeGroupBox)

        # RadioButtons choice
        self.managementRadioButtonPatient = qt.QRadioButton("Create PatientId")
        self.managementRadioButtonPatient.setChecked(True)
        self.managementRadioButtonDate = qt.QRadioButton("Add a new date")
        self.creationTypeGroupBoxLayout.addWidget(self.managementRadioButtonPatient)
        self.creationTypeGroupBoxLayout.addWidget(self.managementRadioButtonDate)
        self.managementFormLayout.addRow(self.creationTypeGroupBox)

        # Directory Button
        self.managementFilepathSelector = ctk.ctkDirectoryButton()
        self.managementFilepathSelector.toolTip = "Choose the path to the folder where you saved patient files."
        self.managementFormLayout.addRow(qt.QLabel("Choose collection folder: "), self.managementFilepathSelector)

        # Patient name input
        self.newPatientIdInput = qt.QLineEdit()
        self.newPatientIdInput.text = ''
        self.newPatientIdInputLabel = qt.QLabel("Enter PatiendId: ")
        self.managementFormLayout.addRow(self.newPatientIdInputLabel, self.newPatientIdInput)

        # Patient Selector
        self.managementPatientSelector = qt.QComboBox()
        self.managementPatientSelector.addItem("None")
        self.managementPatientSelectorLabel = qt.QLabel("Choose a patient: ")
        self.managementFormLayout.addRow(self.managementPatientSelectorLabel, self.managementPatientSelector)
        self.managementPatientSelector.hide()
        self.managementPatientSelectorLabel.hide()

        # Date Selector
        self.createDate = qt.QCalendarWidget()
        self.createDate.setStyleSheet(
            "QCalendarWidget QWidget#qt_calendar_navigationbar{background-color:rgb(200,200,200);}"
            "QCalendarWidget QWidget#qt_calendar_nextmonth{"
            "qproperty-icon: url(" + scriptedModulesPath + "/Resources/Icons/ArrowRight.png);"
            "qproperty-iconSize: 10px;width:20px;}"
            "QCalendarWidget QWidget#qt_calendar_prevmonth{"
            "qproperty-icon: url(" + scriptedModulesPath + "/Resources/Icons/ArrowLeft.png);"
            "qproperty-iconSize: 10px;width:20px;}"
            "QCalendarWidget QToolButton{height:25px;width:90px;color:black;icon-size:25px,25px;"
            "background-color:rgb(200,200,200);}"
            "QCalendarWidget QMenu{width:125px;background-color:rgb(200,200,200);}"
            "QCalendarWidget QSpinBox{width:65px;background-color:rgb(200,200,200);"
            "selection-background-color:rgb(200,200,200);selection-color:black;}"
            "QCalendarWidget QWidget{alternate-background-color:rgb(225,225,225);}"
            "QCalendarWidget QAbstractItemView:enabled{color:rgb(100,100,100);"
            "selection-background-color:rgb(200,200,200);selection-color:white;}"
            "QCalendarWidget QAbstractItemView:disabled {color: rgb(200, 200, 200);}")
        self.createDateLabel = qt.QLabel("Choose a date: ")
        self.managementFormLayout.addRow(self.createDateLabel, self.createDate)

        # Patient & Date Creator Button
        self.createButton = qt.QPushButton("Create patient Id")
        self.createButton.enabled = False
        self.managementFormLayout.addRow(self.createButton)

        # Add vertical spacer
        self.layout.addStretch(1)

        # --------------------------------------------------------- #
        # ----------------------- Signals ------------------------- #
        # --------------------------------------------------------- #

        # Buttons
        self.connectionButton.connect('clicked(bool)', self.onConnectionButton)
        self.disconnectionButton.connect('clicked(bool)', self.onDisconnectionButton)
        self.downloadButton.connect('clicked(bool)', self.onDownloadButton)
        self.downloadCollectionButton.connect('clicked(bool)',self.onDownloadCollectionButton)
        self.uploadButton.connect('clicked(bool)', self.onUploadButton)
        self.createButton.connect('clicked(bool)',self.onCreateButton)

        # Radio Buttons
        self.downloadRadioButtonPatientOnly.toggled.connect(self.onRadioButtontoggled)
        self.downloadRadioButtonPatientDate.toggled.connect(self.onRadioButtontoggled)
        self.managementRadioButtonDate.toggled.connect(self.onManagementRadioButtontoggled)
        self.managementRadioButtonPatient.toggled.connect(self.onManagementRadioButtontoggled)

        # Inputs
        self.emailInput.textChanged.connect(self.onInputChanged)
        self.passwordInput.textChanged.connect(self.onInputChanged)
        self.newPatientIdInput.textChanged.connect(self.isPossibleCreatePatient)

        # ComboBoxes
        self.downloadCollectionSelector.connect('currentIndexChanged(const QString&)',self.fillSelectorWithPatients)
        self.downloadPatientSelector.connect('currentIndexChanged(const QString&)', self.onDownloadPatientChosen)
        self.managementPatientSelector.connect('currentIndexChanged(const QString&)', self.isPossibleAddDate)

        # Calendar
        self.downloadDate.connect('clicked(const QDate&)',self.fillSelectorWithAttachments)

        # FilePath selectors
        self.uploadFilepathSelector.connect('directorySelected(const QString &)', self.checkUploadDifferences)
        self.managementFilepathSelector.connect('directorySelected(const QString &)', self.onManagementDirectorySelected)

        # --- Try to connect when launching the module --- #
        file = open(self.tokenFilePath, 'r')
        first_line = file.readline()
        myLib.getServer(self.serverFilePath)
        if first_line != "":
            # self.token = first_line
            myLib.token = first_line
            self.connected = True
            self.connectionGroupBox.hide()
            self.connectionButton.hide()
            self.disconnectionButton.show()
            self.fillSelectorWithCollections()
            self.downloadCollapsibleButton.show()
            self.uploadCollapsibleButton.show()
            if myLib.getUserScope() > 2:
                self.managementCollapsibleButton.show()

        file.close()

    def cleanup(self):
        pass

    # Function used to connect user to the database and store token in a file
    def onConnectionButton(self):
        myLib.setServer(self.serverInput.text,self.serverFilePath)
        token,error = myLib.connect(self.emailInput.text, self.passwordInput.text)
        if token != -1 and myLib.getUserScope() >= 2:
            # Write the token in a temporary file
            file = open(self.tokenFilePath, 'w+')
            file.write(token)
            file.close()
            self.connected = True
            self.connectionGroupBox.hide()
            self.connectionButton.hide()
            self.disconnectionButton.show()
            self.fillSelectorWithCollections()
            self.downloadCollapsibleButton.show()
            self.uploadCollapsibleButton.show()
            self.managementCollapsibleButton.show()
            if myLib.getUserScope() < 3:
                self.managementCollapsibleButton.hide()
        elif token == -1:
            self.errorLoginText.text = error
            self.errorLoginText.show()
        else:
            self.errorLoginText.text = "Insufficient scope ! Email luciacev@umich.edu for access."
            self.errorLoginText.show()

    # Function used to disconnect user to the database
    def onDisconnectionButton(self):
        myLib.disconnect()
        self.connected = False
        self.passwordInput.text = ''
        self.connectionGroupBox.show()
        self.connectionButton.show()
        self.errorLoginText.hide()
        self.disconnectionButton.hide()
        self.downloadCollapsibleButton.hide()
        self.uploadCollapsibleButton.hide()
        self.managementCollapsibleButton.hide()
        # Erase token from file
        with open(self.tokenFilePath, "w"):
            pass

    def onRadioButtontoggled(self):
        self.downloadErrorText.hide()
        self.fillSelectorWithAttachments()
        if self.downloadRadioButtonPatientOnly.isChecked():
            self.downloadDateLabel.hide()
            self.downloadDate.hide()
        else:
            self.downloadDateLabel.show()
            self.downloadDate.show()

    def onManagementRadioButtontoggled(self):
        if self.managementRadioButtonPatient.isChecked():
            self.managementPatientSelector.hide()
            self.managementPatientSelectorLabel.hide()
            self.newPatientIdInput.show()
            self.newPatientIdInputLabel.show()
            self.createButton.setText("Create this patientId")
            self.isPossibleCreatePatient()
        else:

            self.fillSelectorWithDescriptorPatients()
            self.newPatientIdInput.hide()
            self.newPatientIdInputLabel.hide()
            self.managementPatientSelector.show()
            self.managementPatientSelectorLabel.show()
            self.createButton.setText("Add this date")
            self.isPossibleAddDate()


    # Function used to download data with information provided
    def onDownloadButton(self):
        for items in self.morphologicalData:
            if items["_attachments"].keys()[0] == self.downloadAttachmentSelector.currentText:
                documentId = items["_id"]
        data = myLib.getAttachment(documentId, self.downloadAttachmentSelector.currentText, None).text
        # Write the attachment in a file
        filePath = self.downloadFilepathSelector.directory + '/' + self.downloadAttachmentSelector.currentText
        file = open(filePath, 'w+')
        file.write(data)
        file.close()

        # Load the file
        slicer.util.loadModel(filePath)

    # Function used to download an entire collection and organise it with folders
    def onDownloadCollectionButton(self):
        collectionPath = self.downloadFilepathSelector.directory + '/' + self.downloadCollectionSelector.currentText
        # Check if folder already exists
        if not os.path.exists(collectionPath):
            os.makedirs(collectionPath)
        index = 0

        # Write collection document
        for items in myLib.getMorphologicalDataCollections().json():
            if items["name"] == self.downloadCollectionSelector.currentText:
                collectionId = items["_id"]
        descriptor = {
            "_id": collectionId,
            "type": "morphologicalDataCollection",
            "items": {}
        }

        # Create a folder for each patient
        while index < self.downloadPatientSelector.count:
            if self.downloadPatientSelector.itemText(index) != "None":
                descriptor["items"][self.downloadPatientSelector.itemText(index)] = {}
                if not os.path.exists(collectionPath + "/" + self.downloadPatientSelector.itemText(index)):
                    os.makedirs(collectionPath + "/" + self.downloadPatientSelector.itemText(index))
            index += 1

        # Fill the folders with attachments
        for items in self.morphologicalData:
            if "_attachments" in items:
                documentId = items["_id"]
                attachmentName = items["_attachments"].keys()[0]
                patientId = items["patientId"]
                date = items["date"]
                descriptor["items"][patientId][date[:10]] = collectionPath + "/" + patientId + "/" + date[:10] + "/.DBIDescriptor"

                if not os.path.exists(collectionPath + "/" + patientId + "/" + date[:10]):
                    os.makedirs(collectionPath + "/" + patientId + "/" + date[:10])
                data = myLib.getAttachment(documentId, attachmentName, None).text
                # Save the document
                file = open(collectionPath + '/' + patientId + '/' + date[:10] + '/.DBIDescriptor','w+')
                json.dump(items, file, indent=3, sort_keys=True)
                file.close()

                # Save the attachment
                file = open(collectionPath + '/' + patientId + '/' + date[:10] + '/' + attachmentName,'w+')
                file.write(data)
                file.close()

        file = open(collectionPath + '/.DBIDescriptor', 'w+')
        json.dump(descriptor,file, indent=3, sort_keys=True)
        file.close()
        self.uploadFilepathSelector.directory = collectionPath
        self.managementFilepathSelector.directory = collectionPath

    # Function used to upload a data to the correct patient
    def onUploadButton(self):
        collection = self.uploadFilepathSelector.directory[self.uploadFilepathSelector.directory.rfind("/") + 1:]
        # Create new patients in DB
        for newPatientId in self.newPatientsList:
            data = {"patientId": newPatientId, "type": "morphologicalData"}
            id = myLib.createMorphologicalData(data).json()["id"]
            for items in self.collections:
                if items["name"] == collection:
                    collectionJson = myLib.getMorphologicalDataCollection(items["_id"]).json()
            collectionJson["items"].append({'_id': id})
            myLib.updateMorphologicalDataCollection(json.dumps(collectionJson))
            # Refill the patient selector
            self.fillSelectorWithPatients()
        # Add new attachments to patient

    def onCreateButton(self):
        collectionPath = self.managementFilepathSelector.directory
        patientId = self.managementPatientSelector.currentText
        date = str(self.createDate.selectedDate)
        collection = self.managementFilepathSelector.directory[self.managementFilepathSelector.directory.rfind("/") + 1:]

        # Check if it is a new patient
        if self.managementRadioButtonPatient.isChecked():
            patientId = self.newPatientIdInput.text

        # Add to database
        owner = myLib.getUserEmail()
        data = {
            "patientId": patientId,
            "date": date,
            "owners": [{"user": owner}],
            "type": "morphologicalData",
        }
        docId = myLib.createMorphologicalData(json.dumps(data)).json()["id"]
        for items in self.collections:
            if items["name"] == collection:
                collectionJson = myLib.getMorphologicalDataCollection(items["_id"]).json()
        collectionJson["items"].append({'_id': docId})
        myLib.updateMorphologicalDataCollection(json.dumps(collectionJson))

        # Create date folder
        if not os.path.exists(collectionPath + "/" + patientId + "/" + date):
            os.makedirs(collectionPath + "/" + patientId + "/" + date)

        # Write descriptor
        for items in myLib.getMorphologicalData(collectionJson["_id"]).json():
            if items["_id"] == docId:
                file = open(collectionPath + '/' + patientId + '/' + date + '/.DBIDescriptor', 'w+')
                json.dump(items, file, indent=3, sort_keys=True)
                file.close()

        # Update collection descriptor
        file = open(collectionPath + '/.DBIDescriptor','r')
        jsonfile = json.load(file)
        file.close()
        if patientId not in jsonfile["items"]:
            jsonfile["items"][patientId] = {}
        jsonfile["items"][patientId][date] = collectionPath + '/' + patientId + '/' + date + '/.DBIDescriptor'
        file = open(collectionPath + '/.DBIDescriptor','w+')
        json.dump(jsonfile,file, indent=3, sort_keys=True)
        file.close()
        self.fillSelectorWithPatients()

    # Function used to enable the connection button if userlogin and password are provided
    def onInputChanged(self):
        self.connectionButton.enabled = (len(self.emailInput.text) != 0 and len(self.passwordInput.text) != 0)

    # Function used to fill the comboBoxes with morphologicalCollections
    def fillSelectorWithCollections(self):
        self.collections = myLib.getMorphologicalDataCollections().json()
        self.downloadCollectionSelector.clear()
        for items in self.collections:
            self.downloadCollectionSelector.addItem(items["name"])
        if self.downloadCollectionSelector.count == 0:
            self.downloadCollectionSelector.addItem("None")

    # Function used to fill the comboBox with patientId corresponding to the collection selected
    def fillSelectorWithPatients(self):
        text = self.downloadCollectionSelector.currentText
        self.downloadButton.enabled = text
        if text != "None":
            self.downloadCollectionButton.enabled = True
            # Get the patientIds in the selected collection
            for items in self.collections:
                if items["name"] == text:
                    self.morphologicalData = myLib.getMorphologicalData(items["_id"]).json()
            self.downloadPatientSelector.clear()
            for items in self.morphologicalData:
                if self.downloadPatientSelector.findText(items["patientId"]) ==-1:
                    self.downloadPatientSelector.addItem(items["patientId"])
            if self.downloadPatientSelector.count == 0:
                self.downloadPatientSelector.addItem("None")
        self.downloadPatientSelector.model().sort(0)
        self.downloadPatientSelector.setCurrentIndex(0)

    def fillSelectorWithDescriptorPatients(self):
        directoryPath = self.managementFilepathSelector.directory
        self.managementPatientSelector.clear()
        if os.path.exists(directoryPath + '/.DBIDescriptor'):
            file = open(directoryPath + '/.DBIDescriptor')
            collectionDescriptor = json.load(file)
            patientList = collectionDescriptor["items"].keys()
            self.managementPatientSelector.addItems(patientList)
        else:
            self.managementPatientSelector.addItem("None")
        self.managementPatientSelector.model().sort(0)
        self.managementPatientSelector.setCurrentIndex(0)

    # Function used to fill a comboBox with attachments retrieved by queries
    def fillSelectorWithAttachments(self):
        self.downloadAttachmentSelector.clear()
        self.downloadErrorText.hide()
        self.downloadButton.enabled = True
        attachmentName = ""
        if self.downloadRadioButtonPatientOnly.isChecked():
            for items in self.morphologicalData:
                if items["patientId"] == self.downloadPatientSelector.currentText:
                    if "_attachments" in items:
                        attachmentName = items["_attachments"].keys()[0]
                        self.downloadAttachmentSelector.addItem(attachmentName)
        else:
            for items in self.morphologicalData:
                # Check if the date is the same
                if items["patientId"] == self.downloadPatientSelector.currentText and items["date"][:10] == str(self.downloadDate.selectedDate):
                    if "_attachments" in items:
                        attachmentName = items["_attachments"].keys()[0]
                        self.downloadAttachmentSelector.addItem(attachmentName)
        if attachmentName == "":
            self.downloadAttachmentSelector.addItem("None")
            self.downloadErrorText.show()
            self.downloadButton.enabled = False

    # Function used to enable the download button when everything is ok
    def onDownloadPatientChosen(self):
        collectionName = self.downloadCollectionSelector.currentText
        patientId = self.downloadPatientSelector.currentText
        if collectionName != "None" and patientId != "None":
            self.downloadButton.enabled = True
            self.fillSelectorWithAttachments()

    def checkUploadDifferences(self):
        self.newPatientsList = []
        self.newAttachmentsList = []
        self.uploadListView.clear()

        directoryPath = self.uploadFilepathSelector.directory
        if os.path.exists(directoryPath + '/.DBIDescriptor'):
            file = open(directoryPath + '/.DBIDescriptor')
            collectionDescriptor = json.load(file)
            patientList = collectionDescriptor["items"].keys()
        else:
            return -1
        # Check for new patients
        for folderName in os.listdir(self.uploadFilepathSelector.directory):
            if folderName[0] != "." and folderName not in patientList:
                print ("New patient: " + folderName)
                self.newPatientsList.append(folderName)
                for dates in os.listdir(self.uploadFilepathSelector.directory + "/" + folderName):
                    if dates[0] != ".":
                        for newFileName in os.listdir(self.uploadFilepathSelector.directory + "/" + folderName + '/' + dates):
                            if newFileName[0] != '.':
                                print ("New attachment: " + folderName + '/' + dates + '/' + newFileName)
                                self.newAttachmentsList.append(folderName + '/' + dates + '/' + newFileName)

            # Check for new data for already existing patients
            elif folderName in patientList:
                attachmentList = collectionDescriptor["items"][folderName].keys()
                for dates in os.listdir(self.uploadFilepathSelector.directory + "/" + folderName):
                    if dates[0] != "." and dates not in attachmentList:
                        for newFileName in os.listdir(self.uploadFilepathSelector.directory + "/" + folderName + '/' + dates):
                            if newFileName[0] != '.':
                                print ("New attachment: " + folderName + '/' + dates + '/' + newFileName)
                                self.newAttachmentsList.append(folderName + '/' + dates + '/' + newFileName)

        # Display new attachments in the ListWidget
        self.uploadListView.addItems(self.newAttachmentsList)
        if self.uploadListView.count != 0:
            self.uploadButton.enabled = True
        else:
            self.uploadButton.enabled = False

    def onManagementDirectorySelected(self):
        if self.managementRadioButtonPatient.isChecked():
            self.isPossibleCreatePatient()
        else:
            self.fillSelectorWithDescriptorPatients()
            self.isPossibleAddDate()


    def isPossibleCreatePatient(self):
        directoryPath = self.managementFilepathSelector.directory
        self.createButton.enabled = False
        if self.newPatientIdInput.text != '' and os.path.exists(directoryPath + '/.DBIDescriptor'):
            self.createButton.enabled = True

    def isPossibleAddDate(self):
        directoryPath = self.managementFilepathSelector.directory
        self.createButton.enabled = False
        if self.managementPatientSelector.currentText != 'None' and os.path.exists(directoryPath + '/.DBIDescriptor'):
            self.createButton.enabled = True


#
# DatabaseInteractorLogic
#

class DatabaseInteractorLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def hasImageData(self, volumeNode):
        """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
        if not volumeNode:
            logging.debug('hasImageData failed: no volume node')
            return False
        if volumeNode.GetImageData() is None:
            logging.debug('hasImageData failed: no image data in volume node')
            return False
        return True

    def run(self, email, password):
        return myLib.connect(email, password)


class DatabaseInteractorTest(ScriptedLoadableModuleTest):
    """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        """Run as few or as many tests as needed here.
    """
        self.setUp()
        self.test_DatabaseInteractor1()

    def test_DatabaseInteractor1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

        self.delayDisplay("Starting the test")
        #
        # first, get some data
        #
        import urllib
        downloads = (
            ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

        for url, name, loader in downloads:
            filePath = slicer.app.temporaryPath + '/' + name
            if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
                logging.info('Requesting download %s from %s...\n' % (name, url))
                urllib.urlretrieve(url, filePath)
            if loader:
                logging.info('Loading %s...' % (name,))
                loader(filePath)
        self.delayDisplay('Finished with download and loading')

        volumeNode = slicer.util.getNode(pattern="FA")
        logic = DatabaseInteractorLogic()
        self.assertIsNotNone(logic.hasImageData(volumeNode))
        self.delayDisplay('Test passed!')
