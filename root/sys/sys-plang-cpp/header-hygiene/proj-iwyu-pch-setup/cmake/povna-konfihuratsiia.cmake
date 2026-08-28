cmake_minimum_required(VERSION 3.20)
project(EngineCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Створення статичної бібліотеки ядра
add_library(core_lib STATIC
    src/UserSession.cpp
    src/Database.cpp
    src/Network.cpp
)

target_include_directories(core_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Оголошення попередньо скомпільованих заголовків для бібліотеки
target_precompile_headers(core_lib
    PRIVATE
        # Контейнери та утиліти STL
        <vector>
        <string>
        <string_view>
        <memory>
        <unordered_map>
        <map>
        <algorithm>
        <chrono>
        <functional>
        <optional>
        <variant>
        # Сторонні важкі заголовки
        <fmt/format.h>
)

# Використання спільного PCH між кількома цілями (REUSE_FROM)
add_executable(engine_app
    src/main.cpp
)

target_link_libraries(engine_app PRIVATE core_lib)

# Повторне використання вже згенерованого PCH від core_lib для уникнення дублювання
target_precompile_headers(engine_app REUSE_FROM core_lib)

# Тестовий бінарник, який також повторно використовує базовий PCH
add_executable(engine_tests
    tests/test_main.cpp
    tests/test_session.cpp
)
target_link_libraries(engine_tests PRIVATE core_lib)
target_precompile_headers(engine_tests REUSE_FROM core_lib)
