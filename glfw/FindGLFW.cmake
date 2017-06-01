find_path(GLFW_INCLUDE_DIR NAMES GLFW PATHS include)
find_library(GLFW_LIBRARY NAMES glfw glfw3 glfw3dll PATHS lib )

MESSAGE("** GLFW FOUND BY CONAN")
SET(GLFW_FOUND TRUE)
MESSAGE("** FOUND GLFW:  ${GLFW_LIBRARY}")
MESSAGE("** FOUND GLFW INCLUDE:  ${GLFW_INCLUDE_DIR}")

set(GLFW_INCLUDE_DIRS ${GLFW_INCLUDE_DIR})
set(GLFW_LIBRARIES ${GLFW_LIBRARY})

mark_as_advanced(GLFW_LIBRARY GLFW_INCLUDE_DIR)

set(OGG_MAJOR_VERSION "3")
set(OGG_MINOR_VERSION "2")
set(OGG_PATCH_VERSION "1")

