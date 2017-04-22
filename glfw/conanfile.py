from conans import ConanFile, CMake, os
from conans.tools import download, unzip
import os, subprocess

class GlfwConan(ConanFile):
    name = "glfw"
    version = "3.2.1"
    description = "The GLFW library"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    url="http://github.com/dimi309/conan-packages"
    license="https://github.com/glfw/glfw/blob/master/LICENSE.md"
    exports = "*"

    def source(self):
        download("https://github.com/glfw/glfw/archive/%s.zip" % self.version, "%s.zip" % self.ZIP_FOLDER_NAME)
        unzip("%s.zip" % self.ZIP_FOLDER_NAME)
        os.unlink("%s.zip" % self.ZIP_FOLDER_NAME)

    def build(self):
        cmake = CMake(self)
        self.run("cmake %s/%s %s" % (self.conanfile_directory, self.ZIP_FOLDER_NAME, cmake.command_line))
        self.run("cmake --build %s %s" % (self.conanfile_directory, cmake.build_config))

    def package(self):

        self.copy("FindGLFW.cmake", self.ZIP_FOLDER_NAME, ".")
        
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.ZIP_FOLDER_NAME, keep_path=True)

        if self.settings.os == "Windows":
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.settings.os == "Macos":
                self.copy(pattern="*.a", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['glfw3']

