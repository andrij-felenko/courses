# Крок 1. Збірка програми з обов'язковим збереженням таблиць релокацій
clang++ -O3 -flto=thin -Wl,-q -Wl,--emit-relocs main.cpp -o app_bin

# Крок 2. Збір апаратного LBR-профілю під навантаженням
perf record -e cycles:u -j any,u -o perf.data -- ./app_bin

# Крок 3. Перетворення бінарної траси perf у текстовий профіль переходів BOLT
perf2bolt -p perf.data -o app.fdata app_bin

# Крок 4. Запуск бінарної трансформації коду
llvm-bolt app_bin -o app_bin.bolt \
          -data=app.fdata \
          -reorder-blocks=ext-tsp \
          -reorder-functions=hfsort+ \
          -split-functions \
          -split-all-cold \
          -dyno-stats
