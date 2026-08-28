cmake_minimum_required(VERSION 3.20...3.30)
project(SystemApp VERSION 2.4.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 1. Перевизначення опцій підпроєкту до виклику add_subdirectory.
# Завдяки політиці CMP0077 (NEW) підпроєкт не перезапише це значення у кеші.
set(CODEC_ENABLE_TESTS OFF)
set(CODEC_ENABLE_LOGGING ON)

# 2. Підключення легасі-підпроєкту.
# CMake автоматично створює ізольовану копію стека політик для каталогу third_party/legacy_codec.
add_subdirectory(third_party/legacy_codec)

# 3. Підключення власного модуля пошуку.
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
find_package(SensorEngine REQUIRED)

# 4. Головний виконуваний файл.
add_executable(system_app src/main.cpp)
target_link_libraries(system_app PRIVATE legacy_codec SensorEngine::SensorEngine)
