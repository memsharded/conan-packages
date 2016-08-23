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
