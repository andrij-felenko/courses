if(FastCodec_INCLUDE_DIR AND EXISTS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec.h")
    # Зчитуємо лише рядки, що містять макроси версії, не завантажуючи весь файл
    file(STRINGS "${FastCodec_INCLUDE_DIR}/fastcodec/fastcodec.h" _fastcodec_version_lines
         REGEX "^#define[ \t]+FASTCODEC_VERSION_(MAJOR|MINOR|PATCH)[ \t]+[0-9]+")

    # Витягуємо окремі компоненти версії
    string(REGEX MATCH "FASTCODEC_VERSION_MAJOR[ \t]+([0-9]+)" _ "${_fastcodec_version_lines}")
    set(FastCodec_VERSION_MAJOR "${CMAKE_MATCH_1}")

    string(REGEX MATCH "FASTCODEC_VERSION_MINOR[ \t]+([0-9]+)" _ "${_fastcodec_version_lines}")
    set(FastCodec_VERSION_MINOR "${CMAKE_MATCH_1}")

    string(REGEX MATCH "FASTCODEC_VERSION_PATCH[ \t]+([0-9]+)" _ "${_fastcodec_version_lines}")
    set(FastCodec_VERSION_PATCH "${CMAKE_MATCH_1}")

    if(FastCodec_VERSION_MAJOR AND FastCodec_VERSION_MINOR AND FastCodec_VERSION_PATCH)
        set(FastCodec_VERSION "${FastCodec_VERSION_MAJOR}.${FastCodec_VERSION_MINOR}.${FastCodec_VERSION_PATCH}")
    endif()

    unset(_fastcodec_version_lines)
endif()
