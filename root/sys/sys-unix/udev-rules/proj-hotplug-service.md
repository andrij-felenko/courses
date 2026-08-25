# ⚙️ Правило плюс служба: як зустріти пристрій довгою роботою

Зберемо установку, у якій увімкнений у гніздо перехідник сам піднімає агента, що з ним розмовляє, а висмикнутий — сам того агента ховає. Ніякого `systemctl start` руками — і жодного процесу-сироти, який після висмикування шнура крутиться й лається в порожнечу.

## Чого хочемо

```sh
$ systemctl list-units --type=device 'dev-ttyUSB*'
UNIT               LOAD   ACTIVE SUB     DESCRIPTION
dev-ttyUSB0.device loaded active plugged FT232 USB-Serial

$ systemctl is-active laser-agent@ttyUSB0.service
active

# висмикнули шнур
$ systemctl is-active laser-agent@ttyUSB0.service
inactive
```

Агент — звичайна програма: відкриває послідовний порт, налаштовує швидкість, читає рядки від верстата й пише їх у журнал. Уся складність не в ній, а в тому, **хто нею володіє**.

## Чому цього не зробити з RUN

Спокуса очевидна: правило вже спрацювало на потрібний пристрій, лишилося дописати `RUN+="/usr/local/lib/laser-agent /dev/%k &"`. Не працює, і кожна з трьох причин самостійна.

**Демон убивають разом із подією.** Робочий процес udev, який обробляє подію, після останнього правила прибирає за собою все, що встиг породити. Довідка `udev(7)` каже це без натяків: запускати демонів заборонено, а породжені процеси — «detached or not», відв'язані чи ні — будуть безумовно вбиті, коли обробку події завершено. Тобто ані `&`, ані `setsid`, ані `nohup` не рятують: рахують не батьківське посилання, а сам факт народження всередині події.

**Поки програма живе, подія триває.** На обробку однієї події є ліміт — типово 180 секунд (`--event-timeout=` демона, або `udev.event_timeout=` у командному рядку ядра). Агент, який не збирається завершуватись ніколи, упреться в цю стелю, і подію обірвуть разом із ним. А до тієї хвилини робочий процес зайнятий саме ним, і події цього пристрою та його нащадків стоять у черзі.

**Пісочниця.** `systemd-udevd.service` працює під жорсткими обмеженнями, і їх успадковує все, що запущено з правил: доступ до мережі демонові закрито, а простір монтування в нього власний — змонтоване з правила побачить лише він сам. Агент, що звітує на сервер, з `RUN` не запрацює взагалі — і зламається не помилкою, яку видно, а тишею.

Отже, `RUN` — це тицьнути пальцем: записати байт у sysfs, увімкнути живлення, покласти прапорець. Робота живе деінде.

## Ідея: правило називає, systemd тримає

Передача робиться двома рядками й спирається на те, що systemd уже вміє показувати пристрої юнітами.

Позначка `TAG+="systemd"` робить пристрій видимим для менеджера служб: із цієї миті існує юніт `dev-ttyUSB0.device`, який активний рівно тоді, коли пристрій на місці. Без позначки жодна з властивостей, названих нижче, навіть не читається — пристрою для systemd просто немає. Кому тег дістається типово, вирішують правила дистрибутива: блоковим і мережевим пристроям його ставлять завжди, решта залежить від набору правил і версії systemd. Тому його пишуть у власному правилі й тоді, коли він, можливо, вже є: тег тримає список, і `+=` того самого значення нічого не псує.

Властивість `SYSTEMD_WANTS` називає юніт, який слід підняти, коли юніт пристрою стає активним. Це залежність виду `Wants=` — «добре б підняти», без зобов'язань.

А зворотний хід — зупинку — не програмують узагалі. Його дає `BindsTo=` в самій службі: юніт, прив'язаний до неактивного юніта, зупиняється. Довідка `systemd.unit(5)` серед причин, з яких прив'язаний юніт раптово стає неактивним, називає саме наш випадок — «пристрій під юнітом пристрою висмикнули».

![Три ланцюжки. Червоний: подія add — правило з RUN — агент працює всередині події — подію завершено, усе породжене вбито. Зелений: подія add — правило з TAG systemd і SYSTEMD_WANTS — подію завершено, робочий процес вільний — systemd підняв laser-agent@ttyUSB0 у власному cgroup. Синій: подія remove — dev-ttyUSB0.device стає неактивним — BindsTo і After зупиняють службу](img/handoff-run-vs-service.svg)

