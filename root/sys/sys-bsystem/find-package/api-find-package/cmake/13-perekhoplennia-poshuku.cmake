# Реєстрація постачальника залежностей (викликається у файлі тулчейна)
cmake_language(SET_DEPENDENCY_PROVIDER my_custom_provider
               SUPPORTED_METHODS FIND_PACKAGE)

function(my_custom_provider method package_name)
    if(method STREQUAL "FIND_PACKAGE")
        message(STATUS "Перехоплено пошук пакета: ${package_name}")
        # Тут можна автоматично завантажити джерела через FetchContent
        # або підтягнути бінарні пакети через зовнішній менеджер
    endif()
endfunction()
