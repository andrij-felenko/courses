# суперблок 1.2 — на 8-му секторі; магія у перших чотирьох байтах
dd if=/dev/sdb1 bs=512 skip=8 count=1 2>/dev/null | od -An -tx1 -N 16
#  fc 4e 2b a9 01 00 00 00 01 00 00 00 00 00 00 00
#  └ magic ──┘ └ version ┘ └ feature_map = 1 — карта намірів

# лічильник подій: 8 байтів зі зсуву 200 всередині суперблока
dd if=/dev/sdb1 bs=1 skip=$((8 * 512 + 200)) count=8 2>/dev/null | od -An -tu8

# те саме з розшифруванням усіх полів
mdadm --examine /dev/sdb1
mdadm --examine-badblocks /dev/sdb1
