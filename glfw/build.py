from conan.packager import ConanMultiPackager
import os, platform

if __name__ == "__main__":
    builder = ConanMultiPackager(args="--build missing")
    builder.add_common_builds()
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if not (settings["arch"] == "x86" or (settings["compiler"] == "apple-clang" and (settings["build_type"] =="Release" or settings["compiler.version"] == "8.0"))):
            filtered_builds.append([settings, options, env_vars, build_requires])
            print("%s %s %s %s " % (settings, options, env_vars, build_requires))
    builder.builds = filtered_builds
    builder.run()
