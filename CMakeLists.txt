cmake_minimum_required(VERSION 3.14)

# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.
project(gempyrepy LANGUAGES CXX C)

if(NOT WIN32)
	find_program(PYTHON "python3" REQUIRED)
	set (PYTHON3 python3)
else()
	find_program(PYTHON "python" REQUIRED)
	set (PYTHON3 python)
endif() 

project(gempyrepy LANGUAGES CXX C)

set(Python_ADDITIONAL_VERSIONS 3.8)
find_package(Python COMPONENTS Interpreter Development)

set(CMAKE_REQUIRED_INCLUDES /usr/local/include)
include_directories(${PYTHON_INCLUDE_PATH})

include(GNUInstallDirs)
include(ExternalProject)
include(FetchContent)

find_path(PYTHON_HEADER_PATH "Python.h" HINTS ${Python_INCLUDE_DIRS} REQUIRED )

if(NOT PYTHON_HEADER_PATH)
    message(FATAL_ERROR "I assume you need '$sudo apt-get install python3-dev'")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_compile_options(-fPIC)


# gempyre has to be installed
find_package(gempyre REQUIRED)

include_directories (
    /usr/local/include
    include
)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.6.2
)

FetchContent_GetProperties(pybind11)

if(NOT pybind11_POPULATED)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
endif()

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/README.md
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR})


set(PYBIND11_PYTHON_VERSION 3.8)
pybind11_add_module(Gempyre
	src/gempyre_python.cpp)

add_custom_command(
    TARGET Gempyre
    POST_BUILD
    COMMAND ${PYTHON3} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py sdist bdist_wheel
    )
    
target_link_libraries (Gempyre PRIVATE gempyre::gempyre)			

#add_custom_command(
#    TARGET Gempyre
#    POST_BUILD
#    COMMAND ${PYTHON3} -m pip install --user -q -r ${GEMPYRE_DIR}/affiliates/py_client/requirements.txt
#    )

#add_custom_command(
#    TARGET Gempyre
#    POST_BUILD
#    COMMAND ${CMAKE_COMMAND} -E copy
#            ${GEMPYRE_DIR}/affiliates/py_client/pyclient.py
#            ${Python_SITELIB}/pyclient.py)

