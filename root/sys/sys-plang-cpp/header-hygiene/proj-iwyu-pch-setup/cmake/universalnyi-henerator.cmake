# Функція генерації автономних перевірочних одиниць
function(add_header_self_containment_test target_name header_files)
    set(test_sources "")
    
    foreach(hdr_path IN LISTS header_files)
        get_filename_component(hdr_base "${hdr_path}" NAME_WE)
        set(gen_cpp "${CMAKE_CURRENT_BINARY_DIR}/header_checks/test_${hdr_base}.cpp")
        
        # Генерація ізольованого файлу трансляції
        file(WRITE "${gen_cpp}"
            "// Автоматичний синтетичний тест самодостатності\n"
            "#include \"${hdr_path}\"\n"
            "int main() { return 0; }\n"
        )
        list(APPEND test_sources "${gen_cpp}")
    endforeach()

    # Створення тестового таргета
    add_executable(${target_name}_verify_headers EXCLUDE_FROM_ALL ${test_sources})
    target_link_libraries(${target_name}_verify_headers PRIVATE ${target_name})
    
    # Додавання кастомної команди до глобального списку перевірок
    add_custom_target(check_headers DEPENDS ${target_name}_verify_headers)
endfunction()
