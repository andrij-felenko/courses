# 📋 Довідник керування сном: /sys/power і шар systemd

Усі важелі, якими сном керують іззовні ядра, лежать у двох шарах: файли в `/sys/power/` — це сам інтерфейс ядра, а цілі, служби, гачки й заборонники systemd — обгортка, яка зрештою пише в ті самі файли. Тут зібрано обидва шари: що який файл приймає, що показує при читанні, і на якому щаблі перехоплюється кожне рішення.

![Ланцюг згори вниз: подія (systemctl suspend, кришка, кнопка) → logind питає заборонників → systemd-suspend.service читає sleep.conf → гачки system-sleep з аргументами pre suspend → запис у mem_sleep і state → ядро. Праворуч підписи, який важіль чіпляється до якого щабля; ліворуч — прямий запис у /sys/power/state повз усі верхні шари](img/control-path.svg)

*Кожен шар має свій важіль і бачить лише те, що проходить крізь нього: заборонники не зупинять прямого запису в sysfs, а гачки systemd про такий запис навіть не дізнаються.*

## Ворота: state і mem_sleep

Читання `/sys/power/state` дає перелік підтримуваних рядків; запис одного з них починає перехід, а сам виклик `write()` **повертається аж після пробудження**.

| рядок | що замовляє | коли присутній |
|---|---|---|
| `freeze` | s2idle — суто програмний сон | завжди |
| `standby` | S1 (ACPI power-on suspend) | якщо платформа оголосила S1 |
| `mem` | те, що зараз вибрано в `mem_sleep` | завжди |
| `disk` | гібернація | якщо ядро зібране з `CONFIG_HIBERNATION` |

`mem` — не стан, а покажчик. На що саме він показує, каже `/sys/power/mem_sleep`, де чинний варіант стоїть у квадратних дужках:

| рядок у `mem_sleep` | стан | ціна повернення |
|---|---|---|
| `s2idle` | suspend-to-idle | мілісекунди |
| `shallow` | standby / S1 | частка секунди |
| `deep` | suspend-to-RAM / S3 | одна–три секунди |

```sh
$ cat /sys/power/state
freeze mem disk
$ cat /sys/power/mem_sleep
[s2idle] deep
# echo deep > /sys/power/mem_sleep
# echo mem  > /sys/power/state      # повернеться вранці
```

Якщо `deep` у переліку **немає** — прошивка не оголосила S3, і жодним налаштуванням його не додати. Початковий вибір задає параметр [командного рядка ядра](topic:unix-linux/bootloader-and-cmdline) `mem_sleep_default=s2idle|shallow|deep`.

## Гібернація: disk, image_size, resume

`/sys/power/disk` вибирає, **що робити з машиною після того, як образ уже записано** — тим самим форматом «чинне в дужках»:

| значення | після запису образу |
|---|---|
| `platform` | стан на кшталт ACPI S4: прошивка знає, що система в гібернації, і дає більше способів розбудити |
| `shutdown` | звичайне вимкнення живлення |
| `reboot` | перезавантаження — щоб одразу перевірити відновлення |
| `suspend` | гібридний сон: образ на диску є, але засинаємо в пам'ять; прокинулися штатно — образ викидаємо |
| `test_resume` | діагностика: прочитати щойно записаний образ так, ніби машина вже перезавантажилася |

| файл | приймає | зміст |
|---|---|---|
| `/sys/power/image_size` | число (байти) | стеля образу «за змогою»; типово ≈ ⅖ оперативної пам'яті; `0` — тиснути максимально (довша підготовка, менший образ) |
| `/sys/power/resume` | `major:minor` пристрою | звідки читати образ; запис **запускає спробу відновлення** |
| `/sys/power/resume_offset` | число (блоки) | зсув для образу у **файлі** підкачки; писати **перед** `resume` |

Тут є пастка порядку. Свіже ядро мусить знайти образ ще до того, як хоч щось змонтовано, тому звичайне місце для цих значень — не sysfs, а командний рядок:

```
resume=UUID=6f2c-… resume_offset=34816
```

