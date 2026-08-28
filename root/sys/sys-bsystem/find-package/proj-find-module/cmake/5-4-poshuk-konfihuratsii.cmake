# Пошук оптимізованої (Release) версії бібліотеки
find_library(FastCodec_LIBRARY_RELEASE
    NAMES
        fastcodec
        libfastcodec
    HINTS
        ${PC_FastCodec_LIBRARY_DIRS}
        ${FastCodec_ROOT}
        ENV FastCodec_ROOT
    PATH_SUFFIXES
        ${_fastcodec_path_suffixes}
        bin
    DOC "Шлях до Release бібліотеки FastCodec"
)

# Пошук налагоджувальної (Debug) версії (зазвичай має суфікс d або _d)
find_library(FastCodec_LIBRARY_DEBUG
    NAMES
        fastcodecd
        fastcodec_d
        libfastcodecd
        libfastcodec_d
    HINTS
        ${PC_FastCodec_LIBRARY_DIRS}
        ${FastCodec_ROOT}
        ENV FastCodec_ROOT
    PATH_SUFFIXES
        ${_fastcodec_path_suffixes}
        bin
    DOC "Шлях до Debug бібліотеки FastCodec"
)

# Відновлюємо оригінальні суфікси після пошуку
set(CMAKE_FIND_LIBRARY_SUFFIXES ${_fastcodec_orig_suffixes})
unset(_fastcodec_orig_suffixes)
unset(_fastcodec_path_suffixes)

# Допоміжний макрос для об'єднання конфігурацій
include(SelectLibraryConfigurations)
select_library_configurations(FastCodec)
