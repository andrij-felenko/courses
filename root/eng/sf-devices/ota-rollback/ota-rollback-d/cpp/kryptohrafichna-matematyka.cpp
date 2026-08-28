// Безпечна перевірка статусу підпису, стійка до атак ін'єкції збоїв на C++20
volatile auto check1 = crypto::verifySignature(hash, sig, pubkey);
volatile auto check2 = crypto::verifySignature(hash, sig, pubkey);

if ((check1 == crypto::Status::Success) && (check2 == crypto::Status::Success)) {
    // Додатковий контроль через бітову маску
    if ((static_cast<uint32_t>(check1) ^ static_cast<uint32_t>(check2)) == 0) {
        bootCandidateImage();
    }
}
// Будь-який збій ініціює аварійне блокування
systemSecurityLockdown();
