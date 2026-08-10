# Практика: Динамічні користувачі та стійкий стан

У цьому проєкті ми налаштуємо службу з динамічним користувачем (`DynamicUser=yes`), яка зберігає свій стан у `StateDirectory`. Ми переконаємося, що незважаючи на зміну UID після перезапуску, служба не втрачає доступ до своїх даних.

1. **Створіть скрипт демона:**
   Створіть файл `/usr/local/bin/dyn-demo.sh` (і зробіть його виконуваним `chmod +x`):
   ```bash
   #!/bin/bash
   # Читаємо шлях зі змінної, наданої systemd
   STATE_FILE="$STATE_DIRECTORY/counter.txt"
   
   echo "Starting as UID $(id -u). State file is $STATE_FILE"
   
   # Ініціалізація
   if [ ! -f "$STATE_FILE" ]; then
       echo 0 > "$STATE_FILE"
   fi
   
   while true; do
       COUNT=$(cat "$STATE_FILE")
       COUNT=$((COUNT + 1))
       echo $COUNT > "$STATE_FILE"
       echo "Updated counter to $COUNT"
       sleep 5
   done
   ```

2. **Створіть systemd юніт:**
   Створіть `/etc/systemd/system/dyn-demo.service`:
   ```ini
   [Unit]
   Description=Dynamic User State Demo
   
   [Service]
   Type=simple
   ExecStart=/usr/local/bin/dyn-demo.sh
   # Робимо користувача динамічним
   DynamicUser=yes
   # Systemd автоматично створить і захистить цей каталог
   StateDirectory=dyndemo
   ```

3. **Запустіть та перевірте:**
   ```bash
   systemctl daemon-reload
   systemctl start dyn-demo
   systemctl status dyn-demo
   ```
   У логах ви побачите: `Starting as UID 64xxx`.
   Перевірте файли в `/var/lib/private/dyndemo/counter.txt` (саме туди systemd фізично мапить StateDirectory для динамічних юнітів).

4. **Перезапустіть службу:**
   ```bash
   systemctl restart dyn-demo
   ```
   У логах ви побачите, що лічильник продовжує зростати, хоча UID може змінитися, якщо кеш користувачів був очищений або система перезавантажилася. Systemd автоматично виконав `chown` для каталогу під новий динамічний UID.
