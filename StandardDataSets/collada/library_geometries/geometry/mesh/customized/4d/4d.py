# Copyright (C) 2007 - 2009 Khronos Group
# Available only to Khronos members.
# Distribution of this file or its content is strictly prohibited.

# See Core.Logic.FJudgementContext for the information
# of the 'context' parameter.
#

# This sample judging object does the following:
#
# JudgeBaseline: verifies that app did not crash, the required steps have been performed, 
#  the rendered images match, and the required element(s) has been preserved
# JudgeExemplary: returns Baseline status.
# JudgeSuperior: returns Baseline status.

# We import an assistant script that includes the common verifications
# methods. The assistant buffers its checks, so that running them again
# does not incurs an unnecessary performance hint.
from StandardDataSets.scripts import JudgeAssistant

# Please feed your node list here:
tagLst = ['library_geometries', 'geometry', 'mesh', 'float_array']
primTagLstArray = [['library_geometries', 'geometry', 'mesh', 'polylist', 'input'], ['library_geometries', 'geometry', 'mesh', 'triangles', 'input'], ['library_geometries', 'geometry', 'mesh', 'polygons', 'input']]
attrName = 'semantic'
attrVal = 'CUSTOM'
dataToCheck = '0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15'

class SimpleJudgingObject:
    def __init__(self, _tagLst, _primTagLstArray, _attrName, _attrVal, _data):
        self.tagList = _tagLst
        self.primTagListArray = _primTagLstArray
        self.attrName = _attrName
        self.attrVal = _attrVal
        self.dataToCheck = _data
        self.status_baseline = False
        self.status_superior = False
        self.status_exemplary = False
        self.__assistant = JudgeAssistant.JudgeAssistant()
        
    def JudgeBaseline(self, context):
        # No step should not crash
        self.__assistant.CheckCrashes(context)
        
        # Import/export/validate must exist and pass, while Render must only exist.
        self.__assistant.CheckSteps(context, ["Import", "Export", "Validate"], ["Render"])

        self.status_baseline = self.__assistant.GetResults()
        return self.status_baseline
  
    # To pass intermediate you need to pass basic, this object could also include additional 
    # tests that were specific to the intermediate badge.
    def JudgeSuperior(self, context):
        self.status_superior = self.status_baseline
        return self.status_superior 
            
    # To pass advanced you need to pass intermediate, this object could also include additional
    # tests that were specific to the advanced badge
    def JudgeExemplary(self, context):
	# if superior fails, no point in further checking
        if (self.status_superior == False):
            self.status_exemplary = self.status_superior
            return self.status_exemplary

        # Check for preservation of element data and then semantic attribute
        if ( self.__assistant.ElementDataCheck(context, self.tagList, dataToCheck, "float") ):
            attributePreserved = False
            for eachPrimTagList in self.primTagListArray:
                if ( self.__assistant.AttributeCheck(context, eachPrimTagList, self.attrName, self.attrVal) ):
                    attributePreserved = True
                    break
                    
            self.status_exemplary = attributePreserved
        else:
            self.status_exemplary = self.__assistant.DeferJudgement(context)

        return self.status_exemplary 
        
# This is where all the work occurs: "judgingObject" is an absolutely necessary token.
# The dynamic loader looks very specifically for a class instance named "judgingObject".
#
judgingObject = SimpleJudgingObject(tagLst, attrName, attrVal, dataToCheck);