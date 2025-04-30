# implemented with slicer 5.6.0
import os
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import numpy as np
import vtk
import vtk.util.numpy_support as numpy_support
import SpineLib
import vtk_convenience as conv
import pyvista as pv
import time
import logging
import traceback



class ShapeSegmentation(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Spine Shape Segmentation"
        self.parent.categories = ["VisSimTools"]
        self.parent.dependencies = []
        self.parent.contributors = ["Lara Blomenkamp (VisSim Research Group)"]
        self.parent.helpText ='''
        todo
        '''
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """University of Koblenz"""

#
# ShapeSegmentationWidget
#

class ShapeSegmentationWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):

        ScriptedLoadableModuleWidget.setup(self)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)

        scriptPath = os.path.dirname(os.path.abspath(__file__))
        ctblPath = os.path.join(scriptPath, 'VT_ShapeSeg.ctbl')
        slicer.util.loadColorTable(ctblPath)

        ############# Collapsible Button ######################################

        collapsibleButton = ctk.ctkCollapsibleButton()
        collapsibleButton.text = "Segmentation"
        self.layout.addWidget(collapsibleButton)
        self.formLayout = qt.QFormLayout(collapsibleButton)
        
        # RunRegistration Button
        self.segmentationButton = qt.QPushButton("Shape Segmentation")
        self.segmentationButton.enabled = True
        self.segmentationButton.setStyleSheet("font: bold; background-color: blue; font-size: 12px; height: 48px; width: 120px;")
        self.formLayout.addRow(self.segmentationButton)
        self.segmentationButton.connect('clicked(bool)', self.onSegmentationButton)


        
        ###################################################################################

        # Add vertical spacer
        self.layout.addStretch(1)
        
        # enddef setup


    def cleanup(self):
        pass

    def onSegmentationButton(self):
        self.progressBarManager = SpineLib.ProgressBarManager(layout=self.formLayout)
        logic = ShapeSegmentationLogic()
        logic.run(self.progressBarManager)
        self.progressBarManager.closeProgressBar()


#
# ShapeSegmentationLogic
#

class ShapeSegmentationLogic(ScriptedLoadableModuleLogic):


    def run(self, progressBarManager=None):

        start_time = time.time()

        # find vertebra nodes
        lib_vertebraIDs = ["L5", "L4", "L3", "L2", "L1",
                           "T12", "T11", "T10", "T9", "T8", "T7", "T6", "T5", "T4", "T3", "T2", "T1",
                           "C7", "C6", "C5", "C4", "C3"]
        modelNodes      = slicer.util.getNodesByClass("vtkMRMLModelNode")
        processedModels = set()
        vertebraIDs, vt_ModelNodes = zip(*((id, node) for id in lib_vertebraIDs for node in modelNodes if id in node.GetName() and node.GetName() not in processedModels and not processedModels.add(node.GetName())))
        vt_ModelNodes   = list(vt_ModelNodes)
        indices = [lib_vertebraIDs.index(id) for id in vertebraIDs]

        num = (len(vt_ModelNodes) * 7) + 1
        progressBarManager.createProgressBar(parent=slicer.util.mainWindow(), maximum=num)

        # preprocessing vertebra meshes
        vt_Geometries =  [node.GetPolyData() for node in vt_ModelNodes]
        preprocessed_geometries = []
        for vt, node in zip(vt_Geometries, vt_ModelNodes):
            print("Remeshing " + str(node.GetName()) + " ...")
            node.GetDisplayNode().SetOpacity(0.0)
            vt = conv.polydata_remesh(vt, subdivide=2, clusters=5000)
            vt = conv.polydata_smooth(vt, iterations=10)
            vt = conv.polydata_fillHoles(vt, maximumHoleSize=1000.0)
            vt = conv.polydata_clean(vt)
            preprocessed_geometries.append(vt)
            progressBarManager.updateProgress()



        print("Start Shape Segmentation...")

        # SPINE INITIALIZATION
        vt_Spine                     =   SpineLib.Spine(geometries=preprocessed_geometries, indices=indices, max_angle=45.0)

        # SHAPE DECOMPOSITION
        for vt, vertebra in enumerate(vt_Spine.vertebrae):

            try:
                shapeDecomposition = vertebra.get_shape_decomposition(progressBarManager=progressBarManager, with_lamina=True, original_model=vt_Geometries[vt]
                                                                    )
                segmented_model = SpineLib.SlicerTools.createModelNode(shapeDecomposition.segmented_geometry, name=vertebra.name + "_segmented")
                SpineLib.SlicerTools.setModelColorTable(segmented_model, "VT_ShapeSeg")
                vt_ModelNodes[vt].GetDisplayNode().SetVisibility(False)
            except Exception as e:
                print(f"Error in {vertebra.name}: {e}")
                print(traceback.format_exc())
                continue
        
        # get all nodes that have (centerline) in their name
        curve_nodes = slicer.util.getNodesByClass("vtkMRMLMarkupsCurveNode")
        centerline_nodes = [node for node in curve_nodes if "Centerline" in node.GetName()]
        SpineLib.SlicerTools.removeNodes(centerline_nodes)


        print("Elapsed time: ", time.time() - start_time)
        print("Time per vertebra: ", (time.time() - start_time) / len(vt_Spine.vertebrae))

    


class ShapeSegmentationTest(ScriptedLoadableModuleTest):
    
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        self.setUp()
        self.test_ShapeSegmentation()

    def test_ShapeSegmentation(self):

        self.delayDisplay("Starting the test")

        self.delayDisplay('Test passed!')