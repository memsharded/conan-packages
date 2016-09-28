from conans import ConanFile, CMake, os, ConfigureEnvironment
import os, subprocess
from conans.tools import download, unzip

class GlewConan(ConanFile):
    name = "glew"
    version = "1.13.0"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    url="http://github.com/dimi309/conan-glew"
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
            self.run("sudo apt-get update && sudo apt-get install -y " + package)
            if not self.linux_package_installed(package):
                self.output.error(package + " Installation doesn't work... install it manually and try again")
                exit(1)

    def system_requirements(self):
        if self.settings.os == "Linux":
            self.ensure_linux_dependency("mesa-common-dev")
            self.ensure_linux_dependency("libglu1-mesa-dev")

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os != "Windows":
            self.options.remove("shared")

    def build(self):
        if self.settings.os == "Windows":
            cd_build = ""
            proj_name="glew.sln"
            if self.settings.compiler.version == 10:
                cd_build = "cd %s\\build\\vc10" % self.ZIP_FOLDER_NAME
            elif self.settings.compiler.version == 12:
                cd_build = "cd %s\\build\\vc12" % self.ZIP_FOLDER_NAME
            elif self.settings.compiler.version > 12:
                cd_build = "cd %s\\build\\vc12" % self.ZIP_FOLDER_NAME
                self.run("%s && devenv %s /upgrade" % (cd_build, proj_name))
            elif self.settings.compiler.version > 10 and self.settings.compiler.version < 12:
                cd_build = "cd %s\\build\\vc10" % self.ZIP_FOLDER_NAME
                self.run("%s && devenv %s /upgrade" % (cd_build, proj_name))
            platform = "Win32" if self.settings.arch == "x86" else "x64"
            self.run("%s && msbuild %s /property:Configuration=%s /property:Platform=%s" %
                (cd_build, proj_name, self.settings.build_type, platform))
        else:
            cmake = CMake(self.settings)
            self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
            cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
            self.run('%s && cmake ../build/cmake %s -DBUILD_UTILS=OFF' % (cd_build, cmake.command_line))
            self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))

    def package(self):
        self.copy("FindGLEW.cmake", ".", ".")
        self.copy("include/*", ".", "%s" % (self.ZIP_FOLDER_NAME), keep_path=True)

        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*32.lib", dst="lib", keep_path=False)
                self.copy(pattern="*32d.lib", dst="lib", keep_path=False)
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            else:
                self.copy(pattern="*32s.lib", dst="lib", keep_path=False)
                self.copy(pattern="*32sd.lib", dst="lib", keep_path=False)
        elif self.settings.os == "Macos":
            self.copy(pattern="*.a", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.so", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32']
            if not self.options.shared:
                self.cpp_info.libs[0] += "s"
        else:
            self.cpp_info.libs = ['GLEW']

        if self.settings.build_type == "Debug":
                self.cpp_info.libs[0] += "d"
