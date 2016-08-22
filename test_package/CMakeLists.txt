project(GlewTest)
cmake_minimum_required(VERSION 3.0.0)
SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/..)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(testGlew main.cpp)

FIND_PACKAGE(GLEW REQUIRED)
INCLUDE_DIRECTORIES(${GLEW_INCLUDE_DIRS})

IF(APPLE)
  TARGET_LINK_LIBRARIES(testGlew PUBLIC "${GLEW_LIBRARIES}" "-framework OpenGL")
ELSE()
  TARGET_LINK_LIBRARIES(testGlew PUBLIC "${GLEW_LIBRARIES}")
ENDIF()

IF(WIN32)
add_custom_command(TARGET testGlew POST_BUILD        # Adds a post-build event 
    COMMAND ${CMAKE_COMMAND} -E copy_if_different    # which executes "cmake - E copy_if_different..."
        "${GLEW_INCLUDE_DIR}/../bin/glew32.dll"      # <--this is in-file
        $<TARGET_FILE_DIR:testGlew>)                 # <--this is out-file path
ENDIF()
