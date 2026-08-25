# 📋 Інтерфейс org.freedesktop.login1: об'єкти, методи, властивості

Просити logind щось **зробити** можна лише через системну шину — інших дверей у нього немає. А от **прочитати** його стан можна двома шляхами: тією ж шиною або збоку, бібліотекою `sd-login`, яка дивиться просто у файли стану під `/run/systemd/`. Тут зібрано обидва: шляхи об'єктів, сигнатури, типи властивостей, імена помилок, налаштування демона й C-функції.

## Об'єкти й шляхи

| об'єкт | шлях | інтерфейс |
|---|---|---|
| менеджер | `/org/freedesktop/login1` | `org.freedesktop.login1.Manager` |
| сеанс | `/org/freedesktop/login1/session/1` | `…login1.Session` |
| місце | `/org/freedesktop/login1/seat/seat0` | `…login1.Seat` |
| користувач | `/org/freedesktop/login1/user/_1000` | `…login1.User` |

Ідентифікатор сеансу в шляху проходить екранування міток [D-Bus](root:sys-unix/dbus), а UID користувача завжди йде з підкресленням попереду. Крім справжніх шляхів є псевдооб'єкти, що розкриваються відносно того, **хто питає**:

| псевдошлях | у що розкривається |
|---|---|
| `…/session/self` | сеанс того, хто викликає |
| `…/session/auto` | його ж сеанс, а як сеансу немає — дисплейний сеанс цього користувача |
| `…/seat/self`, `…/seat/auto` | місце відповідного сеансу |
| `…/user/self` | користувач, від чийого імені йде виклик |

Сигнали з псевдооб'єктів **не надходять**: їх шлють лише об'єкти зі справжнім ідентифікатором, бо «self» має сенс тільки в межах одного виклику. Підписка на `…/session/self` мовчатиме завжди.

**Найкоротший осмислений виклик — спитати, чи наш сеанс зараз попереду:**

```sh
$ busctl get-property org.freedesktop.login1 \
      /org/freedesktop/login1/session/auto \
      org.freedesktop.login1.Session Active
b true
```

## CreateSession: звідки береться сеанс

```
CreateSession(in  u uid, in  u pid, in  s service, in  s type, in  s class,
              in  s desktop, in  s seat_id, in  u vtnr, in  s tty, in  s display,
              in  b remote, in  s remote_user, in  s remote_host,
              in  a(sv) properties,
              out s session_id, out o object_path, out s runtime_path,
              out h fifo_fd, out u uid, out s seat_id, out u vtnr,
              out b existing)
```

| аргумент | зміст |
|---|---|
| `uid` | чий сеанс заводимо |
| `pid` | ватажок сеансу; `0` — той, хто викликає |
| `service` | ім'я служби [PAM](root:sys-unix/pam-stack), що зареєструвала вхід: `login`, `sshd`, `gdm-password` |
| `type` | `unspecified` · `tty` · `x11` · `wayland` · `mir` · `web` |
| `class` | `user` · `greeter` · `lock-screen` |
| `desktop` | назва середовища, коли відома (`GNOME`) — суто довідкове поле |
| `seat_id` | ім'я місця або порожній рядок, коли місця немає |
| `vtnr` | номер віртуальної консолі; `0`, коли її немає |
| `tty`, `display` | шлях термінала і/або ім'я дисплея X11 |
| `remote`, `remote_user`, `remote_host` | ознака мережевого входу та звідки він |
| `properties` | додаткові властивості для юніта-scope: список пар «ім'я — значення» |

| повернене | зміст |
|---|---|
| `session_id` | текстовий ідентифікатор (`3`, `c2`) |
| `object_path` | шлях новоствореного об'єкта на шині |
| `runtime_path` | `/run/user/<UID>` — те, що стає `XDG_RUNTIME_DIR` |
| `fifo_fd` | дескриптор-повідець: поки він (чи хоч одна його копія) відкритий, сеанс живий; закрився — logind починає згортати сеанс |
| `uid`, `seat_id`, `vtnr` | те, на чому logind зрештою зупинився: він має право виправити прохання |
| `existing` | `true`, коли процес уже був у сеансі й нового не заводили |

