add_library(image_processor STATIC
    src/image.cpp
    src/png_loader.cpp
    src/simd_internal/sse_kernels.cpp
)

# Каталог із закритими заголовками бачить лише сама бібліотека
target_include_directories(image_processor PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/simd_internal
)

# Прапорець компілятора діє лише на файли image.cpp, png_loader.cpp тощо
target_compile_options(image_processor PRIVATE
    -Werror=uninitialized
)

# libpng лінкується всередину, але її заголовки не експортуються назовні
target_link_libraries(image_processor PRIVATE
    PNG::PNG
)
