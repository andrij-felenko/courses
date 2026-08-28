target_sources(geometry_lib
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/geometry/point.hpp
            include/geometry/vector.hpp
    PRIVATE
        src/point.cpp
        src/vector.cpp
)
