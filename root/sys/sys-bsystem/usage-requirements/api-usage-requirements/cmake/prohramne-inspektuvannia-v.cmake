# Отримання списку внутрішніх каталогів включення
get_target_property(local_dirs my_target INCLUDE_DIRECTORIES)
message(STATUS "Власні каталоги: ${local_dirs}")

# Отримання списку експортних вимог включення
get_target_property(iface_dirs my_target INTERFACE_INCLUDE_DIRECTORIES)
message(STATUS "Експортні каталоги: ${iface_dirs}")

# Отримання списку прямих залежностей
get_target_property(link_list my_target LINK_LIBRARIES)
message(STATUS "Залежності лінкування: ${link_list}")
