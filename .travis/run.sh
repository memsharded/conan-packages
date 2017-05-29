#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

cd glew
export CONAN_REFERENCE=glew/2.0.0
python build.py
cd ..
cd glfw
export CONAN_REFERENCE=glfw/3.2.1
python build.py
cd ..
cd glm
export CONAN_REFERENCE=glm/0.9.8.4
python build.py
cd ..
cd ogg
export CONAN_REFERENCE=ogg/1.3.2
python build.py
cd ..
cd vorbis
export CONAN_REFERENCE=vorbis/1.3.5
python build.py
cd ..
cd small3d
export CONAN_REFERENCE=small3d/master
python build.py
