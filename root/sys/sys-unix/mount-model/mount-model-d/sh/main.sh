$ df -h /
Файлова система   Розмір  Викор.  Дост.  Вик%  Змонтовано
/dev/sda2            40G     38G   1.2G   97%  /

$ du -sh /var/log
420M    /var/log            # усе, що видно, — дрібниця

$ mount | grep /var/log
/dev/sda3 on /var/log type ext4 (rw,relatime)

$ umount /var/log && du -sh /var/log
31G     /var/log            # ось вони, 31 ГіБ під точкою монтування
