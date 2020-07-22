cmake_minimum_required(VERSION 3.8)
# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.

set(Python_ADDITIONAL_VERSIONS 3.8)
find_package(Python COMPONENTS Interpreter Development)
include_directories(${PYTHON_INCLUDE_PATH})
find_program(PYTHON "python3" REQUIRED)

include(GNUInstallDirs)
include(ExternalProject)
project(telexpy)
include(FetchContent)

FetchContent_Declare(
    pybind11
    GIT_REPOSITORY https://github.com/pybind/pybind11
    GIT_TAG        v2.4.3
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_compile_options(-fPIC)

include_directories(
    ../Telex-framework/telexlib/include
    )

FetchContent_GetProperties(pybind11)

if(NOT pybind11_POPULATED)
    FetchContent_Populate(pybind11)
    add_subdirectory(${pybind11_SOURCE_DIR} ${pybind11_BINARY_DIR})
endif()


file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/README.md
    DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

find_package (telex REQUIRED PATHS ../Telex-framework/telexlib)

set(PYBIND11_PYTHON_VERSION 3.8)
pybind11_add_module(Telex
    telex_python.cpp)

add_custom_command(
    TARGET Telex
    POST_BUILD
    COMMAND python3 ${CMAKE_CURRENT_SOURCE_DIR}/setup.py sdist bdist_wheel
    )

target_link_libraries(Telex PRIVATE telex)

