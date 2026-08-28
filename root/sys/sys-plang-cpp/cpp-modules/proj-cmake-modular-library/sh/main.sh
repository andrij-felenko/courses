# 1. Генерація BMI розділів
clang++ -std=c++20 --precompile src/matrix_types.cppm -o build/matrix_types.pcm
clang++ -std=c++20 --precompile src/matrix_ops.cppm \
    -fmodule-file=matrix:types=build/matrix_types.pcm \
    -o build/matrix_ops.pcm
clang++ -std=c++20 --precompile src/matrix_storage.cppm \
    -fmodule-file=matrix:types=build/matrix_types.pcm \
    -o build/matrix_storage.pcm

# 2. Генерація головного BMI
clang++ -std=c++20 --precompile src/matrix.cppm \
    -fmodule-file=matrix:types=build/matrix_types.pcm \
    -fmodule-file=matrix:ops=build/matrix_ops.pcm \
    -fmodule-file=matrix:storage=build/matrix_storage.pcm \
    -o build/matrix.pcm

# 3. Генерація об'єктного коду реалізації та споживача
clang++ -std=c++20 -c src/matrix_io.cpp \
    -fmodule-file=matrix=build/matrix.pcm \
    -o build/matrix_io.o

clang++ -std=c++20 -c app/main.cpp \
    -fmodule-file=matrix=build/matrix.pcm \
    -o build/main.o
