function(mediasync_validate_cache_configuration)
    # 1. Валідація вибору мережевого транспорту
    get_property(allowed_backends CACHE MEDIASYNC_NETWORK_BACKEND PROPERTY STRINGS)
    if(NOT MEDIASYNC_NETWORK_BACKEND IN_LIST allowed_backends)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: нечинне значення MEDIASYNC_NETWORK_BACKEND='${MEDIASYNC_NETWORK_BACKEND}'.\n"
            "Дозволені варіанти: ${allowed_backends}\n"
            "Зверніть увагу, що значення чутливі до регістру символів.")
    endif()

    # 2. Валідація рівня журналювання
    get_property(allowed_levels CACHE MEDIASYNC_LOG_LEVEL PROPERTY STRINGS)
    if(NOT MEDIASYNC_LOG_LEVEL IN_LIST allowed_levels)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: нечинне значення MEDIASYNC_LOG_LEVEL='${MEDIASYNC_LOG_LEVEL}'.\n"
            "Дозволені варіанти: ${allowed_levels}")
    endif()

    # 3. Перевірка числового діапазону для розміру кільцевого буфера
    # Буфер не може бути меншим за розмір одного мережевого MTU (1024 байти)
    # та більшим за 10 мегабайтів для запобігання вичерпанню RAM
    if(MEDIASYNC_RING_BUFFER_CAPACITY LESS 1024 OR MEDIASYNC_RING_BUFFER_CAPACITY GREATER 10485760)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: MEDIASYNC_RING_BUFFER_CAPACITY встановлено у ${MEDIASYNC_RING_BUFFER_CAPACITY}.\n"
            "Допустимий діапазон становить від 1024 до 10485760 байтів (1 КБ – 10 МБ).")
    endif()

    # 4. Перевірка мережевого порту метрик
    if(MEDIASYNC_METRICS_PORT LESS 1024 OR MEDIASYNC_METRICS_PORT GREATER 65535)
        message(FATAL_ERROR 
            "ПОМИЛКА КОНФІГУРАЦІЇ: MEDIASYNC_METRICS_PORT (${MEDIASYNC_METRICS_PORT}) "
            "має бути непривілейованим портом у діапазоні 1024–65535.")
    endif()

    message(STATUS "[mediasync] Усі параметри кешу пройшли успішну валідацію.")
endfunction()
