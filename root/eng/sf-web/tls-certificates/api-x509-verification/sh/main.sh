# 1. Повна перевірка з показом усіх сертифікатів ланцюжка та індикацією SNI
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts

# 2. Тестування з використанням власного локального CA бандла
openssl s_client -connect api.internal.corp:443 -servername api.internal.corp -CAfile /etc/ssl/custom-ca.pem

# 3. Тестування mTLS з надсиланням сертифіката та приватного ключа клієнта
openssl s_client -connect secure-gw.bank.com:8443 \
    -servername secure-gw.bank.com \
    -CAfile /etc/ssl/ca-bundle.pem \
    -cert client.crt \
    -key client.key
