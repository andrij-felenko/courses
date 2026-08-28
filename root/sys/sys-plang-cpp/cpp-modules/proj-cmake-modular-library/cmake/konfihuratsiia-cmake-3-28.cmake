cmake_minimum_required(VERSION 3.28)
project(ModularMatrixProject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Додавання модульної бібліотеки
add_library(matrix_lib)

# 1. Реєстрація інтерфейсних файлів модулів та розділів
target_sources(matrix_lib
    PUBLIC
        FILE_SET CXX_MODULES TYPE CXX_MODULES
        BASE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/src
        FILES
            src/matrix.cppm
            src/matrix_types.cppm
            src/matrix_ops.cppm
            src/matrix_storage.cppm
)

# 2. Додавання звичайних файлів реалізації (не потребують генерації експортного BMI)
target_sources(matrix_lib
    PRIVATE
        src/matrix_io.cpp
)

# Налаштування властивостей компілятора
target_compile_features(matrix_lib PUBLIC cxx_std_20)

# Створення клієнтської програми
add_executable(matrix_app app/main.cpp)

# Підключення модульної бібліотеки до клієнта
target_link_libraries(matrix_app PRIVATE matrix_lib)

# Налаштування встановлення бібліотеки для зовнішнього споживання
install(TARGETS matrix_lib
    EXPORT MatrixLibTargets
    FILE_SET CXX_MODULES DESTINATION include/modules
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

install(EXPORT MatrixLibTargets
    FILE MatrixLibConfig.cmake
    NAMESPACE math::
    DESTINATION lib/cmake/MatrixLib
    CXX_MODULES_DIRECTORY modules
)