Метод позначено як привілейований, і кличе його рівно один клієнт — модуль `pam_systemd` у секції `session`. Прикладній програмі кликати його не можна: сеанс, заведений повз PAM, не матиме ані ватажка з живим повідцем, ані правильного оточення.

Від systemd 255 є двійник `CreateSessionWithPIDFD`: замість `u pid` бере `h pidfd`, а перед `properties` додає `t flags` (наразі мусить бути `0`). Різниця не косметична — [pidfd](root:sys-unix/pidfd) вказує на конкретний процес, а не на число, яке система може встигнути видати комусь іншому.

## Властивості сеансу

| властивість | тип | зміст |
|---|---|---|
| `Id`, `Name` | `s` | ідентифікатор сеансу й ім'я користувача |
| `User` | `(uo)` | UID разом зі шляхом об'єкта користувача |
| `Seat` | `(so)` | ім'я місця та шлях його об'єкта; порожнє, коли місця немає |
| `Leader` | `u` | PID процесу, що зареєстрував сеанс |
| `LeaderPIDFDId` | `t` | inode того самого процесу як pidfd — стійкий до повторного вживання PID |
| `Scope` | `s` | ім'я юніта-scope (`session-3.scope`) |
| `Service` | `s` | служба PAM, що завела сеанс |
| `Type` | `s` | `unspecified` · `tty` · `x11` · `wayland` · `mir` · `web` |
| `Class` | `s` | `user` · `greeter` · `lock-screen` |
| `State` | `s` | `online` (живий, але не попереду) · `active` (попереду на своєму місці) · `closing` (вихід оголошено, процеси дотлівають) |
| `Active` | `b` | те саме, що `State == "active"`, окремим прапорцем |
| `VTNr` | `u` | номер віртуальної консолі, `0` — немає |
| `TTY`, `Display` | `s` | шлях термінала; ім'я дисплея X11 |
| `Remote`, `RemoteHost`, `RemoteUser` | `b`, `s`, `s` | мережевий вхід і його походження |
| `Desktop` | `s` | середовище робочого столу, коли відоме |
| `Audit` | `u` | номер сеансу підсистеми [аудиту](root:sys-unix/audit-framework) ядра |
| `IdleHint`, `IdleSinceHint` | `b`, `t` | простій: сеанс сам про нього повідомляє, ядро цього не знає |
| `LockedHint` | `b` | екран замкнено — теж підказка від середовища, а не спостереження |
| `CanIdle`, `CanLock` | `b` | чи взагалі має сенс питати про попередні дві |
| `ExtraDeviceAccess` | `as` | додаткові класи пристроїв: для кожного `ID` сеанс дістає доступ до вузлів із міткою `xaccess-ID` |

Частка `Hint` у назвах не випадкова: простій і замкнений екран — це те, що сеанс **сказав** про себе методами `SetIdleHint`/`SetLockedHint`, а не те, що logind виміряв.

## Місце й користувач

| `…login1.Seat` | тип / підпис | зміст |
|---|---|---|
| `Id` | `s` | `seat0`, `seat1`, … |
| `ActiveSession` | `(so)` | єдиний сеанс, що зараз попереду |
| `Sessions` | `a(so)` | усі сеанси цього місця |
| `CanTTY`, `CanGraphical` | `b` | чи придатне місце для текстового й для графічного входу |
| `ActivateSession(s)` | метод | вивести названий сеанс уперед |
| `SwitchTo(u)`, `SwitchToNext()`, `SwitchToPrevious()` | метод | те саме, але за номером віртуальної консолі |
| `Terminate()` | метод | згорнути всі сеанси місця |

`CanGraphical` — не здогад: місце існує лише тому, що [udev](root:sys-unix/udev-rules) виставив пристроям властивість `ID_SEAT`, а один із них ще й позначив міткою `master-of-seat`. Постійну приписку робить менеджер — `AttachDevice(seat_id, sysfs_path, interactive)`, а скасовує `FlushDevices(interactive)`.

