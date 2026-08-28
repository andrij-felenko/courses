# Пошук виконуваного файлу Clang-Tidy
find_program(CLANG_TIDY_EXE NAMES "clang-tidy" "clang-tidy-17" "clang-tidy-16")

if(CLANG_TIDY_EXE)
    set_target_properties(core_engine PROPERTIES
        CXX_CLANG_TIDY "${CLANG_TIDY_EXE};--config-file=${CMAKE_CURRENT_SOURCE_DIR}/.clang-tidy;--warnings-as-errors=*"
    )
    message(STATUS "Clang-Tidy успішно підключено до таргету core_engine")
else()
    message(WARNING "clang-tidy не знайдено, перевірки modernize вимкнено")
endif()
