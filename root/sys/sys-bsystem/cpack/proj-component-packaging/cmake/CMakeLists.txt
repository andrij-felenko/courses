cmake_minimum_required(VERSION 3.22)
project(telemetry
    VERSION 1.4.2
    DESCRIPTION "High-performance telemetry aggregation service"
    HOMEPAGE_URL "https://github.com/example/telemetry"
    LANGUAGES C CXX
)

include(GNUInstallDirs)

# ── 1. Збірка спільної динамічної бібліотеки ─────────────────────────────────
add_library(telemetry_lib SHARED
    src/metrics.c
)
set_target_properties(telemetry_lib PROPERTIES
    OUTPUT_NAME "telemetry"
    SOVERSION 1
    VERSION 1.4.2
)
target_include_directories(telemetry_lib PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# ── 2. Збірка демона ──────────────────────────────────────────────────────────
add_executable(telemetryd src/daemon.c)
target_link_libraries(telemetryd PRIVATE telemetry_lib)

# ── 3. Правила інсталяції з розподілом за компонентами ────────────────────────

# Компонент Runtime: бінарник демона та версіонована бібліотека
install(TARGETS telemetryd telemetry_lib
    EXPORT TelemetryTargets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT Runtime
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT Runtime
    NAMELINK_COMPONENT Development
)

# Системний юніт systemd також належить компоненту Runtime
install(FILES packaging/telemetryd.service
    DESTINATION /lib/systemd/system
    COMPONENT Runtime
)

# Компонент Development: публічні заголовки
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    COMPONENT Development
)

# Експорт цілей CMake для зовнішніх розробників (find_package(Telemetry))
install(EXPORT TelemetryTargets
    NAMESPACE Telemetry::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Telemetry
    COMPONENT Development
)

# Компонент Documentation: документація
install(FILES README.md
    DESTINATION ${CMAKE_INSTALL_DOCDIR}
    COMPONENT Documentation
)

# ── 4. Налаштування CPack ────────────────────────────────────────────────────
set(CPACK_PACKAGE_NAME "telemetry")
set(CPACK_PACKAGE_VENDOR "Acme Telemetry Systems")
set(CPACK_PACKAGE_CONTACT "ops@telemetry.example.com")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Lightweight system telemetry daemon")
set(CPACK_PACKAGING_INSTALL_PREFIX "/usr")

# Активація покомпонентної генерації для DEB та RPM
set(CPACK_DEBIAN_COMPONENT_INSTALL ON)
set(CPACK_RPM_COMPONENT_INSTALL ON)

# Специфікація DEB генератора
set(CPACK_DEBIAN_PACKAGE_SECTION "utils")
set(CPACK_DEBIAN_PACKAGE_SHLIBDEPS ON) # Автоматичний аналіз DT_NEEDED через dpkg-shlibdeps
set(CPACK_DEBIAN_RUNTIME_PACKAGE_CONTROL_EXTRA "${CMAKE_CURRENT_SOURCE_DIR}/packaging/postinst.sh")
set(CPACK_COMPONENT_DEVELOPMENT_DEPENDS "Runtime") # Пакет dev залежить від runtime

# Специфікація RPM генератора
set(CPACK_RPM_PACKAGE_LICENSE "Apache-2.0")
set(CPACK_RPM_PACKAGE_GROUP "Applications/System")
set(CPACK_RPM_PACKAGE_AUTOREQ YES)
set(CPACK_RPM_RUNTIME_POST_INSTALL_SCRIPT_FILE "${CMAKE_CURRENT_SOURCE_DIR}/packaging/postinst.sh")

# Підключення модуля CPack
include(CPack)
include(CPackComponent)

# Декларація метаданих компонентів для графічних інсталяторів
cpack_add_component(Runtime
    DISPLAY_NAME "Telemetry Service & Daemon"
    DESCRIPTION "Contains the executable daemon, shared library, and systemd service"
    REQUIRED
)

cpack_add_component(Development
    DISPLAY_NAME "C/C++ SDK & CMake Configs"
    DESCRIPTION "Header files and CMake target exports for building applications"
    DEPENDS Runtime
)

cpack_add_component(Documentation
    DISPLAY_NAME "User Documentation"
    DESCRIPTION "Manuals and quick-start guides"
    DISABLED
)
