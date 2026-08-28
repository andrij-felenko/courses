# custom/cmake/CustomOverrides.cmake
function(qgc_override name type value)
    if(NOT DEFINED CACHE{${name}})
        message(FATAL_ERROR "Апстрим більше не оголошує ${name}: перевизначення повисло")
    endif()
    set(${name} "${value}" CACHE ${type} "custom build override" FORCE)
endfunction()

qgc_override(QGC_APP_NAME       STRING "Custom-QGroundControl")
qgc_override(QGC_PACKAGE_NAME   STRING "com.example.gcs")
qgc_override(QGC_SETTINGS_VERSION STRING "1")
