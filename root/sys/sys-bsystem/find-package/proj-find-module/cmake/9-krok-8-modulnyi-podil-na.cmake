# Створення цілі окремого компонента FastCodec::Parallel
if(FastCodec_PARALLEL_FOUND AND NOT TARGET FastCodec::Parallel)
    add_library(FastCodec::Parallel INTERFACE IMPORTED)
    target_link_libraries(FastCodec::Parallel INTERFACE 
        FastCodec::FastCodec 
        Threads::Threads
    )
    target_compile_definitions(FastCodec::Parallel INTERFACE 
        FASTCODEC_PARALLEL_ENABLED=1
    )
endif()
