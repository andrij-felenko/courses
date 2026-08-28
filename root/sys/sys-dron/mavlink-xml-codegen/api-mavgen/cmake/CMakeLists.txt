find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(MAVLINK_XML ${CMAKE_SOURCE_DIR}/modules/mavlink/message_definitions/v1.0/common.xml)
set(MAVLINK_OUT ${CMAKE_BINARY_DIR}/generated/mavlink)

add_custom_command(
    OUTPUT  ${MAVLINK_OUT}/common/mavlink.h
    COMMAND ${Python3_EXECUTABLE} -m pymavlink.tools.mavgen
            --lang=C --wire-protocol=2.0
            --output=${MAVLINK_OUT} ${MAVLINK_XML}
    DEPENDS ${MAVLINK_XML}
    COMMENT "mavgen: C-кодек із common.xml")

add_custom_target(mavlink_headers DEPENDS ${MAVLINK_OUT}/common/mavlink.h)

add_library(mavlink INTERFACE)
add_dependencies(mavlink mavlink_headers)
target_include_directories(mavlink INTERFACE ${MAVLINK_OUT})
