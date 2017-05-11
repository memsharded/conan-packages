from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.tools import download, unzip, replace_in_file, run_in_windows_bash
from conans.util.files import load
import os, subprocess, re

def replace_in_file_regex(file_path, search, replace):
    content = load(file_path)
    content = re.sub(search, replace, content)
    content = content.encode("utf-8")
    with open(file_path, "wb") as handle:
        handle.write(content)

class OggConan(ConanFile):
    name = "ogg"
    version = "1.3.2"
    ZIP_FOLDER_NAME = "lib%s-%s" % (name, version)
    generators = "txt"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/dimi309/conan-packages"
    description="The OGG library"
    requires = ""
    license="BSD"
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
        if self.settings.os == "Linux":
            if subprocess.call("which apt-get", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                self.ensure_debian_dependency("libtool")
            elif subprocess.call("which yum", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
                self.ensure_rpm_dependency("libtool")
            else:
                self.output.warn("Could not determine Linux distro, skipping system requirements check.")

    def configure(self):
        del self.settings.compiler.libcxx

        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
                
        download("http://downloads.xiph.org/releases/ogg/%s" % zip_name, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        
        if self.settings.compiler == "Visual Studio":
            
            env = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env.vars):
                vcvars = tools.vcvars_command(self.settings)
            
                if self.options.shared:
                    vs_project = "libogg_dynamic"
                else:
                    vs_project = "libogg_static"

                cd_build = "cd %s\\win32\\VS2010" % self.ZIP_FOLDER_NAME
                self.run("%s && %s && devenv %s.sln /upgrade" % (vcvars, cd_build, vs_project))
                vs_runtime = {
                    "MT": "MultiThreaded",
                    "MTd": "MultiThreadedDebug",
                    "MD": "MultiThreadedDLL",
                    "MDd": "MultiThreadedDebugDLL"
                }
                replace_in_file_regex(
                    "%s\\win32\\VS2010\\%s.vcxproj" % (self.ZIP_FOLDER_NAME, vs_project),
                    r"<RuntimeLibrary>\w+</RuntimeLibrary>",
                    "<RuntimeLibrary>%s</RuntimeLibrary>" % vs_runtime.get(str(self.settings.compiler.runtime), "Invalid"))
                platform = "Win32" if self.settings.arch == "x86" else "x64"
                self.run("%s && %s && msbuild %s.sln /property:Configuration=%s /property:Platform=%s" % \
            (vcvars, cd_build, vs_project, self.settings.build_type, platform))
        else:
            env = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env.vars):

                if self.settings.os != "Windows":
                    env.fpic = self.options.fPIC

                if self.settings.os == "Macos":
                    old_str = '-install_name \\$rpath/\\$soname'
                    new_str = '-install_name \\$soname'
                    replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)
            
                cd_build = "cd %s" % self.ZIP_FOLDER_NAME

                with tools.environment_append(env.vars):
                    
                    # This solves an automake version mismatch problem
                    if self.settings.os == "Linux":
                        if self.settings.compiler.version >= 5.3:
                            self.run("%s && autoreconf --force --install" % cd_build)
                        self.run("%s && aclocal" % cd_build)
                        self.run("%s && automake" % cd_build)

                    if self.settings.os == "Windows":
                        self.run("%s && .\configure" % cd_build)
                        self.run("%s && make" % cd_build)
                    else:
                        self.run("%s && .\configure" % cd_build)
                        self.run("%s && make" % cd_build)

    def package(self):
        self.copy("FindOGG.cmake", ".", ".")
        self.copy("include/ogg/*.h", ".", "%s" % (self.ZIP_FOLDER_NAME), keep_path=True)

        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                elif self.settings.os == "Windows":
                    self.copy(pattern="*.dll", dst="bin", keep_path=False)
                    self.copy(pattern="*.dll.a", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*g.a", dst="lib", keep_path=False)
     
    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ['libogg']
            else:
                self.cpp_info.libs = ['libogg_static']             
        else:
            self.cpp_info.libs = ['ogg']
