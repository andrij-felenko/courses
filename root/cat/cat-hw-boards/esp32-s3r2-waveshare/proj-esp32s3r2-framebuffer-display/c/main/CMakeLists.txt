idf_component_register(
    SRCS "main.c" "psram_framebuffer.c"
    INCLUDE_DIRS "."
    REQUIRES esp_heap_caps esp_psram driver esp_driver_async_memcpy esp_mm
)
