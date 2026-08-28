add_library(strict_warnings INTERFACE)

target_compile_options(strict_warnings INTERFACE
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4
        /permissive-
        /Zc:__cplusplus
        /we4996
    >
    $<$<OR:$<CXX_COMPILER_ID:GNU>,$<CXX_COMPILER_ID:Clang>>:
        -Wall
        -Wextra
        -Wpedantic
        -Wdeprecated
        -Werror=deprecated-declarations
        -Wsuggest-override
    >
)

# Підключення до цільових бібліотек
target_link_libraries(core_engine PRIVATE strict_warnings)
