repo for working with nao 
Goal is to have nao recognize objects using YOLO and then name them
Can also have nano point 

# installation 
https://www.instructables.com/DJ-Darcy-Real-Time-Python-Music-Adaptation-Through/

Creating the Wheel:

Clone your libraries and install cmake
git clone https://github.com/aldebaran/libqi-python.git

git clone https://github.com/aldebaran/libqi.git

brew install cmake

Setup conan
#cd into virtual environment folder

source [YOUR_VENV]/bin/activate

pip install --upgrade conan

conan profile detect

conan export "$HOME/libqi" --version "4.0.1"

# [YOUR_PATH] is whatever directory you put libqi in (step 1)

Conan Install
cd libqi-python

conan install . --build=missing -s build_type=Debug

Cmake build
cmake --list-presets

#above line gets conan_string and string

cmake --preset [conan_string]

cmake --build --preset [conan_string]

Test build (passed 79/80 tests?)
deactivate

source build/[string]/generators/conanrun.sh

ctest --preset [conan_string] --output-on-failure

source build/[string]/generators/deactivate_conanrun.sh

Install project
cd ..

#reactivate your venv

source [YOUR_VENV]/bin/activate

cd libqi-python

cmake --install build/[string] \

--component Module --prefix ~/my-libqi-python-install

Make wheel
conan install . --build=missing -c tools.build:skip_test=true

pip install -U build

cmake --list-presets

#gets conan_release_string & release_string

python -m build --config-setting cmake.define.CMAKE_TOOLCHAIN_FILE=$PWD/build/[release_string]/generators/conan_toolchain.cmake

Install wheel
cd dist

pip3 install qi-3.1.5-cp39-cp39-macosx_14_0_arm64.whl

Check install in python interpreter

python3

import qi

exit()

After Creating the Wheel:

(Install these in the same virtual environment)

pip install pyserial

pip install qi