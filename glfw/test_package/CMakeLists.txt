project(glfwTest)
cmake_minimum_required(VERSION 3.0.0)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(test_glfw main.cpp)

target_link_libraries(test_glfw ${CONAN_LIBS})

set_target_properties(test_glfw PROPERTIES LINK_FLAGS "${CONAN_EXE_LINKER_FLAGS}")
