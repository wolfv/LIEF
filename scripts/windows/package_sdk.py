from setuptools import msvc
import pathlib
import os
import sys
import subprocess
import shutil

env = os.environ

CWD = pathlib.WindowsPath(__file__).parent
LIEF_SRC = CWD / ".." / ".."
print("LIEF src: {}".format(LIEF_SRC))

BUILD_PATH = LIEF_SRC / "build"
BUILD_STATIC_PATH = BUILD_PATH / "static-release"
BUILD_SHARED_PATH = BUILD_PATH / "shared-release"
CPACK_CONFIG_PATH = (LIEF_SRC / "cmake" / "cpack.config.cmake").resolve()

CMAKE_PATH = pathlib.WindowsPath(shutil.which("cmake.exe"))
CPACK_PATH = CMAKE_PATH.parent / "cpack.exe"

if not CPACK_PATH.is_file():
    print("Can't find cpack.exe at: {}".format(CPACK_PATH), file=sys.stderr)
    sys.exit(1)


if not CMAKE_PATH.is_file():
    print("Can't find cmake.exe at: {}".format(CMAKE_PATH), file=sys.stderr)
    sys.exit(1)

CPACK_BIN = CPACK_PATH.as_posix()

BUILD_PATH.mkdir(exist_ok=True)
BUILD_STATIC_PATH.mkdir(exist_ok=True)
BUILD_STATIC_PATH = BUILD_STATIC_PATH.resolve().as_posix()
BUILD_SHARED_PATH.mkdir(exist_ok=True)
BUILD_SHARED_PATH = BUILD_SHARED_PATH.resolve().as_posix()

is64 = sys.maxsize > 2**32
arch = 'x64' if is64 else 'x86'

ninja_env = msvc.msvc14_get_vc_env(arch)
env.update(ninja_env)

cmake_config_static = [
    "-G", "Ninja",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DBUILD_SHARED_LIBS=off",
    "-DLIEF_INSTALL_COMPILED_EXAMPLES=on",
    "-DLIEF_USE_CRT_RELEASE=MT",
]

cmake_config_shared = [
    "-G", "Ninja",
    "-DCMAKE_BUILD_TYPE=Release",
    "-DBUILD_SHARED_LIBS=on",
    "-DLIEF_INSTALL_COMPILED_EXAMPLES=off",
    "-DLIEF_USE_CRT_RELEASE=MT",
]


build_args = ['--config', 'Release']


configure_cmd = ['cmake', LIEF_SRC.resolve().as_posix()]
print("Shared lib Configured with {} in {}".format(" ".join(configure_cmd + cmake_config_shared), BUILD_SHARED_PATH))

subprocess.check_call(configure_cmd + cmake_config_shared, cwd=BUILD_SHARED_PATH, env=env )
subprocess.check_call(['cmake', '--build', '.', '--target', "all"] + build_args, cwd=BUILD_SHARED_PATH, env=env)

print("Static lib Configured with {} in {}".format(" ".join(configure_cmd + cmake_config_static), BUILD_STATIC_PATH))

subprocess.check_call(configure_cmd + cmake_config_static, cwd=BUILD_STATIC_PATH, env=env)
subprocess.check_call(['cmake', '--build', '.', '--target', "all"] + build_args, cwd=BUILD_STATIC_PATH, env=env)

subprocess.check_call([CPACK_BIN, '--config', CPACK_CONFIG_PATH.resolve().as_posix()], cwd=BUILD_PATH, env=env)
