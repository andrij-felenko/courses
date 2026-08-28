cmake_minimum_required(VERSION 3.23)
project(proj CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(ProjectLibrary)

add_subdirectory(libs/core)
add_subdirectory(apps/tool)

get_property(all_libs GLOBAL PROPERTY PROJ_LIBRARIES)
message(STATUS "бібліотек у проєкті: ${all_libs}")
