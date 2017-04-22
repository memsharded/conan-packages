#!/bin/bash

set -e
set -x

if [[ "$(uname -s)" == 'Darwin' ]]; then
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
    fi
    pyenv activate conan
fi

: 'cd ogg
python build.py
cd ..
cd vorbis
python build.py
cd ..'
cd glew
python build.py
