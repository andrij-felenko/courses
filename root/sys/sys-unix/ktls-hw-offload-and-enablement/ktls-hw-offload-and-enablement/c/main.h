/* Реєстрація ULP 'tls' на підключеному TCP-сокеті */
setsockopt(sock_fd, SOL_TCP, TCP_ULP, "tls", sizeof("tls"));

/* Передача симетричного ключа AES-GCM 128 біт у рівень SOL_TLS */
struct tls12_crypto_info_aes_gcm_128 crypto_info;
/* ... заповнення ключів, IV, солі та seq_num ... */
setsockopt(sock_fd, SOL_TLS, TLS_TX, &crypto_info, sizeof(crypto_info));

/* Відправка зашифрованого файлу без копіювання у пам'ять користувача */
sendfile(sock_fd, file_fd, &offset, file_size);