*Різниця не в тому, хто запускає агента, а в тому, у чиєму житті він живе: події udev — чи менеджера служб.*

## Правило

```udev
# /etc/udev/rules.d/70-laser-agent.rules
ACTION!="remove", SUBSYSTEM=="tty", \
  ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="A6008isP", \
  SYMLINK+="laser", GROUP="dialout", MODE="0660", \
  TAG+="systemd", ENV{SYSTEMD_WANTS}+="laser-agent@%k.service"
```

Три дрібниці, кожна з причиною. `%k` підставляє ім'я пристрою від ядра — `ttyUSB0`, тож примірник служби ми називаємо самі. `+=` замість `=` і в тегові, і у властивості: обидва тримають список, а до нас у цьому списку вже могли щось покласти правила дистрибутива, і затирати їх немає підстав. `ACTION!="remove"` замість звичного `ACTION=="add"` — про це нижче, у пастках.

## Юніт-шаблон

```ini
# /etc/systemd/system/laser-agent@.service
[Unit]
Description=Агент верстата на /dev/%i
BindsTo=dev-%i.device
After=dev-%i.device

[Service]
Type=exec
ExecStart=/usr/local/lib/laser-agent /dev/%i
Restart=on-failure
RestartSec=2s
User=laser
SupplementaryGroups=dialout
```

`BindsTo=` і `After=` стоять парою навмисно. Сама по собі прив'язка зупиняє службу, коли пристрій зникає. Разом із упорядкуванням вона стає строгішою: юніт, до якого ми прив'язані, **мусить бути активним**, поки активні ми, — а отже, служба не спробує стартувати попереду пристрою й гарантовано піде слідом за ним. Довідка радить поєднувати їх у більшості випадків саме тому.

`Type=exec` означає, що службу вважають запущеною, коли `execve` вдався, — агент нікуди не відгалужується, і [долати демонізацію](root:sys-unix/daemonize) тут не треба. `Restart=on-failure`, а не `always`: висмикнутий шнур — не збій, і перезапускатися після нього нема сенсу. Розділ `[Install]` відсутній, і це не забудькуватість — шаблон нікому не вмикають, його тягне пристрій. Про решту важелів — [життєвий цикл служби](root:sys-unix/service-lifecycle) і [модель юнітів systemd](root:sys-unix/systemd-model).

Шаблон, а не звичайний юніт, узятий не для краси. Увімкніть у сусіднє гніздо другий такий самий перехідник — і піднімуться `laser-agent@ttyUSB0` і `laser-agent@ttyUSB1`, кожен зі своїм пристроєм, своєю прив'язкою, своїм лічильником перезапусків і своїм рядком у журналі. Один юніт на всіх дав би замість цього одну службу, яка мусила б сама стежити, скільки в неї нині пристроїв, — тобто робити вдруге те, що systemd уже зробив. Різне налаштування для різних верстатів чіпляють тим самим примірником: `EnvironmentFile=-/etc/laser/%i.conf`.

![Ланцюг імен. Угорі подія про ttyUSB0 з KERNEL, DEVNAME. Униз три гілки: шлях у /dev, екранований systemd, дає dev-ttyUSB0.device; %k, підставлений правилом у SYSTEMD_WANTS, дає laser-agent@ttyUSB0.service; порожній примірник laser-agent@.service дає примірник зі шляху sysfs. Унизу: у юніті BindsTo=dev-%i.device, %i — примірник як є, тоді як %I розгорнув би дефіс у скісну риску](img/unit-naming.svg)

*Три імені з однієї події — і жодне не виводиться з іншого автоматично.*

## Агент

Задача агента вузька: відкрити порт, читати рядки й **чесно померти** — і за сигналом, і коли пристрій зник. Нижче дві рівноцінні версії: Python — коли агента кладуть разом із дистрибутивом і правлять просто на машині; Go — коли на десяток цехових коробок везуть один статичний файл.

:::tabs

