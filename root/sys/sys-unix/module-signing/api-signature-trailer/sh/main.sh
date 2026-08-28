# 1. пара ключів і самопідписаний сертифікат ЦС (для .machine потрібен саме ЦС)
openssl req -new -x509 -newkey rsa:4096 -nodes -days 36500 \
    -subj "/CN=Module signing key/" \
    -addext "basicConstraints=critical,CA:TRUE" \
    -addext "keyUsage=critical,keyCertSign" \
    -keyout MOK.priv -out MOK.pem

# 2. форма DER — саме її приймає mokutil
openssl x509 -in MOK.pem -outform DER -out MOK.der

# 3. підпис; назва хешу мусить збігтися з вбудованим у це ядро
/usr/src/linux-headers-$(uname -r)/scripts/sign-file sha512 \
    MOK.priv MOK.pem ./mydriver.ko
