cmake_minimum_required(VERSION 3.20)
project(CalcApp VERSION 1.0.0 LANGUAGES CXX)

# Встановлюємо сучасний стандарт C++
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Підключаємо стандартні конвенції розміщення каталогів
include(GNUInstallDirs)

# 1. Спільна динамічна бібліотека обчислень
add_library(calc SHARED src/math_ops.cpp)
target_include_directories(calc PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
set_target_properties(calc PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION 1
)

# 2. Виконуваний файл консольного клієнта
add_executable(calc_cli src/main.cpp)
target_link_libraries(calc_cli PRIVATE calc)

# Передаємо цільовий абсолютний шлях до ресурсів у константи компілятора
target_compile_definitions(calc_cli PRIVATE
    APP_DATADIR="${CMAKE_INSTALL_FULL_DATADIR}/calcapp"
)

# 3. Налаштування RPATH для встановленого двійкового файлу
# Використовуємо $ORIGIN для відносного пошуку lib/ відносно bin/
set_target_properties(calc_cli PROPERTIES
    INSTALL_RPATH "$ORIGIN/../${CMAKE_INSTALL_LIBDIR}"
    BUILD_WITH_INSTALL_RPATH FALSE
)

# 4. Правила встановлення цілей та заголовків
install(TARGETS calc calc_cli
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(DIRECTORY include/calc
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(FILES assets/operations.json
    DESTINATION ${CMAKE_INSTALL_DATADIR}/calcapp
)