```python
#!/usr/bin/env python3
"""Агент послідовного пристрою: живе рівно стільки, скільки живе пристрій."""
import errno, os, select, signal, sys, termios

SPEED = termios.B115200


def open_port(path):
    # O_NOCTTY — не робити цей термінал керівним для процесу.
    # O_NONBLOCK — не зависнути в open, чекаючи на сигнал носія.
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    iflag, oflag, cflag, lflag, _, _, cc = termios.tcgetattr(fd)
    iflag = 0                        # без перекладів CR/LF і без XON/XOFF
    oflag = 0
    lflag = 0                        # сирий режим: без рядків і без відлуння
    cflag = termios.CS8 | termios.CREAD | termios.CLOCAL
    cc = list(cc)
    cc[termios.VMIN] = 1
    cc[termios.VTIME] = 0
    termios.tcsetattr(fd, termios.TCSANOW,
                      [iflag, oflag, cflag, lflag, SPEED, SPEED, cc])
    termios.tcflush(fd, termios.TCIFLUSH)
    return fd


def main(path):
    # Самопіпа: обробник сигналу лише будить select, рішення ухвалює цикл.
    wake_r, wake_w = os.pipe()
    os.set_blocking(wake_w, False)
    signal.set_wakeup_fd(wake_w)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: None)   # без обробника fd не збудять

    fd, tail = open_port(path), b""
    print(f"агент {path}: почали", flush=True)

    while True:
        ready, _, _ = select.select([fd, wake_r], [], [])
        if wake_r in ready:
            print("SIGTERM: закриваємо порт", flush=True)
            break
        try:
            chunk = os.read(fd, 4096)
        except OSError as e:
            if e.errno == errno.EAGAIN:
                continue
            if e.errno in (errno.EIO, errno.ENXIO, errno.ENODEV):
                print("пристрій зник", flush=True)
                break                         # НЕ помилка, інакше перезапустять
            raise
        if not chunk:                         # POLLHUP: шнур висмикнули
            print("порт закрито з того боку", flush=True)
            break
        tail += chunk
        *lines, tail = tail.split(b"\n")
        for ln in lines:
            print("верстат:", ln.rstrip(b"\r").decode("ascii", "replace"),
                  flush=True)                 # stdout забирає journald

    os.close(fd)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

```go
// go get golang.org/x/sys/unix
package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"os/signal"

	"golang.org/x/sys/unix"
)

func openPort(path string) (*os.File, error) {
	fd, err := unix.Open(path, unix.O_RDWR|unix.O_NOCTTY|unix.O_NONBLOCK, 0)
	if err != nil {
		return nil, fmt.Errorf("open %s: %w", path, err)
	}
	// На Linux швидкість живе в бітах CBAUD усередині c_cflag —
	// полів Ispeed/Ospeed ядро при TCSETS не читає.
	t := unix.Termios{Cflag: unix.CS8 | unix.CREAD | unix.CLOCAL | unix.B115200}
	t.Cc[unix.VMIN], t.Cc[unix.VTIME] = 1, 0
	if err := unix.IoctlSetTermios(fd, unix.TCSETS, &t); err != nil {
		unix.Close(fd)
		return nil, fmt.Errorf("termios: %w", err)
	}
	// Дескриптор лишається неблокувальним — так os.File потрапляє під
	// опитувач середовища виконання, і Close розбудить чужий Read.
	return os.NewFile(uintptr(fd), path), nil
}

