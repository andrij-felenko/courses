# Зберігаємо поточний стан суфіксів пошуку бібліотек
set(_fastcodec_orig_suffixes ${CMAKE_FIND_LIBRARY_SUFFIXES})

if(FastCodec_USE_STATIC_LIBS)
    if(WIN32)
        set(CMAKE_FIND_LIBRARY_SUFFIXES .lib .a)
    else()
        set(CMAKE_FIND_LIBRARY_SUFFIXES .a)
    endif()
endif()
