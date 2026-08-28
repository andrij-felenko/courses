# Перевірка наявності програми IWYU в системі
find_program(IWYU_TOOL_PATH NAMES include-what-you-use iwyu)

option(ENABLE_IWYU "Увімкнути автоматичний аудит заголовків через IWYU" OFF)

if(IWYU_TOOL_PATH AND ENABLE_IWYU)
    message(STATUS "IWYU знайдено: ${IWYU_TOOL_PATH}")
    
    # Формування аргументів командного рядка для аналізатора
    set(IWYU_COMMAND_LINE
        "${IWYU_TOOL_PATH}"
        "-Xiwyu" "--mapping_file=${CMAKE_CURRENT_SOURCE_DIR}/iwyu_mappings.imp"
        "-Xiwyu" "--max_line_length=120"
        "-Xiwyu" "--no_fwd_decls"
        "-Xiwyu" "--verbose=1"
    )
    
    # Прив'язка аналізатора до бібліотеки
    set_target_properties(core_lib PROPERTIES
        CXX_INCLUDE_WHAT_YOU_USE "${IWYU_COMMAND_LINE}"
    )
endif()
