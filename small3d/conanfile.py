from conans import ConanFile, CMake
from conans.tools import download, unzip, replace_in_file, os_info
import os, subprocess

class Small3dConan(ConanFile):
    name = "small3d"
    version = "master"
    description = "A small, cross-platform 3D game engine (C++, OpenGL, GLFW) - runs on Win/MacOS/Linux"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "cmake"
    settings = "os", "arch", "build_type", "compiler"
    options = {"localUnitTests": [True, False]}
    url="http://github.com/dimi309/conan-packages"
    requires = "glfw/3.2.1@dimi309/stable", "freetype/2.6.3@lasote/stable","glew/2.0.0@dimi309/stable", \
        "libpng/1.6.23@lasote/stable","zlib/1.2.8@lasote/stable","glm/0.9.8.4@dimi309/stable", \
        "vorbis/1.3.5@dimi309/stable", "portaudio/rc.v190600.20161001@jgsogo/stable"
    default_options = "localUnitTests=False"
    license="https://github.com/dimi309/small3d/blob/master/LICENSE"
    exports = ["FindSMALL3D.cmake"]

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
        if os_info.is_linux:
            if subprocess.call("which apt-get", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                self.ensure_debian_dependency("libglu1-mesa-dev")
            elif subprocess.call("which yum", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                self.ensure_rpm_dependency("mesa-libGL-devel")
            else:
                self.output.warn("Could not determine package manager, skipping Linux system requirements installation.")
    
    def source(self):        
        download("https://github.com/dimi309/small3d/archive/%s.zip" % self.version, "%s.zip" % self.ZIP_FOLDER_NAME)
        unzip("%s.zip" % self.ZIP_FOLDER_NAME)
        os.unlink("%s.zip" % self.ZIP_FOLDER_NAME)

    def requirements(self):
        if self.options.localUnitTests:
            self.requires("gtest/1.8.0@lasote/stable")
            
    def build(self):

        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self.output.error("On Windows, only Visual Studio compilation is supported for the time being.")
            quit()

        replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "project(small3d)",
                        """
project(small3d)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
if(CMAKE_COMPILER_IS_GNUCXX)
add_definitions(-D_GLIBCXX_USE_CXX11_ABI=1)
endif(CMAKE_COMPILER_IS_GNUCXX)
                        """)

        replace_in_file("%s/small3d/src/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "${OPENGL_LIBRARIES}", "")
        replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'file(COPY "small3d/include" DESTINATION ".")', """
if(FALSE)
file(COPY "small3d/include" DESTINATION ".")
""")

        replace_in_file("%s/CMakeLists.txt" % self.ZIP_FOLDER_NAME, 'set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)', """
set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)
endif()
""")
        if not self.options.localUnitTests:
            replace_in_file("%s/small3d/src/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "# Unit testing",
                        """
if(FALSE)
                        """)

            replace_in_file("%s/small3d/src/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "endif(APPLE)",
                        """
endif(APPLE)
endif()
                        """)
        else:
            replace_in_file("%s/small3d/src/CMakeLists.txt" % self.ZIP_FOLDER_NAME, "target_link_libraries(small3dTest PUBLIC ${GTEST_BOTH_LIBRARIES} small3d )", "target_link_libraries(small3dTest PUBLIC ${CONAN_LIBS} small3d)")
        
        cmake = CMake(self)
        self.run("cmake %s/%s %s" % (self.conanfile_directory, self.ZIP_FOLDER_NAME, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):

        self.copy("FindSMALL3D.cmake", ".", ".")
        self.copy(pattern="*", dst="shaders", src="%s/small3d/resources/shaders" % self.ZIP_FOLDER_NAME, keep_path=True)
        self.copy(pattern="*.hpp", dst="include", src="%s/small3d/include" % self.ZIP_FOLDER_NAME, keep_path=True)

        if self.settings.os == "Windows":
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.pdb", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.settings.os == "Macos":
                self.copy(pattern="*.a", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)
                self.copy(pattern="*.a", dst="lib", keep_path=False)
    def imports(self):
        if self.options.localUnitTests:
            self.copy("*.dll", "", "")
            
    def package_info(self):
        self.cpp_info.libs = ['small3d']
        if self.settings.os == "Windows":
            self.cpp_info.cppflags.append("/EHsc")
            self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMTD')
            self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMT')
        else:
            self.cpp_info.cppflags.append("-std=c++11")
            if self.settings.os == "Macos":
                self.cpp_info.cppflags.append("-stdlib=libc++")
