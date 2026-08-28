# Публічні заголовки потрібні і файлам реалізації, і споживачам
target_include_directories(image_processor PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Макрос змінює ABI структури ImageBuffer — він має бути ідентичним скрізь
target_compile_definitions(image_processor PUBLIC
    IMG_COLOR_DEPTH_16BIT=1
)

# Оскільки тип Matrix3x3 присутній у відкритому заголовку, залежність має бути PUBLIC
target_link_libraries(image_processor PUBLIC
    linear_math
)
