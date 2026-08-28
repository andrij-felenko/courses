# 1. Компіляція з інструментацією LibFuzzer, ASan та UBSan
clang++ -O2 -g -fsanitize=fuzzer,address,undefined \
    -Wall -Wextra -std=c++20 \
    fuzz_harness.cpp -o protocol_fuzzer

# 2. Підготовка початкового корпусу валідних пакетів
mkdir -p corpus artifacts
python3 -c "
import struct
# Створюємо валідний пакет Heartbeat (0xAA, msg_type=0x01, len=2, payload='OK', crc16)
payload = b'OK'
# CRC для b'\x01\x02OK' = 0x7849
frame = struct.pack('<BBB2sH', 0xAA, 0x01, len(payload), payload, 0x7849)
open('corpus/seed_valid_heartbeat.raw', 'wb').write(frame)
"

# 3. Запуск фазингу на 4 паралельних потоках
./protocol_fuzzer corpus/ \
    -dict=protocol.dict \
    -artifact_prefix=artifacts/ \
    -max_len=256 \
    -rss_limit_mb=512 \
    -jobs=4 \
    -workers=4
