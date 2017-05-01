from conans import ConanFile, CMake
from conans.tools import download, unzip, replace_in_file
import os, subprocess

class Small3dConan(ConanFile):
    name = "small3d"
    version = "master"
    description = "A small, cross-platform 3D game engine (C++, OpenGL, SDL or GLFW) - runs on Win/MacOS/Linux"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    url="http://github.com/dimi309/conan-packages"
    requires = "glfw/3.2.1@coding3d/stable", "freetype/2.6.3@lasote/stable","glew/2.0.0@coding3d/stable", \
        "libpng/1.6.23@lasote/stable","zlib/1.2.8@lasote/stable","glm/0.9.8.4@coding3d/stable", \
        "vorbis/1.3.5@coding3d/stable", "portaudio/rc.v190600.20161001@coding3d/temp"
    default_options = "glew:shared=False"
    license="https://github.com/dimi309/small3d/blob/master/LICENSE"
    exports = "*"

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
            self.ensure_debian_dependency("libjack-dev")
        elif subprocess.call("which yum", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            self.ensure_rpm_dependency("jack-audio-connection-kit-devel")
            self.ensure_rpm_dependency("alsa-lib-devel")
        else:
            self.output.warn("Could not determine Linux distro, skipping system requirements check.")

    def source(self):
        download("https://github.com/dimi309/small3d/archive/%s.zip" % self.version, "%s.zip" % self.ZIP_FOLDER_NAME)
        unzip("%s.zip" % self.ZIP_FOLDER_NAME)
        os.unlink("%s.zip" % self.ZIP_FOLDER_NAME)
        
    def build(self):
        self.system_requirements()
        replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "project(small3d)",
                        """
project(small3d)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_C_FLAGS "${CONAN_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CONAN_CXX_FLAGS}")
set(CMAKE_SHARED_LINKER_FLAGS "${CONAN_SHARED_LINKER_FLAGS}")

                        """)

        replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'file(COPY "small3d/include" DESTINATION ".")', """
if(FALSE)
file(COPY "small3d/include" DESTINATION ".")
""")

        replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)', """
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
endif()
""")
        
        replace_in_file("%s/small3d/src/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "# Unit testing",
                        """
if(FALSE)
                        """)

        replace_in_file("%s/small3d/src/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "endif(APPLE)",
                        """
endif(APPLE)
endif()
                        """)
        
        
        cmake = CMake(self)
        self.run("cmake %s/%s %s" % (self.conanfile_directory, self.ZIP_FOLDER_NAME, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):

        self.copy("FindSMALL3D.cmake", ".", ".")
        self.copy(pattern="*", dst="shaders", src="%s/small3d/resources/shaders" % self.ZIP_FOLDER_NAME, keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="%s/small3d/include" % self.ZIP_FOLDER_NAME, keep_path=True)

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
        self.cpp_info.libs = ['small3d']
        if self.settings.os == "Windows":
            self.cpp_info.cppflags.append("/EHsc")
            self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMTD')
            self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMT')
        elif self.settings.os == "Macos":
            self.cpp_info.cppflags.append("-std=c++11")
            self.cpp_info.cppflags.append("-stdlib=libc++")
            self.cpp_info.exelinkflags.append("-framework CoreAudio -framework AudioToolbox -framework AudioUnit -framework CoreServices -framework Carbon")
        else:
            self.cpp_info.cppflags.append("-std=c++11")
            self.cpp_info.cppflags.append("-Wl,--no-as-needed")
            self.cpp_info.exelinkflags.append("-ljack -lasound -lpthread")
