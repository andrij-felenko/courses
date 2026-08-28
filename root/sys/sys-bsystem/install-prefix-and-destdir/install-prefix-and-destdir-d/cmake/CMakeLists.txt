# Встановлення двійкових цілей
install(TARGETS myapp mylib
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Встановлення публічних заголовків
install(DIRECTORY include/
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Встановлення статичних ресурсів
install(DIRECTORY assets/
    DESTINATION ${CMAKE_INSTALL_DATADIR}/myapp
)
