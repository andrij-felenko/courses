# Помилковий наївний підхід при крос-компіляції
cmake_minimum_required(VERSION 3.20)
project(MyEmbeddedDevice C CXX)

# Допоміжна утиліта для генерації хеш-таблиці
add_executable(generate_lookup_tables tools/table_generator.c)

# Генерація файлу під час компіляції
add_custom_command(
    OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/lookup_table.c"
    COMMAND generate_lookup_tables -o "${CMAKE_CURRENT_BINARY_DIR}/lookup_table.c"
    DEPENDS generate_lookup_tables
)

# Цільова прошивка
add_executable(firmware main.c "${CMAKE_CURRENT_BINARY_DIR}/lookup_table.c")
