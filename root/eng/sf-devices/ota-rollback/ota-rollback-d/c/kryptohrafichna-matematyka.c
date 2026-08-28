/* Безпечна перевірка статусу підпису, стійка до атак ін'єкції збоїв на C99 */
volatile uint32_t check1 = crypto_verify_signature(hash, sig, pubkey);
volatile uint32_t check2 = crypto_verify_signature(hash, sig, pubkey);

if ((check1 == CRYPTO_SUCCESS) && (check2 == CRYPTO_SUCCESS)) {
    /* Додатковий контроль через бітову маску */
    if ((check1 ^ check2) == 0x00000000UL) {
        boot_candidate_image();
    }
}
/* Будь-який збій ініціює аварійне блокування */
system_security_lockdown();
