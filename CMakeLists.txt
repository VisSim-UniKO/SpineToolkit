cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SpineToolkit)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SpineToolkit")
set(EXTENSION_CONTRIBUTORS "Lara Blomenkamp (University of Koblenz)")
set(EXTENSION_DESCRIPTION "Tools for Creation, Reconstruction, and Analysis of 3D Spine Models")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/SpineToolkit.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/SpineToolkit/Screenshots/1.png")
set(EXTENSION_DEPENDS [SlicerIGT, SlicerVMTK]) # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LumbarSpineCreator)
add_subdirectory(LumbarSpineReconstruction)
add_subdirectory(VertebraShapeSegmentation)
add_subdirectory(ShapeSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
