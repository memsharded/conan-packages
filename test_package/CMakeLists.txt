project(GlewTest)
cmake_minimum_required(VERSION 3.0.0)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(testGlew main.cpp)

FIND_PACKAGE(GLEW REQUIRED)
INCLUDE_DIRECTORIES(${GLEW_INCLUDE_DIRS})
TARGET_LINK_LIBRARIES(testGlew PUBLIC "${GLEW_LIBRARIES}")

IF(WIN32)
add_custom_command(TARGET testGlew POST_BUILD        # Adds a post-build event to MyTest
    COMMAND ${CMAKE_COMMAND} -E copy_if_different    # which executes "cmake - E copy_if_different..."
        "${GLEW_INCLUDE_DIR}/../bin/glew32.dll"      # <--this is in-file
        $<TARGET_FILE_DIR:testGlew>)                 # <--this is out-file path
ENDIF()
