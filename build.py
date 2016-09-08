from conan.packager import ConanMultiPackager
import os

username = os.getenv("CONAN_USERNAME", "coding3d")

if __name__ == "__main__":
    builder = ConanMultiPackager(username=username)
    builder.add_common_builds(pure_c=True)
    builder.run()
