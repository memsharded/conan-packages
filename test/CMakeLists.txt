project(GlewTest)
cmake_minimum_required(VERSION 3.0.0)
SET(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/..)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(testGlew main.c)

IF(APPLE)
  TARGET_LINK_LIBRARIES(testGlew PUBLIC "${CONAN_LIBS}" "-framework OpenGL")
ELSE()
  TARGET_LINK_LIBRARIES(testGlew PUBLIC "${CONAN_LIBS}")
ENDIF()

IF(WIN32 AND NOT MINGW)
  SET_TARGET_PROPERTIES(testGlew PROPERTIES LINK_FLAGS "/NODEFAULTLIB:\"LIBCMTD\" /NODEFAULTLIB:\"LIBCMT\"")
ENDIF()
