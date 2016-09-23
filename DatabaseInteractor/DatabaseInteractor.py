import os, sys, tempfile
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
        self.tokenFilePath = tempfile.gettempdir() + 'user.slicer_token'

        # ---------------------------------------------------------------- #
        # ---------------- Definition of the UI interface ---------------- #
        # ---------------------------------------------------------------- #

        # --- Definition of connection collapsible button --- #
        # Collapsible button
        self.connectionCollapsibleButton = ctk.ctkCollapsibleButton()
        self.connectionCollapsibleButton.text = "Authentication"
        self.layout.addWidget(self.connectionCollapsibleButton)
        self.connectionVBoxLayout = qt.QVBoxLayout(self.connectionCollapsibleButton)

        # - GroupBox containing Email and Password Inputs - #
        self.connectionGroupBox = qt.QGroupBox("Login")
        self.connectionGroupBoxLayout = qt.QFormLayout(self.connectionGroupBox)
        self.connectionVBoxLayout.addWidget(self.connectionGroupBox)

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

        # --- Definition of download collapsible button --- #
        # Collapsible button
        self.downloadCollapsibleButton = ctk.ctkCollapsibleButton()
        self.downloadCollapsibleButton.text = "Download data"
        self.layout.addWidget(self.downloadCollapsibleButton, 0)
        self.downloadFormLayout = qt.QFormLayout(self.downloadCollapsibleButton)
        self.downloadCollapsibleButton.hide()

        # Collection Selector
        self.downloadCollectionSelector = qt.QComboBox()
        self.downloadCollectionSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose a collection: ", self.downloadCollectionSelector)

        # Patient Selector
        self.downloadPatientSelector = qt.QComboBox()
        self.downloadPatientSelector.addItem("None")
        self.downloadFormLayout.insertRow(1, "Choose a patient: ", self.downloadPatientSelector)

        # Download Button
        self.downloadButton = qt.QPushButton("Download")
        self.downloadButton.toolTip = "Download patient data."
        self.downloadFormLayout.addRow(self.downloadButton)
        self.downloadButton.enabled = False

        # --- Definition of upload collapsible button --- #
        # Collapsible button
        self.uploadCollapsibleButton = ctk.ctkCollapsibleButton()
        self.uploadCollapsibleButton.text = "Upload data"
        self.layout.addWidget(self.uploadCollapsibleButton, 0)
        self.uploadFormLayout = qt.QFormLayout(self.uploadCollapsibleButton)
        self.uploadCollapsibleButton.hide()

        # Volume selector
        self.volumeSelector = slicer.qMRMLNodeComboBox()
        self.volumeSelector.nodeTypes = (("vtkMRMLScalarVolumeNode"), "")
        self.volumeSelector.addEnabled = False
        self.volumeSelector.removeEnabled = False
        self.volumeSelector.setMRMLScene(slicer.mrmlScene)
        self.uploadFormLayout.addRow("Choose a volume: ", self.volumeSelector)

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
        self.downloadButton.connect('clicked(bool)', self.onDownloadButton)
        self.uploadButton.connect('clicked(bool)', self.onUploadButton)
        self.emailInput.textChanged.connect(self.onInputChanged)
        self.passwordInput.textChanged.connect(self.onInputChanged)
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
                                             lambda text, type = "upload":
                                             self.onUploadPatientChosen(text,type))




        # --- Try to connect when launching the module --- #
        file = open(self.tokenFilePath,'r')
        first_line = file.readline()
        if first_line != "":
            #self.token = first_line
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

    def onConnectionButton(self):
        # Try to connect to server
        token = myLib.connect(self.emailInput.text, self.passwordInput.text)
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
            self.errorLoginText.text = "Wrong email or password !"
            self.errorLoginText.show()
        else:
            self.errorLoginText.text = "Insufficient scope !"
            self.errorLoginText.show()

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

    def onCreateCollectionButton(self):
        newName = self.newCollectionNameInput.text
        # Create payload for posting new collection
        data={"name": newName,"type": "morphologicalDataCollection"}
        myLib.createMorphologicalDataCollection(data)

        # Prepare to display patientId in this collection
        self.collections = myLib.getMorphologicalDataCollections().json()
        self.downloadCollectionSelector
        self.fillSelectorsWithCollections()
        index = self.uploadCollectionSelector.findText(newName)
        self.uploadCollectionSelector.setCurrentIndex(index)

        # Hide create groupBox
        self.collectionCreatorGroupBox.hide()

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
        self.fillSelectorsWithPatients(collection,"upload")
        self.fillSelectorsWithPatients(collection, "download")
        index = self.uploadPatientSelector.findText(newPatientId)
        self.uploadPatientSelector.setCurrentIndex(index)

        # Hide create groupBox
        self.patientCreatorGroupBox.hide()

    def onDownloadButton(self):
        print "This is something to do."

    def onUploadButton(self):
        print "This is something to do."

    def onInputChanged(self):
        self.connectionButton.enabled = (len(self.emailInput.text) != 0 and len(self.passwordInput.text) != 0)

    def onNewCollectionNameInputChanged(self):
        self.createCollectionButton.enabled = len(self.newCollectionNameInput.text) != 0
    def onNewPatientIdInputChanged(self):
        collectionName = self.uploadCollectionSelector.currentText
        self.createPatientButton.enabled = len(self.newPatientIdInput.text) != 0 and collectionName != "Create" and collectionName != "None"

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

    def onDownloadPatientChosen(self):
        collectionName = self.downloadCollectionSelector.currentText
        patientId = self.downloadPatientSelector.currentText
        if collectionName != "None" and patientId != "None":
            self.downloadButton.enabled = True


    def onUploadPatientChosen(self,text,type):
        collectionName = self.uploadCollectionSelector.currentText
        if collectionName != "None" and collectionName != "Create" and text != "None" and text != "None":
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
