set(FastCodec_PARALLEL_FOUND FALSE)

if("PARALLEL" IN_LIST FastCodec_FIND_COMPONENTS)
    # Перевіряємо заголовок на наявність прапорця активації багатопотоковості
    if(FastCodec_INCLUDE_DIR AND EXISTS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec_features.h")
        file(STRINGS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec_features.h" _has_parallel
             REGEX "^#define[ \t]+FASTCODEC_HAS_PARALLEL[ \t]+1")
        if(_has_parallel)
            # Компонент вимагає системної бібліотеки потоків
            find_package(Threads QUIET)
            if(Threads_FOUND)
                set(FastCodec_PARALLEL_FOUND TRUE)
            endif()
        endif()
        unset(_has_parallel)
    endif()
endif()
