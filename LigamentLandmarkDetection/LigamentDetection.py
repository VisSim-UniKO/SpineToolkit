# implemented with slicer 5.6.0
import os
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
import SpineLib
import vtk_convenience as conv
import time
import traceback



class LigamentDetection(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Ligament Landmark Detection"
        self.parent.categories = ["VisSimTools"]
        self.parent.dependencies = []
        self.parent.contributors = ["Lara Blomenkamp (VisSim Research Group, University of Koblenz)"]
        self.parent.helpText ='''
        This plugin uses shape segmentation of vertebrae to detect spinal ligament landmarks.
        '''
        self.parent.helpText += self.getDefaultModuleDocumentationLink()
        self.parent.acknowledgementText = """University of Koblenz"""
#
# LigamentDetectionWidget
#

class LigamentDetectionWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setup(self):

        ScriptedLoadableModuleWidget.setup(self)
        slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)

        scriptPath = os.path.dirname(os.path.abspath(__file__))
        ctblPath = os.path.join(scriptPath, 'VT_ShapeSeg.ctbl')
        slicer.util.loadColorTable(ctblPath)

        collapsibleButton = ctk.ctkCollapsibleButton()
        collapsibleButton.text = "Ligament Detection"
        self.layout.addWidget(collapsibleButton)
        self.formLayout = qt.QFormLayout(collapsibleButton)
        
        # Detect Ligament Landmarks Button
        self.ligDetButton = qt.QPushButton("Detect Ligament Landmarks")
        self.ligDetButton.enabled = True
        self.ligDetButton.setStyleSheet("font: bold; background-color: blue; font-size: 12px; height: 48px; width: 120px;")
        self.formLayout.addRow(self.ligDetButton)
        self.ligDetButton.connect('clicked(bool)', self.onLigDetButton)
        self.layout.addStretch(1)


    def cleanup(self):
        pass

    def onLigDetButton(self):
        self.progressBarManager = SpineLib.ProgressBarManager(layout=self.formLayout)
        logic = LigamentDetectionLogic()
        logic.run(self.progressBarManager)
        self.progressBarManager.closeProgressBar()


#
# LigamentDetectionLogic
#

class LigamentDetectionLogic(ScriptedLoadableModuleLogic):


    def run(self, progressBarManager=None):

        start_time = time.time()

        # organize vertebra model nodes
        lib_vertebraIDs = ["L5", "L4", "L3", "L2", "L1",
                           "T13", "T12", "T11", "T10", "T9", "T8", "T7", "T6", "T5", "T4", "T3", "T2", "T1",
                           "C7", "C6", "C5", "C4", "C3", "C2", "C1"]
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
            vt = conv.polydata_remesh(vt, subdivide=3, clusters=5000)   # Remeshing
            vt = conv.polydata_smooth(vt, iterations=10)                # Smoothing
            vt = conv.polydata_fillHoles(vt, maximumHoleSize=1000.0)    # Fill Holes
            vt = conv.polydata_clean(vt)                                # Clean redundant vertices
            preprocessed_geometries.append(vt)
            progressBarManager.updateProgress()

        # initialize spine
        vt_Spine                     =   SpineLib.Spine(model_nodes=vt_ModelNodes,
                                                        geometries=preprocessed_geometries,
                                                        indices=indices,
                                                        max_angle=60.0,
                                                        calculate_orientation=True)


        # Visualization
        for vt, vertebra in enumerate(vt_Spine.vertebrae):

            try:
                # get shape decomposition
                shapeDecomposition = vertebra.get_shape_decomposition(progressBarManager=progressBarManager, with_lamina=False)
                body               = shapeDecomposition.body
                processes          = shapeDecomposition.processes
                landmarks          = shapeDecomposition.landmarks

                SpineLib.SlicerTools.createModelNode(shapeDecomposition.segmented_geometry, name=vertebra.modelName + "_SegmentedGeometry")
            
            except Exception as e:
                print(f"Error in vertebra {vertebra.name}: {e}")
                print(traceback.format_exc())
                continue

        # Ligament Landmark Detection
        SpineLib.LigamentLandmarks(vt_Spine, progressBarManager=progressBarManager)
        
        for vt, vertebra in enumerate(vt_Spine.vertebrae):
            ligament_landmarks = vertebra.ligament_landmarks
            landmark_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", vertebra.modelName + "_LigamentLandmarks")
            landmark_node.GetDisplayNode().SetSelectedColor(1.0, 0.0, 0.0)
            landmark_node.GetDisplayNode().SetTextScale(0.0)

            # add landmarks to markup node
            for key, points in ligament_landmarks.items():
                try:
                    # find closest points on original geometry surface
                    points = conv.find_closest_points(vertebra.modelNode.GetPolyData(), points)
                except Exception as e:
                    print(f"Error in vertebra {vertebra.name} at landmark {key}: {e}")
                    print(traceback.format_exc())
                    continue

                # add to markup node
                for idx, point in enumerate(points):
                    label = f"{key}_{idx+1}" if len(points) > 1 else key
                    landmark_node.AddFiducialFromArray(point, label)
            
            # remove the centerline curve nodes from scene
            centerline_nodes = slicer.util.getNodes('*Centerline*')
            SpineLib.SlicerTools.removeNodes(list(centerline_nodes.values()))

        print("Elapsed time: ", time.time() - start_time)
        print("Time per vertebra: ", (time.time() - start_time) / len(vt_Spine.vertebrae))

    


class LigamentDetectionTest(ScriptedLoadableModuleTest):
    
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        slicer.mrmlScene.Clear(0)

    def runTest(self):
        self.setUp()
