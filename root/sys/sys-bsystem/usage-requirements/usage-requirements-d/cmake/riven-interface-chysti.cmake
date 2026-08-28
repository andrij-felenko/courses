# Створення інтерфейсної бібліотеки (не збирає жодного .o/.obj файлу)
add_library(fast_json INTERFACE)

# Споживач отримує шлях до заголовків
target_include_directories(fast_json INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Споживач зобов'язаний збиратися у режимі C++20 або новішому
target_compile_features(fast_json INTERFACE
    cxx_std_20
)
