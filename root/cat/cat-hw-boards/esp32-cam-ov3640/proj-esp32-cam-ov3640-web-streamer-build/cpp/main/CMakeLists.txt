idf_component_register(
    SRCS "main.cpp" "ov3640_camera.cpp" "web_server.cpp"
    INCLUDE_DIRS "."
    REQUIRES esp32-camera esp_http_server esp_wifi nvs_flash esp_psram
)
