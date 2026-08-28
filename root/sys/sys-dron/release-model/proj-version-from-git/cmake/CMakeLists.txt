# Виконується на КОНФІГУРАЦІЇ, один раз, а не на кожній збірці.
find_package(Git QUIET)
set(QGC_TAG_GLOB "v[0-9]*" CACHE STRING "теги лінії, від яких лічити версію")

set(APP_DESCRIBE "")
if(Git_FOUND AND EXISTS "${CMAKE_SOURCE_DIR}/.git")
    execute_process(
        COMMAND ${GIT_EXECUTABLE} describe --tags --long --dirty
                                  --match "${QGC_TAG_GLOB}"
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        OUTPUT_VARIABLE  APP_DESCRIBE
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE  _git_rc
        ERROR_QUIET)
    if(NOT _git_rc EQUAL 0)
        set(APP_DESCRIBE "")
    endif()
endif()

# Новий коміт мусить змусити CMake переконфігуруватися — інакше в застосунку
# лишиться число, пораховане першого разу. Рефлог оновлюється на кожному
# коміті й переході, індекс — на кожному «git add».
foreach(_watch "logs/HEAD" "index")
    if(EXISTS "${CMAKE_SOURCE_DIR}/.git/${_watch}")
        set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS
                     "${CMAKE_SOURCE_DIR}/.git/${_watch}")
    endif()
endforeach()

# Хвіст «-<комітів>-g<хеш>[-dirty]» відкушуємо окремо: ім'я тега саме
# може містити дефіси, тому спершу знімаємо те, чия форма відома точно.
set(APP_VERSION_DIRTY "")
set(_desc "${APP_DESCRIBE}")
if(_desc MATCHES "-dirty$")
    set(APP_VERSION_DIRTY "-dirty")
    string(REGEX REPLACE "-dirty$" "" _desc "${_desc}")
endif()

if(_desc MATCHES "^(.+)-([0-9]+)-g([0-9a-f]+)$")
    set(APP_TAG          "${CMAKE_MATCH_1}")
    set(APP_VERSION_DEV  "${CMAKE_MATCH_2}")
    set(APP_VERSION_HASH "${CMAKE_MATCH_3}")
else()
    message(WARNING "QGC: історію не прочитано ('${APP_DESCRIBE}') — версія буде 0.0.0")
    set(APP_TAG "v0.0.0")
    set(APP_VERSION_DEV 0)
    set(APP_VERSION_HASH "unknown")
endif()

# Знімаємо буквений префікс лінії: «v» — стабільна, «d» — основа щоденних.
string(REGEX REPLACE "^[vd]" "" _num "${APP_TAG}")
if(_num MATCHES "^([0-9]+)\\.([0-9]+)\\.([0-9]+)")
    set(APP_VERSION_MAJOR "${CMAKE_MATCH_1}")
    set(APP_VERSION_MINOR "${CMAKE_MATCH_2}")
    set(APP_VERSION_PATCH "${CMAKE_MATCH_3}")
else()
    message(FATAL_ERROR "QGC: тег '${APP_TAG}' не схожий на X.Y.Z — уточніть QGC_TAG_GLOB")
endif()

set(APP_VERSION     "${APP_VERSION_MAJOR}.${APP_VERSION_MINOR}.${APP_VERSION_PATCH}")
set(APP_VERSION_STR "${APP_TAG}-${APP_VERSION_DEV}-g${APP_VERSION_HASH}${APP_VERSION_DIRTY}")

if(ANDROID)
    # Межі полів перевіряємо тут, доки помилка коштує повідомлення,
    # а не відмови магазину прийняти пакунок.
    if(APP_VERSION_MAJOR GREATER 9 OR APP_VERSION_MINOR GREATER 9)
        message(FATAL_ERROR "QGC: мажорна й мінорна мусять бути однією цифрою")
    endif()
    if(APP_VERSION_PATCH GREATER 99)
        message(FATAL_ERROR "QGC: патч мусить бути двома цифрами")
    endif()

    set(_dev "${APP_VERSION_DEV}")
    if(_dev GREATER 999)
        message(WARNING "QGC: ${_dev} комітів після ${APP_TAG}; лічильник обрізано на 999")
        set(_dev 999)
    endif()

    if(CMAKE_ANDROID_ARCH_ABI MATCHES "^(arm64-v8a|x86_64)$")
        set(_bitness 66)
    else()
        set(_bitness 34)
    endif()

    set(_pp "${APP_VERSION_PATCH}")
    if(APP_VERSION_PATCH LESS 10)
        set(_pp "0${APP_VERSION_PATCH}")
    endif()
    set(_ddd "${_dev}")
    if(_dev LESS 10)
        set(_ddd "00${_dev}")
    elseif(_dev LESS 100)
        set(_ddd "0${_dev}")
    endif()

    # BB M I PP DDD
    set(ANDROID_VERSION_CODE
        "${_bitness}${APP_VERSION_MAJOR}${APP_VERSION_MINOR}${_pp}${_ddd}")
    message(STATUS "QGC: код версії ${ANDROID_VERSION_CODE}")
endif()
