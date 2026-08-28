# Створюємо ціль бібліотеки з явним списком сирців
add_library(imgproc STATIC
    src/filter.cpp
    src/internal_simd.cpp
)

# Оголошуємо псевдонім у просторі імен для внутрішніх споживачів
add_library(ImageProcessor::imgproc ALIAS imgproc)

# Задаємо вимогу до стандарту мови C++
target_compile_features(imgproc PUBLIC cxx_std_17)

# Розподіляємо видимість шляхів заголовків
target_include_directories(imgproc
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Приватний макрос, потрібний лише самій бібліотеці
target_compile_definitions(imgproc
    PRIVATE
        IMGPROC_EXPORTS
)

# Компіляторо-незалежні прапорці діагностики
target_compile_options(imgproc PRIVATE
    $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:AppleClang>,$<CXX_COMPILER_ID:GNU>>:
        -Wall -Wextra -Wpedantic -Wconversion
    >
    $<$<CXX_COMPILER_ID:MSVC>:
        /W4 /permissive-
    >
)

# Підключення AddressSanitizer через властивості цілі
if(IMGPROC_ENABLE_ASAN)
    target_compile_options(imgproc PRIVATE
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined -fno-omit-frame-pointer>
    )
    target_link_options(imgproc PUBLIC
        $<$<OR:$<CXX_COMPILER_ID:Clang>,$<CXX_COMPILER_ID:GNU>>:-fsanitize=address,undefined>
    )
endif()

# Підключення OpenMP як імпортованої цілі
if(IMGPROC_ENABLE_OPENMP)
    find_package(OpenMP REQUIRED)
    target_link_libraries(imgproc PUBLIC OpenMP::OpenMP_CXX)
endif()
