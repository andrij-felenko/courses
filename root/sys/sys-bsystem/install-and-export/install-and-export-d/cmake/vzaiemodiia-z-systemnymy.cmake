# Розподіл артефактів за компонентами
install(TARGETS data_engine
    EXPORT DataEngineTargets
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} COMPONENT runtime
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT runtime
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR} COMPONENT devel
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT DataEngineTargets
    FILE DataEngineTargets.cmake
    NAMESPACE DataEngine::
    DESTINATION ${DATAENGINE_CONFIG_DIR}
    COMPONENT devel
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/DataEngineConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/DataEngineConfigVersion.cmake"
    DESTINATION ${DATAENGINE_CONFIG_DIR}
    COMPONENT devel
)
