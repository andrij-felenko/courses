# Оголошення таргету бібліотеки
add_library(core_engine
    src/engine.cpp
    src/memory.cpp
)

# Вимога підтримки функціоналу C++17 для компіляції цієї бібліотеки
target_compile_features(core_engine PUBLIC cxx_std_17)

# Суворе закріплення стандарту та відключення нестандартних вендорних розширень
set_target_properties(core_engine PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
