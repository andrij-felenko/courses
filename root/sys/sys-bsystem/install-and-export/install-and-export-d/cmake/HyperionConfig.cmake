# Шаблон HyperionConfig.cmake.in із підтримкою компонентів
@PACKAGE_INIT@

include(CMakeFindDependencyMacro)

# Список усіх підтримуваних компонентів бібліотеки
set(_supported_components Core Network Gui)

# Якщо споживач не вказав COMPONENTS, вважаємо всі компоненти обов'язковими
if(NOT Hyperion_FIND_COMPONENTS)
    set(Hyperion_FIND_COMPONENTS ${_supported_components})
endif()

# Послідовне підключення запрошених компонентів
foreach(_comp ${Hyperion_FIND_COMPONENTS})
    if(_comp IN_LIST _supported_components)
        set(_target_file "${CMAKE_CURRENT_LIST_DIR}/Hyperion${_comp}Targets.cmake")
        if(EXISTS "${_target_file}")
            include("${_target_file}")
            set(Hyperion_${_comp}_FOUND TRUE)
        else()
            set(Hyperion_${_comp}_FOUND FALSE)
        endif()
    else()
        set(Hyperion_${_comp}_FOUND FALSE)
        set(Hyperion_NOT_FOUND_MESSAGE "Невідомий компонент Hyperion: ${_comp}")
    endif()
endforeach()

# Перевірка наявності всіх REQUIRED компонентів
check_required_components(Hyperion)
