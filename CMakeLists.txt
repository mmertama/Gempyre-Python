cmake_minimum_required(VERSION 3.14)

# Must use GNUInstallDirs to install libraries into correct
# locations on all platforms.
project(gempyrepy LANGUAGES CXX C)


if(UNIX AND NOT APPLE AND NOT RASPBERRY)
    set(LINUX ON)
endif()    


if(MSVC)
    find_program(PYTHON "python" HINTS "${PYTHON_PATH}" REQUIRED)
    set (PYTHON3 python)
    find_package(Python3 HINTS "${PYTHON_PATH}" COMPONENTS Interpreter Development)
    if(NOT Python3)
        find_package(Python3 COMPONENTS Interpreter Development) # this works event not found
    endif()
    find_path(PYTHON_HEADER_PATH "Python.h" HINTS ${Python3_INCLUDE_DIRS})
elseif(MINGW)
    find_program(PY_EXE "python3" HINTS "${PYTHON_PATH}" NO_DEFAULT_PATH REQUIRED)
    set (PYTHON3 python)
    find_package(Python3 HINTS "${PYTHON_PATH}" COMPONENTS Interpreter Development)
    if(NOT Python3)
        find_package(Python3 COMPONENTS Interpreter Development) # the below hack helps as mingw is not really supported
    endif()
    if(NOT Python3)
        execute_process(
                    COMMAND ${PYTHON3} --version
                    OUTPUT_VARIABLE PY_VERSION)
        string(REGEX MATCHALL [0-9]+ VER ${PY_VERSION})
        list(GET VER 0 Python_VERSION_MAJOR)
        list(GET VER 1 Python_VERSION_MINOR)
        get_filename_component(PARENT_DIR ${PYTHON_PATH} DIRECTORY)
        find_path(PYTHON_HEADER_PATH "Python.h" 
            HINTS "${PARENT_DIR}/include/python${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}" REQUIRED)
        set(PYTHON_INCLUDE_PATH ${PYTHON_HEADER_PATH})
    endif()        
else() 
    find_program(PYTHON "python3" HINTS "${PYTHON_PATH}" REQUIRED)
    set (PYTHON3 python3)
    find_package(Python3 HINTS "${PYTHON_PATH}" COMPONENTS Interpreter Development)
    if(NOT Python3)
        find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
    endif() 
    
    find_path(PYTHON_HEADER_PATH "Python.h" HINTS ${Python3_INCLUDE_DIRS})
endif()

include_directories(${PYTHON_INCLUDE_PATH})

include(GNUInstallDirs)
include(ExternalProject)
include(FetchContent)

if(NOT PYTHON_HEADER_PATH)
    message(FATAL_ERROR "I assume you need '$sudo apt-get install python3-dev'")
else()
    message("Using Python headers ar ${PYTHON_HEADER_PATH}")    
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


if(NOT DEFINED Python_VERSION_MAJOR)
	set(Python_VERSION_MAJOR 3)
	set(Python_VERSION_MINOR 8)
endif()

set(PY_VER "${Python_VERSION_MAJOR}.${Python_VERSION_MINOR}")

set(PYBIND11_PYTHON_VERSION ${PY_VER})
pybind11_add_module(Gempyre
        src/gempyre_python.cpp)

add_custom_command(
  TARGET Gempyre
  POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E echo "Building file: $<TARGET_FILE:Gempyre>"
)

if(MSVC)
	set(LIB_TARGET "${CMAKE_SOURCE_DIR}/build/lib.win-amd64-${PY_VER}")
elseif(MINGW)
	set(LIB_TARGET "${CMAKE_SOURCE_DIR}/build/lib.mingw_x86_64-${PY_VER}")
elseif(UNIX)
    execute_process(
        COMMAND uname "-m"
        OUTPUT_STRIP_TRAILING_WHITESPACE
        OUTPUT_VARIABLE ARCH)
    set(LIB_TARGET "${CMAKE_SOURCE_DIR}/build/lib.linux-${ARCH}-${PY_VER}")    
else()
    message(FATAL_ERROR "The environment is not recognized, that may lead ot issues!")
endif()

message("Pyd file will be copied to ${LIB_TARGET}" )


file(MAKE_DIRECTORY ${LIB_TARGET})

add_custom_command(
  TARGET Gempyre
  POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:Gempyre> ${LIB_TARGET}/
  COMMAND ${PYTHON3} ${CMAKE_CURRENT_SOURCE_DIR}/setup.py sdist bdist_wheel
)

target_link_libraries (Gempyre PRIVATE gempyre::gempyre)


