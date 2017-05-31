from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import json
import logging
import os, shutil, zipfile
import subprocess
from urlparse import urlparse

#
# DatabaseInteractor
#

class DatabaseInteractor(slicer.ScriptedLoadableModule.ScriptedLoadableModule):
    def __init__(self, parent):
        slicer.ScriptedLoadableModule.ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Database Interactor"
        self.parent.categories = ["Web System Tools"]
        self.parent.dependencies = []
        self.parent.contributors = [
            "Clement Mirabel (University of Michigan)", "Juan Carlos Prieto (UNC)"]
        self.parent.helpText = """
    For users using the amazon web service Website developed by Clement Mirabel and Juan Prieto for Lucia Cevidanes project, the server address should be 'https://ec2-52-42-49-63.us-west-2.compute.amazonaws.com:8180/'. If you have any issue connecting, contact juanprieto@gmail.com or clement.mirabel@gmail.com.
    """
        self.parent.acknowledgementText = """
    To be completed.
"""


#
# DatabaseInteractorWidget
#

class DatabaseInteractorWidget(slicer.ScriptedLoadableModule.ScriptedLoadableModuleWidget):
    def setup(self):
        """ 
            Function used to setup the UI, global variables and libraries used in this extension 
        """
        slicer.ScriptedLoadableModule.ScriptedLoadableModuleWidget.setup(self)
        # ---------------------------------------------------------------- #
        # ------------------------ Global variables ---------------------- #
        # ---------------------------------------------------------------- #

        import DatabaseInteractorLib
        self.DatabaseInteractorLib = DatabaseInteractorLib.DatabaseInteractorLib()

        import ClusterpostLib
        self.ClusterpostLib = ClusterpostLib.ClusterpostLib()

        self.logic = DatabaseInteractorLogic()

        self.connected = False
        self.collections = dict()
        self.morphologicalData = dict()
        self.attachmentsList = {}
        self.tokenFilePath = os.path.join(slicer.app.temporaryPath, 'user.slicer_token')
        self.serverFilePath = os.path.join(slicer.app.temporaryPath, 'user.slicer_server')
        self.moduleName = 'DatabaseInteractor'
        scriptedModulesPath = eval('slicer.modules.%s.path' % self.moduleName.lower())
        scriptedModulesPath = os.path.dirname(scriptedModulesPath)
        self.modulesLoaded = dict()

        # Timer definition
        self.timer = qt.QTimer()
        self.timer.timeout.connect(self.overflow)
        self.timerPeriod = 60 * 60 * 1000

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
        self.serverInput.text = ''
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
        self.downloadCollectionButton = qt.QPushButton("Download entire collection")
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
            "qproperty-icon: url(" + os.path.join(scriptedModulesPath, "Resources", "Icons", "ArrowRight.png") + ");"
            "qproperty-iconSize: 10px;width:20px;}"
            "QCalendarWidget QWidget#qt_calendar_prevmonth{"
            "qproperty-icon: url(" + os.path.join(scriptedModulesPath, "Resources", "Icons", "ArrowLeft.png") + ");"
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

        # Clickable dates formats
        self.brushBlue = qt.QBrush()
        self.brushBlue.setColor(qt.QColor(107,171,200))
        self.checkableDateFormat = qt.QTextCharFormat()
        self.checkableDateFormat.setBackground(self.brushBlue)
        self.checkableDateFormat.setFontWeight(qt.QFont.Bold)
        self.normalBrush = qt.QBrush()
        self.normalBrush.setColor(qt.QColor(255, 255, 255))
        self.normalDateFormat = qt.QTextCharFormat()
        self.normalDateFormat.setBackground(self.normalBrush)
        self.normalDateFormat.setFontWeight(qt.QFont.Normal)

        # Attachment selector
        self.downloadAttachmentSelector = qt.QComboBox()
        self.downloadAttachmentSelector.addItem("None")
        self.downloadFormLayout.addRow("Choose an attachment: ", self.downloadAttachmentSelector)

        # Error download Label
        self.downloadErrorText = qt.QLabel("No file found for this patientId !")
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

        # Patient Selector
        self.uploadPatientSelector = qt.QComboBox()
        self.uploadPatientSelector.addItem("None")
        self.uploadFormLayout.addRow("Choose a patient: ", self.uploadPatientSelector)

        # Date Selector
        self.uploadDateSelector = qt.QComboBox()
        self.uploadDateSelector.addItem("None")
        self.uploadFormLayout.addRow("Choose a date: ", self.uploadDateSelector)

        # Layout of the differences between local folder and online database
        self.uploadListLayout = qt.QVBoxLayout()
        self.uploadFormLayout.addRow("Files to upload: ", self.uploadListLayout)
        self.noneLabel = qt.QLabel("None")
        self.uploadListLayout.addWidget(self.noneLabel)

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

        self.uploadLabel = qt.QLabel("Files successfully uploaded !")
        self.uploadLabel.setStyleSheet("color: rgb(0, 150, 0);")
        self.uploadFormLayout.addRow(self.uploadLabel)
        self.uploadLabel.hide()

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
            "qproperty-icon: url(" + os.path.join(scriptedModulesPath, "Resources", "Icons", "ArrowRight.png") + ");"
            "qproperty-iconSize: 10px;width:20px;}"
            "QCalendarWidget QWidget#qt_calendar_prevmonth{"
            "qproperty-icon: url(" + os.path.join(scriptedModulesPath, "Resources", "Icons", "ArrowLeft.png") + ");"
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

        # -------------------------------------------------------------- #
        # -------- Definition of task creator collapsible button ------- #
        # -------------------------------------------------------------- #
        # Collapsible button
        self.taskCreatorCollapsibleButton = ctk.ctkCollapsibleButton()
        self.taskCreatorCollapsibleButton.text = "Create a task"
        self.layout.addWidget(self.taskCreatorCollapsibleButton)
        self.taskCreatorFormLayout = qt.QFormLayout(self.taskCreatorCollapsibleButton)

        self.executableSelector = qt.QComboBox()
        self.taskCreatorFormLayout.addRow("Select an executable:", self.executableSelector)

        self.widgetSelectedGroupBox = qt.QGroupBox()
        self.widgetSelectedGroupBoxLayout = qt.QVBoxLayout(self.widgetSelectedGroupBox)
        self.taskCreatorFormLayout.addRow(self.widgetSelectedGroupBox)
        self.widgetSelectedGroupBox.hide()

        self.currentExecutable = None
        # self.condyleClassificationCollapsibleButton.hide()

        self.taskCreatorCollapsibleButton.hide()

        # -------------------------------------------------------------- #
        # ------------- Job computing collapsible button --------------- #
        # -------------------------------------------------------------- #
        # Collapsible button
        self.jobComputerCollapsibleButton = ctk.ctkCollapsibleButton()
        self.jobComputerCollapsibleButton.text = "Auto compute tasks"
        self.layout.addWidget(self.jobComputerCollapsibleButton)
        self.jobComputerCollapsibleFormLayout = qt.QFormLayout(self.jobComputerCollapsibleButton)

        self.jobComputerHostInput = qt.QLineEdit()
        self.jobComputerHostInput.setReadOnly(True)
        self.jobComputerPortInput = qt.QLineEdit()
        self.jobComputerPortInput.setReadOnly(True)
        self.jobComputerPortInput = qt.QLineEdit()
        self.jobComputerPortInput.setReadOnly(True)
        self.timePeriodSelector = qt.QDoubleSpinBox()
        self.timePeriodSelector.setSuffix(' min')
        self.timePeriodSelector.setRange(1,1440)
        self.timePeriodSelector.setDecimals(0)

        self.jobComputerParametersLayout = qt.QHBoxLayout()
        self.jobComputerParametersLayout.addWidget(qt.QLabel("Host: "))
        self.jobComputerParametersLayout.addWidget(self.jobComputerHostInput)
        self.jobComputerParametersLayout.addWidget(qt.QLabel("Port: "))
        self.jobComputerParametersLayout.addWidget(self.jobComputerPortInput)
        self.jobComputerParametersLayout.addWidget(qt.QLabel("Period: "))
        self.jobComputerParametersLayout.addWidget(self.timePeriodSelector)

        self.jobComputerCollapsibleFormLayout.addRow(self.jobComputerParametersLayout)

        # Connect Socket Button
        self.connectListenerButton = qt.QPushButton("Connect")

        # Disconnect Socket Button
        self.disconnectListenerButton = qt.QPushButton("Disconnect")
        self.disconnectListenerButton.enabled = False

        # HBox Layout for (dis)connection buttons
        self.connectionHBoxLayout = qt.QHBoxLayout()
        self.connectionHBoxLayout.addWidget(self.connectListenerButton)
        self.connectionHBoxLayout.addWidget(self.disconnectListenerButton)

        self.jobComputerCollapsibleFormLayout.addRow(self.connectionHBoxLayout)

        # Websocket Console
        self.displayConsole = qt.QTextEdit()
        self.displayConsole.readOnly = True
        self.displayConsole.setStyleSheet(
            "color: white;"
            "background-color: black;"
            "font-family: Courier;font-style: normal;font-size: 12pt;"
        )
        self.jobComputerCollapsibleFormLayout.addRow(self.displayConsole)

        self.jobComputerCollapsibleButton.hide()

        # Add vertical spacer
        self.layout.addStretch(1)

        # --------------------------------------------------------- #
        # ----------------------- Signals ------------------------- #
        # --------------------------------------------------------- #

        # Buttons
        self.connectionButton.connect('clicked(bool)', self.onConnectionButton)
        self.disconnectionButton.connect('clicked(bool)', self.onDisconnectionButton)
        self.downloadButton.connect('clicked(bool)', self.onDownloadButton)
        self.downloadCollectionButton.connect('clicked(bool)', self.onDownloadCollectionButton)
        self.uploadButton.connect('clicked(bool)', self.onUploadButton)
        self.createButton.connect('clicked(bool)', self.onCreateButton)
        self.connectListenerButton.connect('clicked(bool)', self.onConnectListenerButton)
        self.disconnectListenerButton.connect('clicked(bool)', self.onDiconnectListenerButton)

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
        self.downloadCollectionSelector.connect('currentIndexChanged(const QString&)', self.fillSelectorWithPatients)
        self.downloadPatientSelector.connect('currentIndexChanged(const QString&)', self.onDownloadPatientChosen)
        self.uploadPatientSelector.connect('currentIndexChanged(const QString&)', self.onUploadPatientChosen)
        self.uploadDateSelector.connect('currentIndexChanged(const QString&)', self.onUploadDateChosen)
        self.managementPatientSelector.connect('currentIndexChanged(const QString&)', self.isPossibleAddDate)
        self.executableSelector.connect('currentIndexChanged(const QString&)', self.executableSelected)

        # Calendar
        self.downloadDate.connect('clicked(const QDate&)', self.fillSelectorWithAttachments)

        # FilePath selectors
        self.uploadFilepathSelector.connect('directorySelected(const QString &)', self.createFilesDictionary)
        self.managementFilepathSelector.connect('directorySelected(const QString &)',
                                                self.onManagementDirectorySelected)

        # --- Try to connect when launching the module --- #
        if os.path.exists(self.tokenFilePath):
            file = open(self.tokenFilePath, 'r')
            first_line = file.readline()
            self.DatabaseInteractorLib.getServer(self.serverFilePath)
            if first_line != "":
                # self.token = first_line
                self.ClusterpostLib.setToken(first_line)
                self.ClusterpostLib.setServerUrl(self.DatabaseInteractorLib.server[:-1])
                self.DatabaseInteractorLib.token = first_line
                self.connected = True
                self.connectionGroupBox.hide()
                self.connectionButton.hide()
                self.disconnectionButton.show()
                self.fillSelectorWithCollections()
                self.downloadCollapsibleButton.show()
                self.uploadCollapsibleButton.show()
                self.taskCreatorCollapsibleButton.show()
                self.jobComputerCollapsibleButton.show()
                self.fillExecutableSelector()
                server = self.DatabaseInteractorLib.server
                self.jobComputerHostInput.text = urlparse(server).hostname
                self.jobComputerPortInput.text = urlparse(server).port
                if "admin" in self.DatabaseInteractorLib.getUserScope():
                    self.managementCollapsibleButton.show()

            file.close()
        

    def exit(self):
        """ 
            Function used to reset the CLI widget when exiting the module 
        """
        print("-----------EXIT------------")
        for moduleName, slot in self.modulesLoaded.iteritems():
            node = getattr(slicer.modules, moduleName)
            applyButton = node.widgetRepresentation().ApplyPushButton
            applyButton.disconnect(applyButton, 'clicked(bool)')
            applyButton.connect('clicked(bool)', slot)
        self.modulesLoaded = dict()

    # ------------ Buttons -------------- #
    def onConnectionButton(self):
        """ 
            Function used to connect user to the database and store token in a file 
        """
        self.DatabaseInteractorLib.setServer(self.serverInput.text, self.serverFilePath)
        self.ClusterpostLib.setServerUrl(self.serverInput.text[:-1])
        token, error = self.DatabaseInteractorLib.connect(self.emailInput.text, self.passwordInput.text)
        print(error)
        if token != -1:
            userScope = self.DatabaseInteractorLib.getUserScope()
            if len(userScope) != 1 or "default" not in userScope:
                # Write the token in a temporary file
                file = open(self.tokenFilePath, 'w+')
                file.write(token)
                file.close()
                self.ClusterpostLib.setToken(token)
                self.connected = True
                self.connectionGroupBox.hide()
                self.connectionButton.hide()
                self.disconnectionButton.show()
                self.fillSelectorWithCollections()
                self.downloadCollapsibleButton.show()
                self.uploadCollapsibleButton.show()
                self.managementCollapsibleButton.show()
                self.taskCreatorCollapsibleButton.show()
                self.jobComputerCollapsibleButton.show()
                self.fillExecutableSelector()
                self.jobComputerHostInput.text = urlparse(self.serverInput.text).hostname
                self.jobComputerPortInput.text = urlparse(self.serverInput.text).port
                if "admin" not in userScope:
                    self.managementCollapsibleButton.hide()
        elif token == -1:
            self.errorLoginText.text = error
            self.errorLoginText.show()
        else:
            self.errorLoginText.text = "Insufficient scope ! Email luciacev@umich.edu for access."
            self.errorLoginText.show()

    def onDisconnectionButton(self):
        """
            Function used to disconnect user to the database  
        """
        self.serverInput.text = self.DatabaseInteractorLib.server
        self.emailInput.text = self.DatabaseInteractorLib.getUserEmail()
        self.DatabaseInteractorLib.disconnect()
        self.connected = False
        self.passwordInput.text = ''
        self.connectionGroupBox.show()
        self.connectionButton.show()
        self.errorLoginText.hide()
        self.disconnectionButton.hide()
        self.downloadCollapsibleButton.hide()
        self.uploadCollapsibleButton.hide()
        self.managementCollapsibleButton.hide()
        self.taskCreatorCollapsibleButton.hide()
        self.jobComputerCollapsibleButton.hide()
        # Erase token from file
        with open(self.tokenFilePath, "w"):
            pass

    def onDownloadButton(self):
        """
            Function used to download data with information provided
        """
        for items in self.morphologicalData:
            if "_attachments" in items:
                for attachments in items["_attachments"].keys():
                    if attachments == self.downloadAttachmentSelector.currentText:
                        documentId = items["_id"]
        data = self.DatabaseInteractorLib.getAttachment(documentId, self.downloadAttachmentSelector.currentText, None)
        # Write the attachment in a file
        filePath = os.path.join(self.downloadFilepathSelector.directory, self.downloadAttachmentSelector.currentText)
        if data != -1:
            with open(filePath, 'wb+') as file:
                for chunk in data.iter_content(2048):
                    file.write(chunk)
        file.close()

        # Load the file
        self.logic.fileLoader(filePath)

    def onDownloadCollectionButton(self):
        """ 
            Function used to download an entire collection and organise it with folders
        """
        collectionPath = os.path.join(self.downloadFilepathSelector.directory,
                                      self.downloadCollectionSelector.currentText)
        # Check if folder already exists
        if not os.path.exists(collectionPath):
            os.makedirs(collectionPath)
        index = 0

        # Write collection document
        for items in self.DatabaseInteractorLib.getMorphologicalDataCollections().json():
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
                if not os.path.exists(os.path.join(collectionPath, self.downloadPatientSelector.itemText(index))):
                    os.makedirs(os.path.join(collectionPath, self.downloadPatientSelector.itemText(index)))
            index += 1

        # Fill the folders with attachments
        for items in self.morphologicalData:
            if "_attachments" in items:
                documentId = items["_id"]

                patientId = items["patientId"]
                if "date" in items:
                    date = items["date"]
                else:
                    date = "NoDate"
                descriptor["items"][patientId][date[:10]] = os.path.join(collectionPath, patientId, date[:10],
                                                                         ".DBIDescriptor")

                if not os.path.exists(os.path.join(collectionPath, patientId, date[:10])):
                    os.makedirs(os.path.join(collectionPath, patientId, date[:10]))
                for attachments in items["_attachments"].keys():
                    data = self.DatabaseInteractorLib.getAttachment(documentId, attachments, None).text
                    # Save the document
                    file = open(os.path.join(collectionPath, patientId, date[:10], '.DBIDescriptor'), 'w+')
                    json.dump(items, file, indent=3, sort_keys=True)
                    file.close()

                    # Save the attachment
                    filePath = os.path.join(collectionPath, patientId, date[:10], attachments)
                    with open(filePath, 'wb+') as file:
                        for chunk in data:
                            file.write(chunk)
                    file.close()

        file = open(os.path.join(collectionPath, '.DBIDescriptor'), 'w+')
        json.dump(descriptor, file, indent=3, sort_keys=True)
        file.close()
        self.uploadFilepathSelector.directory = collectionPath
        self.managementFilepathSelector.directory = collectionPath

    def onUploadButton(self):
        """
            Function used to upload a data to the correct patient
        """
        collection = self.uploadFilepathSelector.directory
        self.checkBoxesChecked()
        for patient in self.checkedList.keys():
            for date in self.checkedList[patient].keys():
                for attachment in self.checkedList[patient][date]["items"]:
                    with open(os.path.join(collection, patient, date, '.DBIDescriptor'), 'r') as file:
                        descriptor = json.load(file)
                    documentId = descriptor["_id"]
                    # Add new attachments to patient
                    path = os.path.join(collection,patient,date,attachment)
                    with open(path, 'r') as file:
                        self.DatabaseInteractorLib.addAttachment(documentId, attachment, file)
                    # Update descriptor
                    data = self.DatabaseInteractorLib.getMorphologicalDataByPatientId(patient).json()[0]
                    file = open(os.path.join(self.uploadFilepathSelector.directory, patient, date,
                                             '.DBIDescriptor'), 'w+')
                    json.dump(data, file, indent=3, sort_keys=True)
                    file.close()
        # Update morphologicalData list
        for items in self.collections:
            if items["name"] == self.downloadCollectionSelector.currentText:
                self.morphologicalData = self.DatabaseInteractorLib.getMorphologicalData(items["_id"]).json()
        self.uploadLabel.show()

    def onCreateButton(self):
        """
            Function used to create the architecture for a new patient or new date, updating descriptors
        """
        collectionPath = self.managementFilepathSelector.directory
        patientId = self.managementPatientSelector.currentText
        date = str(self.createDate.selectedDate)
        collection = os.path.split(self.managementFilepathSelector.directory)[1]

        # Check if it is a new patient
        if self.managementRadioButtonPatient.isChecked():
            patientId = self.newPatientIdInput.text

        # Add to database
        owner = self.DatabaseInteractorLib.getUserEmail()
        data = {
            "patientId": patientId,
            "date": date,
            "owners": [{"user": owner}],
            "type": "morphologicalData",
        }
        docId = self.DatabaseInteractorLib.createMorphologicalData(json.dumps(data)).json()["id"]
        for items in self.collections:
            if items["name"] == collection:
                collectionJson = self.DatabaseInteractorLib.getMorphologicalDataCollection(items["_id"]).json()
        collectionJson["items"].append({'_id': docId})
        self.DatabaseInteractorLib.updateMorphologicalDataCollection(json.dumps(collectionJson))

        # Create date folder
        if not os.path.exists(os.path.join(collectionPath, patientId, date)):
            os.makedirs(os.path.join(collectionPath, patientId, date))

        # Write descriptor
        for items in self.DatabaseInteractorLib.getMorphologicalData(collectionJson["_id"]).json():
            if items["_id"] == docId:
                file = open(os.path.join(collectionPath, patientId, date, '.DBIDescriptor'), 'w+')
                json.dump(items, file, indent=3, sort_keys=True)
                file.close()

        # Update collection descriptor
        file = open(os.path.join(collectionPath, '.DBIDescriptor'), 'r')
        jsonfile = json.load(file)
        file.close()
        if patientId not in jsonfile["items"]:
            jsonfile["items"][patientId] = {}
        jsonfile["items"][patientId][date] = os.path.join(collectionPath, patientId, date, '.DBIDescriptor')
        file = open(os.path.join(collectionPath, '.DBIDescriptor'), 'w+')
        json.dump(jsonfile, file, indent=3, sort_keys=True)
        file.close()
        self.fillSelectorWithPatients()

    def onConnectListenerButton(self):
        """
            Function used to create a timer with the period selected in the UI
        """
        self.timerPeriod = int(self.timePeriodSelector.value) * 60 * 1000 # Timer period is in ms
        self.timer.start(self.timerPeriod)
        self.connectListenerButton.enabled = False
        self.disconnectListenerButton.enabled = True

    def onDiconnectListenerButton(self):
        """
            Function used to stop the timer and the job listening
        """
        self.timer.stop()
        self.connectListenerButton.enabled = True
        self.disconnectListenerButton.enabled = False

    # ---------- Radio Buttons ---------- #
    def onRadioButtontoggled(self):
        """
            Function used to display interface corresponding to the query checked
        """
        self.downloadErrorText.hide()
        self.fillSelectorWithAttachments()
        if self.downloadRadioButtonPatientOnly.isChecked():
            self.downloadErrorText.text = "No file found for this patientId !"
            self.downloadDateLabel.hide()
            self.downloadDate.hide()
        else:
            self.downloadErrorText.text = "No file found for this date !"
            self.downloadDateLabel.show()
            self.downloadDate.show()

    def onManagementRadioButtontoggled(self):
        """
            Function used to display interface corresponding to the management action checked
        """
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

    # ------------- Inputs -------------- #
    def onInputChanged(self):
        """
            Function used to enable the connection button if userlogin and password are provided
        """
        self.connectionButton.enabled = (len(self.emailInput.text) != 0 and len(self.passwordInput.text) != 0)

    def isPossibleCreatePatient(self):
        """
            Function used to enable the creation button if path contains a descriptor and is a name is given
        """
        directoryPath = self.managementFilepathSelector.directory
        self.createButton.enabled = False
        # Check if the folder is a collection with a DBIDescriptor file
        if self.newPatientIdInput.text != '' and os.path.exists(os.path.join(directoryPath, '.DBIDescriptor')):
            self.createButton.enabled = True

    # ----------- Combo Boxes ----------- #
    def fillSelectorWithCollections(self):
        """
            Function used to fill the comboBoxes with morphologicalCollections
        """
        self.collections = self.DatabaseInteractorLib.getMorphologicalDataCollections().json()
        self.downloadCollectionSelector.clear()
        for items in self.collections:
            self.downloadCollectionSelector.addItem(items["name"])
        if self.downloadCollectionSelector.count == 0:
            self.downloadCollectionSelector.addItem("None")

    def fillSelectorWithPatients(self):
        """
            Function used to fill the comboBox with patientId corresponding to the collection selected
        """
        for items in self.morphologicalData:
            if "date" in items:
                date = items["date"]
                self.downloadDate.setDateTextFormat(qt.QDate(int(date[:4]), int(date[5:7]), int(date[8:10])),
                                                    self.normalDateFormat)
            else:
                date = "NoDate"

        text = self.downloadCollectionSelector.currentText
        self.downloadButton.enabled = text
        if text != "None":
            self.downloadCollectionButton.enabled = True
            # Get the patientIds in the selected collection
            for items in self.collections:
                if items["name"] == text:
                    self.morphologicalData = self.DatabaseInteractorLib.getMorphologicalData(items["_id"]).json()
            self.downloadPatientSelector.clear()
            for items in self.morphologicalData:
                if self.downloadPatientSelector.findText(items["patientId"]) == -1:
                    self.downloadPatientSelector.addItem(items["patientId"])
            if self.downloadPatientSelector.count == 0:
                self.downloadPatientSelector.addItem("None")
        self.downloadPatientSelector.model().sort(0)
        self.downloadPatientSelector.setCurrentIndex(0)

    def fillSelectorWithDescriptorPatients(self):
        """
            Function used to fill the comboBox with a list of attachment corresponding to the query results
        """
        directoryPath = self.managementFilepathSelector.directory
        self.managementPatientSelector.clear()
        if os.path.exists(os.path.join(directoryPath, '.DBIDescriptor')):
            file = open(os.path.join(directoryPath, '.DBIDescriptor'), 'r')
            collectionDescriptor = json.load(file)
            patientList = collectionDescriptor["items"].keys()
            self.managementPatientSelector.addItems(patientList)
        else:
            self.managementPatientSelector.addItem("None")
        self.managementPatientSelector.model().sort(0)
        self.managementPatientSelector.setCurrentIndex(0)

    def fillExecutableSelector(self):
        """
            Function used to fill the comboBox with a list of executable in the current Slicer
        """
        self.modules = {}
        modules = slicer.modules.__dict__.keys()
        for moduleName in modules:
            module = getattr(slicer.modules, moduleName)
            if hasattr(module, "cliModuleLogic"):
                self.executableSelector.addItem(module.name)

    def isPossibleAddDate(self):
        """
            Function used to enable creation button if path contains a descriptor and is a patient is chosen 
        """
        directoryPath = self.managementFilepathSelector.directory
        self.createButton.enabled = False
        if self.managementPatientSelector.currentText != 'None' and os.path.exists(
                os.path.join(directoryPath, '.DBIDescriptor')):
            self.createButton.enabled = True

    def onDownloadPatientChosen(self):
        """
            Function used to enable the download button when everything is ok
        """
        collectionName = self.downloadCollectionSelector.currentText
        patientId = self.downloadPatientSelector.currentText
        if collectionName != "None" and patientId != "None":
            self.downloadButton.enabled = True
            self.fillSelectorWithAttachments()
        self.highlightDates()

    def onUploadPatientChosen(self):
        """
            Function used to show in a list the new documents for a patient
        """
        self.uploadDateSelector.clear()
        self.uploadLabel.hide()
        if self.uploadPatientSelector.currentText != "" and self.uploadPatientSelector.currentText != "None":
            for dates in self.attachmentsList[self.uploadPatientSelector.currentText].keys():
                self.uploadDateSelector.addItem(dates)
        if self.uploadDateSelector.count == 0:
            self.uploadDateSelector.addItem("None")

    def onUploadDateChosen(self):
        """
            Function used to display the checkboxes corresponding on the patient and timepoint selected
        """
        self.clearCheckBoxList()
        # Display new attachments in the layout
        if self.uploadDateSelector.currentText != "" and self.uploadDateSelector.currentText != "None":
            timepoint = self.attachmentsList[self.uploadPatientSelector.currentText][self.uploadDateSelector.currentText]
            for items in timepoint["items"]:
                item = qt.QCheckBox(items)
                self.uploadListLayout.addWidget(item)
                timepoint["checkbox"][items] = item
        if self.uploadListLayout.count() != 0:
            self.uploadButton.enabled = True
        else:
            self.uploadButton.enabled = False
            self.uploadListLayout.addWidget(self.noneLabel)
            self.noneLabel.setText("None")

    def executableSelected(self):
        """
            Function used to display the widget corresponding to the CLI selected
        """
        if hasattr(slicer.modules, self.executableSelector.currentText.lower()):
            self.modulesLoaded[str(self.executableSelector.currentText.lower())] = getattr(slicer.modules, self.executableSelector.currentText.lower()).widgetRepresentation().apply
            self.widgetSelectedGroupBox.show()
            if self.currentExecutable:
                self.layout.removeWidget(self.currentExecutable.widgetRepresentation())
                self.currentExecutable.widgetRepresentation().hide()
            self.currentExecutable = getattr(slicer.modules, self.executableSelector.currentText.lower())
            self.widgetSelectedGroupBoxLayout.addWidget(self.currentExecutable.widgetRepresentation())

            #  Adjust height
            self.currentExecutable.widgetRepresentation().setFixedHeight(350)

            # Change Apply connection to send a remote task
            applyButton = self.currentExecutable.widgetRepresentation().ApplyPushButton
            self.currentExecutable.widgetRepresentation().show()
            applyButton.disconnect(applyButton,'clicked()')
            applyButton.connect('clicked(bool)', self.createJobFromModule)

    def createJobFromModule(self):
        """
            Function used to create and submit a job based on the CLI interface 
        """
        cli = {}
        attachments = []
        if self.currentExecutable.widgetRepresentation().currentCommandLineModuleNode():
            node = self.currentExecutable.widgetRepresentation().currentCommandLineModuleNode()
            executionServer = ""
            if slicer.app.applicationName == "Slicer":
                executionServer = "Slicer" + slicer.app.applicationVersion[:5]
            else:
                executionServer = slicer.app.applicationName
            cli = {
                "executable": self.executableSelector.currentText,
                "parameters": [],
                "inputs": [],
                "outputs": [],
                "type": "job",
                "userEmail": self.DatabaseInteractorLib.getUserEmail(),
                "executionserver": executionServer
            }
            for groupIndex in xrange(0, node.GetNumberOfParameterGroups()):
                for parameterIndex in xrange(0, node.GetNumberOfParametersInGroup(groupIndex)):
                    if node.GetParameterLongFlag(groupIndex, parameterIndex):
                        flag = node.GetParameterLongFlag(groupIndex, parameterIndex)
                        if flag:
                            while flag[0] == "-":
                                flag = flag[1:]
                            flag = "--" + flag
                    else:
                        flag = node.GetParameterFlag(groupIndex, parameterIndex)
                        if flag:
                            while flag[0] == "-":
                                flag = flag[1:]
                            flag = "-" + flag

                    value = node.GetParameterAsString(node.GetParameterName(groupIndex, parameterIndex))
                    path = ''
                    tag = node.GetParameterTag(groupIndex, parameterIndex)

                    if tag == "image" or tag == "geometry" or tag == "transform":
                        # Write file in a temporary
                        IOnode = slicer.util.getNode(node.GetParameterAsString(node.GetParameterName(groupIndex, parameterIndex)))
                        if IOnode:
                            path = self.logic.nodeWriter(IOnode, slicer.app.temporaryPath)
                        value = os.path.basename(path)

                    if tag == "file":
                        path = node.GetParameterAsString(node.GetParameterName(groupIndex, parameterIndex))
                        value = os.path.basename(path)

                    if tag == "table" and node.GetParameterType(groupIndex, parameterIndex) == "color":
                        i = 1
                        while parameterIndex - i >= 0 :
                            if node.GetParameterType(groupIndex, parameterIndex-i) == 'label':
                                labelNode = slicer.util.getNode(node.GetParameterAsString(node.GetParameterName(groupIndex, parameterIndex-i)))
                                path = self.logic.nodeWriter(labelNode.GetDisplayNode().GetColorNode(), slicer.app.temporaryPath)
                                value = os.path.basename(path)
                                i = 100
                            i += 1

                    channel = node.GetParameterChannel(groupIndex, parameterIndex)
                    if channel and path:
                        if channel == "input":
                            attachments.append(path)
                            cli["inputs"].append({
                                "name": value
                            })
                        else:
                            if os.path.isdir(path) or os.path.basename(path).find('.') == -1:
                                type = 'directory'
                            else:
                                type = 'file'
                            cli["outputs"].append({
                                "type": type,
                                "name": value
                            })
                    cli['parameters'].append({
                        "flag": flag,
                        "name": value
                        # "name": node.GetParameterName(groupIndex, parameterIndex),
                        # "value": value,
                        # "type": node.GetParameterTag(groupIndex, parameterIndex)
                    })
        import pprint
        pprint.pprint(cli)
        if not self.ClusterpostLib.server:
            self.ClusterpostLib.setServerUrl(self.DatabaseInteractorLib.server[:-1])
        self.ClusterpostLib.createAndSubmitJob(cli, attachments)

    # ----------- Calendars ----------- #
    def fillSelectorWithAttachments(self):
        """
            Function used to fill a comboBox with attachments retrieved by queries
        """
        self.downloadAttachmentSelector.clear()
        self.downloadErrorText.hide()
        self.downloadButton.enabled = True
        attachmentName = ""
        if self.downloadRadioButtonPatientOnly.isChecked():
            for items in self.morphologicalData:
                if items["patientId"] == self.downloadPatientSelector.currentText:
                    if "_attachments" in items:
                        for attachmentName in items["_attachments"].keys():
                            self.downloadAttachmentSelector.addItem(attachmentName)
        else:
            for items in self.morphologicalData:
                # Check if the date is the same
                if not "date" in items:
                    items["date"] = "NoDate"
                if items["patientId"] == self.downloadPatientSelector.currentText and items["date"][:10] == str(
                        self.downloadDate.selectedDate):
                    if "_attachments" in items:
                        for attachmentName in items["_attachments"].keys():
                            self.downloadAttachmentSelector.addItem(attachmentName)
        if attachmentName == "":
            self.downloadAttachmentSelector.addItem("None")
            self.downloadErrorText.show()
            self.downloadButton.enabled = False

    # ------ Filepath selectors ------- #
    def createFilesDictionary(self):
        """
            Function used to create a dictionary corresponding to the collection architecture
        """
        directoryPath = self.uploadFilepathSelector.directory
        # Check if the directory selected is a valid collection
        if not os.path.exists(os.path.join(directoryPath, '.DBIDescriptor')):
            self.clearCheckBoxList()
            self.attachmentsList = {}
            self.uploadPatientSelector.clear()
            self.uploadPatientSelector.addItem("None")
            self.uploadDateSelector.clear()
            self.uploadDateSelector.addItem("None")
            return
        self.clearCheckBoxList()
        self.attachmentsList = {}
        # Iterate over patients
        for folderName in os.listdir(directoryPath):
            if folderName[0] != '.':
                self.attachmentsList[folderName] = {}
                # Iterate over dates
                for dates in os.listdir(os.path.join(directoryPath, folderName)):
                    if dates[0] != '.':
                        self.attachmentsList[folderName][dates] = {}
                        self.attachmentsList[folderName][dates]["items"] = []
                        self.attachmentsList[folderName][dates]["checkbox"] = {}
                        # Fill with attachment names
                        for files in os.listdir(os.path.join(directoryPath, folderName, dates)):
                            if files[0] != ".":
                                self.attachmentsList[folderName][dates]["items"].append(files)

        # Fill the patient selector comboBox with patients with changes
        self.uploadPatientSelector.clear()
        self.uploadPatientSelector.addItems(self.attachmentsList.keys())
        if self.uploadPatientSelector.count != 0:
            self.uploadButton.enabled = True
        else:
            self.uploadButton.enabled = False
            self.uploadPatientSelector.addItem("None")

    def onManagementDirectorySelected(self):
        """
            Function used to chose what signal to connect depending on management action checked
        """
        if self.managementRadioButtonPatient.isChecked():
            self.isPossibleCreatePatient()
        else:
            self.fillSelectorWithDescriptorPatients()
            self.isPossibleAddDate()

    # ---------------------------------------------------- #
    # ------------------ Other functions ----------------- #
    # ---------------------------------------------------- #
    def clearCheckBoxList(self):
        """
            Function used to clear the layout which displays the checkboxes for upload
        """
        for patient in self.attachmentsList.keys():
            for date in self.attachmentsList[patient].keys():
                for items in self.attachmentsList[patient][date]["checkbox"].keys():
                    self.uploadListLayout.removeWidget(self.attachmentsList[patient][date]["checkbox"][items])
                    self.attachmentsList[patient][date]["checkbox"][items].delete()
                self.attachmentsList[patient][date]["checkbox"] = {}

        self.noneLabel.setText("")
        self.uploadListLayout.removeWidget(self.noneLabel)

    def checkBoxesChecked(self):
        """
            Function used to store in a dictionary the attachments selected to be uploaded
        """
        self.checkedList = {}
        for patient in self.attachmentsList.keys():
            self.checkedList[patient] = {}
            for date in self.attachmentsList[patient].keys():
                self.checkedList[patient][date] = {}
                self.checkedList[patient][date]["items"] = []
                for items in self.attachmentsList[patient][date]["checkbox"].keys():
                    if str(self.attachmentsList[patient][date]["checkbox"][items].checkState()) == "2" :
                        self.checkedList[patient][date]["items"].append(items)

    def highlightDates(self):
        """
            Function used to color the dates which contain one or multiple attachments for a given patientId
        """
        for items in self.morphologicalData:
            if "date" in items:
                date = items["date"]
                if items["patientId"] == self.downloadPatientSelector.currentText:
                    date = items["date"]
                    self.downloadDate.setDateTextFormat(qt.QDate(int(date[:4]),int(date[5:7]),int(date[8:10])),
                                                        self.checkableDateFormat)
                else:
                    self.downloadDate.setDateTextFormat(qt.QDate(int(date[:4]), int(date[5:7]), int(date[8:10])),
                                                        self.normalDateFormat)

    def overflow(self):
        """
            Function triggered by the overflow of the timer  
        """
        self.timer.stop()
        print(">>>>>>>>>>>>>>>>")
        # Retrieve the jobs to be computed in the database
        jobs = self.ClusterpostLib.getJobs(jobstatus='QUEUE')
        if jobs:
            self.runJob(jobs[0])
        self.timer.start(self.timerPeriod)

    def runJob(self, job):
        """
            Function used to run a job and send it back to the server 
        """
        # Creates a folder to store IO for the job. Folder is in Slicer temporary path and named with job id
        jobpath = os.path.join(slicer.app.temporaryPath, job["_id"])
        if os.path.exists(jobpath):
            shutil.rmtree(jobpath)
        os.makedirs(jobpath)
        # Check if the executable needed is in the current instance of Slicer
        if hasattr(slicer.modules, job["executable"].lower()):
            executableNode = getattr(slicer.modules, job["executable"].lower())
            command = list()
            # Depending on Slicer version, the executable path is pointing to the library or the executable
            if os.path.basename(executableNode.path).find('.') == -1:
                command.append(executableNode.path)
            else:
                command.append(os.path.join(os.path.dirname(executableNode.path), executableNode.name))
            # Parse all the parameters to create de CLI command
            for parameter in job["parameters"]:
                if not parameter["name"] == "" and not parameter["flag"] == "":
                    if parameter["name"] == "true":
                        command.append(parameter["flag"])
                    elif not parameter["name"] == "false":
                        command.append(parameter["flag"])
                        command.append(parameter["name"])
                elif parameter["flag"] == "":
                    command.append(parameter["name"])
            self.ClusterpostLib.updateJobStatus(job["_id"], "DOWNLOADING")
            # Downloads the attachments and store them in the previously created folder
            for attachment in job["_attachments"]:
                self.ClusterpostLib.getAttachment(job["_id"], attachment, os.path.join(jobpath, attachment))
                if attachment in command:
                    i = command.index(attachment)
                    command[i] = os.path.join(jobpath, attachment)
            # This value is set as true if there is at least one output with type folder
            directory = False
            # Formating the ouput content (file/directory)
            for output in job["outputs"]:
                if output['type'] == 'directory':
                    if os.path.basename(output["name"]):
                        if output["name"] in command:
                            i = command.index(output["name"])
                            command[i] = os.path.join(jobpath, os.path.basename(output["name"]))
                        folderName = os.path.basename(output["name"])
                    else:
                        if output["name"] in command:
                            i = command.index(output["name"])
                            command[i] = os.path.join(jobpath)
                        folderName = os.path.basename(os.path.dirname(output["name"]))
                    directory = True
                else:
                    file = open(os.path.join(jobpath, output["name"]), 'w+')
                    file.close()
                    if output["name"] in command:
                        i = command.index(output["name"])
                        command[i] = os.path.join(jobpath, output["name"])
            # Check the files before computation
            filesBeforeComputation = os.listdir(jobpath)
            print(command)
            self.ClusterpostLib.updateJobStatus(job["_id"], "RUN")
            try:
                # Subprocess is a way to run a cli from python
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                self.displayConsole.append(out)
                self.displayConsole.append(err)
                # Check files differences before and after computation for output with type directory
                filesAfterComputation = os.listdir(jobpath)
                filesDifference = list(set(filesAfterComputation) - set(filesBeforeComputation))
                self.ClusterpostLib.updateJobStatus(job["_id"], "UPLOADING")
                # Upload stdout and stderr
                with open(os.path.join(jobpath, 'stdout.out'), 'w') as f:
                    f.write(out)
                with open(os.path.join(jobpath, 'stderr.err'), 'w') as f:
                    f.write(err)
                self.ClusterpostLib.addAttachment(job["_id"], os.path.join(jobpath, 'stdout.out'))
                self.ClusterpostLib.addAttachment(job["_id"], os.path.join(jobpath, 'stderr.err'))
                outputSize = []
                for output in job["outputs"]:
                    if output['type'] == 'file':
                        self.ClusterpostLib.addAttachment(job["_id"],
                                                          os.path.join(jobpath, output["name"]))
                        outputSize.append(os.stat(os.path.join(jobpath, output["name"])).st_size)
                # Add all the new files in a zip file
                if not directory:
                    folderName = "computationFiles"
                print filesDifference
                if len(filesDifference) > 0:
                    with zipfile.ZipFile(os.path.join(jobpath, folderName + '.zip'), 'w') as myzip:
                        for file in filesDifference:
                            myzip.write(os.path.join(jobpath, file), file)
                    self.ClusterpostLib.addAttachment(job["_id"],
                                                      os.path.join(jobpath, folderName + '.zip'))
                    outputSize.append(os.stat(os.path.join(jobpath, folderName + '.zip')).st_size)
                # Check if the output file is not empty
                if 0 in outputSize:
                    self.ClusterpostLib.updateJobStatus(job["_id"], "FAIL")
                else:
                    self.ClusterpostLib.updateJobStatus(job["_id"], "DONE")
            except Exception as e:
                with open(os.path.join(jobpath, 'stderr.err'), 'w') as f:
                    f.write(str(e))
                self.ClusterpostLib.addAttachment(job["_id"], os.path.join(jobpath, 'stderr.err'))
                self.ClusterpostLib.updateJobStatus(job["_id"], "FAIL")

