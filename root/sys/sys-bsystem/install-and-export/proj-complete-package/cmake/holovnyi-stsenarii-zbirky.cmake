cmake_minimum_required(VERSION 3.20)
project(Hyperion
    VERSION 1.2.0
    DESCRIPTION "Виробнича модульна бібліотека телеметрії та обчислень"
    LANGUAGES CXX
)

# Задання обов'язкового стандарту C++20 для всіх цілей
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Підключення стандартних допоміжних модулів
include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

# Опція типу бібліотеки: за замовчуванням динамічна збірка
option(BUILD_SHARED_LIBS "Збирати спільні (shared) бібліотеки" ON)

# -----------------------------------------------------------------------------
# 1. Оголошення цілі Hyperion::core (скомпільована частина)
# -----------------------------------------------------------------------------
add_library(hyperion_core src/core.cpp)

# Створення локального псевдоніма для однакового синтаксису в тестах
add_library(Hyperion::core ALIAS hyperion_core)

# Розділення шляхів включення для дерева джерел та дерева інсталяції
target_include_directories(hyperion_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_compile_features(hyperion_core PUBLIC cxx_std_20)

# Якщо бібліотека збирається як статична, транслюємо макрос споживачам
if(NOT BUILD_SHARED_LIBS)
    target_compile_definitions(hyperion_core PUBLIC HYPERION_STATIC_DEFINE)
endif()

# -----------------------------------------------------------------------------
# 2. Оголошення цілі Hyperion::math (заголовочна частина)
# -----------------------------------------------------------------------------
add_library(hyperion_math INTERFACE)
add_library(Hyperion::math ALIAS hyperion_math)

target_include_directories(hyperion_math
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

target_compile_features(hyperion_math INTERFACE cxx_std_20)

# -----------------------------------------------------------------------------
# 3. Правила інсталяції двійкових артефактів та заголовків
# -----------------------------------------------------------------------------
install(TARGETS hyperion_core hyperion_math
    EXPORT HyperionTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Встановлення структури публічних файлів заголовків
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.hpp"
)

# -----------------------------------------------------------------------------
# 4. Генерація файла імпортованих цілей HyperionTargets.cmake
# -----------------------------------------------------------------------------
set(HYPERION_CONFIG_INSTALL_DIR "${CMAKE_INSTALL_LIBDIR}/cmake/Hyperion")

install(EXPORT HyperionTargets
    FILE HyperionTargets.cmake
    NAMESPACE Hyperion::
    DESTINATION ${HYPERION_CONFIG_INSTALL_DIR}
)

# -----------------------------------------------------------------------------
# 5. Генерація файлів конфігурації пакета та перевірки версій
# -----------------------------------------------------------------------------
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/HyperionConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfig.cmake"
    INSTALL_DESTINATION ${HYPERION_CONFIG_INSTALL_DIR}
)

# Інсталяція конфігураційних файлів поруч із HyperionTargets.cmake
install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/HyperionConfigVersion.cmake"
    DESTINATION ${HYPERION_CONFIG_INSTALL_DIR}
)
