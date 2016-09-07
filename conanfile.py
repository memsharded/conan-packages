from conans import ConanFile, CMake, os
import os, subprocess

class GlewConan(ConanFile):
    name = "glew"
    version = "1.13.0"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    url="http://github.com/coding3d/conan-glew"
    requires = ""
    license="https://github.com/nigels-com/glew#copyright-and-licensing"
    exports = "*"

    def linux_package_installed(self, package):
        p = subprocess.Popen(['dpkg', '-s', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return 'install ok' in out

    def ensure_linux_dependency(self, package):
        if not self.linux_package_installed(package):
            self.output.warn(package + " is not installed in this machine! Conan will try to install it.")
            self.run("sudo apt-get install -y " + package)
            if not self.linux_package_installed(package):
                self.output.error(package + " Installation doesn't work... install it manually and try again")
                exit(1)

    def system_requirements(self):
        if self.settings.os == "Linux":
            self.ensure_linux_dependency("mesa-common-dev")
            self.ensure_linux_dependency("libglu1-mesa-dev")
                
    def build(self):
        self.system_requirements()
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
        self.copy("FindGLEW.cmake", ".", ".")
        self.copy("include/*", ".", "%s" % (self.ZIP_FOLDER_NAME), keep_path=True)

        if self.settings.os == "Windows":
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.settings.os == "Macos":
                self.copy(pattern="*.a", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
                self.copy(pattern="*.so*", dst="lib", keep_path=False)


    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32'] 
        else:
            self.cpp_info.libs = ['GLEW']
