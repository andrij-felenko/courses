# 1. Компонент виконання: бінарники та динамічні бібліотеки
install(TARGETS myapp mylib
    EXPORT MyAppTargets
    RUNTIME DESTINATION bin COMPONENT Runtime
    LIBRARY DESTINATION lib COMPONENT Runtime
    ARCHIVE DESTINATION lib COMPONENT Development
    NAMELINK_COMPONENT Development
)

# 2. Компонент розробника: заголовки та метадані експорту цілей
install(DIRECTORY include/
    DESTINATION include
    COMPONENT Development
)
install(EXPORT MyAppTargets
    NAMESPACE MyApp::
    DESTINATION lib/cmake/MyApp
    COMPONENT Development
)

# 3. Компонент документації: man-сторінки та HTML-довідка
install(DIRECTORY doc/html/
    DESTINATION share/doc/myapp
    COMPONENT Documentation
)
