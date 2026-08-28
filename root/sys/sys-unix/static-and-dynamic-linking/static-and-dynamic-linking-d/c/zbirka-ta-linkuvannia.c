/* Команди збірки для C (GCC / Clang) */

/* === 1. СТА ТИЧНЕ ЛІНКУВАННЯ === */
/* Компіляція об'єктного файла бібліотеки */
gcc -c my_math.c -o my_math.o

/* Створення статичного архіву .a за допомогою ar */
ar rcs libmy_math.a my_math.o

/* Компіляція програми та статичне лінкування */
gcc app.c -L. -lmy_math -static -o app_static


/* === 2. ДИНАМІЧНЕ ЛІНКУВАННЯ === */
/* Компіляція об'єктного файла з прапорцем -fPIC (Position Independent Code) */
gcc -fPIC -c my_math.c -o my_math_pic.o

/* Створення спільновживаного об'єкта .so */
gcc -shared my_math_pic.o -o libmy_math.so

/* Компіляція програми з динамічним лінкуванням */
gcc app.c -L. -lmy_math -Wl,-rpath,'.' -o app_dynamic
