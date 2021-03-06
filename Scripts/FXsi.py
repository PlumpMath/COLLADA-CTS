# Copyright (c) 2012 The Khronos Group Inc.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and /or associated documentation files (the "Materials "), to deal in the Materials without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Materials, and to permit persons to whom the Materials are furnished to do so, subject to 
# the following conditions: 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Materials. 
# THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.

import os
import os.path
import shutil
import codecs

import Core.Common.FUtils as FUtils
from Core.Logic.FSettingEntry import *
from Scripts.FApplication import *

class FXsi (FApplication):
    """The class which represents XSI to the testing framework."""
    
    __EXTENSION = ".vbs"
    __PROJECT_NAME = "XsiCtfProject"
    __PROJECT_SCENE = os.path.join(__PROJECT_NAME, "Scenes")
    __REPLACE_PATH = "C:\\CTFReplaceWithFilepath"
    
    __IMPORT_OPTIONS = [
            ("Optimize For XSI", "OptimizeForXSI", "False"),]
    
    __EXPORT_OPTIONS = [
            ("Convert to Triangles", "Triangulate", "False"),
            ("Apply Subdivision", "ApplySubdivisionToGeometry", "False"),
            ("Tangents as Vertex Colors", "ExportTangentsAsVtxColor", "False"),
			("XSI Extra in COLLADA", "ExportXSIExtra", "False"),
			("Keep Reference Paths Relative", "PathRelative", "False")]
    
    __RENDER_X = "Render Resolution X"
    __RENDER_Y = "Render Resolution Y"
    __RENDER_ANIMATION_START = "Animation Start Time"
    __RENDER_ANIMATION_END = "Animation End Time"
    __RENDER_ANIMATION_FRAMES = "Animation Frames"
    __RENDER_STILL_START = "Non-Animation Start Time"
    __RENDER_STILL_END = "Non-Animation End Time"
    __RENDER_STILL_FRAMES = "Non-Animation Frames"
    __RENDER_OPTIONS = [
            (__RENDER_X, "xres", "512"),
            (__RENDER_Y, "yres", "512"),
            (__RENDER_ANIMATION_START, "FrameStart", "1"),
            (__RENDER_ANIMATION_END, "FrameEnd", "45"),
            (__RENDER_ANIMATION_FRAMES, "FrameStep", "3"),
            (__RENDER_STILL_START, "FrameStart", "1"),
            (__RENDER_STILL_END, "FrameEnd", "1"),
            (__RENDER_STILL_FRAMES, "FrameStep", "1")]
    
    def __init__(self, configDict):
        """__init__() -> FXsi"""
        FApplication.__init__(self, configDict)
        
        self.__projectDir = None
        self.__scenesDir = None
        self.__pathMap = []
        self.__currentImportProperName = None
        self.__logFiles = []
        self.__importLogFiles = []
        self.__testCount = 0
        self.__workingDir = None
    
    def GetPrettyName(self):
        """GetPrettyName() -> str
        
        Implements FApplication.GetPrettyName()
        
        """
        return "Softimage 2011"
    
    def GetSettingsForOperation(self, operation):
        """GetSettingsForOperation(operation) -> list_of_FSettingEntry
        
        Implements FApplication.GetSettingsForOperation()
        
        """
        if (operation == IMPORT):
            options = []
            for entry in FXsi.__IMPORT_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        elif (operation == EXPORT):
            options = []
            for entry in FXsi.__EXPORT_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        elif (operation == RENDER): 
            options = []
            for entry in FXsi.__RENDER_OPTIONS:
                options.append(FSettingEntry(*entry))
            return options
        else:
            return []
    
    def BeginScript(self, workingDir):
        """BeginScript(workingDir) -> None
        
        Implements FApplication.BeginScript()
        
        """
        filename = ("script" + str(self.applicationIndex) + 
                FXsi.__EXTENSION)
        self.__script = open(os.path.join(workingDir, filename) , "w")
        
        self.__projectDir = os.path.join(workingDir, FXsi.__PROJECT_NAME)
        self.__scenesDir = os.path.join(workingDir, FXsi.__PROJECT_SCENE)
        self.__pathMap = []
        self.__currentImportProperName = None
        self.__logFiles = []
        self.__importLogFiles = []
        
        if (os.path.isdir(self.__projectDir)):
            shutil.rmtree(self.__projectDir)
        
        self.__script.write("CreateProject \"" + 
                self.__projectDir.replace("\\", "\\\\") + "\"\n")
        self.__script.write(
                "SetValue \"preferences.scripting.cmdlogfile\", True\n" +
                "SetValue \"preferences.scripting.cmdlog\", True\n"
                "SetValue \"preferences.scripting.msglog\", True\n"
                "SetValue \"preferences.scripting.msglog\", True\n"
                "SetValue \"preferences.scripting.msglogverbose\", True\n"
                "SetValue \"preferences.scripting.cmdlogall\", True\n"
                )
        
        self.__testCount = 0
        self.__workingDir = workingDir
    
    def EndScript(self):
        """EndScript() -> None
        
        Implements FApplication.EndScript()
        
        """
        self.__script.close()
    
    def RunScript(self):
        """RunScript() -> None
        
        Implements FApplication.RunScript()
        
        """
        if (not os.path.isfile(self.configDict["xsiPath"])):
            print "XSI does not exist"
            return True
        
        print ("start running " + os.path.basename(self.__script.name))
        returnValue = self.RunApplication(self.configDict["xsiPath"] + 
                " -script \"" + self.__script.name + "\" > NUL 2>>&1", 
                self.__workingDir)
        
        if (returnValue == 0):
            print "finished running " + os.path.basename(self.__script.name)
        else:
            print "crashed running " + os.path.basename(self.__script.name)
            # since may not be able to do anything with the generated files
            return False 
        
        # XSI generates unicode logs -- convert to UTF-8
        (encoder, decoder, reader, writer) = codecs.lookup("utf-16-le")
        for logfile in self.__logFiles:
            logInMemory = ""
            log = reader(open(logfile))
            line = log.readline()
            while (line):
                logInMemory = logInMemory + line
                line = log.readline()
            log.close()
            logInMemory.encode("utf-8")
            log = open(logfile, "w")
            log.write(logInMemory)
            log.close()
        
        for logfile in self.__importLogFiles:
            logInMemory = ""
            log = open(logfile)
            line = log.readline()
            while (line):
                warningFind = line.find("WARNING")
                ctfPathFind = line.find(FXsi.__REPLACE_PATH)
                if ((warningFind != -1) and (ctfPathFind != -1)):
                    line = line.replace("WARNING", "CTF_OVERRIDE")
                logInMemory = logInMemory + line
                line = log.readline()
            log.close()
            log = open(logfile, "w")
            log.write(logInMemory)
            log.close()
        
        # since XSI has to save in its own project tree, need to relocate files
        for projectPath, testProcedurePath in self.__pathMap:
            for entry in os.listdir(projectPath):
                shutil.move(os.path.join(projectPath, entry), 
                                os.path.join(testProcedurePath, entry))
        
        return True
    
    def WriteImport(self, filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(filename, logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteImport()
        
        """
        step = os.path.basename(outputDir)
        execution = os.path.basename(os.path.dirname(outputDir))
        test = os.path.basename(os.path.dirname(os.path.dirname(outputDir)))
        path = os.path.join(self.__scenesDir, test, execution, step)
        if (not os.path.isdir(path)):
            os.makedirs(path)
        self.__pathMap.append((path, outputDir))
        
        self.__logFiles.append(os.path.join(path, os.path.basename(logname)))
        self.__importLogFiles.append(self.__logFiles[-1])
        
        command = ("SetValue \"preferences.scripting.cmdlogfilename\", \"" +  
                   self.__logFiles[-1].replace("\\", "\\\\") + "\"\n"
                   "NewScene, false\n")
        if (FUtils.GetExtension(filename) == "dae"):
            command = (command + 
                    "set myIProp = CreateImportFTKOptions()\n" +
                    "myIProp.Parameters(\"Filename\").Value = \"" + 
                            filename.replace("\\", "\\\\") +"\"\n" +
                    "myIProp.Parameters(\"Verbose\").Value = True\n")
            for setting in settings:
                value = setting.GetValue().strip()
                if (value == ""):
                    value = self.FindDefault(FXsi.__IMPORT_OPTIONS, 
                                             setting.GetPrettyName())
                command = (command + "myIProp.Parameters(\"" + 
                        setting.GetCommand() + "\").Value = " + value + "\n")
            command = command + "ImportFTK myIProp.Name \n"
        elif (FUtils.GetExtension(filename) == "scn"):
            command = (command +
                    "OpenScene \"" + filename.replace("\\","\\\\") + "\"\n")
        else: 
            return
        
        self.__currentImportProperName = FUtils.GetProperFilename(filename)
        basename = self.__currentImportProperName + ".scn"

#        self.__script.write(
#                command +
#                "SearchAndReplacePath \"All\", \"" + FXsi.__REPLACE_PATH + 
#                        "\", \"" + 
#                        os.path.dirname(filename).replace("\\", "\\\\") + 
#                        "\", True\n" +
#                "SaveSceneAs \"" + 
#                        os.path.join(path, basename).replace("\\", "\\\\") +
#                        "\"\n"
#                )
                        
        self.__script.write(
                command +
                "SaveSceneAs \"" + 
                        os.path.join(path, basename).replace("\\", "\\\\") +
                        "\"\n"
                )
        
        self.__testCount = self.__testCount + 1
        
        return [basename,]
    
    def WriteRender(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteRender(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteRender().
        
        """
        if (self.__currentImportProperName == None): return
        
        step = os.path.basename(outputDir)
        execution = os.path.basename(os.path.dirname(outputDir))
        test = os.path.basename(os.path.dirname(os.path.dirname(outputDir)))
        path = os.path.join(self.__scenesDir, test, execution, step)
        if (not os.path.isdir(path)):
            os.makedirs(path)
        self.__pathMap.append((path, outputDir))
        
        start = 0
        end = 0
        step = 1
        xres = 512
        yres = 512
        
        command = ""
        
        for setting in settings:
            prettyName = setting.GetPrettyName()
            if (prettyName == FXsi.__RENDER_ANIMATION_START):
                if (not isAnimated):
                    continue
                start = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                               int)
            elif (prettyName == FXsi.__RENDER_ANIMATION_END):
                if (not isAnimated):
                    continue
                end = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                             int)
            elif (prettyName == FXsi.__RENDER_ANIMATION_FRAMES):
                if (not isAnimated):
                    continue
                step = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FXsi.__RENDER_STILL_START):
                if (isAnimated):
                    continue
                start = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                               int)
            elif (prettyName == FXsi.__RENDER_STILL_END):
                if (isAnimated):
                    continue
                end = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                             int)
            elif (prettyName == FXsi.__RENDER_STILL_FRAMES):
                if (isAnimated):
                    continue
                step = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FXsi.__RENDER_X):
                xres = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                              int)
            elif (prettyName == FXsi.__RENDER_Y):
                yres = self.GetSettingValueAs(FXsi.__RENDER_OPTIONS, setting,
                                              int)


            type = "png"        
