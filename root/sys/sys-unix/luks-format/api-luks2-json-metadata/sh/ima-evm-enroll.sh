#!/usr/bin/env bash
# Розгортання стеку цілісності IMA/EVM поверх тома LUKS2: ключі в ключниці ядра,
# підписи security.ima та security.evm на системних деревах, перевірка результату.
#
# Запускати з правами root на вже відкритому томі LUKS2, який змонтовано в /.
set -euo pipefail

KEYDIR=${KEYDIR:-/etc/keys}
IMA_CERT="$KEYDIR/x509_ima.der"
IMA_PRIVKEY="$KEYDIR/privkey.pem"
EVM_BLOB="$KEYDIR/evm-key.blob"
TREES=(/usr/bin /usr/lib)
PROBE=/usr/bin/sudo

die() {
    printf 'ima-evm-enroll: %s\n' "$1" >&2
    exit 1
}

need_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "немає утиліти $1 (пакет $2)"
}

need_file() {
    [ -r "$1" ] || die "немає або нечитний файл $1"
}

[ "$(id -u)" -eq 0 ] || die "потрібні права root"

need_cmd keyctl keyutils
need_cmd evmctl ima-evm-utils
need_cmd getfattr attr

[ -d /sys/kernel/security/ima ] ||
    die "ядро зібране без IMA (немає /sys/kernel/security/ima) — підписи нікому перевіряти"

need_file "$IMA_CERT"
need_file "$IMA_PRIVKEY"
need_file "$EVM_BLOB"

# 1. Сертифікат перевірки підписів IMA — у ключницю ядра .ima.
if keyctl search %:.ima asymmetric x509_ima_cert >/dev/null 2>&1; then
    echo "1/5 сертифікат x509_ima_cert уже в ключниці .ima"
else
    keyctl padd asymmetric x509_ima_cert %keyring:.ima <"$IMA_CERT" >/dev/null ||
        die "ключниця .ima не приймає ключ: ядро могло її замкнути після завантаження"
    echo "1/5 сертифікат IMA завантажено"
fi

# 2. Симетричний ключ EVM (розпечатується TPM2) — у ключницю користувача, далі в .evm.
if keyctl search @u encrypted evm-key >/dev/null 2>&1; then
    echo "2/5 ключ evm-key уже розпечатано"
else
    keyctl add encrypted evm-key "load $(cat "$EVM_BLOB")" @u >/dev/null ||
        die "TPM2 не розпечатав evm-key: перевір політику PCR"
    echo "2/5 ключ evm-key розпечатано"
fi
keyctl padd trusted evm-key %keyring:.evm <"$EVM_BLOB" >/dev/null 2>&1 ||
    echo "    (ключниця .evm недоступна — HMAC-режим EVM лишиться вимкненим)"

# 3. Підписи security.ima на виконуваному коді й бібліотеках.
echo "3/5 підписування security.ima"
for tree in "${TREES[@]}"; do
    [ -d "$tree" ] || die "немає дерева $tree"
    evmctl ima_sign --key "$IMA_PRIVKEY" --cert "$IMA_CERT" -r "$tree"
done

# 4. Підписи security.evm поверх метаданих інода й усіх security.*-атрибутів.
echo "4/5 підписування security.evm"
for tree in "${TREES[@]}"; do
    evmctl sign --imahash --key "$IMA_PRIVKEY" -r "$tree"
done

# 5. Контроль: на пробному бінарнику мусять бути обидва атрибути.
echo "5/5 перевірка на $PROBE"
attrs=$(getfattr -m . -d -e hex "$PROBE" 2>/dev/null || true)
for xattr in security.ima security.evm; do
    printf '%s\n' "$attrs" | grep -q "^$xattr=" ||
        die "на $PROBE немає атрибута $xattr — підписування не спрацювало"
done
printf '%s\n' "$attrs" | grep -E '^security\.(ima|evm)='

cat <<'NOTE'

Лишилось увімкнути політику в командному рядку ядра й перезавантажитись:
    ima_policy=appraise_tcb ima_appraise=enforce evm=enforce
Доти ядро лише пише вимірювання в журнал і нічого не блокує.
NOTE
