from conans import ConanFile, CMake, os
import os

class GlewConan(ConanFile):
    name = "glew"
    version = "1.13.0"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    url="http://github.com/coding3d/conan-glew"
    requires = ""
    license="https://github.com/nigels-com/glew#copyright-and-licensing"
    exports = "*"

    def config(self):
        try: # Try catch can be removed when conan 0.8 is released
            del self.settings.compiler.libcxx
        except:
            pass

    def build(self):
        cmake = CMake(self.settings)

        try:
            if self.settings.os == "Windows":
                self.run("cd %s && rd /s /q _build" % self.ZIP_FOLDER_NAME)
            else:
                self.run("cd %s && rm -rf _build" % self.ZIP_FOLDER_NAME)
        except:
            pass

        self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
        cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
        self.run('%s && cmake ../build/cmake %s -DBUILD_UTILS=OFF' % (cd_build, cmake.command_line))
        self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))

    def package(self):
        # Copying headers
        self.copy("include/*", ".", "%s" % (self.ZIP_FOLDER_NAME), keep_path=True)

        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.run("cd %s/_build/lib/%s && del glew* && ren libglew32.lib glew32.lib && ren libglew32mx.lib glew32mx.lib" % (self.ZIP_FOLDER_NAME, self.settings.build_type))
                self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32'] if self.options.shared else ['libglew32']
        else:
            self.cpp_info.libs = ['libGLEW']
