add_library(driver_legacy STATIC legacy.cpp)
set_target_properties(driver_legacy PROPERTIES
    INTERFACE_USE_64BIT_ADDR "OFF"
    COMPATIBLE_INTERFACE_BOOL USE_64BIT_ADDR
)

add_library(driver_modern STATIC modern.cpp)
set_target_properties(driver_modern PROPERTIES
    INTERFACE_USE_64BIT_ADDR "ON"
    COMPATIBLE_INTERFACE_BOOL USE_64BIT_ADDR
)

add_executable(controller main.cpp)
# ПОМИЛКА під час генерації: несумісні вимоги інтерфейсу!
target_link_libraries(controller PRIVATE driver_legacy driver_modern)
