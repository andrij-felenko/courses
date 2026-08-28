# Створення тестових каталогів:
mkdir -p /tmp/gen-test/normal /tmp/gen-test/early /tmp/gen-test/late

# Запуск генератора з трьома тестовими аргументами:
/lib/systemd/system-generators/custom-generator \
  /tmp/gen-test/normal /tmp/gen-test/early /tmp/gen-test/late

# Перевірка наявності та вмісту згенерованих файлів:
ls -la /tmp/gen-test/normal/
cat /tmp/gen-test/normal/custom-app.service
ls -la /tmp/gen-test/normal/multi-user.target.wants/
