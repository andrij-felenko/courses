# components/sensor_hub/CMakeLists.txt
idf_component_register(
    SRCS 
        "sensor_hub.c"
        "sensor_filter.c"
    INCLUDE_DIRS 
        "include"
    PRIV_INCLUDE_DIRS 
        "private_headers"
    REQUIRES 
        esp_timer
    PRIV_REQUIRES 
        driver
        nvs_flash
)
