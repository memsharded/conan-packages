from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
from conans.tools import download, unzip, replace_in_file
import os
class VorbisConan(ConanFile):
    name = "vorbis"
    version = "1.3.5"
    ZIP_FOLDER_NAME = "lib%s-%s" % (name, version)
    generators = "txt"
    settings = "os", "arch", "build_type", "compiler"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url="http://github.com/dimi309/conan-packages"
    description="The VORBIS library"
    requires = "ogg/1.3.2@coding3d/stable"
    license="BSD"
    exports = "*"

    def configure(self):
        del self.settings.compiler.libcxx

        if self.settings.os == "Windows":
            self.options.remove("fPIC")
        else:
            self.options.remove("shared")

    def source(self):
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME

        download("http://downloads.xiph.org/releases/vorbis/%s" % zip_name, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):

        if self.settings.os == "Windows":

            if self.settings.compiler != "Visual Studio":
                self.output.error("On Windows, only Visual Studio compilation is supported for the time being.")
                quit()
            
            env = VisualStudioBuildEnvironment(self)
            with tools.environment_append(env.vars):
                vcvars = tools.vcvars_command(self.settings)
            
                if self.options.shared:
                    vs_suffix = "_dynamic"
                else:
                    vs_suffix = "_static"

                libdirs="<AdditionalLibraryDirectories>"
                libdirs_ext="<AdditionalLibraryDirectories>$(LIB);"
                replace_in_file("%s\\win32\\VS2010\\libvorbis\\libvorbis%s.vcxproj" % (self.ZIP_FOLDER_NAME, vs_suffix), libdirs, libdirs_ext)
                replace_in_file("%s\\win32\\VS2010\\libvorbisfile\\libvorbisfile%s.vcxproj" % (self.ZIP_FOLDER_NAME, vs_suffix), libdirs, libdirs_ext)
                replace_in_file("%s\\win32\\VS2010\\vorbisdec\\vorbisdec%s.vcxproj" % (self.ZIP_FOLDER_NAME, vs_suffix), libdirs, libdirs_ext)
                replace_in_file("%s\\win32\\VS2010\\vorbisenc\\vorbisenc%s.vcxproj" % (self.ZIP_FOLDER_NAME, vs_suffix), libdirs, libdirs_ext)
                cd_build = "cd %s\\%s\\win32\\VS2010" % (self.conanfile_directory, self.ZIP_FOLDER_NAME)
                self.run("%s && %s && devenv vorbis%s.sln /upgrade" % (vcvars, cd_build, vs_suffix))
                platform = "Win32" if self.settings.arch == "x86" else "x64"
                self.run("%s && %s & msbuild vorbis%s.sln /property:Configuration=%s /property:Platform=%s" %
                         (vcvars, cd_build, vs_suffix, self.settings.build_type, platform))
        else:
            env = AutoToolsBuildEnvironment(self)
            with tools.environment_append(env.vars):
                env.fpic = self.options.fPIC

                cd_build = "cd %s" % self.ZIP_FOLDER_NAME

                if self.settings.os == "Macos":
                    old_str = '-install_name \\$rpath/\\$soname'
                    new_str = '-install_name \\$soname'
                    replace_in_file("./%s/configure" % self.ZIP_FOLDER_NAME, old_str, new_str)

                self.run("%s && chmod +x ./configure && ./configure" % cd_build)
                self.run("%s && make" % cd_build)

    def package(self):
        self.copy("FindVORBIS.cmake", ".", ".")
        self.copy("include/vorbis/*", ".", "%s" % (self.ZIP_FOLDER_NAME), keep_path=True)

        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.settings.os == "Macos":
                self.copy(pattern="*.a", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.options.shared:
                self.cpp_info.libs = ['libvorbis', 'libvorbisfile']
            else:
                self.cpp_info.libs = ['libvorbis_static', 'libvorbisfile_static']
                self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMTD')
                self.cpp_info.exelinkflags.append('/NODEFAULTLIB:LIBCMT')
        else:
            self.cpp_info.libs = ['vorbis', 'vorbisfile', 'vorbisenc']
