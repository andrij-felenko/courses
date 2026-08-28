# 1. Пошук мережевих адрес керуючих серверів (C2 / API endpoints):
$ strings -a -n 8 sensor-agent | grep -Ei 'https?://|tcp://|wss?://|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]+'
https://telemetry.internal-cloud.net/v2/metrics
https://backup-sink.storage.io/auth
192.168.10.45:8443

# 2. Пошук шляхів файлової системи Linux:
$ strings -a -n 6 sensor-agent | grep -E '^/(etc|var|tmp|proc|sys|dev|usr)/'
/etc/sensor-agent/config.yaml
/var/log/sensor-agent.log
/tmp/.agent-lock
/proc/sys/kernel/random/uuid

# 3. Пошук ключів командного рядка та змінних оточення:
$ strings -a -n 4 sensor-agent | grep -E '^\-\-[a-zA-Z0-9_-]+|^[A-Z0-9_]{4,}='
--config
--daemon
--verbose
--dry-run
AUTH_TOKEN=
LOG_LEVEL=

# 4. Пошук шляхів до вихідного коду розробника (Artifacts of build environment):
$ strings -a -n 8 sensor-agent | grep -Ei '\.(c|cpp|cc|go|rs|h):[0-9]+'
/home/builder/work/sensor-agent/src/network/client.cpp:142
/home/builder/work/sensor-agent/src/crypto/aes_engine.c:58
