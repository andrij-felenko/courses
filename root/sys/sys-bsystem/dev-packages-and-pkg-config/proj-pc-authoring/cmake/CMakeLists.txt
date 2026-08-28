# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(geomcalc VERSION 1.2.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 23)

include(GNUInstallDirs)

# Пошук внутрішньої залежності zlib
find_package(ZLIB REQUIRED)

# Створення бібліотеки (підтримує збірку як SHARED, так і STATIC через BUILD_SHARED_LIBS)
add_library(geomcalc
    src/geomcalc.c
    src/geomcalc.cpp
)

target_include_directories(geomcalc PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_link_libraries(geomcalc PRIVATE
    ZLIB::ZLIB
    m # Підключення libm для Unix
)

# Генерація файлу метаданих geomcalc.pc
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/geomcalc.pc.in"
    "${CMAKE_CURRENT_BINARY_DIR}/geomcalc.pc"
    @ONLY
)

# Правила інсталяції бінарних файлів та заголовків
install(TARGETS geomcalc
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES include/geomcalc.h include/geomcalc.hpp
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Інсталяція згенерованого .pc файлу в каталог pkgconfig
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/geomcalc.pc"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig"
)
