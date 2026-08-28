# Визначення шляхів
set(I18N_CONFIG_DIR "${CMAKE_CURRENT_SOURCE_DIR}/i18n_sources")
set(I18N_OUTPUT_BIN "${CMAKE_CURRENT_BINARY_DIR}/locales.bin")
set(I18N_OUTPUT_C   "${CMAKE_CURRENT_BINARY_DIR}/locales_data.c")

# Користувацька команда генерації двійкового блобу
add_custom_command(
    OUTPUT "${I18N_OUTPUT_BIN}"
    COMMAND python3 "${CMAKE_CURRENT_SOURCE_DIR}/tools/i18n_pack.py"
            --input "${I18N_CONFIG_DIR}"
            --output "${I18N_OUTPUT_BIN}"
    DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tools/i18n_pack.py"
            "${I18N_CONFIG_DIR}/uk_UA.json"
            "${I18N_CONFIG_DIR}/en_US.json"
    COMMENT "Компіляція двійкових ресурсів локалізації .emb_i18n..."
)

# Перетворення бінарного файлу на об'єктний модуль через objcopy
add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/locales.o"
    COMMAND arm-none-eabi-objcopy
            -I binary -O elf32-littlearm -B arm
            --rename-section .data=.rodata.i18n,alloc,load,readonly,data,contents
            "${I18N_OUTPUT_BIN}" "${CMAKE_CURRENT_BINARY_DIR}/locales.o"
    DEPENDS "${I18N_OUTPUT_BIN}"
    COMMENT "Вбудовування locales.bin у секцію .rodata Flash-пам'яті..."
)

# Додавання об'єктного файлу до таргету прошивки
target_sources(${PROJECT_NAME}.elf PRIVATE
    src/main.c
    src/emb_i18n.c
    "${CMAKE_CURRENT_BINARY_DIR}/locales.o"
)
