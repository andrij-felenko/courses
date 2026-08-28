# --- ідентичність ---
set(QGC_APP_NAME         "Acme GCS"        CACHE STRING "Application name" FORCE)
set(QGC_ORG_NAME         "Acme Robotics"   CACHE STRING "Organization name" FORCE)
set(QGC_ORG_DOMAIN       "acme.example"    CACHE STRING "Organization domain" FORCE)
set(QGC_PACKAGE_NAME     "com.acme.gcs"    CACHE STRING "Package identifier" FORCE)
set(QGC_APP_DESCRIPTION  "Acme ground control station" CACHE STRING "Application description" FORCE)
set(QGC_APP_COPYRIGHT    "Copyright (c) 2026 Acme Robotics" CACHE STRING "Copyright notice" FORCE)
set(QGC_SETTINGS_VERSION "1"               CACHE STRING "Settings schema version" FORCE)

# похідні ідентифікатори — окремими рядками, бо їхні типові значення вже обчислені
set(QGC_MACOS_BUNDLE_ID       "com.acme.gcs" CACHE STRING "macOS bundle identifier" FORCE)
set(QGC_ANDROID_PACKAGE_NAME  "com.acme.gcs" CACHE STRING "Android package identifier" FORCE)

# --- набір функцій ---
set(QGC_DISABLE_APM_MAVLINK        ON CACHE BOOL "Disable ArduPilot MAVLink dialect" FORCE)
set(QGC_DISABLE_APM_PLUGIN         ON CACHE BOOL "Disable ArduPilot plugin" FORCE)
set(QGC_DISABLE_APM_PLUGIN_FACTORY ON CACHE BOOL "Disable ArduPilot plugin factory" FORCE)
set(QGC_DISABLE_PX4_PLUGIN_FACTORY ON CACHE BOOL "Disable PX4 plugin factory" FORCE)
set(QGC_STABLE_BUILD               ON CACHE BOOL "Stable release build" FORCE)

# --- значки: тільки те, що справді поклали ---
foreach(_pair
        "QGC_MACOS_ICON_PATH|res/icons/acme.icns"
        "QGC_APPIMAGE_ICON_SCALABLE_PATH|res/icons/acme.svg"
        "QGC_WINDOWS_ICON_PATH|deploy/windows/acme.ico")
    string(REPLACE "|" ";" _pair "${_pair}")
    list(GET _pair 0 _var)
    list(GET _pair 1 _rel)
    set(_abs "${CMAKE_SOURCE_DIR}/${QGC_CUSTOM_DIR}/${_rel}")
    if(EXISTS "${_abs}")
        set(${_var} "${_abs}" CACHE FILEPATH "custom ${_var}" FORCE)
    endif()
endforeach()
