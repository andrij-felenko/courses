if(FastCodec_FOUND)
    set(FastCodec_INCLUDE_DIRS "${FastCodec_INCLUDE_DIR}")
    set(FastCodec_LIBRARIES "${FastCodec_LIBRARY}")
endif()

# Приховуємо внутрішні змінні в графічних інтерфейсах ccmake / cmake-gui
mark_as_advanced(
    FastCodec_INCLUDE_DIR
    FastCodec_LIBRARY
    FastCodec_LIBRARY_RELEASE
    FastCodec_LIBRARY_DEBUG
    FastCodec_DLL
)
