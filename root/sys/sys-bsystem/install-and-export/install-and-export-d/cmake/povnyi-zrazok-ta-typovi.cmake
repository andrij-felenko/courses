cmake_minimum_required(VERSION 3.20)
project(DataEngine VERSION 2.1.0 LANGUAGES CXX)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

# 1. Оголошення цілі бібліотеки
add_library(data_engine src/engine.cpp)
add_library(DataEngine::engine ALIAS data_engine)

target_compile_features(data_engine PUBLIC cxx_std_20)

target_include_directories(data_engine
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# 2. Інсталяція двійкових артефактів та заголовків
install(TARGETS data_engine
    EXPORT DataEngineTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)

# 3. Експорт набору цілей
set(DATAENGINE_CONFIG_DIR "${CMAKE_INSTALL_LIBDIR}/cmake/DataEngine")

install(EXPORT DataEngineTargets
    FILE DataEngineTargets.cmake
    NAMESPACE DataEngine::
    DESTINATION ${DATAENGINE_CONFIG_DIR}
)

# 4. Генерація та встановлення файлів конфігурації
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/DataEngineConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/DataEngineConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/DataEngineConfig.cmake"
    INSTALL_DESTINATION ${DATAENGINE_CONFIG_DIR}
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/DataEngineConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/DataEngineConfigVersion.cmake"
    DESTINATION ${DATAENGINE_CONFIG_DIR}
)
