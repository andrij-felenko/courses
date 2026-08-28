set(VCPKG_TARGET_ARCHITECTURE arm64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Linux)

# Підключення зовнішнього тулчейна компілятора
set(VCPKG_CHAINLOAD_TOOLCHAIN_FILE "${CMAKE_CURRENT_LIST_DIR}/../../cmake/toolchains/aarch64-linux-gnu.cmake")

# Оптимізаційні прапорці збірки
set(VCPKG_C_FLAGS "-O3 -march=armv8-a+crc -pipe")
set(VCPKG_CXX_FLAGS "-O3 -march=armv8-a+crc -pipe -fno-rtti")
