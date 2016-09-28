project(GlewTest)
cmake_minimum_required(VERSION 3.0.0)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(testGlew main.c)

TARGET_LINK_LIBRARIES(testGlew PUBLIC "${CONAN_LIBS}")

IF(APPLE)
  TARGET_LINK_LIBRARIES(testGlew PUBLIC "-framework OpenGL")
ELSEIF(WIN32)
  TARGET_LINK_LIBRARIES(testGlew PUBLIC OpenGL32.lib)
ENDIF()
