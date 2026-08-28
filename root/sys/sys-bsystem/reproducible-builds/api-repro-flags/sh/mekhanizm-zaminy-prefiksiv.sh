# Універсальне правило заміни префіксів (GCC >= 8, Clang >= 10)
-ffile-prefix-map=/home/builder/workspace/myproject=.
-ffile-prefix-map=$PWD=.

# Спеціалізована заміна префіксів для налагоджувальних секцій DWARF
-fdebug-prefix-map=/home/builder/workspace/myproject=/usr/src/debug

# Спеціалізована заміна префіксів для макросів препроцесора (__FILE__, __BASE_FILE__)
-fmacro-prefix-map=/home/builder/workspace/myproject=.

# Заміна шляхів у файлах профілювання gcov (.gcno, .gcda)
-fprofile-prefix-map=/home/builder/workspace/myproject=.
