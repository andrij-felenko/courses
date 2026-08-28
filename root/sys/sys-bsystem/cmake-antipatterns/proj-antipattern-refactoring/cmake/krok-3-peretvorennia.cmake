function(imgproc_add_filter_metadata target_name)
    cmake_parse_arguments(ARG "" "STAGE" "" ${ARGN})
    
    # Змінна temp_meta_dir є строго локальною для стек-фрейму цієї функції
    set(temp_meta_dir "${CMAKE_CURRENT_BINARY_DIR}/meta_${target_name}")
    
    add_custom_target("${target_name}_metadata"
        COMMAND ${CMAKE_COMMAND} -E make_directory "${temp_meta_dir}"
        COMMENT "Формування метаданих фільтра для ${target_name}"
        VERBATIM
    )
endfunction()
