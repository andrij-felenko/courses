add_library(project_warnings INTERFACE)

target_compile_options(project_warnings INTERFACE
    # Прапорці для компіляторів сімейства Clang та GCC
    $<$<COMPILE_LANG_AND_ID:CXX,Clang,AppleClang,GNU>:
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
        -Wshadow
        -Wnon-virtual-dtor
        $<$<CONFIG:Debug>:-Og -g3>
        $<$<CONFIG:Release>:-O3>
    >
    # Прапорці для компілятора Microsoft Visual C++
    $<$<COMPILE_LANG_AND_ID:CXX,MSVC>:
        /W4
        /permissive-
        /w14242 # Попередження про неявне звуження типів
        /w14254
        $<$<CONFIG:Debug>:/Od /Zi>
        $<$<CONFIG:Release>:/O2>
    >
)
