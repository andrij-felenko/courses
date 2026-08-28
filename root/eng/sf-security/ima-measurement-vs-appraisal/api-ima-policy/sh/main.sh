# 1. Ключ підписувача. Закритий лишається поза машиною, яку захищаємо.
openssl req -new -x509 -nodes -days 3650 -sha256 -batch \
        -keyout privkey_ima.pem -out x509_ima.pem
openssl x509 -in x509_ima.pem -outform DER -out x509_ima.der

# 2. Підписати виконуваний файл і глянути, що лягло в атрибут.
evmctl ima_sign -a sha256 -k privkey_ima.pem /usr/sbin/myservice
getfattr -m security.ima -e hex -d /usr/sbin/myservice

# 3. На цільовій машині — сертифікат у кільце .ima.
evmctl import x509_ima.der $(keyctl search @u keyring .ima)

# 4. Вимагати підпис на кожному запуску.
echo 'appraise func=BPRM_CHECK appraise_type=imasig' \
     > /sys/kernel/security/ima/policy
