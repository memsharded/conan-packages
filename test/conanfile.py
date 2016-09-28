from conans import ConanFile, CMake
import os

channel = os.getenv("CONAN_CHANNEL", "test")
username = os.getenv("CONAN_USERNAME", "coding3d")

class TestGlew(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "glew/1.13.0@%s/%s" % (username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def test(self):
        self.run(os.sep.join([".","bin", "testGlew"]))

    def imports(self):
        self.copy("*.dll", "bin", "bin")
