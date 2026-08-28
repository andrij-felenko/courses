# Переключення у багатокористувацький консольний режим
systemctl isolate multi-user.target

# Переключення у повноцінний графічний режим
systemctl isolate graphical.target

# Переключення у режим однокористувацького відновлення
systemctl isolate rescue.target

# Екстрене виклики режимів аварійного відновлення
systemctl isolate emergency.target
