add_library(core_framework STATIC core.cpp utils.cpp)

# Внутрішній PCH прискорює лише збірку файлів самої бібліотеки
target_precompile_headers(core_framework PRIVATE
    <vector>
    <string>
    <memory>
    "src/internal_pch.h"
)

# Публічний PCH примусово підключається до кожного споживача
target_precompile_headers(core_framework PUBLIC
    <algorithm>
    <chrono>
)
