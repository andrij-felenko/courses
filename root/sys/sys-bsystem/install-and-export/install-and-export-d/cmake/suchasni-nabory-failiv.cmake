# Сучасний стиль CMake 3.23+ із використанням FILE_SET
add_library(mylib_core src/core.cpp)

target_sources(mylib_core
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES include/mylib/core.hpp include/mylib/export.hpp
)

install(TARGETS mylib_core
    EXPORT MyLibTargets
    FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
