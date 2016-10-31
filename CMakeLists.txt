cmake_minimum_required(VERSION 2.8.9)

project(DatabaseInteractor)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/DatabaseInteractor")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Clement Mirabel (University of Michigan)")
set(EXTENSION_DESCRIPTION "This extension can interact with online data in a database and local folders.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/DatabaseInteractor.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/DatabaseInteractor/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(DatabaseInteractor)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
