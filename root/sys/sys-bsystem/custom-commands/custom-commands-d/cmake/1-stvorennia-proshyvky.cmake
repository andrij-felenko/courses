add_executable(firmware src/main.cpp)

add_custom_command(
    TARGET firmware
    POST_BUILD
    COMMAND arm-none-eabi-objcopy -O binary
            "$<TARGET_FILE:firmware>"
            "$<TARGET_FILE_DIR:firmware>/firmware.bin"
    COMMAND arm-none-eabi-size "$<TARGET_FILE:firmware>"
    COMMENT "Створення двійкового образу firmware.bin та аналіз розміру пам'яті"
    VERBATIM
)
