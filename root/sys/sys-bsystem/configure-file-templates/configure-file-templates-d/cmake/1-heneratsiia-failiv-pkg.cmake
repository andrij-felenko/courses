# Генерація файлу для pkg-config
include(GNUInstallDirs)
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/libdiag.pc.in"
    "${CMAKE_CURRENT_BINARY_DIR}/libdiag.pc"
    @ONLY
)

install(FILES "${CMAKE_CURRENT_BINARY_DIR}/libdiag.pc"
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/pkgconfig"
)