#            value = setting.GetValue().strip()
#            if (value == ""):
#                value = self.FindDefault(FXsi.__RENDER_OPTIONS, 
#                                         setting.GetPrettyName())
#            
#            command = (command + "SetValue " +
#                    "\"Passes.RenderOptions." +
#                    setting.GetCommand() + "\", " + value + "\n")
        
        basename = self.__currentImportProperName + "#." + type
        
        self.__logFiles.append(os.path.join(path, os.path.basename(logname)))
        self.__script.write(
                "SetValue \"preferences.scripting.cmdlogfilename\", \"" +  
                        self.__logFiles[-1].replace("\\", "\\\\") + 
                        "\"\n" +
                "SetValue \"preferences.output_format.preset\", 0\n" +
                "SetValue \"preferences.output_format.picture_standard\", 0\n" +
                "SetValue \"preferences.output_format.picture_ratio\", 1\n" +
                "SetValue \"preferences.output_format.ir_pixel_ratio\", 1\n" +
                "SetValue \"preferences.output_format.ir_xres\", " + str(xres) + "\n" +
                "SetValue \"preferences.output_format.ir_yres\", " + str(yres) + "\n" +
                "SetValue \"Passes.RenderOptions." +
                        "OutputDir\", \"" + 
                        os.path.join(path).replace("\\", "\\\\") +
                        "\"\n" +
                "SetValue \"Passes.mentalray.SamplesMin\", -2\n" +
                "SetValue \"Passes.mentalray.SamplesMax\", 0\n" +
                "SetValue \"Passes.Default_Pass.Main.Filename\", \"" + basename + "\"\n" +
                "SetValue \"Passes.Default_Pass.Main.Format\", \"" + type + "\"\n" +                      
                "DeleteObj \"B:Camera_Root\"\n" +
                "DeleteObj \"light\"\n" +
				"SetValue \"Passes.RenderOptions.FrameStart\", " + str(start) + "\n" +
				"SetValue \"Passes.RenderOptions.FrameEnd\", " + str(end) + "\n" +
				"SetValue \"Passes.RenderOptions.FrameStep\", " + str(step) + "\n" +
				"SetValue \"preferences.output_format.frame_step\", " + str(step) + "\n" +
                command +                
                "SIUpdateCamerasFromGlobalPref\n" +
                "SIUpdateRenderOptionsFromGlobalPref\n" +
                "Set pass = GetValue( \"Passes.Default_Pass\" )\n" +
                "RenderPass pass\n")
        
        if (step == 1):
            return [self.__currentImportProperName + str(start) + "." + type,]
        
        outputList = []
        for i in range(start, end + 1, step):
            outputList.append(self.__currentImportProperName + str(i) + "." + 
                              type,)
        return outputList
    
    def WriteExport(self, logname, outputDir, settings, isAnimated, cameraRig, lightingRig):
        """WriteImport(logname, outputDir, settings, isAnimated, cameraRig, lightingRig) -> list_of_str
        
        Implements FApplication.WriteExport().
        
        """
        if (self.__currentImportProperName == None): return
        
        step = os.path.basename(outputDir)
        execution = os.path.basename(os.path.dirname(outputDir))
        test = os.path.basename(os.path.dirname(os.path.dirname(outputDir)))
        path = os.path.join(self.__scenesDir, test, execution, step)
        if (not os.path.isdir(path)):
            os.makedirs(path)
        self.__pathMap.append((path, outputDir))
        
        basename = self.__currentImportProperName + ".dae"
        
        command = ""
        
        for setting in settings:
            value = setting.GetValue().strip()
            if (value == ""):
                value = self.FindDefault(FXsi.__EXPORT_OPTIONS, 
                                         setting.GetPrettyName())
            command = (command + "myEProp.Parameters(\"" + 
                    setting.GetCommand() + "\").Value = " + 
                    setting.GetValue() + "\n")
        
        self.__logFiles.append(os.path.join(path, os.path.basename(logname)))
        
        self.__script.write(
                "SetValue \"preferences.scripting.cmdlogfilename\", \"" +  
                        self.__logFiles[-1].replace("\\", "\\\\") + "\"\n"
                "set myEProp = CreateExportFTKOptions()\n"
                "myEProp.Parameters(\"Filename\").Value = \"" + 
                        os.path.join(path, basename).replace("\\", "\\\\") + 
                        "\"\n" +
                "myEProp.Parameters(\"Format\").Value = 1\n"
                "myEProp.Parameters(\"Verbose\").Value = True\n" +
                command +
                "ExportFTK myEProp.Name\n"
                )
        
        return [basename,]
    