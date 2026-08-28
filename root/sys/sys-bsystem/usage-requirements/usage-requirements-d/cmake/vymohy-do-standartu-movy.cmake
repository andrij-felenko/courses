# Бібліотека template_helpers використовує концептуальні обмеження C++20 у відкритих заголовках
add_library(template_helpers INTERFACE)
target_compile_features(template_helpers INTERFACE cxx_std_20)

# Бібліотека legacy_engine використовує можливості C++17 у власних .cpp файлах
add_library(legacy_engine STATIC engine.cpp)
target_compile_features(legacy_engine PRIVATE cxx_std_17)

# Підключаємо template_helpers до legacy_engine
target_link_libraries(legacy_engine PUBLIC template_helpers)
