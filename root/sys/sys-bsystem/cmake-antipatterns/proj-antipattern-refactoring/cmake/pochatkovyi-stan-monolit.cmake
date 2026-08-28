# ❌ Застарілий CMakeLists.txt із комплексом антипатернів
cmake_minimum_required(VERSION 2.8)
project(image_processor)

# Антипатерн 1: Відсутність захисту від складання в сирцях
# Антипатерн 2: Ручна конкатенація глобальних прапорців компілятора
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17 -O3 -Wall")

# Антипатерн 3: Примусове знищення значень кешу
set(ENABLE_OPENMP ON CACHE BOOL "Увімкнути OpenMP" FORCE)

# Антипатерн 4: Збір файлів через GLOB_RECURSE
file(GLOB_RECURSE LIB_SOURCES "src/*.cpp")
file(GLOB_RECURSE APP_SOURCES "app/*.cpp")

# Антипатерн 5: Глобальні директиви каталогу та зашиті системні шляхи
include_directories(include src /usr/local/include)
add_definitions(-DIMGPROC_EXPORTS)
link_directories(/usr/local/lib)

# Антипатерн 6: Небезпечний макрос із витоком змінних
macro(add_filter_target TARGET_NAME)
    set(TEMP_DIR "generated_${TARGET_NAME}")
    add_custom_target("${TARGET_NAME}_meta" COMMAND echo "Building ${TARGET_NAME}")
endmacro()

add_filter_target(imgproc)

# Антипатерн 7: Глобальне лінкування без контролю видимості
add_library(imgproc STATIC ${LIB_SOURCES})
add_executable(imgcli ${APP_SOURCES})
link_libraries(pthread m)
target_link_libraries(imgcli imgproc)
