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
