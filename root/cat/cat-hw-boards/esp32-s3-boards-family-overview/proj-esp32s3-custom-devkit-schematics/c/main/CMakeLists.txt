idf_component_register(
    SRCS "main.c" "board_diag.c"
    INCLUDE_DIRS "."
    REQUIRES driver esp_driver_gpio esp_system vfs esp_rom
)
