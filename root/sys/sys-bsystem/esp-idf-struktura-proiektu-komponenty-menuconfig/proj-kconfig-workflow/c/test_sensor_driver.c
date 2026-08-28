/* components/sensor_driver/test/test_sensor_driver.c (C) */
#include "unity.h"
#include "sensor_driver.h"

TEST_CASE("sensor_driver ініціалізація та деініціалізація", "[sensor]") {
    TEST_ASSERT_EQUAL(ESP_OK, sensor_driver_init());
    TEST_ASSERT_EQUAL(ESP_OK, sensor_driver_deinit());
}

TEST_CASE("sensor_driver зчитування даних без ініціалізації повертає помилку", "[sensor]") {
    sensor_reading_t reading;
    TEST_ASSERT_EQUAL(ESP_ERR_INVALID_STATE, sensor_driver_read(&reading));
}
