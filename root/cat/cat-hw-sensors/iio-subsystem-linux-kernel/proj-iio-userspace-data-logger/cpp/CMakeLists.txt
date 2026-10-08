cmake_minimum_required(VERSION 3.14)
project(iio_inertial_sensor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_library(LIBIIO_LIBRARIES NAMES iio REQUIRED)
find_path(LIBIIO_INCLUDE_DIRS NAMES iio.h REQUIRED)

add_executable(iio_sensor_app
    main.cpp
    iio_device.cpp
    iio_device.hpp
)

target_include_directories(iio_sensor_app PRIVATE ${LIBIIO_INCLUDE_DIRS})
target_link_libraries(iio_sensor_app PRIVATE ${LIBIIO_LIBRARIES})
