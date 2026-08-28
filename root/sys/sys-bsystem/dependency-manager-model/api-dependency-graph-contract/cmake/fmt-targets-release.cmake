# Приклад згенерованого файлу fmt-targets-release.cmake
add_library(fmt::fmt STATIC IMPORTED GLOBAL)

set_target_properties(fmt::fmt PROPERTIES
    IMPORTED_LOCATION_RELEASE "/home/user/.conan2/p/pkg_4a91c78e3b1290ff/p/lib/libfmt.a"
    INTERFACE_INCLUDE_DIRECTORIES "/home/user/.conan2/p/pkg_4a91c78e3b1290ff/p/include"
    INTERFACE_COMPILE_DEFINITIONS "FMT_SHARED=0"
    INTERFACE_COMPILE_FEATURES "cxx_std_17"
    INTERFACE_LINK_LIBRARIES "m"
)
