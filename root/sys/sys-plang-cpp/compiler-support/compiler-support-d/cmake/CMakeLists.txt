# Створення бібліотечної цілі
add_library(core_engine STATIC
    src/engine.cpp
    src/renderer.cpp
)

# Встановлення версії стандарту для конкретної цілі
set_target_properties(core_engine PROPERTIES
    CXX_STANDARD 20
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
)
