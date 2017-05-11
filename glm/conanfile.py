import os
from conans import ConanFile
from conans.tools import download, unzip

class GlmConan(ConanFile):
    name = "glm"
    version = "0.9.8.4"
    ZIP_FOLDER_NAME = "%s-%s" % (name, version)
    generators = "txt"
    url="http://github.com/dimi309/conan-packages"
    description="The GLM library"
    requires = ""
    license = "https://github.com/nigels-com/glew#copyright-and-licensing"
    exports = "FindGLM.cmake"

    def source(self):
        zip_name = "%s.zip" % self.ZIP_FOLDER_NAME
        download("https://github.com/g-truc/glm/archive/%s.zip" % self.version, zip_name)
        unzip(zip_name)
        os.unlink(zip_name)

    def build(self):
        self.output.warn("No compilation necessary for GLM")

    def package(self):
        self.copy("FindGLM.cmake", ".", ".")
        self.copy("*", src="./%s/glm" % self.ZIP_FOLDER_NAME, dst="./include/glm")
