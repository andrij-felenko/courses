# Проект: Налаштування SCSI Fencing у кластері

Якщо ви розгортаєте кластер на базі Pacemaker та Corosync і використовуєте спільне блокове сховище (iSCSI, FC), ви можете налаштувати STONITH через SCSI PR. Це один із найнадійніших методів I/O Fencing.

1. Переконайтеся, що ваші LUN підтримують SCSI-3 PR (перевірте через `sg_persist --in --read-keys /dev/mapper/mpatha`).
2. Встановіть пакет агента:
   ```bash
   # RHEL/CentOS/AlmaLinux
   yum install fence-agents-scsi
   # Ubuntu/Debian
   apt install fence-agents
   ```
3. Створіть ресурс STONITH у кластері:
   ```bash
   pcs stonith create scsi-fencing fence_scsi devices=/dev/mapper/mpatha meta provides=unfencing
   ```
4. Під час збою (наприклад, втрати зв'язку), кластер автоматично викличе `fence_scsi`, який зробить дію `Preempt and Abort` для ключа проблемного вузла (`sg_persist -n -o -A -T 5 …`, див. `agents/scsi/fence_scsi.py`), повністю відключивши його від запису на диск і обірвавши його недограні команди.
