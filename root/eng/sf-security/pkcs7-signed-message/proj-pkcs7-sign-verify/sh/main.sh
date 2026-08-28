# 1. Генерація закритого ключа та самопідписаного сертифіката Root CA
openssl req -x509 -newkey rsa:3072 -nodes -keyout ca.key -out ca.crt -days 3650 \
    -subj "/CN=Embedded Root CA/O=Industrial IoT/C=UA"

# 2. Генерація ключа та сертифіката підписувача коду (Code Signing Leaf)
openssl req -newkey rsa:3072 -nodes -keyout signer.key -out signer.csr \
    -subj "/CN=Firmware Release Signer/O=Industrial IoT/C=UA"

# 3. Підпис сертифіката підписувача з розширенням ExtendedKeyUsage = codeSigning
openssl x509 -req -in signer.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out signer.crt -days 730 -extfile <(echo -e "extendedKeyUsage=critical,codeSigning\nkeyUsage=critical,digitalSignature")

# 4. Створення тестового бінарного файлу прошивки
dd if=/dev/urandom of=firmware.bin bs=1M count=10

# 5. Генерація відокремленого підпису CMS через OpenSSL CLI
openssl cms -sign -binary -nodetach -in firmware.bin -signer signer.crt -inkey signer.key \
    -outform DER -out firmware.bin.p7s

# 6. Перевірка підпису через OpenSSL CLI
openssl cms -verify -binary -in firmware.bin.p7s -inform DER -content firmware.bin \
    -CAfile ca.crt -out /dev/null
