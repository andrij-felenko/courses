# Крок 1. Збірка інструментованого релізного бінарника
RUSTFLAGS="-C profile-generate=/tmp/pgo-data" cargo build --release

# Крок 2. Тренувальний прогін під типовим робочим навантаженням
./target/release/server_app --benchmark

# Крок 3. Індексація зібраних профілів через llvm-profdata
llvm-profdata merge -output=/tmp/pgo-data/merged.profdata /tmp/pgo-data

# Крок 4. Оптимізована збірка з використанням профілю та діагностикою
RUSTFLAGS="-C profile-use=/tmp/pgo-data/merged.profdata -C llvm-args=-pgo-warn-missing-function" cargo build --release
