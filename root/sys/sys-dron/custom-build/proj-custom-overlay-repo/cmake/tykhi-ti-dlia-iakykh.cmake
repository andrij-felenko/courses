# custom/CMakeLists.txt
set(CUSTOM_SHADOWED
    src/UI/toolbar/MainToolBar.qml
    src/UI/preferences/GeneralSettings.qml
)
foreach(f IN LISTS CUSTOM_SHADOWED)
    if(NOT EXISTS "${CMAKE_SOURCE_DIR}/${f}")
        message(FATAL_ERROR "Апстрим більше не має ${f}: наша підміна нікуди не діє")
    endif()
endforeach()
