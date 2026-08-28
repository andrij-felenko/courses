int ret = crypto_skcipher_encrypt(req);
if (ret == 0) {
    /* Операція виконана миттєво (synchronous fast-path) */
} else if (ret == -EINPROGRESS) {
    /* Запит поставлено в чергу апаратури; чекаємо на callback */
} else if (ret == -EBUSY) {
    /* Чергу переповнено: із CRYPTO_TFM_REQ_MAY_BACKLOG запит став у резервну чергу,
       без цього прапорця його відкинуто — надсилати треба повторно */
} else {
    /* Виникла помилка шифрування */
}
