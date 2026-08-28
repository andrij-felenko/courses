# Фрагмент CMakeLists.txt для вбудованої цілі
add_library(terrain_manager STATIC
    src/terrain_cache.c
    src/terrain_interpolator.c
)

target_include_directories(terrain_manager PUBLIC include)
target_compile_options(terrain_manager PRIVATE
    -mcpu=cortex-m7
    -mfpu=fpv5-d16
    -mfloat-abi=hard
    -O3
    -ffast-math
    -Wall
    -Wextra
    -Werror
)
