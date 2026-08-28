# 1. Пошук кореневого каталогу включення заголовків
find_path(FastCodec_INCLUDE_DIR
    NAMES
        fastcodec/fastcodec.h
    HINTS
        ${PC_FastCodec_INCLUDE_DIRS}
        ${FastCodec_ROOT}
        ENV FastCodec_ROOT
        ${FASTCODEC_ROOT}
        ENV FASTCODEC_ROOT
    PATH_SUFFIXES
        include
        include/fastcodec
    DOC "Каталог із заголовковими файлами бібліотеки FastCodec"
)
