# 1. Конфігурація споживача
cmake -B build-consumer -S examples/consumer_app \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=/tmp/hyperion-dist

# 2. Збірка виконуваного файла
cmake --build build-consumer

# 3. Запуск зібраної програми
./build-consumer/consumer_app
