sudo integritysetup open /dev/loop0 int0
sudo mount /dev/mapper/int0 /mnt/int
sudo cat /mnt/int/probe.txt > /dev/null
# cat: /mnt/int/probe.txt: Input/output error

sudo dmesg | tail -4
# device-mapper: integrity: dm-0: Checksum failed at sector 0x1a48
# Buffer I/O error on dev dm-0, logical block 841, async page read
sudo dmsetup status int0
# 0 507904 integrity 1 507904 -
#                              ^ позиція перерахунку («-» — не рахували)
#                        ^ скільки секторів віддає ціль нагору
#              ^ лічильник розбіжностей
