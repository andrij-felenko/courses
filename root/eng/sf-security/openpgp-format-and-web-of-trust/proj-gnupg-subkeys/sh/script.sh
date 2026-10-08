#!/usr/bin/env bash
set -euo pipefail

# 1. Створення конфігураційного файла для неінтерактивної генерації майстер-ключа
cat <<EOF > gpg_master_spec.txt
Key-Type: EDDSA
Key-Curve: ed25519
Key-Usage: sign
Name-Real: Security Demo Master
Name-Email: master@example.com
Expire-Date: 0
%no-protection
%commit
EOF

echo "[+] Генерація первинного майстер-ключа підпису (Certify / Sign)..."
gpg --batch --generate-key gpg_master_spec.txt
rm -f gpg_master_spec.txt

KEY_ID=$(gpg --list-secret-keys --keyid-format LONG master@example.com | grep sec | awk '{print $2}' | cut -d'/' -f2)
echo "[+] Створено майстер-ключ ID: ${KEY_ID}"

# 2. Додавання підключа для шифрування (Encryption Subkey) та підпису (Signing Subkey)
echo "[+] Створення підключа шифрування (cv25519)..."
gpg --batch --quick-add-key "${KEY_ID}" cv25519 encr 1y

echo "[+] Створення підключа підпису (ed25519)..."
gpg --batch --quick-add-key "${KEY_ID}" ed25519 sign 1y

# 3. Експорт публічного та приватного ключів
echo "[+] Експорт публічного ключа..."
gpg --armor --export "${KEY_ID}" > public_key.asc

echo "[+] Експорт повного приватного ключа (майстер + підключі) для офлайн-архіву..."
gpg --armor --export-secret-keys "${KEY_ID}" > full_private_key.gpg.backup

echo "[+] Експорт лише приватних підключів (без майстер-ключа)..."
gpg --armor --export-secret-subkeys "${KEY_ID}" > subkeys_only.gpg.backup

# 4. Безпечне видалення майстер-ключа з локальної системи та імпорт лише підключів
echo "[+] Видалення секретного ключа з локального сховища..."
gpg --batch --yes --delete-secret-keys "${KEY_ID}"

echo "[+] Відновлення лише підключів для щоденного використання..."
gpg --import subkeys_only.gpg.backup

echo "[+] Перевірка стану секретних ключів (знак sec# означає, що майстер-ключ відсутній у локальному сховищі):"
gpg --list-secret-keys --keyid-format LONG "${KEY_ID}"
