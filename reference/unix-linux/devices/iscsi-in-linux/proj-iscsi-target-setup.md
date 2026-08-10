# ⚙️ Налаштування iSCSI Target через LIO (targetcli)

Щоб перетворити сервер Linux на iSCSI-таргет і надати диск іншому серверу, використовується підсистема ядра LIO (Linux-IO Target) та зручна утиліта `targetcli`.

## Завдання

Надати локальний логічний том `/dev/vg0/iscsi_disk1` (розміром 50 ГБ) як iSCSI LUN для сервера-ініціатора з IP-адресою `192.168.1.50`. Наш сервер-таргет має IP `192.168.1.100`.

## Крок 1: Встановлення пакетів

У більшості сучасних дистрибутивів потрібно встановити `targetcli`:

```bash
sudo apt update
sudo apt install targetcli-fb
```

## Крок 2: Запуск інтерактивної оболонки

Запускаємо `targetcli` (від root). Ця утиліта має власну віртуальну файлову систему для налаштувань.

```bash
sudo targetcli
```
З'явиться запрошення виду `/>`. Ви можете використовувати `ls` для перегляду конфігурації та `cd` для навігації.

## Крок 3: Створення бекенду (Backstore)

Спершу треба пояснити підсистемі LIO, що саме ми будемо експортувати. У нашому випадку це блочний пристрій. LIO підтримує різні типи бекендів (fileio, block, ramdisk). Ми використаємо `block` (або `iblock`).

```text
/> cd /backstores/block
/backstores/block> create name=disk1 dev=/dev/vg0/iscsi_disk1
Created block storage object disk1 using /dev/vg0/iscsi_disk1.
```

## Крок 4: Створення IQN для Таргета

Тепер створимо сам iSCSI-таргет (його унікальне ім'я).

```text
/backstores/block> cd /iscsi
/iscsi> create iqn.2026-08.com.example:storage.target1
Created target iqn.2026-08.com.example:storage.target1.
Created TPG 1.
```

LIO автоматично створює Target Portal Group 1 (TPG 1) під цим таргетом.

## Крок 5: Додавання LUN

Прив'яжемо наш бекенд `disk1` до створеного таргета як LUN 0.

```text
/iscsi> cd iqn.2026-08.com.example:storage.target1/tpg1/luns
/iscsi/iqn.20...t1/tpg1/luns> create /backstores/block/disk1
Created LUN 0.
```

## Крок 6: Налаштування порталу (Portal)

Вказуємо, на якій IP-адресі таргет буде слухати запити (за замовчуванням він може слухати на `0.0.0.0`, що часто автоматично додається, але краще налаштувати явно).

```text
/iscsi/iqn.20...t1/tpg1/luns> cd ../portals
/iscsi/iqn.20...pg1/portals> delete 0.0.0.0 3260   # якщо існує
/iscsi/iqn.20...pg1/portals> create 192.168.1.100
Using default IP port 3260
Created network portal 192.168.1.100:3260.
```

## Крок 7: ACL (Контроль доступу)

iSCSI за замовчуванням забороняє підключення всім. Щоб ініціатор міг підключитися, ми маємо знати його IQN (з файлу `/etc/iscsi/initiatorname.iscsi` на клієнті). Припустимо, IQN ініціатора — `iqn.2005-03.com.redhat:01.client50`.

```text
/iscsi/iqn.20...pg1/portals> cd ../acls
/iscsi/iqn.20.../tpg1/acls> create iqn.2005-03.com.redhat:01.client50
Created Node ACL for iqn.2005-03.com.redhat:01.client50
Created mapped LUN 0.
```
*LIO автоматично дозволить цьому ініціатору доступ до LUN 0.*

Якщо ви хочете вимкнути CHAP (автентифікацію за паролем) і дозволити доступ лише на основі IQN, змініть налаштування TPG:
```text
/iscsi/iqn.20.../tpg1/acls> cd ..
/iscsi/iqn.20...rget1/tpg1> set attribute authentication=0
Parameter authentication is now '0'.
```

## Крок 8: Збереження конфігурації

Виходимо з `targetcli`. Конфігурація буде автоматично збережена у файл (зазвичай `/etc/target/saveconfig.json`).

```text
/> exit
Global pref auto_save_on_exit=true
Last 10 configs saved in /etc/target/backup/.
Configuration saved to /etc/target/saveconfig.json
```

Тепер ініціатор (`192.168.1.50`) може виконати Discovery і Login до `192.168.1.100` та отримати свій новий диск!
