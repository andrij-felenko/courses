# CMakeLists.txt
add_executable(pinmux_validator
    tools/pinmux_validator.cpp
)

add_custom_target(validate_board_pins
    COMMAND pinmux_validator
    COMMENT "Валідація карти пінів плати на апаратні колізії..."
    VERBATIM
)

# Прошивка залежить від успішного проходження валідації
add_dependencies(firmware_elf validate_board_pins)
