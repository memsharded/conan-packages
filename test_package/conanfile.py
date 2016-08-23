from conans import ConanFile, CMake
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "ci")
username = os.getenv("CONAN_USERNAME", "coding3d")

class TestGlew(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "glew/1.13.0@%s/%s" % (username, channel)
    generators = "cmake"

    def configure(self):
        del self.settings.compiler.libcxx

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def test(self):
        # equal to ./bin/greet, but portable win: .\bin\greet
        self.run(os.sep.join([".","bin", "testGlew"]))

    def imports(self):
        if self.settings.os == "Windows":
            self.copy("*.dll", "bin", "bin")
