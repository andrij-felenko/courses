if(CMAKE_CROSSCOMPILING AND NOT TARGET host_table_gen)
    set(HOST_BUILD_DIR "${CMAKE_BINARY_DIR}/host-tools")
    
    # Виклик конфігурації хостового бінарника рідним компілятором
    execute_process(
        COMMAND "${CMAKE_COMMAND}" -S "${CMAKE_CURRENT_SOURCE_DIR}/tools"
                                   -B "${HOST_BUILD_DIR}"
        RESULT_VARIABLE res
    )
    if(res)
        message(FATAL_ERROR "Помилка конфігурації хостових інструментів")
    endif()

    # Збірка інструмента під хост
    execute_process(
        COMMAND "${CMAKE_COMMAND}" --build "${HOST_BUILD_DIR}" --target table_gen
        RESULT_VARIABLE res
    )
    if(res)
        message(FATAL_ERROR "Помилка компіляції хостового table_gen")
    endif()

    add_executable(table_gen IMPORTED GLOBAL)
    set_target_properties(table_gen PROPERTIES
        IMPORTED_LOCATION "${HOST_BUILD_DIR}/table_gen${CMAKE_EXECUTABLE_SUFFIX}"
    )
endif()
