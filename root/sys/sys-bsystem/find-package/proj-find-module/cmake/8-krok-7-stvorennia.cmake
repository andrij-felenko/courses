if(FastCodec_FOUND AND NOT TARGET FastCodec::FastCodec)
    # Створюємо імпортовану ціль із типом UNKNOWN
    add_library(FastCodec::FastCodec UNKNOWN IMPORTED)

    # Прив'язуємо каталог заголовків як інтерфейсну вимогу
    set_target_properties(FastCodec::FastCodec PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES "${FastCodec_INCLUDE_DIR}"
    )

    # Прив'язуємо Release бінарний файл, якщо він є
    if(FastCodec_LIBRARY_RELEASE)
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            IMPORTED_CONFIGURATIONS RELEASE)
        set_target_properties(FastCodec::FastCodec PROPERTIES
            IMPORTED_LOCATION_RELEASE "${FastCodec_LIBRARY_RELEASE}"
        )
    endif()

    # Прив'язуємо Debug бінарний файл, якщо він є
    if(FastCodec_LIBRARY_DEBUG)
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            IMPORTED_CONFIGURATIONS DEBUG)
        set_target_properties(FastCodec::FastCodec PROPERTIES
            IMPORTED_LOCATION_DEBUG "${FastCodec_LIBRARY_DEBUG}"
        )
    endif()

    # Якщо немає явного поділу на конфігурації, використовуємо загальну локацію
    if(NOT FastCodec_LIBRARY_RELEASE AND NOT FastCodec_LIBRARY_DEBUG)
        set_target_properties(FastCodec::FastCodec PROPERTIES
            IMPORTED_LOCATION "${FastCodec_LIBRARY}"
        )
    endif()

    # Якщо знайдено динамічну бібліотеку на Windows, задаємо імпортну бібліотеку
    if(WIN32 AND FastCodec_LIBRARY MATCHES "\\.lib$")
        # Шукаємо відповідний DLL файл поруч або у bin
        get_filename_component(_lib_dir "${FastCodec_LIBRARY}" DIRECTORY)
        find_file(FastCodec_DLL
            NAMES fastcodec.dll
            HINTS "${_lib_dir}/../bin" "${_lib_dir}"
        )
        if(FastCodec_DLL)
            set_target_properties(FastCodec::FastCodec PROPERTIES
                IMPORTED_IMPLIB "${FastCodec_LIBRARY}"
                IMPORTED_LOCATION "${FastCodec_DLL}"
            )
        endif()
    endif()

    # Якщо активовано компонент багатопотоковості, додаємо транзитивну залежність
    if(FastCodec_PARALLEL_FOUND)
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            INTERFACE_LINK_LIBRARIES Threads::Threads
        )
        set_property(TARGET FastCodec::FastCodec APPEND PROPERTY
            INTERFACE_COMPILE_DEFINITIONS FASTCODEC_PARALLEL_ENABLED=1
        )
    endif()
endif()
