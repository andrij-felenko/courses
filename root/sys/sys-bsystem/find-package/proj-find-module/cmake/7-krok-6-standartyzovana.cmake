include(FindPackageHandleStandardArgs)

find_package_handle_standard_args(FastCodec
    REQUIRED_VARS
        FastCodec_LIBRARY
        FastCodec_INCLUDE_DIR
    VERSION_VAR
        FastCodec_VERSION
    HANDLE_COMPONENTS
)
