add_library(core_engine STATIC src/engine.cpp)

# 1. Керування стандартом (додасть -std=c++20 або /std:c++20)
target_compile_features(core_engine PUBLIC cxx_std_20)
set_target_properties(core_engine PROPERTIES
    CXX_EXTENSIONS OFF  # вимкне gnu++ розширення на користь чистого ISO C++
)

# 2. Керування видимістю (додасть -fvisibility=hidden на GCC/Clang)
set_target_properties(core_engine PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
)

# 3. Попередження як помилки (додасть -Werror або /WX)
set_target_properties(core_engine PROPERTIES
    COMPILE_WARNING_AS_ERROR ON
)
