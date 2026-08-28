# custom/CMakeLists.txt
list(APPEND CUSTOM_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/SokilFirmwarePluginFactory.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/SokilFirmwarePluginFactory.h
    ${CMAKE_CURRENT_SOURCE_DIR}/src/SokilFirmwarePlugin.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/SokilFirmwarePlugin.h
    ${CMAKE_CURRENT_SOURCE_DIR}/src/SokilFirmwarePluginInstanceData.h
    ${CMAKE_CURRENT_SOURCE_DIR}/src/SokilMAVLink.h
)
set(CUSTOM_SOURCES ${CUSTOM_SOURCES} CACHE INTERNAL "" FORCE)
