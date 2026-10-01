# CMakeLists.txt для компонента main прошивки C (ESP8266 RTOS SDK / ESP-IDF)
# Описує джерела та залежності компонента для збірки тестового проєкту ESP-01/ESP-01S

idf_component_register(
    SRCS "user_main.c"
    INCLUDE_DIRS "."
    REQUIRES driver freertos esp_hw_support
)
