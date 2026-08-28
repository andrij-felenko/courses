#!/bin/sh
# walk-the-chain.sh — по одному доказу на кожну ланку ланцюга завантаження.
# Нічого не змінює. Частину виводу може приховати kernel.dmesg_restrict.

say() { printf '\n== %s ==\n' "$1"; }
cmdline=$(cat /proc/cmdline)

say "1. прошивка"
if [ -d /sys/firmware/efi ]; then
    echo "ядро дістало таблицю EFI → вхід через UEFI"
    efibootmgr 2>/dev/null | grep -E '^BootCurrent|^BootOrder' \
        || echo "efibootmgr не встановлено"
else
    echo "каталогу /sys/firmware/efi немає → вхід через BIOS або режим сумісності"
fi

say "2. рядок параметрів"
echo "$cmdline"
case " $cmdline " in
    *" BOOT_IMAGE="*) echo "→ рядок складав GRUB: звіряти з /boot/grub/grub.cfg" ;;
    *) echo "→ BOOT_IMAGE немає: systemd-boot, вшитий у образ рядок або ядро прямо з ESP" ;;
esac
case "$cmdline" in
    *root=UUID=*|*root=LABEL=*) echo "→ корінь заданий міткою: без initramfs не обійтися" ;;
esac

say "3. образ initramfs"
img=/boot/initrd.img-$(uname -r)
[ -f "$img" ] || img=/boot/initramfs-$(uname -r).img
if [ -f "$img" ]; then
    printf '%s\n  розмір %s Б, змінений %s\n' \
        "$img" "$(stat -c %s "$img")" "$(stat -c %y "$img")"
    boot=$(awk -v now="$(date +%s)" '{ printf "%d", now - $1 }' /proc/uptime)
    if [ "$(stat -c %Y "$img")" -gt "$boot" ]; then
        echo "  ⚠ файл молодший за поточний запуск — його перегенерували вже після завантаження"
    else
        echo "  файл старший за запуск — завантажувався саме він"
    fi
else
    echo "образу немає — ядро монтувало корінь власними драйверами"
fi

say "4. перехід switch_root"
dmesg 2>/dev/null | grep -m1 'as init process' \
    || echo "рядок недоступний (закритий dmesg або переповнений буфер)"
journalctl -b -o short-monotonic 2>/dev/null | grep -m1 'Switching root' \
    || echo "переходу в журналі немає — в initramfs працював не systemd, а оболонка"

say "5. хто такий PID 1"
printf 'exe:     %s\n' "$(readlink /proc/1/exe)"
printf 'argv[0]: %s\n' "$(tr '\0' ' ' < /proc/1/cmdline)"
printf 'корінь:  %s\n' "$(findmnt -no SOURCE,FSTYPE /)"
ticks=$(sed 's/.*) //' /proc/1/stat | awk '{print $20}')
awk -v t="$ticks" -v hz="$(getconf CLK_TCK)" \
    'BEGIN { printf "старт:   %.2f с від завантаження\n", t / hz }'
[ -e /etc/initrd-release ] && echo "⚠ /etc/initrd-release на місці — це ще тимчасовий корінь"

say "6. розкладка часу"
if command -v systemd-analyze >/dev/null; then
    systemd-analyze time
    ls /sys/firmware/efi/efivars 2>/dev/null | grep -q LoaderTimeInitUSec \
        && echo "→ завантажувач веде облік: рядки firmware і loader будуть" \
        || echo "→ завантажувач не пише LoaderTime*: цих рядків не буде, і це нормально"
else
    echo "systemd немає — розкладку показати нічим"
fi
