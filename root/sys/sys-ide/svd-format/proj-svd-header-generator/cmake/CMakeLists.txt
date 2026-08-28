# Автоматична генерація заголовків C99 та C++20 під час збирання проєкту
set(SVD_FILE "${CMAKE_CURRENT_SOURCE_DIR}/hw/stm32f407.svd")
set(GEN_C99_HEADER "${CMAKE_CURRENT_BINARY_DIR}/generated/stm32f407_cmsis.h")
set(GEN_CPP20_HEADER "${CMAKE_CURRENT_BINARY_DIR}/generated/stm32f407_hal.hpp")

add_custom_command(
    OUTPUT ${GEN_C99_HEADER} ${GEN_CPP20_HEADER}
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/svd_generator.py
            ${SVD_FILE} ${GEN_C99_HEADER} ${GEN_CPP20_HEADER}
    DEPENDS ${SVD_FILE} ${CMAKE_CURRENT_SOURCE_DIR}/tools/svd_generator.py
    COMMENT "Генерація типізованих системних заголовків із SVD..."
    VERBATIM
)

add_custom_target(generate_device_headers
    DEPENDS ${GEN_C99_HEADER} ${GEN_CPP20_HEADER}
)

add_executable(firmware_app
    src/main.cpp
    ${GEN_C99_HEADER}
    ${GEN_CPP20_HEADER}
)
target_include_directories(firmware_app PRIVATE ${CMAKE_CURRENT_BINARY_DIR}/generated)
add_dependencies(firmware_app generate_device_headers)
