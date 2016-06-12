project(GlewTest)
cmake_minimum_required(VERSION 3.0.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(testGlew main.cpp)

FIND_PACKAGE(GLEW REQUIRED)
INCLUDE_DIRECTORIES(${GLEW_INCLUDE_DIRS})
TARGET_LINK_LIBRARIES(testGlew PUBLIC "${GLEW_LIBRARIES}")

# target_link_libraries(testGlew ${CONAN_LIBS})