| `…login1.User` | тип | зміст |
|---|---|---|
| `UID`, `GID`, `Name` | `u`, `u`, `s` | хто це |
| `RuntimePath` | `s` | `/run/user/<UID>` |
| `Slice`, `Service` | `s` | `user-1000.slice` і `user@1000.service` |
| `Display` | `(so)` | «головний» графічний сеанс користувача |
| `Sessions` | `a(so)` | усі його сеанси |
| `State` | `s` | `offline` · `lingering` · `online` · `active` · `closing` |
| `Linger` | `b` | чи дозволено юнітам жити без жодного входу |

## Захоплення пристроїв

| метод | підпис | що робить |
|---|---|---|
| `TakeControl` | `(in b force)` | заявити себе розпорядником сеансу; `force` (лише для root) виштовхує чинного |
| `ReleaseControl` | `()` | зректися; водночас відпускає всі взяті пристрої |
| `TakeDevice` | `(in u major, in u minor, out h fd, out b inactive)` | дістати відкритий дескриптор символьного пристрою за [номерами](root:sys-unix/major-minor-numbers) |
| `ReleaseDevice` | `(in u major, in u minor)` | віддати його назад |
| `PauseDeviceComplete` | `(in u major, in u minor)` | відповісти «я вже не тримаю» на прохання спинитися |
| `SetBrightness` | `(in s subsystem, in s name, in u brightness)` | яскравість `backlight`/`leds` без прав root |

| сигнал | підпис | коли |
|---|---|---|
| `PauseDevice` | `(u major, u minor, s type)` | пристрій спиняють; `type` — `pause`, `force` або `gone` |
| `ResumeDevice` | `(u major, u minor, h fd)` | пристрій повертають, і **новим** дескриптором |
| `Lock`, `Unlock` | `()` | середовищу наказано замкнути чи відімкнути екран |

Три значення `type` означають різні речі. `pause` — logind дає обмежений час спинитися самому й **чекає** на `PauseDeviceComplete`; не дочекавшись, зробить те саме силою. `force` — уже зробив, це лише сповіщення. `gone` — пристрій вийняли з машини, віддавати нема чого.

Порядок повідомлень гарантовано: `PauseDevice` приходить **перед** зміною властивості `Active`, а `ResumeDevice` — **після** неї. Клієнт, який дочікується `Active = false` і аж тоді припиняє читати пристрій, спізнюється завжди.

Обмежень п'ять, і кожне варто знати наперед: пристрій мусить належати місцю **цього** сеансу; підтримано лише частину класів символьних пристроїв; один пристрій береться рівно один раз, доки не відпущений; розрив з'єднання з шиною знімає і розпорядництво, і всі дескриптори; поки сеанс неактивний, виданий дескриптор приглушено (`inactive = true` вже у відповіді).

## Inhibit: попросити систему зачекати

```
Inhibit(in s what, in s who, in s why, in s mode, out h pipe_fd)
```

Замок тримається, поки відкритий повернений дескриптор, — і жодної миті довше. `what` — одне або кілька значень через двокрапку:

| `what` | що стримує |
|---|---|
| `shutdown` | вимкнення й перезавантаження |
| `sleep` | [сон і гібернацію](root:sf-os/suspend-and-resume) |
| `idle` | автоматичну дію за простоєм |
| `handle-power-key`, `handle-suspend-key`, `handle-hibernate-key`, `handle-reboot-key`, `handle-lid-switch` | власну обробку клавіш і кришки самим logind |

| `mode` | сила |
|---|---|
| `block` | заборона: дія не станеться, поки замок живий |
| `block-weak` | те саме, але привілейований запит і сам власник замка його обходять |
| `delay` | лише відкладає — і не довше за `InhibitDelayMaxSec`; чинне тільки для `sleep` і `shutdown` |

