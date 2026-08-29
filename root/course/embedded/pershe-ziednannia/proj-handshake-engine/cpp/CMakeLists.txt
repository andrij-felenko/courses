cmake_minimum_required(VERSION 3.16)
project(gcs_handshake CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Тека, у якій лежить mavlink/v2.0/common/mavlink.h (вивід mavgenerate.py).
set(MAVLINK_INCLUDE_DIR "/usr/local/include" CACHE PATH "Заголовки MAVLink v2")

find_package(Threads REQUIRED)

add_executable(gcs_handshake main.cpp handshake_engine.cpp udp_link.cpp)
target_include_directories(gcs_handshake PRIVATE ${MAVLINK_INCLUDE_DIR})
target_link_libraries(gcs_handshake PRIVATE Threads::Threads)
