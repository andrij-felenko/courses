add_library(my_lib STATIC src/core.cpp)

target_include_directories(my_lib PUBLIC
    # Під час власної збірки проєкту: згенеровані заголовки з каталогу збірки
    $<BUILD_INTERFACE:${GENERATED_DIR}/include>
    # Під час власної збірки: звичайні публічні заголовки з дерева джерел
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    # Після встановлення в систему через CMake install:
    $<INSTALL_INTERFACE:include>
)
