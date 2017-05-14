project(OggTest)
cmake_minimum_required(VERSION 3.0.0)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_C_FLAGS "${CONAN_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CONAN_CXX_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS "${CONAN_SHARED_LINKER_FLAGS}")

add_executable(testOgg main.cpp)
target_link_libraries(testOgg ${CONAN_LIBS})

