cmake_minimum_required(VERSION 3.5)
project(LegacyCodec LANGUAGES C)

# Якщо головний проєкт задав CODEC_ENABLE_TESTS як звичайну змінну,
# за активної CMP0077 ця команда нічого не зробить і збереже OFF.
option(CODEC_ENABLE_TESTS "Build internal unit tests for legacy codec" ON)
option(CODEC_ENABLE_LOGGING "Enable verbose stderr logging" OFF)

add_library(legacy_codec STATIC codec.c)
target_include_directories(legacy_codec PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")

if(CODEC_ENABLE_LOGGING)
  target_compile_definitions(legacy_codec PRIVATE CODEC_VERBOSE=1)
endif()

if(CODEC_ENABLE_TESTS)
  message(STATUS "Legacy codec tests are ENABLED")
else()
  message(STATUS "Legacy codec tests are DISABLED by parent project")
endif()
