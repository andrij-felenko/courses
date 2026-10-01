cmake_minimum_required(VERSION 3.16)

# Підключення системного сценарію збірки ESP-IDF
include($ENV{IDF_PATH}/tools/cmake/project.cmake)

# Визначення назви проєкту автономного сенсорного вузла ESP32-C6
project(esp32c6_sensor_node)
