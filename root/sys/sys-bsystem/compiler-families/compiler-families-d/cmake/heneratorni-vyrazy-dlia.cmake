target_compile_options(core_engine PRIVATE
    # Набір попереджень для GCC та Clang
    $<$<CXX_COMPILER_ID:GNU,Clang,AppleClang>:
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
    >
    # Набір попереджень для MSVC та clang-cl
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4
        /permissive-
        /Zc:__cplusplus
        /Zc:preprocessor
    >
)
