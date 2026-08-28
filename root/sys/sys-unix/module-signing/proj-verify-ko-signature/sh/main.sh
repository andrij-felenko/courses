$ openssl req -new -x509 -newkey rsa:4096 -nodes -days 3650 \
      -keyout my.key -out my.crt -subj '/CN=Мій ключ для модулів'
$ cp /tmp/xfs.ko /tmp/copy.ko
$ /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 my.key my.crt /tmp/copy.ko
$ ./verify-ko /tmp/copy.ko my.crt
розкладка: тіло 3512792 + підпис 758 + опис 12 + маркер 28 = 3513590
підписант: видавець /CN=Мій ключ для модулів
           серійний 5B0FE31C7A94D2680B
хеш:       sha256
ПІДПИС ЗБІГСЯ
