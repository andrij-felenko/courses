add_library(project_warnings INTERFACE)

target_compile_options(project_warnings INTERFACE
    $<$<CXX_COMPILER_ID:GNU,Clang>:
        -Wall
        -Wextra
        -Wpedantic
        -Wconversion
        -Wshadow
    >
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4
        /permissive-
    >
)

# Застосовуємо прапорці лише до власних цілей
add_library(core_engine STATIC engine.cpp)
target_link_libraries(core_engine PRIVATE project_warnings)

add_executable(game_server main.cpp)
target_link_libraries(game_server PRIVATE project_warnings)
