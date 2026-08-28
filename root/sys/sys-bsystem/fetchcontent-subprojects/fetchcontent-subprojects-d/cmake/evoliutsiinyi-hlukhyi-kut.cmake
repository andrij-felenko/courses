# Історичний підхід через ExternalProject_Add
include(ExternalProject)

ExternalProject_Add(fmt_external
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        10.2.0
    PREFIX         ${CMAKE_BINARY_DIR}/external/fmt
    CMAKE_ARGS     -DCMAKE_INSTALL_PREFIX:PATH=<INSTALL_DIR>
                   -DFMT_TEST:BOOL=OFF
)
