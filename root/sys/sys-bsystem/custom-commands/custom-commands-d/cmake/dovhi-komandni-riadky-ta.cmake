# 1. Формування файлу відповідей на етапі генерації CMake
set(RSP_FILE "${CMAKE_CURRENT_BINARY_DIR}/tool_args.rsp")

file(GENERATE
    OUTPUT "${RSP_FILE}"
    CONTENT "$<JOIN:$<TARGET_PROPERTY:my_lib,INCLUDE_DIRECTORIES>,\n>"
)

# 2. Передача файлу відповідей утиліті через синтаксис @file
add_custom_command(
    OUTPUT "${GEN_DIR}/bundle.cpp"
    COMMAND tool_packer "@${RSP_FILE}" --out "${GEN_DIR}/bundle.cpp"
    DEPENDS "${RSP_FILE}" "${INPUT_ASSETS}"
    COMMENT "Пакування ресурсів через файл відповідей"
    VERBATIM
)
