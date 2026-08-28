# src/Vehicle/FactGroups/CMakeLists.txt

target_sources(${CMAKE_PROJECT_NAME}
    PRIVATE
        ...
        VehicleWinchFactGroup.cc
        VehicleWinchFactGroup.h
)

set(JSON_FILES
    ...
    WinchFact.json
)

qt_add_resources(${CMAKE_PROJECT_NAME} json_vehicle_fact_group
    PREFIX "/json/Vehicle"
    FILES ${JSON_FILES}
)
