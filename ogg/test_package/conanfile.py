from conans import ConanFile, CMake
import os

channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "dimi309")

class TestOgg(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "ogg/1.3.2@%s/%s" % (username, channel)
    generators = "cmake"

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def test(self):
        self.run(os.sep.join(["cd bin && .", "testOgg"]))

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin")
        self.copy(pattern="*.dylib", dst="bin", src="lib")
