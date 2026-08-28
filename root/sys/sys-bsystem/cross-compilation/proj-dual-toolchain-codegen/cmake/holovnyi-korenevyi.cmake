cmake_minimum_required(VERSION 3.20)
project(FirmwareProject LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(GENERATED_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(GENERATED_CRC_SRC "${GENERATED_DIR}/crc32_table.cpp")
file(MAKE_DIRECTORY "${GENERATED_DIR}")

if(CMAKE_CROSSCOMPILING)
    # Крос-компіляція: збираємо автономний нативний підпроєкт для хоста
    include(ExternalProject)

    set(HOST_TOOLS_DIR "${CMAKE_CURRENT_BINARY_DIR}/host_tools-build")
    set(HOST_TABLE_GEN_EXE "${HOST_TOOLS_DIR}/bin/table_gen")

    ExternalProject_Add(host_tools_subproject
        SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/host_tools"
        BINARY_DIR "${HOST_TOOLS_DIR}"
        INSTALL_DIR "${HOST_TOOLS_DIR}"
        CMAKE_ARGS
            -DCMAKE_INSTALL_PREFIX=${HOST_TOOLS_DIR}
            # Критично: скидаємо файл тулчейна для нативного складання хостом
            -DCMAKE_TOOLCHAIN_FILE=
            -DCMAKE_BUILD_TYPE=Release
        BUILD_BYPRODUCTS "${HOST_TABLE_GEN_EXE}"
    )

    # Оголошуємо імпортовану виконувану ціль
    add_executable(generator_tool IMPORTED GLOBAL)
    set_target_properties(generator_tool PROPERTIES
        IMPORTED_LOCATION "${HOST_TABLE_GEN_EXE}"
    )
    add_dependencies(generator_tool host_tools_subproject)
else()
    # Нативна збірка (хост і ціль однакові): збираємо напряму
    add_subdirectory(host_tools)
    add_executable(generator_tool ALIAS table_gen)
endif()

# Команда запуску хостового генератора
add_custom_command(
    OUTPUT "${GENERATED_CRC_SRC}"
    COMMAND generator_tool "${GENERATED_CRC_SRC}"
    DEPENDS generator_tool
    COMMENT "Генерація CRC-32 таблиці нативною утилітою хоста..."
    VERBATIM
)

# Цільовий бінарник прошивки під цільову архітектуру
add_executable(firmware_app
    src/main.cpp
    "${GENERATED_CRC_SRC}"
)

target_include_directories(firmware_app PRIVATE "${GENERATED_DIR}")
