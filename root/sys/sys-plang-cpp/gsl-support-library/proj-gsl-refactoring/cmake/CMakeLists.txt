# CMakeLists.txt: автоматична перевірка Core Guidelines у CI
find_program(CLANG_TIDY_EXE NAMES clang-tidy)
if(CLANG_TIDY_EXE)
    set(CMAKE_CXX_CLANG_TIDY 
        "${CLANG_TIDY_EXE};--config-file=${CMAKE_CURRENT_SOURCE_DIR}/.clang-tidy"
    )
endif()

# Прапорці MSVC C++ Core Check для Windows CI
if(MSVC)
    target_compile_options(telemetry_parser PRIVATE /analyze /analyze:ruleset "${CMAKE_CURRENT_SOURCE_DIR}/CppCoreCheckRules.ruleset")
endif()
