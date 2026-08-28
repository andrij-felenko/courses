# Повний безпечний запуск із виправленням прав, ініціалізатором та DNS
docker run -d \
  --name app-production \
  --init \                                # Підключає вбудований tini (PID 1 reaper)
  --user 1000:1000 \                      # Явне вирівнювання UID/GID
  --network custom-bridge \               # Вмикає embedded DNS 127.0.0.11
  --dns 1.1.1.1 \                         # Резервний зовнішній upstream DNS
  --pids-limit 512 \                      # Захист cgroups v2 від fork-бомб та зомбі
  --read-only \                           # Незмінний кореневий шар (захист ФС)
  --tmpfs /tmp:rw,noexec,nosuid \         # Тимчасові файли без прав виконання
  -v /host/data:/app/data:rw \            # Монтування тому з відповідними правами
  my-app:v1.0.0
