project(VorbisTest)
cmake_minimum_required(VERSION 3.0.0)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_C_FLAGS "${CONAN_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CONAN_CXX_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS "${CONAN_SHARED_LINKER_FLAGS}")

add_executable(testVorbis main.c)
target_link_libraries(testVorbis ${CONAN_LIBS})
SET_TARGET_PROPERTIES(testVorbis PROPERTIES LINK_FLAGS "${CONAN_EXE_LINKER_FLAGS}")

