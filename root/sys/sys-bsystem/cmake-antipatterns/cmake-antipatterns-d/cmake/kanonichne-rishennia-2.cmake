# ✅ Канонічний Modern CMake: ізоляція через властивості цілі
add_library(network_engine STATIC
    src/socket.cpp
    src/packet.cpp
)

target_include_directories(network_engine
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src/internal
)

target_compile_definitions(network_engine
    PRIVATE
        INTERNAL_BUFFER_SIZE=4096
    PUBLIC
        NET_ENGINE_ACTIVE=1
)

target_link_libraries(network_engine
    PUBLIC
        Threads::Threads
)
