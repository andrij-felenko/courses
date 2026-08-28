# Отримання прапорців препроцесора (шляхи пошуку заголовків):
$ pkg-config --cflags openssl
-I/usr/include

# Отримання прапорців лінкера (шляхи до бібліотек та прапорці зв'язування):
$ pkg-config --libs openssl
-lssl -lcrypto

# Перевірка версії бібліотеки:
$ pkg-config --modversion openssl
3.0.13
