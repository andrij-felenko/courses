add_library(img img.cpp resize.cpp)
add_library(img::img ALIAS img)

target_include_directories(img PUBLIC include PRIVATE src)
target_compile_definitions(img PUBLIC IMG_SIMD)
target_compile_features(img PUBLIC cxx_std_17)
target_link_libraries(img PRIVATE Threads::Threads)
set_property(TARGET img APPEND PROPERTY COMPILE_OPTIONS -Wall -Wextra)

set_target_properties(img PROPERTIES
    OUTPUT_NAME imgcore
    VERSION 1.4.2
    SOVERSION 1
    POSITION_INDEPENDENT_CODE ON
    EXPORT_NAME img
    FOLDER "libs")

get_target_property(kind img TYPE)
get_property(pic_set TARGET img PROPERTY POSITION_INDEPENDENT_CODE SET)
message(STATUS "${kind}, PIC задано явно: ${pic_set}")
# -- STATIC_LIBRARY, PIC задано явно: 1
