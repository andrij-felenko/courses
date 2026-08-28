// components/sensor_driver/test/test_sensor_driver.cpp (C++)
#include "unity.h"
#include "sensor_driver.hpp"

TEST_CASE("EnvironmentSensor RAII життєвий цикл та зчитування", "[sensor][cpp]") {
    sensors::EnvironmentSensor sensor;
    TEST_ASSERT_TRUE(sensor.is_ready());

    const auto result = sensor.read();
    TEST_ASSERT_TRUE(result.has_value());
    TEST_ASSERT_FLOAT_WITHIN(50.0f, 25.0f, result.value().temperature_celsius);
}
