from conan.packager import ConanMultiPackager
import os

username = os.getenv("CONAN_USERNAME", "coding3d")

if __name__ == "__main__":
    builder = ConanMultiPackager(username=username, archs =  ["x86_64"],  visual_versions = [14])
    builder.add_common_builds()
    builder.run()
