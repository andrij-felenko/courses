set(WWW_SRC "${CMAKE_CURRENT_LIST_DIR}/www/index.html")
set(WWW_GZ "${CMAKE_CURRENT_BINARY_DIR}/index.html.gz")

# EMBED_FILES вимагає, щоб файл існував уже на етапі конфігурації, а не збірки,
# тому стискаємо сторінку саме тут. Python завжди є в оточенні ESP-IDF.
find_package(Python3 REQUIRED COMPONENTS Interpreter)

execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c
            "import gzip,sys; open(sys.argv[2],'wb').write(gzip.compress(open(sys.argv[1],'rb').read(), 9))"
            "${WWW_SRC}" "${WWW_GZ}"
    RESULT_VARIABLE WWW_GZ_RESULT)

if(NOT WWW_GZ_RESULT EQUAL 0)
    message(FATAL_ERROR "Не вдалося стиснути ${WWW_SRC}")
endif()

# Правка index.html має перезапускати конфігурацію, інакше у прошивку
# мовчки поїде попередній стиснений образ сторінки.
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${WWW_SRC}")

# Ім'я символа лінкер виводить із імені файла: index.html.gz дає
# _binary_index_html_gz_start та _binary_index_html_gz_end.
idf_component_register(
    SRCS "app_main.c"
         "wifi_ap.c"
         "dns_server.c"
         "http_server.c"
         "config_store.c"
         "deferred_reboot.c"
    INCLUDE_DIRS "."
    REQUIRES esp_wifi esp_netif esp_http_server nvs_flash json
    EMBED_FILES "${WWW_GZ}")
