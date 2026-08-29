cmake_minimum_required(VERSION 3.20)
project(rule_engine_sil CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(sil_bench
    main.cpp
    rule_engine.cpp
    plant_model.cpp
    dry_run_sink.cpp
)
