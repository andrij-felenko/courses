include(CMakePackageConfigHelpers)

# Створення файлу версії
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/MyAppConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

# Встановлення допоміжних файлів конфігурації у компонент Development
install(FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/MyAppConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/MyAppConfigVersion.cmake"
    DESTINATION lib/cmake/MyApp
    COMPONENT Development
)