#
# DatabaseInteractorLogic
#

class DatabaseInteractorLogic(slicer.ScriptedLoadableModule.ScriptedLoadableModuleLogic):
    def fileLoader(self, filepath):
        """
            Function used to load a file in the node corresponding to the file extension
            Documentation : http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.5/SlicerApplication/SupportedDataFormat
        """
        sceneExtensions = ["mrml","mrb","xml","xcat"]
        volumeExtensions = ["dcm","nrrd","nhdr","mhd","mha","vtk","hdr","img","nia","nii","bmp","pic","mask","gipl","jpg","jpeg","lsm","png","spr","tif","tiff","mgz","mrc","rec"]
        modelExtensions = ["vtk","vtp","stl","obj","orig","inflated","sphere","white","smoothwm","pial","g","byu"]
        fiducialExtensions = ["fcsv","txt"]
        rulerExtensions = ["acsv","txt"]
        transformExtensions = ["tfm","mat","txt","nrrd","nhdr","mha","mhd","nii"]
        volumeRenderingExtensions = ["vp","txt"]
        colorsExtensions = ["ctbl","txt"]
        extension = ""

        if filepath.rfind(".") != -1:
            extension = filepath[filepath.rfind(".") + 1:]
            if extension == "gz":
                extension = filepath[filepath[:filepath.rfind(".")].rfind(".") + 1:filepath.rfind(".")]
        if extension in sceneExtensions:
            slicer.util.loadScene(filepath)
        if extension in volumeExtensions:
            slicer.util.loadVolume(filepath)
        if extension in modelExtensions:
            slicer.util.loadModel(filepath)
        if extension in fiducialExtensions:
            if not slicer.util.loadFiducialList(filepath):
                if not slicer.util.loadAnnotationFiducial(filepath):
                    slicer.util.loadNodeFromFile(filepath)
        # if extension in rulerExtensions:
        if extension in transformExtensions:
            slicer.util.loadTrandform(filepath)
        # if extension in volumeRenderingExtensions:
        if extension in colorsExtensions:
            slicer.util.loadColorTable(filepath)

    def nodeWriter(self, node, dirpath):
        """
            Function used to write the content of a node in a file given the node and the path
        """
        fileName = node.GetName()

        # Window UI to choose file extension
        extensionBox = qt.QDialog()
        extensionBox.setWindowTitle("Select file extension")

        extensionBoxLayout = qt.QFormLayout()
        extensionComboBox = qt.QComboBox()
        extensionBoxLayout.addRow(fileName, extensionComboBox)
        buttonBox = qt.QDialogButtonBox(qt.QDialogButtonBox.Ok)
        extensionBoxLayout.addWidget(buttonBox)
        extensionBox.setLayout(extensionBoxLayout)

        buttonBox.accepted.connect(extensionBox.accept)
        buttonBox.rejected.connect(extensionBox.reject)

        if "LabelMap" in node.GetClassName() or "ScalarVolume" in node.GetClassName():
            extensionComboBox.addItems([".nrrd",".nii",".gipl.gz"])
            extensionBox.exec_()
            extension = extensionComboBox.currentText
        if "ColorTable" in node.GetClassName():
            extension = '.txt'
        if "ModelHierarchy" in node.GetClassName():
            extension = '.mrml'
        if "ModelNode" in node.GetClassName():
            extensionComboBox.addItems([".vtk", ".stl", ".obj"])
            extensionBox.exec_()
            extension = extensionComboBox.currentText
        if "Transform" in node.GetClassName():
            extension = ".mat"

        write = slicer.util.saveNode(node,os.path.join(dirpath,fileName + extension))
        if not write and extension == ".mrml":
            slicer.util.saveScene(os.path.join(dirpath, fileName + extension))
        return os.path.join(dirpath,fileName + extension)


