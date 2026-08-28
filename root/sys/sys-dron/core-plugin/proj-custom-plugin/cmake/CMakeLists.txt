# custom/CMakeLists.txt — усе, що апстримова збірка про нас дізнається

# 1. Три імені, на яких тримається підміна класу.
set(CUSTOM_DEFINITIONS
    QGC_CUSTOM_BUILD
    CUSTOMHEADER="CustomPlugin.h"
    CUSTOMCLASS=CustomPlugin
    CACHE INTERNAL "" FORCE
)

# 2. Наші файли — їх компілюють разом із застосунком, одним модулем.
set(CUSTOM_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/CustomPlugin.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/CustomPlugin.h
    CACHE INTERNAL "" FORCE
)

# 3. Де препроцесор шукатиме CustomPlugin.h, дійшовши до #include CUSTOMHEADER.
set(CUSTOM_INCLUDE_DIRECTORIES
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    CACHE INTERNAL "" FORCE
)

# 4. Модулі Qt, потрібні саме нашому кодові понад ті, що апстрим шукає й так.
set(CUSTOM_QT_COMPONENTS Core Qml CACHE INTERNAL "" FORCE)

# 5. Наш ресурсний файл — у хвіст списку ресурсів застосунку.
set(QGC_RESOURCES ${QGC_RESOURCES} ${CMAKE_CURRENT_SOURCE_DIR}/custom.qrc
    CACHE STRING "Paths to .qrc Resources" FORCE)
