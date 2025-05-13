cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(SpineToolkit)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/VisSim-UniKO/SpineToolkit")
set(EXTENSION_CONTRIBUTORS "Lara Blomenkamp (University of Koblenz)")
set(EXTENSION_DESCRIPTION "The SpineToolkit includes modules for automated Creation, Reconstruction, and Analysis of 3D Spine Models")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/VisSim-UniKO/SpineToolkit/main/SpineToolkit.png")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/VisSim-UniKO/SpineToolkit/main/SpineToolkitScreenshot.png")
set(EXTENSION_DEPENDS SlicerIGT, SlicerVMTK) # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LumbarSpineCreator)
add_subdirectory(LumbarSpineReconstruction)
add_subdirectory(ShapeSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
