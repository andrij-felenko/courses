# Перемістимо каталог інсталяції в абсолютно інший каталог
mv /tmp/hyperion-dist /tmp/hyperion-relocated

# Сконфігуруємо споживача з новим шляхом (використовуючи --fresh для скидання кешу)
cmake -B build-consumer-relocated -S examples/consumer_app \
    --fresh \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=/tmp/hyperion-relocated

# Зберемо та запустимо програму
cmake --build build-consumer-relocated
./build-consumer-relocated/consumer_app
