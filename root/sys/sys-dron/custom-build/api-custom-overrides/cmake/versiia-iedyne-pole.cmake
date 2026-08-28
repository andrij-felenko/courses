execute_process(
    COMMAND ${GIT_EXECUTABLE} describe --always --tags --abbrev=0
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    OUTPUT_VARIABLE QGC_APP_VERSION
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
)
string(REGEX REPLACE "^v" "" QGC_APP_VERSION_CLEAN "${QGC_APP_VERSION}")
if(QGC_APP_VERSION_CLEAN MATCHES "^([0-9]+)\\.([0-9]+)\\.([0-9]+)")
    set(QGC_APP_VERSION "${QGC_APP_VERSION_CLEAN}")
    …
else()
    message(WARNING "QGC: Could not parse semantic version from Git tag: …")
    set(QGC_APP_VERSION "0.0.0")
endif()