Право взяти замок дає [polkit](root:sys-unix/polkit), і дія в нього своя на кожну пару: `org.freedesktop.login1.inhibit-block-shutdown`, `…inhibit-delay-sleep`, `…inhibit-block-idle`, `…inhibit-handle-lid-switch` і решта. Перелік чинних замків віддає `ListInhibitors() → a(ssssuu)`: `what`, `who`, `why`, `mode`, UID, PID.

## Решта менеджера

| метод | підпис |
|---|---|
| `ActivateSession`, `ActivateSessionOnSeat` | `(in s session_id[, in s seat_id])` |
| `LockSession`, `UnlockSession` | `(in s session_id)`; на всі одразу — `LockSessions()`, `UnlockSessions()` |
| `GetSession`, `GetSessionByPID` | `(in s session_id, out o path)` та `(in u pid, out o path)` |
| `ListSessions` | `(out a(susso))` — ід, UID, ім'я, місце, шлях |
| `ListSessionsEx` | `(out a(sussussbto))` — те саме плюс PID ватажка, клас, tty, підказка простою й час |
| `KillSession` | `(in s session_id, in s whom, in i signal)`, де `whom` — `leader` або `all` |
| `KillUser` | `(in u uid, in i signal)` |
| `TerminateSession`, `TerminateUser`, `TerminateSeat` | `(in s id)` / `(in u uid)` |
| `SetUserLinger` | `(in u uid, in b enable, in b interactive)` — те, що робить `loginctl enable-linger` |
| `AttachDevice`, `FlushDevices` | `(in s seat_id, in s sysfs_path, in b interactive)` / `(in b interactive)` |

Сигнали менеджера: `SessionNew`/`SessionRemoved`, `UserNew`/`UserRemoved`, `SeatNew`/`SeatRemoved` — усі несуть ідентифікатор і шлях; `PrepareForShutdown(b)` і `PrepareForSleep(b)` приходять двічі — з `true` перед дією й `false` після неї.

Помилки — власні імена, не загальні коди:

| ім'я | коли |
|---|---|
| `org.freedesktop.login1.NoSuchSession` · `NoSuchSeat` · `NoSuchUser` | названого об'єкта немає |
| `org.freedesktop.login1.NoSessionForPID` · `NoUserForPID` | процес не належить жодному сеансу |
| `org.freedesktop.login1.NotInControl` | не викликали `TakeControl` |
| `org.freedesktop.login1.DeviceIsTaken` · `DeviceNotTaken` · `NotYourDevice` | пристрій уже взято, ще не взято або взято не вами |
| `org.freedesktop.login1.SessionNotOnSeat` | сеанс просять активувати на чужому місці |
| `org.freedesktop.login1.BlockedByInhibitorLock` | дію спинив чийсь `block`-замок |

## logind.conf

Секція `[Login]` у `/etc/systemd/logind.conf` і в накладках із теки `logind.conf.d/`. Нижче — значення, з якими systemd приходить від розробників; дистрибутиви частину з них перевизначають.

| директива | типово | зміст |
|---|---|---|
| `NAutoVTs` | `6` | скільки віртуальних консолей отримують `getty` при переході на них |
| `ReserveVT` | `6` | консоль, яку тримають вільною завжди |
| `KillUserProcesses` | `yes` | чи вбивати процеси сеансу при виході (збірковий ключ `-Ddefault-kill-user-processes=`) |
| `KillExcludeUsers` | `root` | кого це не стосується |
| `InhibitDelayMaxSec` | `5` | стеля для `delay`-замків |
| `UserStopDelaySec` | `10s` | скільки тримати `user@.service` після останнього виходу |
| `HandlePowerKey` | `poweroff` | клавіша живлення |
| `HandleRebootKey` · `HandleSuspendKey` · `HandleHibernateKey` | `reboot` · `suspend` · `hibernate` | решта клавіш |
| `HandleLidSwitch` | `suspend` | кришка ноутбука |
| `HandleLidSwitchDocked` | `ignore` | кришка, коли машина в док-станції або має другий екран |
| `HandleLidSwitchExternalPower` | не задано | поведінка від розетки; поки не виставлено явно — діє попереднє |
| `LidSwitchIgnoreInhibited` | `yes` | кришка не зважає на `sleep`-замки (клавіші — зважають) |
| `HoldoffTimeoutSec` | `30s` | не реагувати на кришку одразу після старту чи пробудження |
| `IdleAction` | `ignore` | що робити за простоєм: `suspend`, `poweroff`, `lock`, … |
| `IdleActionSec` | `30min` | скільки чекати перед цим |
| `RuntimeDirectorySize` | `10%` | стеля `/run/user/<UID>` |
| `RemoveIPC` | `yes` | виносити черги, семафори й спільну пам'ять UID після останнього виходу |
| `SessionsMax`, `InhibitorsMax` | `8192` | стелі |
| `StopIdleSessionSec` | `infinity` | вимикати сеанси, що простоюють; `greeter` і `lock-screen` не чіпає |

