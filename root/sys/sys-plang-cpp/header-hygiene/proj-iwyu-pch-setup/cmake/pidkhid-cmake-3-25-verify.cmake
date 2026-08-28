# Оголошення публічного набору заголовків бібліотеки
target_sources(core_lib
    PUBLIC
        FILE_SET HEADERS
        BASE_DIRS include
        FILES
            include/UserSession.h
            include/Database.h
            include/Network.h
)

# Увімкнення автоматичної перевірки самодостатності
set_target_properties(core_lib PROPERTIES
    VERIFY_INTERFACE_HEADER_SETS ON
)