func main() {
	port, err := openPort(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("агент %s: почали\n", port.Name())

	sigc := make(chan os.Signal, 1)
	signal.Notify(sigc, unix.SIGTERM, unix.SIGINT)
	go func() {
		<-sigc
		fmt.Println("SIGTERM: закриваємо порт")
		port.Close() // розблокує Read у головній горутині
	}()

	sc := bufio.NewScanner(port)
	for sc.Scan() {
		fmt.Println("верстат:", sc.Text()) // stdout забирає journald
	}

	switch err := sc.Err(); {
	case err == nil, errors.Is(err, io.EOF), errors.Is(err, os.ErrClosed):
		// нас закрили за сигналом або шнур висмикнули
	case errors.Is(err, unix.EIO), errors.Is(err, unix.ENODEV),
		errors.Is(err, unix.ENXIO):
		fmt.Println("пристрій зник") // теж не збій: виходимо нулем
	default:
		fmt.Fprintln(os.Stderr, "читання:", err)
		os.Exit(1)
	}
}
```

:::

Обидві версії роблять одне й те саме і в одному місці однаково вперті: **зникнення пристрою — це не помилка**. Вихід із ненульовим кодом тут коштував би нового примірника служби, запущеного на вузол, якого вже немає. Чому порт відкривають із `O_NOCTTY` і навіщо `CLOCAL` — [термінал і termios](root:sys-unix/tty-and-termios); чому дескриптор лишили неблокувальним — [блокувальний і неблокувальний ввід-вивід](root:sys-unix/blocking-and-nonblocking). Друк у `stdout` нікуди не пропадає: усе, що служба каже, забирає [journald](root:sys-unix/journald-structured-entry-model).

## Перевірка

Спершу — насухо, не чіпаючи системи: `udevadm test` проганяє весь набір правил по вже під'єднаному пристрою й друкує, що вийшло.

```sh
$ sudo udevadm control --reload
$ sudo udevadm test /sys/class/tty/ttyUSB0 2>&1 | grep -E 'SYSTEMD_WANTS|TAGS'
TAGS=:systemd:
SYSTEMD_WANTS=laser-agent@ttyUSB0.service
```

Далі — наживо. В одному вікні `udevadm monitor --udev --property --subsystem-match=tty` показує події з усіма властивостями після правил, у другому висмикують і встромляють шнур:

```sh
$ systemctl list-units --type=device 'dev-ttyUSB*'
$ systemctl status laser-agent@ttyUSB0.service
$ journalctl -u 'laser-agent@*' -f
```

Якщо служба не піднялася, `udevadm info --query=property --name=/dev/ttyUSB0 | grep SYSTEMD` скаже, чи властивість узагалі дійшла до бази даних: там або помилка в правилі, або те, про що йдеться далі. Шнур для цього смикати не обов'язково — `sudo udevadm trigger --action=add --subsystem-match=tty` синтезує подію наново по вже під'єднаних пристроях.

## Пастки

**Wants діє один раз — на події, що вперше робить пристрій активним.** Довідка `systemd.device(5)` каже просто: менеджер служб зважає на `Wants=` тоді, коли пристрій **уперше** стає активним, і не зважає, якщо властивість додалася до вже активного пристрою. Наслідок болючий: один пристрій зазвичай дає кілька подій підряд — `add`, потім `bind`, потім `change`, — і якщо прикмета, за якою ви його впізнаєте, на `add` ще не читається, служба не підніметься ніколи. Виходів два: або питати в правилі лише те, що є вже на `add`, або на `add` виставити `ENV{SYSTEMD_READY}="0"` — тоді пристрій для systemd ще не з'явився, — а на пізнішій події поставити одиницю разом із `SYSTEMD_WANTS`. Із того самого кореня росте й порада ставити `ACTION!="remove"` замість звичного `ACTION=="add"`: тег і властивості мусять бути на **кожній** події про цей пристрій, бо udev складає їх наново щоразу, а не пам'ятає з минулого.

**Ім'я примірника екранують, і `%i` — не `%I`.** Юніт пристрою названо за шляхом у `/dev`, а не за іменем від ядра: `/dev/ttyUSB0` дає `dev-ttyUSB0.device`, а `/dev/bus/usb/001/003` — `dev-bus-usb-001-003.device`, бо скісну риску в іменах юнітів заміняє дефіс. Звідси й правило всередині шаблона: `%i` — примірник як є, `%I` — примірник, розекранований назад у шлях. Для `ttyUSB0` вони збігаються й помилки не видно, а для примірника `1-2` (так звуться USB-пристрої за гніздами) `%I` тихо дасть `1/2`. Коли ім'я береться не з `%k`, а звідкись іще, його безпечніше зібрати наперед: `systemd-escape --template=laser-agent@.service 'bus/usb/001/003'`.

**Порожній примірник — не скорочення.** Якщо написати `ENV{SYSTEMD_WANTS}="laser-agent@.service"`, systemd підставить примірник сам — і візьме для нього **шлях у sysfs**, екранований: вийде `laser-agent@sys-devices-pci0000:00-0000:00:14.0-usb1-1\x2d2-…`. Механізм робочий і зручний, коли примірників багато й читати їхні імена не треба; але `BindsTo=dev-%i.device` у шаблоні після цього не складеться, бо `%i` більше не ім'я вузла.

**Гонки з появою вузла немає — а з висмикуванням є.** Вузол у `/dev` створює `devtmpfs` ще до того, як почнуть працювати правила, а юніт пристрою стає активним лише після того, як udev подію дообробив, — отже, на момент старту служби і вузол, і посилання, і права вже на місці. Небезпечний бік інший: агент читає з порту тієї миті, коли шнур уже висмикнули, і його `read` падає **раніше**, ніж до служби доїде команда зупинки від systemd. Саме тому обидві версії агента виходять нулем на `EIO`/`ENODEV`: ненульовий код у цю щілину встиг би зачепити `Restart=` і породити примірник-привид.

**Пристрої, що з'явилися до демона, не забуті.** Під час завантаження `systemd-udevd` піднімається не першим, і всі події про вже знайдене залізо пішли в нікуди. Дірку латає `systemd-udev-trigger.service`, який синтезує події `add` наново, — і саме тому агент піднімається на старті сам, без жодного `WantedBy=` у шаблоні.
