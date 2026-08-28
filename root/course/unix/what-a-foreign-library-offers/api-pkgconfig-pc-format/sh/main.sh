# 1. Перевірка наявності пакета та відповідності версійному діапазону
$ pkg-config --exists 'libtelemetry >= 2.0.0' && echo "Пакет знайдено та сумісний"

# 2. Отримання точного номера версії встановленого пакета
$ pkg-config --modversion libtelemetry
2.4.1

# 3. Отримання прапорців компілятора (включення каталогів заголовків та макросів)
$ pkg-config --cflags libtelemetry
-I/usr/local/include/telemetry -DTELEMETRY_API_V2

# 4. Отримання прапорців лінкера для динамічного зв'язування
$ pkg-config --libs libtelemetry
-L/usr/local/lib/x86_64-linux-gnu -ltelemetry -lssl -lcrypto

# 5. Отримання прапорців лінкера для статичного зв'язування (повний граф залежностей)
$ pkg-config --libs --static libtelemetry
-L/usr/local/lib/x86_64-linux-gnu -ltelemetry -lssl -lcrypto -lz -lsodium -pthread -lm -latomic

# 6. Читання довільної стандартної або користувацької змінної
$ pkg-config --variable=schemadir libtelemetry
/usr/local/share/telemetry/schemas

# 7. Тимчасове перевизначення змінної в командному рядку
$ pkg-config --define-variable=prefix=/opt/custom-sdk --cflags libtelemetry
-I/opt/custom-sdk/include/telemetry -DTELEMETRY_API_V2

# 8. Виведення повного списку всіх зареєстрованих у системі пакетів .pc
$ pkg-config --list-all
