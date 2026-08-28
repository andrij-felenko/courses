# 1. Завантаження вихідного коду з репозиторію GitHub із перевіркою SHA-512
vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO example-org/fast-telemetry
    REF "v${VERSION}"
    SHA512 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    HEAD_REF main
    PATCHES
        patches/0001-fix-arm-affinity.patch
)

# 2. Перевірка обраних опцій (features)
vcpkg_check_features(
    OUT_FEATURE_OPTIONS FEATURE_OPTIONS
    FEATURES
        compression ENABLE_ZLIB_COMPRESSION
)

# 3. Конфігурація системи збірки CMake через хелпери vcpkg
vcpkg_cmake_configure(
    SOURCE_PATH "${SOURCE_PATH}"
    OPTIONS
        -DFAST_TELEMETRY_BUILD_TESTS=OFF
        -DFAST_TELEMETRY_BUILD_EXAMPLES=OFF
        ${FEATURE_OPTIONS}
)

# 4. Компіляція та встановлення в буфер packages/fast-telemetry_<triplet>/
vcpkg_cmake_install()

# 5. Нормалізація структури CMake-конфігурацій
# Переносить fast-telemetryConfig.cmake з lib/cmake/ у share/fast-telemetry/
vcpkg_cmake_config_fixup(
    PACKAGE_NAME fast-telemetry
    CONFIG_PATH lib/cmake/fast-telemetry
)

# 6. Очищення дубльованих файлів заголовків у налагоджувальній конфігурації
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/include")
file(REMOVE_RECURSE "${CURRENT_PACKAGES_DIR}/debug/share")

# 7. Збереження ліцензійного файлу (обов'язкова вимога vcpkg)
vcpkg_install_copyright(
    FILE_LIST "${SOURCE_PATH}/LICENSE"
)
