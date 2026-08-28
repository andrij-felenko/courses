# Базова бібліотека зі стандартом C++11
add_library(math_core src/math.cpp)
target_compile_features(math_core PUBLIC cxx_std_11)

# Проміжний модуль, що використовує C++17 для внутрішньої оптимізації
add_library(network_engine src/net.cpp)
target_compile_features(network_engine PRIVATE cxx_std_17)
target_compile_features(network_engine INTERFACE cxx_std_11)
target_link_libraries(network_engine PRIVATE math_core)

# Головний бінарник на C++20
add_executable(app main.cpp)
target_compile_features(app PRIVATE cxx_std_20)
target_link_libraries(app PRIVATE network_engine)
