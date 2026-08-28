$ make
gcc -Wall -Wextra -O2 -I/tmp/opt/geomcalc/include client.c -Wl,-rpath,/tmp/opt/geomcalc/lib -L/tmp/opt/geomcalc/lib -lgeomcalc -o client
gcc -static -Wall -Wextra -O2 -I/tmp/opt/geomcalc/include client.c -L/tmp/opt/geomcalc/lib -lgeomcalc -lz -lm -o client_static

$ ./client
Обчислена площа трикутника: 6.00 (очікується 6.00)
Звіт успішно стиснуто до 26 байтів.

$ ./client_static
Обчислена площа трикутника: 6.00 (очікується 6.00)
Звіт успішно стиснуто до 26 байтів.
