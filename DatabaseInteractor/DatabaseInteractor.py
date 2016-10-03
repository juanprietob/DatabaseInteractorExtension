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
        self.queryTypeGroupBox = qt.QGroupBox("Find data with :")
        self.queryTypeGroupBoxLayout = qt.QHBoxLayout(self.queryTypeGroupBox)

        # RadioButtons choices
        self.downloadRadioButtonPatientOnly = qt.QRadioButton("PatientId only")
        self.downloadRadioButtonPatientOnly.setChecked(True)
        self.downloadRadioButtonPatientDate = qt.QRadioButton("PatientId and date")
        self.queryTypeGroupBoxLayout.addWidget(self.downloadRadioButtonPatientOnly)
        self.queryTypeGroupBoxLayout.addWidget(self.downloadRadioButtonPatientDate)
        self.downloadFormLayout.addRow(self.queryTypeGroupBox)

        # Collection Selector
        self.downloadCollectionSelector = qt.QComboBox()
        self.downloadCollectionSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose a collection: ", self.downloadCollectionSelector)

        # Patient Selector
        self.downloadPatientSelector = qt.QComboBox()
        self.downloadPatientSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose a patient: ", self.downloadPatientSelector)

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

        # Directory Button
        self.downloadFilepathSelector = ctk.ctkDirectoryButton()
        self.downloadFilepathSelector.toolTip = "Choose a path to save the model."
        self.downloadFormLayout.addRow(qt.QLabel("Choose a destination: "), self.downloadFilepathSelector)

        # Error download Label
        self.downloadErrorText = qt.QLabel("No file found for this date !")
        self.downloadErrorText.setStyleSheet("color: rgb(255, 0, 0);")
        self.downloadFormLayout.addWidget(self.downloadErrorText)
        self.downloadErrorText.hide()

        # Download Button
        self.downloadButton = qt.QPushButton("Download")
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

        # Volume selector
        self.modelSelector = slicer.qMRMLNodeComboBox()
        self.modelSelector.nodeTypes = (("vtkMRMLModelNode"), "")
        self.modelSelector.addEnabled = False
        self.modelSelector.removeEnabled = False
        self.modelSelector.setMRMLScene(slicer.mrmlScene)
        self.uploadFormLayout.addRow("Choose a model: ", self.modelSelector)

        # Collection Selector
        self.uploadCollectionSelector = qt.QComboBox()
        self.uploadCollectionSelector.addItem("None")
        self.uploadCollectionSelector.insertSeparator(1)
        self.uploadCollectionSelector.addItem("Create")
        self.uploadFormLayout.addRow("Choose a collection: ", self.uploadCollectionSelector)

        # Collection Creator
        # Collection Creator GroupBox
        self.collectionCreatorGroupBox = qt.QGroupBox("Create a collection")
        self.collectionCreatorGroupBoxLayout = qt.QFormLayout(self.collectionCreatorGroupBox)
        self.uploadFormLayout.addRow(self.collectionCreatorGroupBox)
        self.collectionCreatorGroupBox.hide()

        # Collection name input
        self.newCollectionNameInput = qt.QLineEdit()
        self.newCollectionNameInput.text = ''
        self.newCollectionNameLabel = qt.QLabel("Collection name: ")
        self.collectionCreatorGroupBoxLayout.addRow(self.newCollectionNameLabel, self.newCollectionNameInput)

        # Collection Creator Button
        self.createCollectionButton = qt.QPushButton("Create collection")
        self.createCollectionButton.enabled = False
        self.collectionCreatorGroupBoxLayout.addWidget(self.createCollectionButton)

        # Patient Selector
        self.uploadPatientSelector = qt.QComboBox()
        self.uploadPatientSelector.addItem("None")
        self.uploadPatientSelector.insertSeparator(1)
        self.uploadPatientSelector.addItem("Create")
        self.uploadFormLayout.addRow("Choose a patient: ", self.uploadPatientSelector)

        # Patient Creator
        # Patient Creator GroupBox
        self.patientCreatorGroupBox = qt.QGroupBox("Create a patientId")
        self.patientCreatorGroupBoxLayout = qt.QFormLayout(self.patientCreatorGroupBox)
        self.uploadFormLayout.addRow(self.patientCreatorGroupBox)
        self.patientCreatorGroupBox.hide()

        # Patient name input
        self.newPatientIdInput = qt.QLineEdit()
        self.newPatientIdInput.text = ''
        self.newPatientIdInputLabel = qt.QLabel("Patiend Id: ")
        self.patientCreatorGroupBoxLayout.addRow(self.newPatientIdInputLabel, self.newPatientIdInput)

        # Patient Creator Button
        self.createPatientButton = qt.QPushButton("Create patient Id")
        self.createPatientButton.enabled = False
        self.patientCreatorGroupBoxLayout.addWidget(self.createPatientButton)

        # Attachment name input
        self.attachmentNameInput = qt.QLineEdit()
        self.attachmentNameInput.text = ''
        self.uploadFormLayout.addRow("Attachment name: ", self.attachmentNameInput)

        # Upload Button
        self.uploadButton = qt.QPushButton("Upload")
        self.uploadButton.toolTip = "Upload patient data."
        self.uploadFormLayout.addRow(self.uploadButton)
        self.uploadButton.enabled = False

        # Add vertical spacer
        self.layout.addStretch(1)

        # --------------------------------------------------------- #
        # ----------------------- Signals ------------------------- #
        # --------------------------------------------------------- #
        self.connectionButton.connect('clicked(bool)', self.onConnectionButton)
        self.disconnectionButton.connect('clicked(bool)', self.onDisconnectionButton)
        self.createCollectionButton.connect('clicked(bool)', self.onCreateCollectionButton)
        self.createPatientButton.connect('clicked(bool)', self.onCreatePatientButton)
        self.downloadRadioButtonPatientOnly.toggled.connect(self.onRadioButtontoggled)
        self.downloadRadioButtonPatientDate.toggled.connect(self.onRadioButtontoggled)
        self.downloadButton.connect('clicked(bool)', self.onDownloadButton)
        self.uploadButton.connect('clicked(bool)', self.onUploadButton)
        self.emailInput.textChanged.connect(self.onInputChanged)
        self.passwordInput.textChanged.connect(self.onInputChanged)
        self.attachmentNameInput.textChanged.connect(self.onAttachmentNameChanged)
        self.newCollectionNameInput.textChanged.connect(self.onNewCollectionNameInputChanged)
        self.newPatientIdInput.textChanged.connect(self.onNewPatientIdInputChanged)
        self.downloadCollectionSelector.connect('currentIndexChanged(const QString&)',
                                                lambda text, type="download":
                                                self.fillSelectorsWithPatients(text, type))
        self.uploadCollectionSelector.connect('currentIndexChanged(const QString&)',
                                              lambda text, type="upload":
                                              self.fillSelectorsWithPatients(text, type))
        self.downloadPatientSelector.connect('currentIndexChanged(const QString&)', self.onDownloadPatientChosen)
        self.uploadPatientSelector.connect('currentIndexChanged(const QString&)',
                                           lambda text, type="upload":
                                           self.onUploadPatientChosen(text, type))

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
            self.fillSelectorsWithCollections()
            self.downloadCollapsibleButton.show()
            self.uploadCollapsibleButton.show()

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
            self.fillSelectorsWithCollections()
            self.downloadCollapsibleButton.show()
            self.uploadCollapsibleButton.show()
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
        # Erase token from file
        with open(self.tokenFilePath, "w"):
            pass

    # Function used to create a new collection if everything is ok
    def onCreateCollectionButton(self):
        newName = self.newCollectionNameInput.text
        # Create payload for posting new collection
        data = {"name": newName, "type": "morphologicalDataCollection"}
        myLib.createMorphologicalDataCollection(data)

        # Prepare to display patientId in this collection
        self.collections = myLib.getMorphologicalDataCollections().json()
        self.downloadCollectionSelector
        self.fillSelectorsWithCollections()
        index = self.uploadCollectionSelector.findText(newName)
        self.uploadCollectionSelector.setCurrentIndex(index)

        # Hide create groupBox
        self.collectionCreatorGroupBox.hide()

    # Function used to create a new patientId if everything is ok
    def onCreatePatientButton(self):
        newPatientId = self.newPatientIdInput.text
        data = {"patientId": newPatientId, "type": "morphologicalData"}
        id = myLib.createMorphologicalData(data).json()["id"]
        collection = self.uploadCollectionSelector.currentText
        for items in self.collections:
            if items["name"] == collection:
                collectionJson = myLib.getMorphologicalDataCollection(items["_id"]).json()
        collectionJson["items"].append({'_id': id})
        myLib.updateMorphologicalDataCollection(json.dumps(collectionJson))

        # Refill the patient selectors
        self.fillSelectorsWithPatients(collection, "upload")
        self.fillSelectorsWithPatients(collection, "download")
        index = self.uploadPatientSelector.findText(newPatientId)
        self.uploadPatientSelector.setCurrentIndex(index)

        # Hide create groupBox
        self.patientCreatorGroupBox.hide()


    def onRadioButtontoggled(self):
        self.downloadErrorText.hide()
        if self.downloadRadioButtonPatientOnly.isChecked():
            self.downloadDateLabel.hide()
            self.downloadDate.hide()
        else:
            self.downloadDateLabel.show()
            self.downloadDate.show()

    # Function used to download data with information provided
    def onDownloadButton(self):
        self.downloadErrorText.hide()
        if self.downloadRadioButtonPatientOnly.isChecked():
            for items in self.morphologicalData:
                if items["patientId"] == self.downloadPatientSelector.currentText:
                    documentId = items["_id"]
                    attachmentName = items["_attachments"].keys()[0]
            data = myLib.getAttachment(documentId, attachmentName, None).text
            # Write the attachment in a file
            filePath = self.downloadFilepathSelector.directory + '/' + attachmentName
            file = open(filePath, 'w+')
            file.write(data)
            file.close()

            # Load the file
            slicer.util.loadModel(filePath)
        else:
            documentId = ""
            for items in self.morphologicalData:
                if items["patientId"] == self.downloadPatientSelector.currentText and items["date"][:10] == str(self.downloadDate.selectedDate):
                    documentId = items["_id"]
                    attachmentName = items["_attachments"].keys()[0]
            if documentId != "":
                data = myLib.getAttachment(documentId, attachmentName, None).text
                # Write the attachment in a file
                filePath = self.downloadFilepathSelector.directory + '/' + attachmentName
                file = open(filePath, 'w+')
                file.write(data)
                file.close()

                # Load the file
                slicer.util.loadModel(filePath)
            else:
                self.downloadErrorText.show()

    # Function used to upload a data to the correct patient
    def onUploadButton(self):
        for items in self.morphologicalData:
            if items["patientId"] == self.uploadPatientSelector.currentText:
                documentId = items["_id"]

        # Write the polydata in a temporary file
        meshWriter = vtk.vtkPolyDataWriter()
        meshWriter.SetInputData(self.modelSelector.currentNode().GetPolyData())
        filepath = slicer.app.temporaryPath + '/' + self.attachmentNameInput.text + '.vtk'
        meshWriter.SetFileName(filepath)
        meshWriter.Write()

        # Send the file to the database
        data = open(filepath)
        myLib.addAttachment(documentId, self.attachmentNameInput.text + '.vtk', data)

    # Function used to enable the connection button if userlogin and password are provided
    def onInputChanged(self):
        self.connectionButton.enabled = (len(self.emailInput.text) != 0 and len(self.passwordInput.text) != 0)

    # Function used to enable the upload button if everything is ok
    def onAttachmentNameChanged(self):
        collectionName = self.uploadCollectionSelector.currentText
        text = self.uploadPatientSelector.currentText
        temp = collectionName != "None" and collectionName != "Create"
        temp = temp and text != "None" and text != "None" and len(self.attachmentNameInput.text) != 0
        self.uploadButton.enabled = temp and self.modelSelector.currentNode() != None

    # Function used to enable the upload button if the collection creation is ok
    def onNewCollectionNameInputChanged(self):
        self.createCollectionButton.enabled = len(self.newCollectionNameInput.text) != 0

    # Function used to enable the upload button if the patientId creation is ok
    def onNewPatientIdInputChanged(self):
        collectionName = self.uploadCollectionSelector.currentText
        self.createPatientButton.enabled = len(
            self.newPatientIdInput.text) != 0 and collectionName != "Create" and collectionName != "None"

    # Function used to fill the comboBoxes with morphologicalCollections
    def fillSelectorsWithCollections(self):
        self.collections = myLib.getMorphologicalDataCollections().json()
        self.downloadCollectionSelector.clear()
        self.uploadCollectionSelector.clear()
        for items in self.collections:
            self.downloadCollectionSelector.addItem(items["name"])
            self.uploadCollectionSelector.addItem(items["name"])

        if self.downloadCollectionSelector.count == 0:
            self.downloadCollectionSelector.addItem("None")
        if self.uploadCollectionSelector.count == 0:
            self.uploadCollectionSelector.addItem("None")
        self.uploadCollectionSelector.insertSeparator(self.uploadCollectionSelector.count)
        self.uploadCollectionSelector.addItem("Create")

    # Function used to fill the comboBoxes with patientId corresponding to the collection selected
    def fillSelectorsWithPatients(self, text, type):
        if text == "Create":
            self.collectionCreatorGroupBox.show()
        else:
            self.collectionCreatorGroupBox.hide()
            self.downloadButton.enabled = text != "None"
            if text != "None":
                # Get the patientIds in the selected collection
                for items in self.collections:
                    if items["name"] == text:
                        self.morphologicalData = myLib.getMorphologicalData(items["_id"]).json()

                # Fill the right comboBox
                if type == "download":
                    self.downloadPatientSelector.clear()
                    for items in self.morphologicalData:
                        self.downloadPatientSelector.addItem(items["patientId"])
                    if self.downloadPatientSelector.count == 0:
                        self.downloadPatientSelector.addItem("None")
                if type == "upload":
                    self.uploadPatientSelector.clear()
                    for items in self.morphologicalData:
                        self.uploadPatientSelector.addItem(items["patientId"])
                    if self.uploadPatientSelector.count == 0:
                        self.uploadPatientSelector.addItem("None")
                    self.uploadPatientSelector.insertSeparator(self.uploadPatientSelector.count)
                    self.uploadPatientSelector.addItem("Create")

    # Function used to enable the download button when everything is ok
    def onDownloadPatientChosen(self):
        collectionName = self.downloadCollectionSelector.currentText
        patientId = self.downloadPatientSelector.currentText
        if collectionName != "None" and patientId != "None":
            self.downloadButton.enabled = True

    # Function used to enable upload button or show the groupBox to create a new patient
    def onUploadPatientChosen(self, text, type):
        # Logic test to enable upload button if everything is ok
        collectionName = self.uploadCollectionSelector.currentText
        if collectionName != "None" and collectionName != "Create":
            if text != "None" and text != "None":
                if len(self.attachmentNameInput.text) != 0 and self.modelSelector.currentNode() != None:
                    self.uploadButton.enabled = True
        if text == "Create":
            self.patientCreatorGroupBox.show()
        else:
            self.patientCreatorGroupBox.hide()


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
