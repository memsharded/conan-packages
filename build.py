from conan.packager import ConanMultiPackager
import os, platform

if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds()
    filtered_builds = []
    for settings, options in builder.builds:
        if not (settings["compiler"] == "Visual Studio" and settings["compiler.version"] != "14"):
            filtered_builds.append([settings, options])
    builder.builds = filtered_builds
    builder.run()
