idf_component_register(
    SRCS "main.c"
    INCLUDE_DIRS "."
    REQUIRES nvs_flash driver ieee802154 esp_hw_support esp_adc esp_timer
)
