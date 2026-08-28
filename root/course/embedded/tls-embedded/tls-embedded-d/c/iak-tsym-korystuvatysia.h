mbedtls_ssl_config conf;
mbedtls_ssl_config_init(&conf);

// ... тут завантажили кореневий сертифікат CA у ланцюг довіри ...
mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);   // ← ось корінь довіри

// ПРАВИЛЬНО: вимагати й перевіряти сертифікат сервера.
// якщо ланцюг не сходиться до нашого кореня — рукостискання провалиться.
mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);

// ЗГУБНО (так робити НЕ можна — це діра, яку ставлять «на час налагодження»):
// mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_NONE);
// шифр лишиться, але сервер не перевіряється — і повертається загроза
// «вдати з себе сервер» у повний зріст: шифруємо з ким завгодно.