Дії з `Handle…` перебиває низькорівневий замок (`handle-power-key` і його родичі): доки середовище тримає такий замок, налаштування просто не діють.

## sd-login: ті самі відповіді без шини

Бібліотека `sd-login` (частина `libsystemd`) не шле жодного повідомлення: вона читає cgroup процесу й файли стану під `/run/systemd/{sessions,seats,users}/`. Тому вона годиться там, де відповідь потрібна синхронно й де чекати на демона не можна.

| функція | що дає |
|---|---|
| `sd_pid_get_session(pid, &s)` | сеанс процесу — розбором його [cgroup](root:sys-unix/cgroups-resource-model), тому підробити відповідь неможливо |
| `sd_pid_get_owner_uid(pid, &uid)` | UID власника сеансу |
| `sd_peer_get_session(fd, &s)` | те саме для співрозмовника на [сокеті Unix](root:sys-unix/unix-domain-sockets) — без гонки з підміною PID |
| `sd_session_is_active(s)`, `sd_session_is_remote(s)` | `>0` — так, `0` — ні |
| `sd_session_get_state/seat/type/class/uid/tty/vt(s, …)` | окремі властивості сеансу |
| `sd_seat_get_active(seat, &s, &uid)` | хто зараз попереду на місці |
| `sd_seat_can_tty(seat)`, `sd_seat_can_graphical(seat)` | придатність місця |
| `sd_uid_is_on_seat(uid, require_active, seat)` | чи цей користувач на цьому місці |
| `sd_get_sessions/seats/uids(&list)` | перелічити все |
| `sd_login_monitor_new(category, &m)` | стежити за змінами; `category` — `session`, `seat`, `uid`, `machine` або `NULL` на все |

Повертають вони `0` або від'ємний `errno`: `-ENODATA` — поля для цього об'єкта немає (процес поза сеансом, сеанс без місця), `-ENXIO` — такого сеансу немає. Аргумент `pid = 0` означає «я сам», `session = NULL` — «мій сеанс».

**Найменша повна програма — хто я і де сиджу:**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-login.h>

int main(void) {
    char *session = NULL, *seat = NULL;
    int r;

    r = sd_pid_get_session(0, &session);      /* 0 — цей процес */
    if (r < 0) {
        fprintf(stderr, "поза сеансом: %s\n", strerror(-r));
        return 1;
    }

    r = sd_session_get_seat(session, &seat);  /* -ENODATA — сеанс без місця */

    printf("сеанс %s, місце %s, попереду: %s\n",
           session,
           r < 0 ? "немає" : seat,
           sd_session_is_active(session) > 0 ? "так" : "ні");

    free(session);
    free(seat);
    return 0;
}
```

```sh
$ cc login.c -o login $(pkg-config --cflags --libs libsystemd)
$ ./login
сеанс 3, місце seat0, попереду: так
```

Стежити за змінами теж можна без шини: `sd_login_monitor_get_fd()` віддає [дескриптор](root:sys-unix/file-descriptor), придатний для `poll()`, а після кожного пробудження треба покликати `sd_login_monitor_flush()` — інакше дескриптор будитиме цикл подій без упину.
