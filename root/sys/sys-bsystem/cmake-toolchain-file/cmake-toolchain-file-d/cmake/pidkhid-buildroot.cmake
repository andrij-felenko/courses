# Автоматично згенерований Buildroot тулчейн (фрагмент)
string(REGEX REPLACE "/+" "/" REL_CACHED_PATH "${CMAKE_CURRENT_LIST_DIR}/../../..")
get_filename_component(HOST_DIR "${REL_CACHED_PATH}" ABSOLUTE)

set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR aarch64)

set(CMAKE_C_COMPILER   "${HOST_DIR}/bin/aarch64-linux-gcc")
set(CMAKE_CXX_COMPILER "${HOST_DIR}/bin/aarch64-linux-g++")

set(CMAKE_SYSROOT "${HOST_DIR}/aarch64-buildroot-linux-gnu/sysroot")
set(CMAKE_FIND_ROOT_PATH "${CMAKE_SYSROOT}")
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
