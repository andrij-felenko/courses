# x64-linux-custom.cmake
set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE static)
set(VCPKG_CMAKE_SYSTEM_NAME Linux)
set(VCPKG_BUILD_TYPE release)

# Додаткові прапорці компілятора для захисту пам'яті
set(VCPKG_C_FLAGS "-fstack-protector-strong -D_FORTIFY_SOURCE=2")
set(VCPKG_CXX_FLAGS "-fstack-protector-strong -D_FORTIFY_SOURCE=2")
