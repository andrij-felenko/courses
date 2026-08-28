# Розшифрування окремого символу:
c++filt _ZN4math6Vector3addERKS0_

# Фільтрація експортованих символів динамічної бібліотеки ELF:
nm -D --defined-only libengine.so | c++filt

# Декодування списку символів із журналу падіння:
cat crash.log | c++filt > readable_crash.log

# Примусове декодування Windows-символів утилітою llvm-cxxfilt:
llvm-cxxfilt --format=msvc "?calculate@MathHelper@@QEAAHHN@Z"
