cmake_minimum_required(VERSION 3.20)
project(ingest_pipeline CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# std::jthread живе в потоках ОС — без Threads збірка не злінкується.
find_package(Threads REQUIRED)

add_executable(ingest
    main.cpp
    wire_format.cpp
    pipeline.cpp
)
target_link_libraries(ingest PRIVATE Threads::Threads)
