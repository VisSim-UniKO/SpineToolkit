import os
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import numpy as np
import vtk

import SpineLib



class LumbarSpineReconstruction(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Lumbar Spine Reconstruction"
        self.parent.categories = ["VisSimTools"]
        self.parent.dependencies = []
        self.parent.contributors = ["Lara Blomenkamp (VisSim Research Group)"]
        self.parent.helpText ='''
        The Spine Registration module registrates a set of artificial sawbone models to custom spine models (L1-L5).
        The goal is to align sawbones with the provided vertebra models, that consist of only the vertebral bodies.
        In the registration process, the position, orientation and size of the sawbones are adjusted to match the custom spine.
        After the registration, the facet joints are aligned to fit together with realistic spacing.
        '''
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """University of Koblenz"""

#
# LumbarSpineReconstructionWidget
#

class LumbarSpineReconstructionWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):

        ScriptedLoadableModuleWidget.setup(self)

        scriptPath = os.path.dirname(os.path.abspath(__file__))
        self.sawboneDir = os.path.join(scriptPath, "SawbonesSpine")

        ############# Collapsible Button ######################################

        collapsibleButton = ctk.ctkCollapsibleButton()
        collapsibleButton.text = "Registration"
        self.layout.addWidget(collapsibleButton)
        formLayout = qt.QFormLayout(collapsibleButton)
        
        # RunRegistration Button
        self.registrationButton = qt.QPushButton("Run Registration Process")
        self.registrationButton.enabled = True
        self.registrationButton.setStyleSheet("font: bold; background-color: blue; font-size: 12px; height: 48px; width: 120px;")
        formLayout.addRow(self.registrationButton)
        self.registrationButton.connect('clicked(bool)', self.onRegistrationButton)

        
        ###################################################################################

        # Add vertical spacer
        self.layout.addStretch(1)
        
        # enddef setup


    def cleanup(self):
        pass

    def onRegistrationButton(self):
        logic = LumbarSpineReconstructionLogic()
        logic.run(self.sawboneDir)

    def onSegButton(self):
        logic = LumbarSpineReconstructionLogic()
        logic.createModelsFromNumpy() 


#
# LumbarSpineReconstructionLogic
#

class LumbarSpineReconstructionLogic(ScriptedLoadableModuleLogic):



    def run(self, sawboneDirectory):

        # find vertebra nodes
        lib_vertebraIDs = ["L5", "L4", "L3", "L2", "L1"]
        modelNodes      = slicer.util.getNodesByClass("vtkMRMLModelNode")
        processedModels = set()
        vertebraIDs, vt_ModelNodes = zip(*((id, node) for id in lib_vertebraIDs for node in modelNodes if id in node.GetName() and node.GetName() not in processedModels and not processedModels.add(node.GetName())))
        vt_ModelNodes   = list(vt_ModelNodes)
        indices = [lib_vertebraIDs.index(id) for id in vertebraIDs]

        # load sawbone object nodes
        sawboneObjects               =   SpineLib.SlicerTools.loadObjectsInDirectory(sawboneDirectory)
        sb_ModelNodes                =   SpineLib.SlicerTools.getSortedNodesByName(nodes=sawboneObjects, sortingKeys=vertebraIDs, name="Sawbone")
        # sb_LandmarksMarkupNodes      =   SpineLib.SlicerTools.getSortedNodesByName(nodes=sawboneObjects, sortingKeys=vertebraIDs, name="Landmarks")
        sb_FacetJointsMarkupNodes    =   SpineLib.SlicerTools.getSortedNodesByName(nodes=sawboneObjects, sortingKeys=vertebraIDs, name="FacetJoints")
        sb_FJA_SourceMarkupNodes     =   SpineLib.SlicerTools.getSortedNodesByName(nodes=sawboneObjects, sortingKeys=vertebraIDs, name="FJA_Source")
        remove_Objects = [node for node in sawboneObjects if node not in sb_ModelNodes and node not in sb_FacetJointsMarkupNodes and node not in sb_FJA_SourceMarkupNodes]
        SpineLib.SlicerTools.removeNodes(remove_Objects)

        # set dispay properties
        for vt in vt_ModelNodes:
            vt.GetDisplayNode().SetOpacity(0.3)
        for sb in sb_ModelNodes:
            sb.GetDisplayNode().SetColor(0.945, 0.839, 0.569)

        
        ####################################################################################################################################################
        # SPINE INITIALIZATION
        vt_Geometries                =   [node.GetPolyData() for node in vt_ModelNodes]
        vt_Spine                     =   SpineLib.Spine(geometries=vt_Geometries, indices=indices, max_angle=45.0)
        vt_ObjectToWorldMatrices     =   [vertebra.objectToWorldMatrix for vertebra in vt_Spine.vertebrae]

        ####################################################################################################################################################
        # SAWBONE INITIALIZATION
        #sb_LandmarkNodes             =   [SpineLib.Landmarks(*(slicer.util.arrayFromMarkupsControlPoints(node))[:8]) for node in sb_LandmarksMarkupNodes]
        #sb_Vertebrae                 =   [SpineLib.Vertebra(landmarks=sb_LandmarkNode) for sb_LandmarkNode in sb_LandmarkNodes]
        sb_Geometries                =   [node.GetPolyData() for node in sb_ModelNodes]
        sb_Spine                     =   SpineLib.Spine(geometries=sb_Geometries, indices=indices, max_angle=45.0)
        sb_ObjectToWorldMatrices     =   [sawbone.objectToWorldMatrix for sawbone in sb_Spine.vertebrae]

        ####################################################################################################################################################
        # SPINE REGISTRATION

        # registrate each vertebra pair (sawbone to target model)
        for vt in range(len(vertebraIDs)):

            # nodes to transform
            transformableObjects = [sb_ModelNodes[vt],
                                    #sb_LandmarksMarkupNodes[vt],
                                    sb_FacetJointsMarkupNodes[vt],
                                    sb_FJA_SourceMarkupNodes[vt]]
            
            # transformation matrices
            sb_ObjectToWorldMatrix = sb_ObjectToWorldMatrices[vt]
            sb_ObjectToWorldMatrix.Invert()
            vt_ObjectToWorldMatrix = vt_ObjectToWorldMatrices[vt]
            
            # concatenate matrices
            registrationMatrix = vtk.vtkMatrix4x4()
            registrationMatrix.Identity()
            vtk.vtkMatrix4x4.Multiply4x4(vt_ObjectToWorldMatrix, sb_ObjectToWorldMatrix, registrationMatrix)

            # apply registration matrix
            SpineLib.SlicerTools.transformVertebraObjects(registrationMatrix, transformableObjects)

        ####################################################################################################################################################
        # FACET JOINT ALIGNMENT
        facetJointSpaces_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "joint_space_width.csv")
        SpineLib.FacetJointAlignment.align(facetJointSpaces_filepath, sb_ModelNodes, vertebraIDs, lib_vertebraIDs, sb_FacetJointsMarkupNodes, sb_FJA_SourceMarkupNodes)

        ####################################################################################################################################################

        # Remove nodes
        SpineLib.SlicerTools.removeNodes([sb_FacetJointsMarkupNodes, sb_FJA_SourceMarkupNodes])




            

class LumbarSpineReconstructionTest(ScriptedLoadableModuleTest):
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
        self.test_LumbarSpineReconstruction1()

    def test_LumbarSpineReconstruction1(self):
         
        self.delayDisplay("Starting the test")

        self.delayDisplay('Test passed!')