class DatabaseInteractorTest(slicer.ScriptedLoadableModule.ScriptedLoadableModuleTest):
    def setUp(self):
        """
            Function used to reset the scene for the tests
        """
        self.widget = slicer.modules.DatabaseInteractorWidget
        self.DatabaseInteractorLib = self.widget.DatabaseInteractorLib
        slicer.mrmlScene.Clear(0)
        self.DatabaseInteractorLib.disconnect()

    def runTest(self):
        """
            Function used to run some tests about the extension behaviour
        """
        self.runTestDbInteractor()
        self.runTestClusterpost()

    # Run the tests
    def runTestDbInteractor(self):
        self.setUp()

        self.delayDisplay(' Starting tests ')

        self.delayDisplay(' Test Login Function ')
        self.assertTrue(self.test_Login())
        self.delayDisplay(' Test createCollection Function ')
        self.assertTrue(self.test_createCollection())
        self.delayDisplay(' Test getCollection Function ')
        self.assertTrue(self.test_getCollection())
        self.delayDisplay(' Test createPatient Function ')
        self.assertTrue(self.test_createPatient())
        self.delayDisplay(' Test importData Function ')
        self.assertTrue(self.test_importData())
        self.delayDisplay(' Test uploadAttachment Function ')
        self.assertTrue(self.test_uploadAttachment())
        self.delayDisplay(' Test getAttachment Function ')
        self.assertTrue(self.test_getAttachment())
        self.delayDisplay(' Test deletePatient Function ')
        self.assertTrue(self.test_deletePatient())
        self.delayDisplay(' Test deleteCollection Function ')
        self.assertTrue(self.test_deleteCollection())

        self.delayDisplay(' Tests Passed! ')


    def test_Login(self):
        """ ---------------------------------------------------------------- 
            ---------------------- Login to the server --------------------- 
            ---------------------------------------------------------------- """
        server = 'http://localhost:8180/'
        user = 'clement.mirabel@gmail.com'
        password = 'Password1234'
        self.delayDisplay('Attempting to connect to %s.' % (server))
        self.DatabaseInteractorLib.setServer(server, slicer.app.temporaryPath + '/user.slicer_server')
        token,error = self.DatabaseInteractorLib.connect(user,password)
        if token == -1:
            print("Connection Failed : " + error)
            return False
        print("Connection Passed !")
        return True

    def test_createCollection(self):
        """ ---------------------------------------------------------------- 
            ------------------ Creating a test collection ------------------ 
            ---------------------------------------------------------------- """
        data = {"items": "[]",
                "type": "morphologicalDataCollection",
                "name": "CollectionTest"}
        rep = self.DatabaseInteractorLib.createMorphologicalDataCollection(data)
        if rep == -1:
            print("Collection creation Failed!")
            return False
        print("Collection creation Passed!")
        return True

    def test_getCollection(self):
        """ ----------------------------------------------------------------
            ------------------ Getting the test collection ----------------- 
            ---------------------------------------------------------------- """
        rep = self.DatabaseInteractorLib.getMorphologicalDataCollections()
        for items in rep.json():
            if items["name"]=="CollectionTest":
                self.collectionTestId = items["_id"]
                print("Getting collection Passed!")
                return True
        print("Getting collection Failed!")
        return False

    def test_createPatient(self):
        """ ----------------------------------------------------------------
            ---------------------- Creating a patient ---------------------- 
            ---------------------------------------------------------------- """
        data = {"type": "morphologicalData", "patientId": "PatientTest"}
        rep = self.DatabaseInteractorLib.createMorphologicalData(data)
        if rep == -1:
            print("Patient creation Failed!")
            return False
        self.patientId = rep.json()["id"]
        rep = self.DatabaseInteractorLib.getMorphologicalDataCollection(self.collectionTestId).json()
        rep["items"].append({'_id': self.patientId})
        upd = self.DatabaseInteractorLib.updateMorphologicalDataCollection(json.dumps(rep))
        if upd == -1:
            print("Patient creation Failed!")
            return False
        print("Patient creation Passed!")
        return True



    def test_uploadAttachment(self):
        """ ---------------------------------------------------------------- 
            -------------------- Uploading an attachment ------------------- 
            ---------------------------------------------------------------- """
        self.moduleName = 'DatabaseInteractor'
        filePath = slicer.app.temporaryPath + '/FA.nrrd'
        file = open(filePath,'rb')
        data = file.read()
        rep = self.DatabaseInteractorLib.addAttachment(self.patientId,'attachmentTest.nrrd',data)
        if rep == -1:
            print("Attachment upload Failed!")
            return False
        print("Attachment upload Passed!")
        return True

    def test_getAttachment(self):
        """ ---------------------------------------------------------------- 
            -------------------- Getting an attachment ------------------- 
            ---------------------------------------------------------------- """
        rep = self.DatabaseInteractorLib.getAttachment(self.patientId,'attachmentTest.nrrd', 'blob')
        if rep == -1:
            print("Getting attachment Failed!")
            return False
        filePath = slicer.app.temporaryPath + '/attachmentTest.nrrd'
        with open(filePath, 'wb+') as fd:
            for chunk in rep.iter_content(2048):
                fd.write(chunk)
        slicer.util.loadVolume(filePath)
        print("Getting attachment Passed!")
        return True

    def test_deletePatient(self):
        """ ---------------------------------------------------------------- 
            -------------------- Delete the test patient ------------------- 
            ---------------------------------------------------------------- """
        rep = self.DatabaseInteractorLib.deleteMorphologicalData(self.patientId)
        if rep == -1:
            print("Patient deletion Failed!")
            return False
        print("Patient deletion Passed!")
        return True

    def test_deleteCollection(self):
        """ ---------------------------------------------------------------- 
            ------------------ Delete the test collection ------------------ 
            ---------------------------------------------------------------- """
        rep = self.DatabaseInteractorLib.deleteMorphologicalDataCollection(self.collectionTestId)
        if rep == -1:
            print("Collection deletion Failed!")
            return False
        print("Collection deletion Passed!")
        return True

    def test_importData(self):
        """ ---------------------------------------------------------------- 
            ------------------- Download some data online ------------------ 
            ---------------------------------------------------------------- """
        import urllib
        downloads = (
            ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd'),
        )

        for url, name in downloads:
            filePath = os.path.join(slicer.app.temporaryPath, name)
            if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
                logging.info('Requesting download %s from %s...\n' % (name, url))
                urllib.urlretrieve(url, filePath)
        return True

    def runTestClusterpost(self):
        import ClusterpostLib
        import urllib

        self.testfile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../DatabaseInteractor.png")

        self.setUp()

        self.clusterpost = ClusterpostLib.ClusterpostLib()

        self.clusterpost.setServerUrl("http://localhost:8180")
        
        self.delayDisplay(' Starting tests ')

        self.assertTrue(self.testClusterpostLogin())

        self.assertTrue(self.testGetExecutionServers())

        self.assertTrue(self.testCreateJob())

        self.assertTrue(self.testAddAttachment())

        self.assertTrue(self.testExecuteJob())

        self.assertTrue(self.testGetJob())

        self.assertTrue(self.testGetJobs())

        self.assertTrue(self.testGetDocumentAttachment())

        self.assertTrue(self.testCreateAndSubmitJob())

        self.assertTrue(self.testGetJobsDone())

    def testClusterpostLogin(self):
        self.clusterpost.userLogin({
            "email": "algiedi85@gmail.com",
            "password": "123Algiedi!"
            })

        return True
        
    def testGetExecutionServers(self):
        servers = self.clusterpost.getExecutionServers()
        print servers
        self.executionserver = servers[0]["name"]
        return True

    def testCreateJob(self):
        job = {
            "executable": "cksum",
            "parameters": [
                {
                    "flag": "",
                    "name": "DatabaseInteractor.png"
                }
            ],
            "inputs": [
                {
                    "name": "DatabaseInteractor.png"
                }
            ],
            "outputs": [
                {
                    "type": "directory",
                    "name": "./"
                },            
                {
                    "type": "tar.gz",
                    "name": "./"
                },
                {
                    "type": "file",
                    "name": "stdout.out"
                },
                {
                    "type": "file",
                    "name": "stderr.err"
                }
            ],
            "type": "job",
            "userEmail": "algiedi85@gmail.com",
            "executionserver": self.executionserver
        }

        res = self.clusterpost.createJob(job)

        self.jobid = res["id"]

        return True

    def testAddAttachment(self):
        res = self.clusterpost.addAttachment(self.jobid, self.testfile)

        return True

    def testExecuteJob(self):

        res = self.clusterpost.executeJob(self.jobid)

        return True

    def testGetJob(self):
        res = self.clusterpost.getJob(self.jobid)

        return True

    def testGetJobs(self):
        res = self.clusterpost.getJobs("cksum")

        return True

    def testGetDocumentAttachment(self):
        res = self.clusterpost.getAttachment(self.jobid, self.testfile, "/tmp/out.png", "blob")

        return True

    def testCreateAndSubmitJob(self):
        job = {
            "executable": "cksum",
            "parameters": [
                {
                    "flag": "",
                    "name": "DatabaseInteractor.png"
                }
            ],
            "inputs": [
                {
                    "name": "DatabaseInteractor.png"
                }
            ],
            "outputs": [
                {
                    "type": "directory",
                    "name": "./"
                },            
                {
                    "type": "tar.gz",
                    "name": "./"
                },
                {
                    "type": "file",
                    "name": "stdout.out"
                },
                {
                    "type": "file",
                    "name": "stderr.err"
                }
            ],
            "type": "job",
            "userEmail": "algiedi85@gmail.com",
            "executionserver": self.executionserver
        }

        files = [self.testfile]
        res = self.clusterpost.createAndSubmitJob(job, [self.testfile])

        return True

    def testGetJobsDone(self):
        outdir = "/tmp/"
        self.clusterpost.getJobsDone(outdir)

        return True
