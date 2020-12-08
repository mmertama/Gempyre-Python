cmake_minimum_required(VERSION 3.8)
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

project(gempyrepy  LANGUAGES CXX C)

find_program(PYTHON "python3" REQUIRED)
set(Python_ADDITIONAL_VERSIONS 3.8)
find_package(Python COMPONENTS Interpreter Development)
include_directories(${PYTHON_INCLUDE_PATH})

include(GNUInstallDirs)
include(ExternalProject)
include(FetchContent)


set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_compile_options(-fPIC)

FetchContent_Declare(
    gempyre_library
    GIT_REPOSITORY https://github.com/mmertama/Gempyre.git
    )

option(HAS_TEST OFF)
option(HAS_BLOG OFF)
option(HAS_AFFILIATES ON)
option(HAS_MDMAKER OFF)
    
FetchContent_GetProperties(gempyre_library)
if(NOT gempyre_library)
  FetchContent_Populate(gempyre_library)
  add_subdirectory(${gempyre_library_SOURCE_DIR} ${gempyre_library_BINARY_DIR})
endif()
set(GEMPYRE_DIR ${gempyre_library_SOURCE_DIR})

include_directories(
    "${gempyre_library_SOURCE_DIR}/gempyrelib/include"
    include
)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.5.0
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
    gempyre_python.cpp)

add_custom_command(
    TARGET Gempyre
    POST_BUILD
    COMMAND ${PYTHON3} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py sdist bdist_wheel
    )

link_directories(${gempyre_library_BINARY_DIR})
target_link_libraries(Gempyre PRIVATE gempyre)

