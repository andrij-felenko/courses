# cmake/FindSensorEngine.cmake
# Захист стека політик викликача:
cmake_policy(PUSH)

# Модуль вимагає строгої поведінки розбору лапок за CMP0054 та нових шляхів коренів за CMP0144:
cmake_policy(SET CMP0054 NEW)
if(POLICY CMP0144)
  cmake_policy(SET CMP0144 NEW)
endif()

find_path(SENSOR_ENGINE_INCLUDE_DIR
  NAMES sensor_engine.hpp sensor_engine.h
  PATHS /opt/sensors/include /usr/local/include
)

find_library(SENSOR_ENGINE_LIBRARY
  NAMES sensor_engine
  PATHS /opt/sensors/lib /usr/local/lib
)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(SensorEngine
  DEFAULT_MSG
  SENSOR_ENGINE_LIBRARY
  SENSOR_ENGINE_INCLUDE_DIR
)

if(SensorEngine_FOUND AND NOT TARGET SensorEngine::SensorEngine)
  add_library(SensorEngine::SensorEngine UNKNOWN IMPORTED)
  set_target_properties(SensorEngine::SensorEngine PROPERTIES
    IMPORTED_LOCATION "${SENSOR_ENGINE_LIBRARY}"
    INTERFACE_INCLUDE_DIRECTORIES "${SENSOR_ENGINE_INCLUDE_DIR}"
  )
endif()

# Обов'язкове відновлення стека викликача наприкінці модуля:
cmake_policy(POP)
