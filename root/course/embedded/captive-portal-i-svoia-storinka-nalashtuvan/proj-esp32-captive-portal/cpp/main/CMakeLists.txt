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

set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${WWW_SRC}")

idf_component_register(
    SRCS "main.cpp"
         "portal/soft_ap.cpp"
         "portal/dns_catch_all.cpp"
         "portal/http_portal.cpp"
         "portal/credential_store.cpp"
    INCLUDE_DIRS "."
    REQUIRES esp_wifi esp_netif esp_http_server nvs_flash json
    EMBED_FILES "${WWW_GZ}")

# std::expected і монадичні операції над ним живуть у бібліотеці C++23.
target_compile_options(${COMPONENT_LIB} PRIVATE
    $<$<COMPILE_LANGUAGE:CXX>:-std=gnu++23>)
