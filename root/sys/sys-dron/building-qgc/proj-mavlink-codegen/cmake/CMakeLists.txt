add_custom_command(OUTPUT ${EXAMPLE_HEADER}
    COMMAND ${Python_EXECUTABLE}
        -m pip install -r pymavlink/requirements.txt --upgrade
           -t ${CMAKE_CURRENT_BINARY_DIR}/pip-dependencies/
    COMMAND ${CMAKE_COMMAND} -E env
        "PYTHONPATH=${CMAKE_CURRENT_BINARY_DIR}/pip-dependencies/" ${Python_EXECUTABLE}
        -m pymavlink.tools.mavgen
        --lang=C
        --wire-protocol=${MAVLINK_VERSION}
        --output ${CMAKE_CURRENT_BINARY_DIR}/include/mavlink/
        message_definitions/v1.0/${MAVLINK_DIALECT}.xml
    DEPENDS message_definitions/v1.0/${MAVLINK_DIALECT}.xml
    COMMENT "Generating C and C++11 headers")
