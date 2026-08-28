# Перегляд усіх зареєстрованих властивостей юніта:
busctl introspect org.freedesktop.systemd1 \
  /org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice \
  org.freedesktop.systemd1.Unit

# Точкове зчитування конкретного поля Result:
busctl get-property org.freedesktop.systemd1 \
  /org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice \
  org.freedesktop.systemd1.Unit Result

# Зчитування лічильника перезапусків з інтерфейсу Service:
busctl get-property org.freedesktop.systemd1 \
  /org/freedesktop/systemd1/unit/nginx_2dcustom_2eservice \
  org.freedesktop.systemd1.Service NRestarts
