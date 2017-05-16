from conans import ConanFile, CMake
from conans.tools import download, unzip
import os, subprocess

class GlfwConan(ConanFile):
    name = "glfw"
    version = "3.2.1"
    description = "The GLFW library - Builds on Windows, Linux and Macos/OSX"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    url="http://github.com/dimi309/conan-packages"
    license="https://github.com/glfw/glfw/blob/master/LICENSE.md"
    exports = "FindGLFW.cmake"

    def rpm_package_installed(self, package):
        p = subprocess.Popen(['rpm', '-q', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate()
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
        out, _ = p.communicate()
        return 'install ok' in out

    def ensure_debian_dependency(self, package):
        if not self.debian_package_installed(package):
            self.output.warn(package + " is not installed in this machine! Conan will try to install it.")
            self.run("sudo apt-get update && sudo apt-get install -y " + package)
            if not self.debian_package_installed(package):
                self.output.error(package + " Installation doesn't work... install it manually and try again")
                exit(1)

    def system_requirements(self):
        if subprocess.call("which apt-get", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            self.ensure_debian_dependency("libglu1-mesa-dev")
            self.ensure_debian_dependency("xorg-dev")
        elif subprocess.call("which yum", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            self.ensure_rpm_dependency("mesa-libGL-devel")
            self.ensure_rpm_dependency("xorg-x11-server-devel")
            self.ensure_rpm_dependency("libXrandr-devel")
            self.ensure_rpm_dependency("libXinerama-devel")
            self.ensure_rpm_dependency("libXcursor-devel")
        else:
            self.output.warn("Could not determine package manager, skipping Linux system requirements installation.")

    def source(self):
        download("https://github.com/glfw/glfw/archive/%s.zip" % self.version, "%s.zip" % self.ZIP_FOLDER_NAME)
        unzip("%s.zip" % self.ZIP_FOLDER_NAME)
        os.unlink("%s.zip" % self.ZIP_FOLDER_NAME)

    def build(self):
        cmake = CMake(self)
        dynlib = '-DBUILD_SHARED_LIBS=ON' if self.options.shared else ''
        self.run("cmake %s/%s %s %s -DGLFW_BUILD_EXAMPLES=OFF -DGLFW_BUILD_TESTS=OFF -DGLFW_BUILD_DOCS=OFF" %
                 (self.conanfile_directory, self.ZIP_FOLDER_NAME, cmake.command_line, dynlib))
        self.run("cmake --build %s %s" % (self.conanfile_directory, cmake.build_config))

    def package(self):
        self.copy("FindGLFW.cmake", ".", ".")
        
        self.copy(pattern="*.h", dst="include", src="%s/include" % self.ZIP_FOLDER_NAME, keep_path=True)

        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
                self.copy(pattern="*.pdb", dst="bin", keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Linux":
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
                elif self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.output.info("conan-detected os: %s" % self.settings.os)
        btype = "shared" if self.options.shared else "static"
        self.output.info("packaging %s library" % btype)
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ['glfw3dll']
            else:
                self.cpp_info.libs = ['glfw3']
        else:
            if self.options.shared:
                self.cpp_info.libs = ['glfw']
                if self.settings.os == "Linux":
                    self.cpp_info.exelinkflags.append("-lXrandr -ldl")
            else:
                self.cpp_info.libs = ['glfw3']
                if self.settings.os == "Macos":
                    self.cpp_info.exelinkflags.append("-framework OpenGL -framework Cocoa -framework IOKit -framework CoreVideo")
                if self.settings.os == "Linux":
                    self.cpp_info.exelinkflags.append("-lXrandr -lXrender -lGL -lm -ldl -ldrm -lXdamage -lX11-xcb -lxcb-glx -lxcb-dri2 -lxcb-dri3 -lxcb-present -lxcb-sync -lXxf86vm -lXfixes -lXext -lX11 -lpthread -lxcb -lXau -lXcursor -lXinerama")
        self.output.info("Link flags set: %s" % self.cpp_info.exelinkflags)
