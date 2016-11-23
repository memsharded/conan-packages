import os
import subprocess
from conans import ConanFile, CMake, os, ConfigureEnvironment
from conans.tools import download, unzip


class GlewConan(ConanFile):
    name = "glew"
    version = "2.0.0"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake", "txt"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    url="http://github.com/dimi309/conan-glew"
    requires = ""
    license="https://github.com/nigels-com/glew#copyright-and-licensing"
    exports = "*"

    def rpm_package_installed(self, package):
        p = subprocess.Popen(['rpm', '-q', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return 'install ok' in out or 'not installed' not in out

    def ensure_rpm_dependency(self, package):
        if not self.rpm_package_installed(package):
            self.output.warn(package + " is not installed in this machine! Conan will try to install it.")
            # Note: yum is automatically redirected to dnf on modern Fedora distros (see 'man yum2dnf')
            self.run("sudo yum install -y " + package)
            if not self.rpm_package_installed(package):
                self.output.error(package + " Installation doesn't work... install it manually and try again")
                exit(1)

    def debian_package_installed(self, package):
        p = subprocess.Popen(['dpkg', '-s', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return 'install ok' in out

    def ensure_debian_dependency(self, package):
        if not self.debian_package_installed(package):
            self.output.warn(package + " is not installed in this machine! Conan will try to install it.")
            self.run("sudo apt-get update && sudo apt-get install -y " + package)
            if not self.debian_package_installed(package):
                self.output.error(package + " Installation doesn't work... install it manually and try again")
                exit(1)

    def system_requirements(self):
        if self.settings.os == "Linux":
            if subprocess.call("which apt-get", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                self.ensure_debian_dependency("mesa-common-dev")
                self.ensure_debian_dependency("libglu1-mesa-dev")
            elif subprocess.call("which yum", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                self.ensure_rpm_dependency("mesa-libGL-devel")
                self.ensure_rpm_dependency("mesa-libGLU-devel")
            else:
                self.output.warn("Could not determine Linux distro, skipping system requirements check.")

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        if self.settings.os == "Windows":
            cd_build = ""
            proj_name="glew.sln"
            compiler_version = int(self.settings.compiler.version.value)
            if compiler_version == 10:
                cd_build = "cd %s\\build\\vc10" % self.ZIP_FOLDER_NAME
            elif compiler_version == 12:
                cd_build = "cd %s\\build\\vc12" % self.ZIP_FOLDER_NAME
            elif compiler_version > 12:
                cd_build = "cd %s\\build\\vc12" % self.ZIP_FOLDER_NAME
                self.run("%s && devenv %s /upgrade" % (cd_build, proj_name))
            elif compiler_version > 10 and compiler_version < 12:
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
            if self.options.shared:
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                self.copy(pattern="*.so", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = ['glew32']
            if not self.options.shared:
                self.cpp_info.libs[0] += "s"
                self.cpp_info.libs.append("OpenGL32.lib")
                self.cpp_info.defines.append("GLEW_STATIC")
                if self.settings.compiler.runtime != "MT":
                    self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMTD')
                    self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMT')

        else:
            self.cpp_info.libs = ['GLEW']
            if self.settings.os == "Macos":
                self.cpp_info.exelinkflags.append("-framework OpenGL")
            elif not self.options.shared:
                self.cpp_info.libs.append("GL")

        if self.settings.build_type == "Debug":
                self.cpp_info.libs[0] += "d"
