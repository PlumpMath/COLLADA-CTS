# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import wx
import os
import os.path
import types

import Core.Common.FUtils as FUtils
from Core.Common.FConstants import *
from Core.Common.FSerializer import *
from Core.Gui.FImageType import *

class FCompareSetupDialog(wx.Dialog, FSerializer):
  
    __COMPARE_STEP = "Different Step"
    __COMPARE_EXECUTION = "Different Execution"
    __COMPARE_TEST = "Different Test"
    __COMPARE_TEST_PROCEDURE = "Different Test Procedure"
    
    __IMAGE_TITLE = "Compare Image With..."
    __EXECUTION_TITLE = "Compare Execution With..."
    __LOG_TITLE = "Compare Log With..."
    __ANIMATION_TITLE = "Compare Animation With..."
    __BLESSED_IMAGE = "Include Default Blessed"
    __BLESSED_EXECUTION = "Include Last Blessed Execution"
    
    def __init__(self, parent, type, testProcedure, test, execution):
        if (type == FImageType.IMAGE):
            dialogTitle = FCompareSetupDialog.__IMAGE_TITLE
        elif (type == FImageType.EXECUTION):
            dialogTitle = FCompareSetupDialog.__EXECUTION_TITLE
        elif (type == FImageType.LOG):
            dialogTitle = FCompareSetupDialog.__LOG_TITLE
        elif (type == FImageType.ANIMATION):
            dialogTitle = FCompareSetupDialog.__ANIMATION_TITLE
        else:
            raise ValueError, "Invalid type."
        
        if (not self.__CheckTestProcedure(testProcedure)):
            raise ValueError, "Invalid procedure: " + testProcedure
        if (not self.__CheckTest(testProcedure, test)):
            raise ValueError, "Invalid test: " + test
        if (not self.__CheckExecution(testProcedure, test, execution)):
            raise ValueError, "Invalid execution: " + execution
        
        wx.Dialog.__init__(self, parent, wx.ID_ANY, dialogTitle)
        self.__ID_OK = wx.NewId()
        self.__ID_CANCEL = wx.NewId()
        self.__ID_COMPARE = wx.NewId()
        self.__ID_TEST_PROCEDURE = wx.NewId()
        self.__ID_TEST = wx.NewId()
        self.__ID_EXECUTION = wx.NewId()
        
        self.__type = type
        self.__testProcedureObject = self.Load(os.path.join(RUNS_FOLDER,
                testProcedure, TEST_PROCEDURE_FILENAME))
        self.__testProcedure = testProcedure
        self.__test = test
        self.__execution = execution
        self.__curTestProcedureObject = None
        self.__curTestProcedure = None
        self.__curTest = None
        self.__curExecution = None
        
        self.__animationSteps = []
        
        self.__blessedCheckBox = None
        self.__compareRadio = None
        self.__browseSizer = None
        self.__testProcedureLabel = None
        self.__testLabel = None
        self.__executionLabel = None
        self.__stepLabel = None
        self.__testProcedureCombo = None
        self.__testCombo = None
        self.__executionCombo = None
        self.__stepCombo = None
        
        outterSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(outterSizer)
        
        middleSizer = self.__GetMiddleSizer(type)
        bottomSizer = self.__GetBottomSizer()
        
        outterSizer.Add(middleSizer, 0, wx.EXPAND | wx.ALL, 5)
        outterSizer.Add(bottomSizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        self.__UpdateShowBrowse(True, True, True, True, False)
        self.Fit()
        self.__OnRadio(None)
    
    def GetShowBlessed(self):
        return self.__blessedCheckBox.IsChecked()
    
    def GetPath(self):
        if ((self.__curExecution == None) or (self.__curTest == None) or
                (self.__curTestProcedure == None)): 
            return None
        
        executionDir = os.path.join(RUNS_FOLDER, self.__curTestProcedure,
                self.__curTest, self.__curExecution)
        
        if (self.__type == FImageType.EXECUTION):
            return os.path.normpath(
                    os.path.join(executionDir, EXECUTION_FILENAME))
        
        filename = self.__stepCombo.GetStringSelection()
        if (filename == ""): return None
        
        if (self.__type == FImageType.LOG):
            return os.path.normpath(os.path.join(executionDir, filename))
        
        paths = []
        for frame in self.__animationSteps[self.__stepCombo.GetSelection()]:
            paths.append(os.path.normpath(os.path.join(executionDir, frame)))
        return paths
    
    def GetTestProcedure(self):
        return self.__curTestProcedure
    
    def GetTest(self):
        return self.__curTest
    
    def GetExecution(self):
        return self.__curExecution
    
    def GetStep(self):
        return self.__stepCombo.GetStringSelection()
    
    def __OnOk(self, e):
        """Call-back function when OK button is pressed.
            
        arguments:
            e -- the event generated by the OK button being pressed.
            
        """
        
        if (self.IsModal()):
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.Show(False)
    
    def __OnCancel(self, e):
        """Call-back function when Cancel button is pressed.
        
        arguments:
            e -- the event generated by the Cancel button being pressed.
            
        """
        if (self.IsModal()):
            self.EndModal(wx.ID_CANCEL)
        else:
            self.SetReturnCode(wx.ID_CANCEL)
            self.Show(False)
    
    def __OnRadio(self, e):
        selection = self.__compareRadio.GetStringSelection()
        
        if (selection == FCompareSetupDialog.__COMPARE_STEP):
            self.__UpdateShowBrowse(False, False, False, True, True)
            self.__DisableBrowse()
            
            self.__curTestProcedureObject = self.__testProcedureObject
            self.__curTestProcedure = self.__testProcedure
            self.__curTest = self.__test
            self.__curExecution = self.__execution
            self.__UpdateStep(self.__execution)
            
            self.__UpdateEnableBrowse(False, False, False, True)
        elif (selection == FCompareSetupDialog.__COMPARE_EXECUTION):
            self.__UpdateShowBrowse(False, False, True, True, True)
            self.__DisableBrowse()
            
            self.__curTestProcedureObject = self.__testProcedureObject
            self.__curTestProcedure = self.__testProcedure
            self.__curTest = self.__test
            self.__UpdateExecution(self.__test)
            
            self.__UpdateEnableBrowse(False, False, True, False)
        elif (selection == FCompareSetupDialog.__COMPARE_TEST):
            self.__UpdateShowBrowse(False, True, True, True, True)
            self.__DisableBrowse()
            
            self.__curTestProcedureObject = self.__testProcedureObject
            self.__curTestProcedure = self.__testProcedure
            self.__UpdateTest(self.__testProcedure)
            
            self.__UpdateEnableBrowse(False, True, False, False)
        elif (selection == FCompareSetupDialog.__COMPARE_TEST_PROCEDURE):
            self.__UpdateShowBrowse(True, True, True, True, True)
            self.__DisableBrowse()
            
            self.__UpdateTestProcedure()
            
            self.__UpdateEnableBrowse(True, False, False, False)
    
    def __OnTestProcedure(self, e):
        self.__curTestProcedure = (self.__testProcedureCombo.
                                                        GetStringSelection())
        self.__curTestProcedureObject = self.Load(os.path.join(RUNS_FOLDER,
                self.__curTestProcedure, TEST_PROCEDURE_FILENAME))
        self.__DisableBrowse()
        self.__UpdateTest(self.__curTestProcedure)
        self.__UpdateEnableBrowse(True, True, False, False)
    
    def __OnTest(self, e):
        self.__curTest = self.__testCombo.GetClientData(
                                            self.__testCombo.GetSelection())
        self.__DisableBrowse()
        self.__UpdateExecution(self.__curTest)
        self.__UpdateEnableBrowse(True, True, True, False)
    
    def __OnExecution(self, e):
        self.__curExecution = self.__executionCombo.GetStringSelection()
        if (not self.__type == FImageType.EXECUTION):
            self.__DisableBrowse()
            self.__UpdateStep(self.__curExecution)
            self.__UpdateEnableBrowse(True, True, True, True)
    
    def __DisableBrowse(self):
        """Call this to disable browsing while calculating."""
        self.__testProcedureCombo.Enable(False)
        self.__testProcedureLabel.Enable(False)
        self.__testCombo.Enable(False)
        self.__testLabel.Enable(False)
        self.__executionCombo.Enable(False)
        self.__executionLabel.Enable(False)
        if (self.__stepCombo != None):
            self.__stepCombo.Enable(False)
            self.__stepLabel.Enable(False)
        self.Update()
    
    def __UpdateEnableBrowse(self, enableTestProcedure, enableTest, 
                             enableExecution, enableStep):
        self.__testProcedureLabel.Enable(enableTestProcedure)
        self.__testProcedureCombo.Enable(enableTestProcedure)
        if (not enableTestProcedure):
            if (self.__testProcedureCombo.IsShown()):
                self.__curTestProcedure = None
            self.__testProcedureCombo.Clear()
        
        self.__testLabel.Enable(enableTest)
        self.__testCombo.Enable(enableTest)
        if (not enableTest):
            if (self.__testCombo.IsShown()):
                self.__curTest = None
            self.__testCombo.Clear()
        
        self.__executionLabel.Enable(enableExecution)
        self.__executionCombo.Enable(enableExecution)
        if (not enableExecution):
            if (self.__executionCombo.IsShown()):
                self.__curExecution = None
            self.__executionCombo.Clear()
            
        if (self.__stepCombo != None) :
            self.__stepLabel.Enable(enableStep)
            self.__stepCombo.Enable(enableStep)
            if (not enableStep):
                self.__stepCombo.Clear()
    
    def __UpdateShowBrowse(self, showTestProcedure, showTest, showExecution, 
                       showStep, resize):
        browseSize = self.__browseSizer.GetSize()
        
        self.__testProcedureLabel.Show(showTestProcedure)
        self.__testLabel.Show(showTest)
        self.__executionLabel.Show(showExecution)
        self.__testProcedureCombo.Show(showTestProcedure)
        self.__testCombo.Show(showTest)
        self.__executionCombo.Show(showExecution)
        if (self.__stepCombo != None):
            self.__stepLabel.Show(showStep)
            self.__stepCombo.Show(showStep)
        
        if (resize):
            self.__browseSizer.SetMinSize(browseSize)
            self.__JiggleSize()
    
    def __JiggleSize(self):
        size = self.GetSize()
        size.SetHeight(size.GetHeight() + 1)
        self.SetSize(size)
        size.SetHeight(size.GetHeight() - 1)
        self.SetSize(size)
    
    def __CheckTestProcedure(self, testProcedure):
        return os.path.isfile(os.path.join(RUNS_FOLDER, testProcedure, 
                              TEST_PROCEDURE_FILENAME))
    
    def __CheckTest(self, testProcedure, test):
        return os.path.isfile(
                os.path.join(RUNS_FOLDER, testProcedure, test, TEST_FILENAME))
    
    def __CheckExecution(self, testProcedure, test, execution):
        return os.path.isfile(
                os.path.join(RUNS_FOLDER, testProcedure, test, execution, 
                             EXECUTION_FILENAME))
    
    def __UpdateStep(self, execution):
        if (not self.__CheckExecution(self.__curTestProcedure, self.__curTest, 
                                      execution)):
            raise ValueError, "An invalid execution came in"
        
        stepList = []
        self.__animationSteps = []
        relExecutionDir = os.path.join(RUNS_FOLDER, self.__curTestProcedure,
                self.__curTest, execution)
        relExecutionPath = os.path.join(relExecutionDir, EXECUTION_FILENAME)
        
        # dangerous method call -- optimization only
        execution = self.Load(relExecutionPath) 
        for step, app, op, settings in (self.__curTestProcedureObject.
                                                        GetStepGenerator()):
            if ((self.__type == FImageType.IMAGE) or 
                    (self.__type == FImageType.ANIMATION)):
                output = execution.GetOutputLocation(step)
                if (output == None): continue
                if (not type(output) is types.ListType): continue #validation
                
                miniList = []
                for entry in output:
                    miniList.append(
                            FUtils.GetRelativePath(entry, relExecutionDir))
                self.__animationSteps.append(miniList)
                stepList.append(FUtils.GetRelativePath(
                        os.path.dirname(output[-1]), relExecutionDir))
                
            elif (self.__type == FImageType.LOG):
                output = execution.GetLog(step)
                if (output == None): continue
                
                stepList.append(
                        FUtils.GetRelativePath(output, relExecutionDir))
        
        self.__stepCombo.Clear()
        self.__stepCombo.AppendItems(stepList)
    
    def __UpdateExecution(self, test):
        if (not self.__CheckTest(self.__curTestProcedure, test)):
            raise ValueError, "An invalid test came in"
        
        executionList = []
        relTestDir = os.path.join(RUNS_FOLDER, self.__curTestProcedure, test)
        entries = os.listdir(relTestDir)
        for entry in entries:
            if (os.path.isfile(os.path.join(relTestDir, entry, 
                                            EXECUTION_FILENAME))):
                executionList.append(entry)
        executionList.sort()
        self.__curExecution = None
        self.__executionCombo.Clear()
        self.__executionCombo.AppendItems(executionList)
    
    def __UpdateTest(self, testProcedure):
        if (not self.__CheckTestProcedure(testProcedure)):
            raise ValueError, "An invalid test procedure came in"
        
        testList = []
        relProcedureDir = os.path.join(RUNS_FOLDER, testProcedure)
        entries = os.listdir(relProcedureDir )
        for entry in entries:
            testObject = os.path.join(relProcedureDir, entry, TEST_FILENAME)
            if (os.path.isfile(testObject)):
                test = self.Load(testObject)
                testList.append((test.GetSeparatedFilename(),entry))
        testList.sort()
        self.__curTest = None
        self.__testCombo.Clear()
        for i in range(len(testList)):
            self.__testCombo.Append(*testList[i])
    
    def __UpdateTestProcedure(self):
        testProcedureList = []
        entries = os.listdir(RUNS_FOLDER)
        for entry in entries:
            relPath = os.path.join(RUNS_FOLDER, entry, TEST_PROCEDURE_FILENAME)
            if (os.path.isfile(relPath)):
                if (self.__type == FImageType.EXECUTION):
                    # dangerous method call -- optimization only
                    procedure = self.QuickLoad(relPath) 
                    if (not self.__testProcedureObject.StepEquals(procedure)):
                        continue
                    procedure = None # safety
                testProcedureList.append(entry)
        testProcedureList.sort()
        self.__curTestProcedure = None
        self.__testProcedureCombo.Clear()
        self.__testProcedureCombo.AppendItems(testProcedureList)
    
    def __GetMiddleSizer(self, type):
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        if (type == FImageType.EXECUTION):
            self.__blessedCheckBox = wx.CheckBox(self, wx.ID_ANY, 
                    FCompareSetupDialog.__BLESSED_EXECUTION)
        else:
            self.__blessedCheckBox = wx.CheckBox(self, wx.ID_ANY, 
                    FCompareSetupDialog.__BLESSED_IMAGE)
        
        if (type == FImageType.EXECUTION):
            compareList = []
        else:
            compareList = [FCompareSetupDialog.__COMPARE_STEP]
        
        compareList = compareList + [FCompareSetupDialog.__COMPARE_EXECUTION, 
                                FCompareSetupDialog.__COMPARE_TEST,
                                FCompareSetupDialog.__COMPARE_TEST_PROCEDURE]
        
        self.__compareRadio = wx.RadioBox(self, self.__ID_COMPARE, 
                "Compare With", wx.DefaultPosition, wx.DefaultSize, 
                compareList, 1, wx.RA_SPECIFY_ROWS)
        self.Bind(wx.EVT_RADIOBOX, self.__OnRadio, self.__compareRadio, 
                  self.__ID_COMPARE)
        
        self.__browseSizer = self.__GetBrowseSizer(type)
        
        sizer.Add(self.__blessedCheckBox, 0, wx.ALL, 5)
        sizer.Add(self.__compareRadio, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.__browseSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        if (type == FImageType.LOG):
            self.__blessedCheckBox.Show(False)
        return sizer 
    
    def __GetBrowseSizer(self, type):
        browseStaticBox = wx.StaticBox(self, wx.ID_ANY, "Browse")
        browseSizer = wx.StaticBoxSizer(browseStaticBox, wx.HORIZONTAL)
        
        gridSizer = wx.FlexGridSizer(cols = 2, vgap = 5, hgap = 5)
        gridSizer.AddGrowableCol(1)
        
        
        self.__testProcedureLabel = wx.StaticText(self, wx.ID_ANY, 
                                                  "Test Procedure:")
        self.__testProcedureCombo = wx.ComboBox(self, self.__ID_TEST_PROCEDURE, 
                size = wx.Size(500, -1), style = wx.CB_READONLY)
        gridSizer.Add(self.__testProcedureLabel)
        gridSizer.Add(self.__testProcedureCombo, 0, wx.EXPAND)
        self.Bind(wx.EVT_COMBOBOX, self.__OnTestProcedure, 
                self.__testProcedureCombo, self.__ID_TEST_PROCEDURE)
        
        self.__testLabel = wx.StaticText(self, wx.ID_ANY, "Test:")
        self.__testCombo = wx.ComboBox(self, self.__ID_TEST, 
                style = wx.CB_READONLY)
        gridSizer.Add(self.__testLabel)
        gridSizer.Add(self.__testCombo, 0, wx.EXPAND)
        self.Bind(wx.EVT_COMBOBOX, self.__OnTest, self.__testCombo, 
                self.__ID_TEST)
        
        self.__executionLabel = wx.StaticText(self, wx.ID_ANY, "Execution:")
        self.__executionCombo = wx.ComboBox(self, self.__ID_EXECUTION, 
                style = wx.CB_READONLY)
        gridSizer.Add(self.__executionLabel)
        gridSizer.Add(self.__executionCombo, 0, wx.EXPAND)
        self.Bind(wx.EVT_COMBOBOX, self.__OnExecution, self.__executionCombo,
                self.__ID_EXECUTION)
        
        if (type != FImageType.EXECUTION):
            self.__stepLabel = wx.StaticText(self, wx.ID_ANY, "Step:")
            self.__stepCombo = wx.ComboBox(self, wx.ID_ANY, 
                                           style = wx.CB_READONLY)
            gridSizer.Add(self.__stepLabel)
            gridSizer.Add(self.__stepCombo, 0, wx.EXPAND)
        
        browseSizer.Add(gridSizer, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.ALL, 5)
        
        return browseSizer
    
    def __GetBottomSizer(self):
        """Returns the Sizer used to confirm or cancel this dialog."""
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        okButton = wx.Button(self, self.__ID_OK, "Ok")
        self.Bind(wx.EVT_BUTTON, self.__OnOk, okButton, self.__ID_OK)
        
        cancelButton = wx.Button(self, self.__ID_CANCEL, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.__OnCancel, cancelButton, 
                  self.__ID_CANCEL)
        
        bottomSizer.Add(okButton, 0, wx.ALIGN_LEFT)
        bottomSizer.Add(cancelButton, 0, wx.ALIGN_RIGHT)
        
        return bottomSizer
    
    def __ShowWarning(self, message):
        """Displays a modal warning dialog.
        
        arguments:
            message -- The message to be written in the dialog.
            
        """
        alert = wx.MessageDialog(self, message, "Alert", 
                                 wx.OK | wx.ICON_EXCLAMATION)
        alert.ShowModal()
        alert.Destroy()
    