Файли в sysfs потрібні іншому клієнту: [initramfs](topic:unix-linux/initramfs), який відкрив [зашифрований том](topic:unix-linux/dm-crypt) і аж тепер може назвати пристрій. Зсув для файла підкачки береться з номера першого фізичного блоку — `filefrag -v /swapfile`; для [розділу підкачки](topic:unix-linux/swap-and-reclaim) `resume_offset` не потрібен зовсім.

## Гонка засинання: wakeup_count

`/sys/power/wakeup_count` — лічильник подій пробудження, і водночас протокол безпечного засинання. Записати в нього вдасться **лише те число, яке файл показував**: розбіжність означає, що подія вже сталася, і засинати не можна.

```sh
#!/bin/sh
count=$(cat /sys/power/wakeup_count) || exit 1
echo "$count" > /sys/power/wakeup_count || exit 1   # ✗ подія випередила нас
echo mem > /sys/power/state
```

Після вдалого запису ядро скасує перехід, щойно надійде хоч одна нова подія. Ядро зі `CONFIG_PM_WAKELOCKS` додає до цього андроїдну пару `/sys/power/wake_lock` та `/sys/power/wake_unlock` (ім'я утримувача, необов'язковий строк у наносекундах) і вмикач `/sys/power/autosleep`, куди пишуть той самий рядок, що і в `state`.

## Хто має право будити: атрибути в дереві пристроїв

Кожен пристрій, здатний будити, має в [sysfs](topic:unix-linux/sysfs-device-model) теку `power/`. Порожнє значення замість числа означає «пробудження для цього пристрою вимкнено».

| атрибут | приймає / показує |
|---|---|
| `power/wakeup` | `enabled` / `disabled` — єдиний тут запису́ваний; типово `enabled` лише для кнопки живлення, клавіатури й мережевої карти з Wake-on-LAN |
| `power/wakeup_count` | скільки подій пристрій подав |
| `power/wakeup_abort_count` | скільки з них зірвали вже початий перехід у сон |
| `power/wakeup_expire_count` | скільки подій протухло за строком |
| `power/wakeup_active` | `1`, поки подія в обробці |
| `power/wakeup_total_time_ms`, `power/wakeup_max_time_ms`, `power/wakeup_last_time_ms` | сумарний, найдовший і останній час обробки |
| `power/wakeup_prevent_sleep_time_ms` | скільки цей пристрій сумарно не давав системі заснути |
| `power/control` | `auto` / `on` — [присипляння на ходу](topic:unix-linux/runtime-power-management), окрема від системного сну річ |

Зведення по всіх джерелах одразу лежить у [debugfs](topic:unix-linux/pseudo-filesystems): `/sys/kernel/debug/wakeup_sources` — таблиця з ім'ям джерела, лічильниками подій і зривів та часом останньої зміни. Це перше місце, куди дивляться, коли машина «сама прокидається».

```sh
# echo enabled > /sys/bus/usb/devices/1-2/power/wakeup
# sort -k6 -nr /sys/kernel/debug/wakeup_sources | head
```

## Налагодження

| важіль | значення | що дає |
|---|---|---|
| `/sys/power/pm_test` | `none`, `freezer`, `devices`, `platform`, `processors`, `core` | зупинити спуск на заданому щаблі й одразу піти назад — так за кілька спроб знаходять поверх, який ламається |
| `/sys/power/pm_freeze_timeout` | мілісекунди, типово `20000` | скільки ядро чекає на задачу, що не заходить у холодильник |
| `no_console_suspend` (командний рядок) | — | не присипляти консоль; на ходу той самий вимикач — `/sys/module/printk/parameters/console_suspend` (`Y`/`N`) |
| `/sys/power/pm_debug_messages` | `1` / `0` | докладні повідомлення підсистеми в журнал |
| `/sys/power/pm_async` | `1` / `0` | паралельне присипляння пристроїв; `0` вибудовує їх у рядок і робить винуватця очевидним |
| `/sys/power/sync_on_suspend` | `1` / `0` | скидати кеш файлових систем перед сном |
| `/sys/power/pm_trace` | `1` / `0` | записати точку відмови в пам'ять годинника реального часу, щоб прочитати її після перезавантаження — ціною зіпсованого годинника |
| `/sys/power/suspend_stats/` | лише читання | `success`, `fail`, `last_failed_dev`, `last_failed_step` і лічильники зривів на кожному щаблі окремо |

