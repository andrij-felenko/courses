# 1. Завантаження еталонного зліпка попереднього стабільного релізу
curl -sO https://releases.example.com/abi/libengine-v1.0.abi

# 2. Генерація поточного зліпка щойно скомпільованої бібліотеки
abidw --drop-private-types build/libengine.so --out-file current.abi

# 3. Виконання диференційного аналізу з перевіркою коду завершення
abidiff --suppressions config/abi.suppr libengine-v1.0.abi current.abi
if [ $? -ne 0 ]; then
    echo "CRITICAL: Виявлено розрив ABI! Злиття заборонено."
    exit 1
fi
