# info
The goal of this repo is to program nao behavior using existing python behavior.
[Active] Use YOLO model to recognize objects from nao's view. (image detection and 
        text2speech logic)
[Future] * Make nao turn head to detected object
         * Make nao point to detected object  

# Building qi from Binaries 
reference:
    https://www.instructables.com/DJ-Darcy-Real-Time-Python-Music-Adaptation-Through/

1. Get prereqs:

    Clone your libraries and install cmake
    git clone https://github.com/aldebaran/libqi-python.git
    git clone https://github.com/aldebaran/libqi.git

2. Setup conan
    #cd into virtual environment folder
    source [YOUR_VENV]/bin/activate

    pip install --upgrade conan

    # find c++ compiler 
    conan profile detect

    # cache conan2 file in repo
    conan export "PATH_TO_libqi" --version "4.0.1"
    eg "$HOME/libqi"


3. Create wheel: conan -> cmake 
    cd libqi-python
    conan install . --build=missing -s build_type=Debug

    Cmake build
    cmake --list-presets

    #above line gets conan_string and string

    cmake --preset [conan_string]
    cmake --build --preset [conan_string]

    deactivate
    
    # TEST

    source build/[string]/generators/conanrun.sh
    ctest --preset [conan_string] --output-on-failure
    source build/[string]/generators/deactivate_conanrun.sh

    # Install project
    
    cd .. #reactivate your venv
    source [YOUR_VENV]/bin/activate

    cd libqi-python

    cmake --install build/[string] --component Module --prefix ~/my-libqi-python-install

    # Make wheel
    conan install . --build=missing -c tools.build:skip_test=true

    pip install -U build

    cmake --list-presets

    #gets conan_release_string & release_string

    python -m build --config-setting cmake.define.CMAKE_TOOLCHAIN_FILE=$PWD/build/[release_string]/generators/conan_toolchain.cmake

3.   Install wheel
    cd dist

    pip3 install qi-3.1.5-cp39-cp39-macosx_14_0_arm64.whl

    # Check install in python interpreter

    python3

    import qi

    # for ImportError: libboost_filesystem.so.1.83.0: 
    # cannot open shared object file: No such file or directory

    path_to_boost = find ~/.conan2 -name "libboost_filesystem.so.1.83.0"
    
    export LD_LIBRARY_PATH=path_to_boost:$LD_LIBRARY_PATH
