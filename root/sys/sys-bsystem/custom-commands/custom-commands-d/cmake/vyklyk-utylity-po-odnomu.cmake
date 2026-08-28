file(GLOB_RECURSE PROTO_FILES "proto/*.proto")

set(GEN_SOURCES "")
set(GEN_HEADERS "")
foreach(p IN LISTS PROTO_FILES)
    cmake_path(GET p STEM name)
    list(APPEND GEN_SOURCES "${CMAKE_CURRENT_BINARY_DIR}/gen/${name}.pb.cc")
    list(APPEND GEN_HEADERS "${CMAKE_CURRENT_BINARY_DIR}/gen/${name}.pb.h")
endforeach()

add_custom_command(
    OUTPUT ${GEN_SOURCES} ${GEN_HEADERS}
    COMMAND protoc --cpp_out="${CMAKE_CURRENT_BINARY_DIR}/gen"
                   -I "${CMAKE_CURRENT_SOURCE_DIR}/proto"
                   ${PROTO_FILES}
    DEPENDS ${PROTO_FILES}
    COMMENT "Пакетна генерація протоколів через protoc"
    VERBATIM
)