## Шар systemd

Служби роблять рівно те, що вручну робить `echo`, — плюс порядок і сповіщення. [Ціль](topic:unix-linux/systemd-model) `sleep.target` спільна для всіх різновидів: юніт із `WantedBy=sleep.target` запускається перед сном і спиняється після пробудження.

| ціль | служба | що зрештою пише |
|---|---|---|
| `suspend.target` | `systemd-suspend.service` | `SuspendState=` у `state` |
| `hibernate.target` | `systemd-hibernate.service` | `HibernateMode=` у `disk`, тоді `disk` у `state` |
| `hybrid-sleep.target` | `systemd-hybrid-sleep.service` | те саме з режимом `suspend` |
| `suspend-then-hibernate.target` | `systemd-suspend-then-hibernate.service` | спершу сон у пам'ять, за строком — гібернація |

Налаштування — секція `[Sleep]` у `/etc/systemd/sleep.conf` (і теці `sleep.conf.d/`):

| директива | значення |
|---|---|
| `AllowSuspend=`, `AllowHibernation=`, `AllowHybridSleep=`, `AllowSuspendThenHibernate=` | `yes` / `no` — дозвіл на різновид узагалі |
| `SuspendState=` | список для `/sys/power/state`, пробуються по черзі; типово `mem standby freeze` |
| `MemorySleepMode=` | рядок для `/sys/power/mem_sleep` (`s2idle`, `shallow`, `deep`) |
| `HibernateMode=` | рядок для `/sys/power/disk`; типово `platform shutdown` |
| `HibernateDelaySec=` | скільки лежати в звичайному сні перед переходом у гібернацію |
| `SuspendEstimationSec=` | крок будильника, яким systemd сам оцінює швидкість розряду, коли строк не заданий |
| `HibernateOnACPower=` | `no` — не гібернувати, поки машина в розетці |

**Гачки** — виконувані файли в `/usr/lib/systemd/system-sleep/` та `/etc/systemd/system-sleep/`. Контракт: усі запускаються паралельно, перехід не триває, доки не завершиться останній; аргументів два.

```sh
#!/bin/sh
# /etc/systemd/system-sleep/50-wifi
# $1 — pre | post ; $2 — suspend | hibernate | hybrid-sleep | suspend-then-hibernate
case "$1/$2" in
    pre/*)  rfkill block wifi ;;
    post/*) rfkill unblock wifi ;;
esac
```

Для `suspend-then-hibernate` другий аргумент лишається незмінним усі рази, а котра саме фаза йде — каже змінна оточення `SYSTEMD_SLEEP_ACTION`: `suspend`, `hibernate` або `suspend-after-failed-hibernate`. Два обмеження варто знати наперед: сеанси користувача на цей момент уже заморожені, тож достукатися до них гачок не може, і **скасувати сон гачок не здатен** — його ненульовий код лише потрапить у журнал.

Скасовує сон інший механізм — **заборонники**. `systemd-inhibit` бере в [logind](topic:unix-linux/logind-sessions-seats) блокування й тримає його, поки живе запущена ним команда (технічно — поки відкритий файловий дескриптор, виданий через [D-Bus](topic:unix-linux/dbus)).

```sh
$ systemd-inhibit --what=sleep --who=backup --why="триває копіювання" \
      --mode=block  rsync -a /home /backup
$ systemd-inhibit --list
```

| ключ | значення |
|---|---|
| `--what=` | `shutdown`, `sleep`, `idle`, `handle-power-key`, `handle-suspend-key`, `handle-hibernate-key`, `handle-lid-switch`, `handle-reboot-key`; типово `idle:sleep:shutdown` |
| `--mode=block` | заборона без строку; обійти може лише привілейований клієнт — рішення ухвалює [polkit](topic:unix-linux/polkit) |
| `--mode=block-weak` | те саме, але власника блокування й привілейовані запити воно не стримує |
| `--mode=delay` | лише відкладає, і лише `sleep` та `shutdown`; межа — `InhibitDelayMaxSec=` з `logind.conf` |

Різниця між режимами практична: `block` — це «не смій», яким користуються довгі операції; `delay` — «дай доробити», яким користуються ті, кому треба кілька секунд на закриття з'єднань перед сном.
