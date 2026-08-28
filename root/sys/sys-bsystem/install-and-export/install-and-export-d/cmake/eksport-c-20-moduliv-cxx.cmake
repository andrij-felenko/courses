# Оголошення бібліотеки з C++20 модулем
add_library(mylib_modern)
target_sources(mylib_modern
    PUBLIC
        FILE_SET CXX_MODULES
        BASE_DIRS src
        FILES src/core_module.cppm
)

install(TARGETS mylib_modern
    EXPORT MyLibModernTargets
    FILE_SET CXX_MODULES DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/MyLibModern/modules
)

install(EXPORT MyLibModernTargets
    FILE MyLibModernTargets.cmake
    NAMESPACE MyLib::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/MyLibModern
    CXX_MODULES_DIRECTORY modules
)
