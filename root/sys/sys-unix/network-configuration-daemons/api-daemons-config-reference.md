# 📋 Довідник конфігурацій: NetworkManager, systemd-networkd, Netplan, systemd-resolved та ifupdown

Цей технічний довідник містить вичерпну специфікацію конфігураційних форматів, правил зіставлення інтерфейсів, інваріантів секцій, директив і контрактів CLI для ключових підсистем керування мережею в Linux: `NetworkManager` (формат `keyfile`), `systemd-networkd` (формати `.link`, `.netdev`, `.network`), декларативного рівня `Netplan` (формат `YAML v2`), підсистеми розпізнавання імен `systemd-resolved` (файл `resolved.conf`) та класичного комплексу `ifupdown` (файл `/etc/network/interfaces` та інтерфейс `resolvconf`).

---

## 1. Специфікація конфігурацій NetworkManager (Keyfile)

Формат конфігураційних файлів `NetworkManager` базується на стандарті INI/Keyfile (специфікація бібліотеки GKeyFile). Профілі з'єднань зберігаються у файловій системі у трьох каталогах відповідно до пріоритету:

1. `/etc/NetworkManager/system-connections/` — постійні профілі системного адміністратора (найвищий пріоритет).
2. `/run/NetworkManager/system-connections/` — тимчасові профілі періоду виконання (runtime), що генеруються зовнішніми агентами (Netplan, Cloud-Init, initramfs).
3. `/usr/lib/NetworkManager/system-connections/` — системні профілі постачальника дистрибутиву (найнижчий пріоритет).

Кожен файл у каталозі `/etc/NetworkManager/system-connections/` повинен мати права доступу `0600` (`-rw-------`) та належати суперкористувачу `root:root`. Якщо права доступу відрізняються від `0600`, NetworkManager ігнорує файл з міркувань безпеки, оскільки конфігурація може містити незашифровані ключі доступу до Wi-Fi, паролі та приватні облікові дані VPN.

### 1.1 Архітектура секцій Keyfile

Конфігураційний файл `.nmconnection` розбитий на функціональні секції, що відображають D-Bus об'єкти підсистеми `org.freedesktop.NetworkManager`.

#### Секція `[connection]` — загальні метадані профілю

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `id=` | Рядок | — | Відображуване ім'я профілю з'єднання в CLI (`nmcli con show`) та графічних інтерфейсах. |
| `uuid=` | UUID v4 | — | Унікальний 128-бітний ідентифікатор профілю у форматі `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`. |
| `type=` | Рядок | — | Базовий тип технології: `ethernet`, `wifi`, `bridge`, `bond`, `vlan`, `wireguard`, `tun`, `vpn`, `pppoe`, `gsm`, `dummy`, `vrf`, `vxlan`. |
| `interface-name=` | Рядок | Відсутнє | Прив'язує профіль до конкретного мережевого адаптера ядра (`enp3s0`, `wlan0`). Якщо параметр відсутній, профіль застосовується до будь-якого вільного сумісного пристрою відповідного типу. |
| `autoconnect=` | `true`, `false` | `true` | Чи повинен NetworkManager автоматично активувати цей профіль при появі інтерфейсу, встановленні носія або виявленні Wi-Fi мережі. |
| `autoconnect-priority=` | Ціле число | `0` | Пріоритет автопідключення (діапазон від `-999` до `999`). При наявності кількох доступних мереж обирається профіль з найвищим числом. |
| `autoconnect-retries=` | Ціле число | `-1` | Кількість спроб автоматичного підключення перед позначенням профілю тимчасово недоступним (`0` — значення за замовчуванням, `-1` — нескінченно). |
| `autoconnect-slaves=` | `0`, `1`, `-1` | `-1` | Чи активувати автоматично підлеглі порти при підйомі керуючого пристрою (`1` — так, `0` — ні, `-1` — системний дефолт). |
| `master=` | Рядок / UUID | Відсутнє | Ім'я інтерфейсу або UUID профілю керуючого пристрою (Bridge або Bond), якщо поточний пристрій працює як підлеглий порт (slave). |
| `slave-type=` | `bridge`, `bond`, `team`, `vrf` | Відсутнє | Тип керуючого інтерфейсу для підлеглого порту. |
| `permissions=` | Рядок | Відсутнє | Обмеження доступу користувачів (наприклад, `user:alice:;`). Якщо пусто — профіль доступний усім локальним користувачам. |
| `zone=` | Рядок | Відсутнє | Прив'язка інтерфейсу до зони міжмережевого екрана `firewalld` (наприклад, `trusted`, `public`, `dmz`, `drop`). |
| `timestamp=` | Ціле число | `0` | Unix timestamp останньої успішної активації з'єднання для сортування нещодавно використовуваних профілів. |
| `metered=` | `0`, `1`, `2`, `3` | `0` | Ознака лімітованого з'єднання: `0` (невідомо/авто), `1` (так, лімітоване), `2` (ні, безлімітне), `3` (успадковувати від батьківського пристрою). |
| `wait-device-delay=` | Ціле число | `0` | Затримка в мілісекундах перед початком конфігурації після появи пристрою в ядрі. |
| `lldp=` | `0`, `1`, `2` | `0` | Обробка кадрів LLDP: `0` (вимкнено), `1` (тільки прийом), `2` (прийом та системне збереження). |
| `mdns=` | `0`, `1`, `2`, `-1` | `-1` | Підтримка Multicast DNS: `-1` (дефолт), `0` (вимкнено), `1` (тільки резолв), `2` (резолв та анонсування). |

#### Секція `[ethernet]` (802-3-ethernet) — канальний рівень провідних адаптерів

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `mac-address=` | MAC-адреса | Відсутнє | Фізична апаратна адреса інтерфейсу (`52:54:00:12:34:56`). Прив'язує профіль до конкретного порту. |
| `cloned-mac-address=` | Рядок / MAC | Відсутнє | Підміна MAC-адреси при підйомі: явна адреса, `preserve` (не змінювати), `permanent` (заводська адреса з EEPROM), `random` (випадкова при кожному лінку), `stable` (хешована адреса на базі machine-id та імені). |
| `mac-address-blacklist=` | Список MAC | Відсутнє | Список MAC-адрес через крапку з комою, на яких цей профіль заборонено активувати. |
| `mtu=` | Ціле число | `0` | Розмір максимального блоку передачі даних MTU у байтах (`0` — автоматичний вибір, типово `1500` або `9000` для Jumbo Frames). |
| `auto-negotiate=` | `true`, `false` | `true` | Автоматичне узгодження швидкості та дуплексу через PHY. |
| `speed=` | Ціле число | `0` | Примусова фіксація швидкості в Мбіт/с (`10`, `100`, `1000`, `10000`, `25000`, `40000`, `100000`) при `auto-negotiate=false`. |
| `duplex=` | `half`, `full` | `full` | Режим дуплексу при вимкненому автоузгодженні. |
| `port=` | `tp`, `aui`, `bnc`, `mii`, `fibre` | `tp` | Тип фізичного порту контролера. |
| `wake-on-lan=` | Число / Рядок | `default` | Керування функцією Wake-on-LAN: `default`, `ignore`, `phy`, `unicast`, `multicast`, `broadcast`, `magic` (Magic Packet), `off`. |
| `wake-on-lan-password=` | Рядок | Відсутнє | Пароль SecureOn для Magic Packet у шістнадцятковому форматі `xx:xx:xx:xx:xx:xx`. |
| `accept-all-mac-addresses=` | `0`, `1`, `-1` | `-1` | Переведення інтерфейсу в нерозбірливий режим (Promiscuous Mode): `1` (увімкнено), `0` (вимкнено). |
| `sriov-num-vfs=` | Ціле число | `0` | Кількість віртуальних функцій SR-IOV (Virtual Functions), які драйвер повинен виділити. |

#### Секція `[wifi]` (802-11-wireless) — бездротовий рівень Wi-Fi

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `ssid=` | Рядок / Байти | — | Ідентифікатор бездротової мережі (Service Set Identifier). До 32 байтів. |
| `mode=` | `infrastructure`, `adhoc`, `ap`, `mesh` | `infrastructure` | Режим роботи: `infrastructure` (клієнт точки доступу), `ap` (програмна точка доступу Hotspot), `adhoc` (з'єднання точка-точка), `mesh` (IEEE 802.11s). |
| `bssid=` | MAC-адреса | Відсутнє | Прив'язка до конкретної фізичної точки доступу за її апаратною адресою для блокування роумінгу. |
| `band=` | `a`, `bg` | Відсутнє | Обмеження діапазону радіочастот: `a` (5 ГГц / 6 ГГц) або `bg` (2.4 ГГц). |
| `channel=` | Ціле число | `0` | Фіксований радіоканал (використовується переважно в режимах `ap` та `adhoc`, `0` — автовибір). |
| `hidden=` | `true`, `false` | `false` | Чи є точка доступу прихованою (не транслює SSID у Beacon-кадрах, вимагає активного Probe Request). |
| `powersave=` | `0`, `1`, `2`, `3` | `0` | Керування енергозбереженням Wi-Fi: `0` (дефолт), `1` (ігнорувати), `2` (вимкнено), `3` (увімкнено). |
| `mac-address-randomization=` | `0`, `1`, `2` | `0` | Рандомізація MAC-адреси під час сканування: `0` (дефолт), `1` (ніколи), `2` (завжди). |
| `seen-bssids=` | Список MAC | Відсутнє | Список BSSID, які раніше спостерігалися для цієї мережі (через крапку з комою). |

#### Секція `[wifi-security]` — автентифікація та шифрування Wi-Fi

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `key-mgmt=` | Рядок | — | Протокол керування ключами: `none` (відкрита мережа), `wpa-psk` (WPA/WPA2 Personal), `sae` (WPA3 Personal SAE), `wpa-eap` (WPA/WPA2/WPA3 Enterprise 802.1X), `owe` (Opportunistic Wireless Encryption). |
| `psk=` | Рядок | Відсутнє | Пароль доступу WPA-PSK/SAE (від 8 до 63 символів ASCII або 64 шістнадцяткові цифри). |
| `auth-alg=` | `open`, `shared`, `leap` | `open` | Алгоритм автентифікації канального рівня. |
| `proto=` | Рядок | Відсутнє | Дозволені протоколи через крапку з комою: `wpa;`, `rsn;` (RSN відповідає WPA2/WPA3). |
| `pairwise=` | Рядок | Відсутнє | Попарні шифри (unicast): `ccmp;`, `tkip;`, `gcmp;`. |
| `group=` | Рядок | Відсутнє | Групові шифри (multicast/broadcast): `ccmp;`, `tkip;`, `gcmp;`. |
| `pmf=` | `0`, `1`, `2`, `3` | `0` | Захищені кадри керування (Protected Management Frames, 802.11w): `0` (дефолт), `1` (вимкнено), `2` (опціонально), `3` (обов'язково для WPA3). |

#### Секція `[ipv4]` — мережевий рівень IPv4

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `method=` | Рядок | `auto` | Режим адресації: `auto` (DHCPv4), `manual` (статична адресація), `link-local` (самопризначення `169.254.0.0/16`), `shared` (NAT/DHCP-сервер для роздачі інтернету), `disabled` (повне вимкнення IPv4). |
| `address1=` .. `addressN=` | Рядок | Відсутнє | Статичні адреси у форматі `<IP>/<Префікс>,<Шлюз>` (`192.168.10.50/24,192.168.10.1`) або тільки `<IP>/<Префікс>`. |
| `gateway=` | IP-адреса | Відсутнє | Окремий запис адреси шлюзу за замовчуванням. |
| `dns=` | Рядок | Відсутнє | Список DNS-серверів через крапку з комою із завершальною крапкою з комою (`1.1.1.1;8.8.8.8;`). |
| `dns-search=` | Рядок | Відсутнє | Домени пошуку DNS через крапку з комою (`corp.internal;local;`). |
| `dns-priority=` | Ціле число | `0` | Пріоритет DNS-серверів інтерфейсу в `systemd-resolved` (від'ємні числа позначають вищий пріоритет). |
| `route1=` .. `routeN=` | Рядок | Відсутнє | Статичні маршрути у форматі `<Мережа>/<Префікс>,<Шлюз>,<Метрика>` (`10.0.0.0/8,192.168.10.254,100`). |
| `route-table=` | Ціле число | `0` | Номер таблиці маршрутизації ядра для всіх маршрутів з'єднання (`0` — головна таблиця `main`). |
| `routing-rules=` | Рядок | Відсутнє | Правила Policy Routing FIB (`priority 5000 from 10.0.0.0/24 table 100;`). |
| `never-default=` | `true`, `false` | `false` | Забороняє встановлювати маршрут за замовчуванням `0.0.0.0/0` через цей інтерфейс. |
| `ignore-auto-dns=` | `true`, `false` | `false` | Ігнорує DNS-сервери, отримані через DHCP Option 6. |
| `ignore-auto-routes=` | `true`, `false` | `false` | Ігнорує маршрути, отримані через DHCP Option 121/249. |
| `route-metric=` | Ціле число | `-1` | Метрика для автоматично згенерованих маршрутів інтерфейсу (`-1` — авто). |
| `dhcp-timeout=` | Ціле число | `0` | Таймаут отримання відповіді DHCP у секундах до переходу з'єднання у стан збою (`0` — системний дефолт). |
| `dhcp-client-id=` | Рядок | Відсутнє | Формат DHCP Option 61 (`mac`, `duid` або довільний рядок). |
| `dhcp-send-hostname=` | `true`, `false` | `true` | Чи передавати Option 12 (Hostname) серверу DHCP. |
| `dhcp-hostname=` | Рядок | Відсутнє | Явне ім'я хоста для передачі у DHCP Option 12 замість системного hostname. |
| `dhcp-fqdn=` | Рядок | Відсутнє | Повністю кваліфіковане доменне ім'я для передачі у DHCP Option 81 (FQDN). |
| `dad-timeout=` | Ціле число | `-1` | Таймаут виявлення дублювання адрес IPv4 ACD (RFC 5227) у мілісекундах. |

#### Секція `[ipv6]` — мережевий рівень IPv6

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `method=` | Рядок | `auto` | Режим адресації: `auto` (SLAAC + DHCPv6), `manual` (статичні IPv6), `dhcp` (тільки DHCPv6 без SLAAC), `link-local` (тільки `fe80::/10`), `shared` (роздача IPv6), `disabled` (вимкнення), `ignore` (ігнорувати стек IPv6). |
| `addr-gen-mode=` | `eui64`, `stable-privacy`, `default` | `stable-privacy` | Метод генерації інтерфейсного ідентифікатора SLAAC: `eui64` (на базі MAC-адреси) або `stable-privacy` (псевдовипадковий стійкий RFC 7217). |
| `address1=` .. `addressN=` | Рядок | Відсутнє | Статичні IPv6-адреси у форматі `<IPv6>/<Префікс>,<Шлюз>` (`2001:db8::10/64,2001:db8::1`). |
| `gateway=` | IPv6-адреса | Відсутнє | Окремий запис адреси IPv6-шлюзу за замовчуванням. |
| `dns=` | Рядок | Відсутнє | Список IPv6 DNS-серверів через крапку з комою (`2606:4700:4700::1111;2001:4860:4860::8888;`). |
| `dns-search=` | Рядок | Відсутнє | Список IPv6 доменів пошуку через крапку з комою. |
| `route1=` .. `routeN=` | Рядок | Відсутнє | Статичні IPv6-маршрути: `<Мережа>/<Префікс>,<Шлюз>,<Метрика>`. |
| `route-table=` | Ціле число | `0` | Номер таблиці маршрутизації IPv6. |
| `never-default=` | `true`, `false` | `false` | Забороняє встановлювати маршрут за замовчуванням `::/0` через цей інтерфейс. |
| `ignore-auto-dns=` | `true`, `false` | `false` | Ігнорує DNS-сервери з пакетів ICMPv6 RDNSS та DHCPv6. |
| `ignore-auto-routes=` | `true`, `false` | `false` | Ігнорує маршрути з префіксів ICMPv6 Router Advertisements. |
| `ip6-privacy=` | `0`, `1`, `2`, `-1` | `-1` | Тимчасові адреси розширення конфіденційності (RFC 4941): `0` (вимкнено), `1` (увімкнено, перевага публічній), `2` (увімкнено, перевага тимчасовій). |
| `dhcp-duid=` | Рядок | Відсутнє | Формат DUID для DHCPv6: `lease`, `llt`, `ll`, `uuid`. |
| `ra-input-rules=` | Рядок | Відсутнє | Правила фільтрації вхідних ICMPv6 Router Advertisements. |

#### Секції віртуальних пристроїв: `[bridge]`, `[bond]`, `[vlan]`

:::tabs
```ini
# [bridge] — параметри мережевого моста
[bridge]
stp=true
priority=32768
forward-delay=15
hello-time=2
max-age=20
ageing-time=300
multicast-snooping=true
vlan-filtering=true
vlan-default-pvid=1
```
```ini
# [bond] — параметри агрегації каналів LACP / Bonding
[bond]
mode=802.3ad
miimon=100
lacp-rate=fast
xmit_hash_policy=layer2+3
updelay=200
downdelay=200
arp-interval=0
arp-validate=none
primary=eth0
primary-reselect=always
fail-over-mac=none
resend-igmp=1
num-grat-arp=1
```
```ini
# [vlan] — параметри 802.1Q тегування
[vlan]
id=100
parent=enp3s0
flags=1
# flags бітова маска: 1 = REORDER_HDR, 2 = GVRP, 4 = LOOSE_BINDING, 8 = MVRP
ingress-priority-map=0:0;1:1;2:2;3:3;4:4;5:5;6:6;7:7;
egress-priority-map=0:0;1:1;2:2;3:3;4:4;5:5;6:6;7:7;
```
:::

#### Секції VPN та тунелів: `[wireguard]`, `[wireguard-peer.*]`, `[vpn]`

:::tabs
```ini
# [wireguard] та [wireguard-peer.<pubkey>]
[connection]
id=wg-corp
uuid=e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b
type=wireguard
interface-name=wg0
autoconnect=false

[wireguard]
private-key=YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWE=
listen-port=51820
fwmark=51820
mtu=1420

[wireguard-peer.cmlhbHNlY3VyZXB1YmxpY2tleWZvcndpcmVndWFyZA==]
endpoint=vpn.corp.example.com:51820
allowed-ips=10.200.0.0/24;192.168.100.0/24;
persistent-keepalive=25

[ipv4]
method=manual
address1=10.200.0.5/24
dns=10.200.0.1;
dns-search=corp.internal;
```
```ini
# [vpn] — OpenVPN плагін NetworkManager
[connection]
id=Corp-OpenVPN
uuid=f2a3b4c5-d6e7-8f9a-0b1c-2d3e4f5a6b7c
type=vpn
autoconnect=false

[vpn]
service-type=org.freedesktop.NetworkManager.openvpn
connection-type=tls
remote=vpn.example.com:1194
proto-tcp=no
ca=/etc/ssl/certs/corp-ca.crt
cert=/etc/ssl/certs/client.crt
key=/etc/ssl/private/client.key
cipher=AES-256-GCM
auth=SHA256
comp-lzo=adaptive

[ipv4]
method=auto
never-default=true
```
:::

#### Секція `[proxy]` — керування системним проксі

| Параметр | Тип | Замовчування | Опис |
|---|---|---|---|
| `method=` | `none`, `auto`, `manual` | `none` | Режим конфігурації проксі: `none` (пряме з'єднання), `auto` (WPAD / PAC URL), `manual` (ручні IP та порти). |
| `browser-only=` | `true`, `false` | `false` | Чи застосовувати налаштування проксі лише до веб-браузерів. |
| `pac-url=` | URL-рядок | Відсутнє | URL-адреса файлу автоматичної конфігурації Proxy Auto-Config (`http://wpad.corp/wpad.dat`). |
| `pac-script=` | Рядок | Відсутнє | Вбудоване тіло скрипту PAC мовою JavaScript. |
| `http-proxy=` | IP / Хост | Відсутнє | Хост HTTP-проксі сервера. |
| `http-port=` | Ціле число | `8080` | Порт HTTP-проксі сервера. |
| `ssl-proxy=` | IP / Хост | Відсутнє | Хост HTTPS-проксі сервера. |
| `ssl-port=` | Ціле число | `8080` | Порт HTTPS-проксі сервера. |
| `socks-proxy=` | IP / Хост | Відсутнє | Хост SOCKS-проксі сервера. |
| `socks-port=` | Ціле число | `1080` | Порт SOCKS-проксі сервера. |
| `socks-version=` | `4`, `5` | `5` | Версія протоколу SOCKS. |

### 1.2 Практичні зразки профілів NetworkManager

:::tabs
```ini
# /etc/NetworkManager/system-connections/enp3s0-static.nmconnection
[connection]
id=enp3s0-static
uuid=a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d
type=ethernet
interface-name=enp3s0
autoconnect=true
autoconnect-priority=10

[ethernet]
auto-negotiate=true

[ipv4]
method=manual
address1=192.168.10.50/24,192.168.10.1
dns=1.1.1.1;1.0.0.1;
dns-search=corp.internal;
route1=10.0.0.0/8,192.168.10.254,100
never-default=false

[ipv6]
method=auto
addr-gen-mode=stable-privacy
```
```ini
# /etc/NetworkManager/system-connections/Office-WiFi.nmconnection
[connection]
id=Office-WiFi
uuid=b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e
type=wifi
interface-name=wlan0
autoconnect=true
autoconnect-priority=50

[wifi]
mode=infrastructure
ssid=Corporate-Secure
powersave=2

[wifi-security]
key-mgmt=sae
psk=SuperSecretPresharedKey99
auth-alg=open
pmf=3

[ipv4]
method=auto

[ipv6]
method=auto
```
```ini
# /etc/NetworkManager/system-connections/bond0.nmconnection
[connection]
id=bond0
uuid=c3d4e5f6-a7b8-9c0d-1e2f-3a4b5c6d7e8f
type=bond
interface-name=bond0
autoconnect=true

[bond]
mode=802.3ad
miimon=100
lacp-rate=fast
xmit_hash_policy=layer2+3

[ipv4]
method=manual
address1=10.20.0.10/24,10.20.0.1
dns=10.20.0.1;

[ipv6]
method=disabled
```
```ini
# /etc/NetworkManager/system-connections/bond0-slave-eth1.nmconnection
[connection]
id=bond0-slave-eth1
uuid=d4e5f6a7-b8c9-0d1e-2f3a-4b5c6d7e8f9a
type=ethernet
interface-name=eth1
master=bond0
slave-type=bond
autoconnect=true
```
:::

### 1.3 Специфікація інтерфейсу командного рядка NetworkManager (`nmcli`)

Утиліта `nmcli` взаємодіє з демоном `NetworkManager` через системну шину D-Bus.

#### Команди керування профілями (`nmcli connection`)

| Команда | Опис операції |
|---|---|
| `nmcli connection show` | Виводить перелік усіх збережених профілів з'єднань. З прапорцем `--active` фільтрує тільки активні. |
| `nmcli connection show <ID/UUID>` | Виводить повний перелік усіх ключів та значень зазначеного профілю. |
| `nmcli connection up <ID/UUID>` | Активує профіль на зіставленому або першому вільному сумісному пристрої. |
| `nmcli connection down <ID/UUID>` | Деактивує з'єднання та переводить пристрій у відключений стан. |
| `nmcli connection add [параметри...]` | Створює новий профіль з'єднання (наприклад, `type ethernet con-name "LAN" ifname eth0`). |
| `nmcli connection modify <ID> [+|-]<ключ> <значення>` | Змінює значення параметра або додає/видаляє елемент зі списку (префікси `+` та `-`). |
| `nmcli connection clone <ID> <новий-ID>` | Створює копію профілю з новим іменем та згенерованим новим UUID. |
| `nmcli connection edit <ID>` | Запускає інтерактивний редактор профілю з автодоповненням директив. |
| `nmcli connection reload` | Перечитує всі файли `.nmconnection` з дисків `/etc/NetworkManager/system-connections/`. |
| `nmcli connection load <файл>` | Зчитує та реєструє окремий конфігураційний файл без повного перезавантаження. |
| `nmcli connection delete <ID/UUID>` | Видаляє конфігураційний файл профілю з диску. |

#### Команди керування пристроями (`nmcli device`)

| Команда | Опис операції |
|---|---|
| `nmcli device status` | Відображає таблицю виявлених пристроїв ядра, їхній тип, стан та прив'язаний профіль. |
| `nmcli device show [пристрій]` | Детальна інспекція мережевого адаптера (драйвер, MAC, MTU, IP, шлюзи, DNS, маршрути). |
| `nmcli device connect <пристрій>` | Переводить пристрій під контроль NetworkManager та активує відповідний авто-профіль. |
| `nmcli device disconnect <пристрій>` | Відключає пристрій від активного профілю та блокує автопідключення до ручного виклику. |
| `nmcli device reapply <пристрій>` | Застосовує зміни в активному профілі до інтерфейсу без розриву фізичного лінка. |
| `nmcli device wifi list` | Сканує радіоефір і виводить список знайдених точок доступу (SSID, BSSID, Signal, Security). |
| `nmcli device wifi connect <SSID> password <key>` | Створює профіль та миттєво підключається до зазначеної бездротової мережі. |
| `nmcli device lldp [пристрій]` | Виводить інформацію про сусідні мережеві комутатори, отриману через протокол LLDP. |

#### Глобальні команди та автоматизація

```bash
# Перевірка загального статусу та прапорців мережі
nmcli general status
nmcli networking on
nmcli networking off

# Керування радіомодулями
nmcli radio wifi on
nmcli radio wwan off

# Машинозчитуваний вивід для шелл-скриптів (розділювач двокрапка :)
nmcli -t -f NAME,UUID,TYPE,DEVICE connection show --active

# Пряме вилучення значення окремого поля (без заголовків)
CURRENT_IP=$(nmcli -g IP4.ADDRESS device show enp3s0 | head -n1)
```

### 1.4 Специфікація об'єктної моделі D-Bus API NetworkManager

Демон `NetworkManager` експортує повне об'єктно-орієнтоване API на системній шині D-Bus за адресою `org.freedesktop.NetworkManager`. Усі операції конфігурації, моніторингу стану та активації з'єднань, які виконують утиліти `nmcli`, `nmtui` або графічні аплети, транслюються у виклики методів і сигналів цього інтерфейсу.

```
/org/freedesktop/NetworkManager
 ├── org.freedesktop.NetworkManager (кореневий менеджер)
 │
 ├── /Settings
 │    ├── org.freedesktop.NetworkManager.Settings (менеджер профілів)
 │    └── /<N> ── org.freedesktop.NetworkManager.Settings.Connection (профіль з'єднання)
 │
 ├── /Devices/<N>
 │    ├── org.freedesktop.NetworkManager.Device (базовий мережевий пристрій)
 │    ├── org.freedesktop.NetworkManager.Device.Wired (специфікація 802.3 Ethernet)
 │    ├── org.freedesktop.NetworkManager.Device.Wireless (специфікація 802.11 Wi-Fi)
 │    └── org.freedesktop.NetworkManager.Device.Bridge / Bond / Vlan / WireGuard
 │
 ├── /ActiveConnection/<N>
 │    └── org.freedesktop.NetworkManager.Connection.Active (активна сесія з'єднання)
 │
 └── /IP4Config/<N>, /IP6Config/<N>
      └── org.freedesktop.NetworkManager.IP4Config / IP6Config (L3 параметри адреси та DNS)
```

#### 1. Кореневий об'єкт `/org/freedesktop/NetworkManager`

Головний об'єкт забезпечує доступ до переліку виявлених пристроїв, списку активних підключень, керування глобальним станом живлення радіомодулів та активації профілів.

##### Методи інтерфейсу `org.freedesktop.NetworkManager`

| Сигнатура методу | Вхідні параметри | Повертуване значення | Опис операції |
|---|---|---|---|
| `GetDevices()` | — | `ao: devices` | Повертає масив D-Bus шляхів усіх мережевих адаптерів, якими керує NetworkManager. |
| `GetAllDevices()` | — | `ao: devices` | Повертає повний список пристроїв ядра, включно з тими, що перебувають у стані `unmanaged`. |
| `GetDeviceByIpIface()` | `s: iface` | `o: device` | Знаходить об'єктний шлях пристрою за його системним іменем інтерфейсу (наприклад, `enp3s0`). |
| `ActivateConnection()` | `o: connection`, `o: device`, `o: specific_object` | `o: active_connection` | Активує зазначений профіль на обраному пристрої. `specific_object` вказує на точку доступу (`AccessPoint`) або `/` для Ethernet. |
| `DeactivateConnection()` | `o: active_connection` | — | Зупиняє активне з'єднання та переводить пристрій у стан `disconnected`. |
| `AddAndActivateConnection()` | `a{sa{sv}}: connection`, `o: device`, `o: specific_object` | `o: path`, `o: active_connection` | Атомарно створює новий профіль у пам'яті/диску та миттєво запускає його на пристрої. |
| `AddAndActivateConnection2()` | `a{sa{sv}}: connection`, `o: device`, `o: specific_object`, `a{sv}: options` | `o: path`, `o: active_connection`, `a{sv}: result` | Розширена версія з прапорцями збереження (`persist`), блокування (`bind-to-device`) тощо. |
| `ReloadConnections()` | `b: monitor_changes` | `b: success` | Примушує демон перечитати всі конфігураційні файли `.nmconnection` з дисків. |
| `CheckConnectivity()` | — | `u: connectivity_state` | Виконує активний HTTP-запит перевірки доступу до Інтернету (виявлення Captive Portal). |
| `Sleep()` | `b: sleep` | — | Призупиняє мережеву активність перед переходом операційної системи в режим глибокого сну. |
| `Enable()` | `b: enable` | — | Глобальне увімкнення або вимкнення всього мережевого стека. |

##### Властивості інтерфейсу `org.freedesktop.NetworkManager`

| Властивість | D-Bus тип | Доступ | Опис |
|---|---|---|---|
| `Devices` | `ao` | Read | Масив об'єктних шляхів активних керованих пристроїв. |
| `AllDevices` | `ao` | Read | Масив усіх зареєстрованих інтерфейсів ядра. |
| `ActiveConnections` | `ao` | Read | Масив об'єктних шляхів активних сесій з'єднань. |
| `PrimaryConnection` | `o` | Read | Об'єктний шлях з'єднання, через яке прокладено маршрут за замовчуванням. |
| `ActivatingConnection` | `o` | Read | Об'єктний шлях з'єднання, що наразі проходить фазу конфігурації. |
| `State` | `u` | Read | Глобальний стан демона: `10` (`ASLEEP`), `20` (`DISCONNECTED`), `40` (`CONNECTING`), `50` (`CONNECTED_LOCAL`), `60` (`CONNECTED_SITE`), `70` (`CONNECTED_GLOBAL`). |
| `Connectivity` | `u` | Read | Стан перевірки зв'язку: `0` (`UNKNOWN`), `1` (`NONE`), `2` (`PORTAL`), `3` (`LIMITED`), `4` (`FULL`). |
| `WirelessEnabled` | `b` | Read/Write | Програмний стан радіомодулів Wi-Fi (Soft Block). |
| `WirelessHardwareEnabled` | `b` | Read | Апаратний стан перемикача Wi-Fi (Hard Block через rfkill). |
| `WwanEnabled` | `b` | Read/Write | Програмний стан стільникових модемів LTE/5G. |
| `Version` | `s` | Read | Версія демона NetworkManager (наприклад, `1.44.2`). |

##### Сигнали інтерфейсу `org.freedesktop.NetworkManager`

* `DeviceAdded(o: device_path)` — випромінюється, коли ядро або драйвер реєструє новий мережевий інтерфейс.
* `DeviceRemoved(o: device_path)` — випромінюється при вилученні пристрою (гаряче відключення USB/PCI або видалення віртуального адаптера).
* `StateChanged(u: state)` — сповіщає про зміну глобального стану підключення хоста до мережі.

#### 2. Підсистема збереження налаштувань `/org/freedesktop/NetworkManager/Settings`

Менеджер налаштувань відповідає за читання, валідацію, створення та видалення статичних профілів з'єднань.

##### Методи інтерфейсу `org.freedesktop.NetworkManager.Settings`

* `ListConnections() -> ao`: повертає масив D-Bus шляхів усіх зареєстрованих профілів (наприклад, `/org/freedesktop/NetworkManager/Settings/1`).
* `GetConnectionByUuid(s: uuid) -> o`: знаходить об'єктний шлях профілю за його 128-бітним ідентифікатором UUID.
* `AddConnection(a{sa{sv}}: connection) -> o`: створює новий профіль з переданого словника параметрів та зберігає його у файл `/etc/NetworkManager/system-connections/`.
* `AddConnectionUnsaved(a{sa{sv}}: connection) -> o`: створює тимчасовий профіль виключно в оперативній пам'яті (без запису на диск).
* `SaveHostname(s: hostname) -> void`: зберігає статичне ім'я машини у системний файл `/etc/hostname`.

##### Об'єкт окремого профілю `org.freedesktop.NetworkManager.Settings.Connection`

Кожен профіль з'єднання експортується як окремий D-Bus об'єкт `/org/freedesktop/NetworkManager/Settings/<N>`:

| Метод / Властивість | Сигнатура | Опис |
|---|---|---|
| Метод `GetSettings()` | `() -> a{sa{sv}}` | Повертає повну структуру профілю: словник секцій (`connection`, `ipv4`, `ethernet`), де кожна секція містить словник ключ-значення у форматі GVariant. |
| Метод `Update()` | `(a{sa{sv}}: settings) -> ()` | Оновлює параметри профілю та атомарно перезаписує відповідний `.nmconnection` файл на диску. |
| Метод `UpdateUnsaved()` | `(a{sa{sv}}: settings) -> ()` | Оновлює налаштування лише в оперативній пам'яті процесу. |
| Метод `Delete()` | `() -> ()` | Видаляє конфігураційний файл профілю з диску та знищує D-Bus об'єкт. |
| Метод `GetSecrets()` | `(s: setting_name) -> a{sa{sv}}` | Вилучає конфіденційні ключі (паролі Wi-Fi, приватні ключі VPN, сертифікати) для зазначеної секції. |
| Властивість `Filename` | `s` (Read) | Абсолютний шлях до файлу конфігурації на диску (`/etc/NetworkManager/system-connections/enp3s0.nmconnection`). |
| Властивість `Unsaved` | `b` (Read) | Чи містить об'єкт у пам'яті незбережені зміни відносно дискової копії. |
| Властивість `Flags` | `u` (Read) | Прапорці профілю (`1` = незбережений, `2` = створений користувачем, `4` = згенерований зовнішнім агентом). |

#### 3. Об'єкти мережевих пристроїв `/org/freedesktop/NetworkManager/Devices/<N>`

Кожен мережевий пристрій ядра представлений об'єктом, що реалізує базовий інтерфейс `org.freedesktop.NetworkManager.Device` та один або кілька спеціалізованих інтерфейсів залежно від апаратної технології.

##### Властивості базового інтерфейсу `org.freedesktop.NetworkManager.Device`

| Властивість | Тип | Опис та значення |
|---|---|---|
| `Interface` | `s` | Системне ім'я адаптера в ядрі (`enp3s0`, `wlan0`, `br0`). |
| `IpInterface` | `s` | Ім'я інтерфейсу, на якому призначаються IP-адреси (може відрізнятися для тунелів). |
| `DeviceType` | `u` | Числовий код типу: `1` (`Ethernet`), `2` (`Wi-Fi`), `5` (`Bluetooth`), `8` (`Modem`), `10` (`Bond`), `11` (`VLAN`), `13` (`Bridge`), `14` (`Generic`), `16` (`TUN`), `17` (`IP-Tunnel`), `18` (`MACVLAN`), `19` (`VXLAN`), `20` (`VETH`), `29` (`WireGuard`), `30` (`VRF`). |
| `State` | `u` | Поточний стан кінцевого автомата пристрою: `0` (`UNKNOWN`), `10` (`UNMANAGED`), `20` (`UNAVAILABLE`), `30` (`DISCONNECTED`), `40` (`PREPARE`), `50` (`CONFIG`), `60` (`NEED_AUTH`), `70` (`IP_CONFIG`), `80` (`IP_CHECK`), `90` (`SECONDARIES`), `100` (`ACTIVATED`), `110` (`DEACTIVATING`), `120` (`FAILED`). |
| `ActiveConnection` | `o` | D-Bus шлях активної сесії `/org/freedesktop/NetworkManager/ActiveConnection/<N>` або `/` якщо пристрій не підключено. |
| `Ip4Config` | `o` | Шлях до об'єкта `IP4Config`, що описує активні IPv4 адреси, DNS та шлюзи. |
| `Ip6Config` | `o` | Шлях до об'єкта `IP6Config` для параметрів IPv6. |
| `Managed` | `b` | Чи перебуває пристрій під контролем NetworkManager (`true`) або ігнорується (`false`). |
| `Autoconnect` | `b` | Дозвіл на автоматичний підбір та запуск сумісних профілів при виявленні носія. |
| `HwAddress` | `s` | Активна фізична MAC-адреса інтерфейсу (`52:54:00:12:34:56`). |
| `Mtu` | `u` | Поточний розмір максимального блоку передачі MTU в ядрі. |
| `Carrier` | `b` | Апаратна наявність фізичного носія (лінка L2) для провідних адаптерів. |

##### Спеціалізовані інтерфейси пристроїв

* `org.freedesktop.NetworkManager.Device.Wired`:
  * `Speed` (`u`): Поточна швидкість фізичного каналу в Мбіт/с (100, 1000, 10000).
  * `PermHwAddress` (`s`): Постійна заводська MAC-адреса, зчитана з EEPROM.
* `org.freedesktop.NetworkManager.Device.Wireless`:
  * `Mode` (`u`): Режим роботи (`1` = Ad-Hoc, `2` = Infrastructure/Client, `3` = AP/Hotspot).
  * `Bitrate` (`u`): Поточна швидкість передачі в кілобітах на секунду (кбіт/с).
  * `AccessPoints` (`ao`): Масив об'єктних шляхів знайдених у радіоефірі точок доступу.
  * `ActiveAccessPoint` (`o`): Шлях до точки доступу, з якою наразі встановлено асоціацію.
* `org.freedesktop.NetworkManager.Device.Bridge` / `Bond`:
  * `Slaves` (`ao`): Масив D-Bus шляхів пристроїв, що входять до складу моста або агрегації як підлеглі порти.

##### Методи керування пристроєм

* `Reapply(a{sa{sv}}: connection, t: version_id, u: flags) -> void`: Застосовує оновлені параметри конфігурації безпосередньо до працюючого інтерфейсу без розриву фізичного зв'язку L2 та скидання TCP-сесій.
* `Disconnect() -> void`: Примусово деактивує поточний профіль і блокує автопідключення до наступної ручної команди.
* `Delete() -> void`: Видаляє програмний віртуальний пристрій (VLAN, Bridge, Bond, WireGuard) із ядра Linux.

#### 4. Об'єкти активних з'єднань `/org/freedesktop/NetworkManager/ActiveConnection/<N>`

Представляють стан активної сесії між фізичним пристроєм та профілем конфігурації під час його виконання:

| Властивість | Тип | Опис |
|---|---|---|
| `Connection` | `o` | Об'єктний шлях статичного профілю `/org/freedesktop/NetworkManager/Settings/<N>`. |
| `SpecificObject` | `o` | Шлях до асоційованого об'єкта (наприклад, точка доступу Wi-Fi `AccessPoint`). |
| `Id` | `s` | Текстова назва профілю (`enp3s0-static`, `Corporate-WiFi`). |
| `Uuid` | `s` | Унікальний ідентифікатор активного профілю. |
| `Type` | `s` | Тип з'єднання (`802-3-ethernet`, `802-11-wireless`, `wireguard`, `vpn`). |
| `Devices` | `ao` | Список пристроїв, задіяних у цьому з'єднанні. |
| `State` | `u` | Стан сесії: `0` (`UNKNOWN`), `1` (`ACTIVATING`), `2` (`ACTIVATED`), `3` (`DEACTIVATING`), `4` (`DEACTIVATED`). |
| `Default` | `b` | Чи надає це з'єднання системний IPv4-маршрут за замовчуванням `0.0.0.0/0`. |
| `Default6` | `b` | Чи надає це з'єднання системний IPv6-маршрут за замовчуванням `::/0`. |
| `Vpn` | `b` | Ознака віртуальної приватної мережі VPN. |
| `Master` | `o` | Шлях до керуючого пристрою (якщо інтерфейс працює у режимі slave). |

#### 5. Моніторинг властивостей та взаємодія через системну шину

NetworkManager суворо дотримується стандарту `org.freedesktop.DBus.Properties`. Будь-яка зміна параметрів адаптера або перемикання станів транслюється сигналом:

```
org.freedesktop.DBus.Properties.PropertiesChanged (
    String interface_name,
    Dict of {String, Variant} changed_properties,
    Array of String invalidated_properties
)
```

##### Приклади інспектування та викликів через CLI (`busctl` та `gdbus`)

:::tabs
```bash
# 1. Запит загального стану NetworkManager через busctl
busctl get-property org.freedesktop.NetworkManager \
    /org/freedesktop/NetworkManager \
    org.freedesktop.NetworkManager State

# 2. Отримання списку всіх зареєстрованих інтерфейсів
busctl call org.freedesktop.NetworkManager \
    /org/freedesktop/NetworkManager \
    org.freedesktop.NetworkManager GetDevices

# 3. Читання IP-адреси та статусу першого пристрою
busctl get-property org.freedesktop.NetworkManager \
    /org/freedesktop/NetworkManager/Devices/1 \
    org.freedesktop.NetworkManager.Device Interface State Ip4Config

# 4. Моніторинг усіх мережевих подій та зміни станів у реальному часі
busctl monitor org.freedesktop.NetworkManager
```
```bash
# 1. Читання повного словника налаштувань профілю через gdbus
gdbus call --system \
    --dest org.freedesktop.NetworkManager \
    --object-path /org/freedesktop/NetworkManager/Settings/1 \
    --method org.freedesktop.NetworkManager.Settings.Connection.GetSettings

# 2. Примусова деактивація активного з'єднання
gdbus call --system \
    --dest org.freedesktop.NetworkManager \
    --object-path /org/freedesktop/NetworkManager \
    --method org.freedesktop.NetworkManager.DeactivateConnection \
    "/org/freedesktop/NetworkManager/ActiveConnection/1"
```
:::

---

## 2. Специфікація unit-файлів systemd-networkd (.link, .netdev, .network)

Підсистема `systemd-networkd` разом із сервісом керування пристроями `udev` використовує три типи декларативних файлів конфігурації у форматі юнітів systemd:

1. **`.link` (Конфігурація канального рівня ядра/udev)**: Застосовується правилом udev `99-systemd.link` у момент появи мережевого пристрою в ядрі. Керує політикою іменування, підміною MAC-адреси, MTU та прапорцями апаратного розвантаження (Offloading).
2. **`.netdev` (Створення віртуальних пристроїв)**: Описує віртуальні адаптери (мости, бонди, VLAN, тунелі WireGuard/VXLAN), які демон створює через Netlink-запити `RTM_NEWLINK` при старті.
3. **`.network` (Конфігурація адресації та маршрутизації)**: Застосовує статичні адреси, налаштування DHCP-клієнтів, правила маршрутизації та членство в мостах до зіставлених інтерфейсів.

### 2.1 Ієрархія розташування файлів та drop-in фрагменти

| Каталог | Призначення | Пріоритет |
|---|---|---|
| `/etc/systemd/network/` | Конфігурація локального адміністратора | 1 (Найвищий) |
| `/run/systemd/network/` | Тимчасова конфігурація періоду виконання (Netplan, Cloud-Init, DHCP initramfs) | 2 (Середній) |
| `/usr/lib/systemd/network/` | Системні шаблони дистрибутиву | 3 (Найнижчий) |

Файли сортуються за лексикографічним порядком їхніх імен. Для перекриття або доповнення директив основного файлу (наприклад, `10-eth0.network`) використовується каталог drop-in фрагментів `10-eth0.network.d/*.conf`.

### 2.2 Специфікація файлів `.link`

#### Секція `[Match]` у файлах `.link`

| Директива | Тип | Опис критерію зіставлення |
|---|---|---|
| `MACAddress=` | MAC-адреса | Апаратна адреса пристрою, зашита в EEPROM (`52:54:00:aa:bb:cc`). |
| `PermanentMACAddress=` | MAC-адреса | Постійна заводська MAC-адреса пристрою. |
| `OriginalName=` | Рядок / Glob | Початкове ім'я, призначене ядром до перейменування (`eth*`). |
| `Path=` | Рядок / Glob | Топологічний шлях на системній шині (`pci-0000:00:1f.6-*`). |
| `Driver=` | Рядок / Glob | Назва драйвера ядра (`e1000e`, `virtio_net`, `r8169`). |
| `Type=` | Рядок | Тип пристрою (`ether`, `wlan`, `bridge`, `bond`, `vlan`). |
| `Host=` | Рядок | Системне ім'я хоста (hostname). |
| `Virtualization=` | Рядок | Перевірка віртуального середовища (`yes`, `no`, `kvm`, `qemu`, `container`). |
| `KernelCommandLine=` | Рядок | Перевірка наявності параметра в `/proc/cmdline`. |

#### Секція `[Link]` у файлах `.link`

| Директива | Тип | Замовчування | Опис та вплив |
|---|---|---|---|
| `Description=` | Рядок | Відсутнє | Текстовий коментар або призначення інтерфейсу. |
| `MACAddressPolicy=` | `persistent`, `random`, `none` | `persistent` | Політика генерації MAC: `persistent` (стабільний хеш на базі machine-id та імені), `random` (випадковий), `none` (використовувати заводський MAC). |
| `MACAddress=` | MAC-адреса | Відсутнє | Примусове призначення конкретної MAC-адреси. |
| `NamePolicy=` | Список значень | `kernel database onboard slot path` | Пріоритет правил іменування інтерфейсу: `kernel`, `database`, `onboard`, `slot`, `path`, `mac`, `keep`. |
| `AlternativeNamesPolicy=` | Список | `database onboard slot path mac` | Політика генерації альтернативних аліасів інтерфейсу (Alternative Names). |
| `Name=` | Рядок | Відсутнє | Фіксоване цільове ім'я інтерфейсу (наприклад, `wan0`, `lan0`). |
| `AlternativeName=` | Рядок | Відсутнє | Додаткове альтернативне ім'я для звернення до пристрою через iproute2. |
| `MTUBytes=` | Розмір / Число | Відсутнє | Розмір кадру MTU у байтах (`1500`, `9000`, `9K`). |
| `BitsPerSecond=` | Число з суфіксом | Відсутнє | Фіксація бітрейту (`100M`, `1G`, `10G`). |
| `Duplex=` | `half`, `full` | Відсутнє | Фіксація дуплексу примусово. |
| `AutoNegotiation=` | `yes`, `no` | `yes` | Увімкнення/вимкнення автоузгодження PHY через ethtool. |
| `WakeOnLan=` | `phy`, `unicast`, `multicast`, `broadcast`, `magic`, `off` | `off` | Налаштування функції Wake-on-LAN. |
| `Port=` | `tp`, `aui`, `bnc`, `mii`, `fibre` | Відсутнє | Фіксація типу трансивера. |
| `TCPOffloadChecksum=` | `yes`, `no` | Відсутнє | Управління апаратним розвантаженням обчислення контрольних сум TCP. |
| `LargeReceiveOffload=` | `yes`, `no` | Відсутнє | Управління розвантаженням об'єднання пакетів LRO. |
| `GenericSegmentationOffload=` | `yes`, `no` | Відсутнє | Управління апаратною сегментацією великих пакетів GSO. |

### 2.3 Специфікація файлів `.netdev` (Створення віртуальних пристроїв)

Файл `.netdev` завжди містить головну секцію `[NetDev]` та специфічну секцію типу, що відповідає значенню директиви `Kind=`.

#### Секція `[NetDev]`

| Директива | Тип | Замовчування | Опис |
|---|---|---|---|
| `Name=` | Рядок | — | Системне ім'я віртуального пристрою в ядрі (`br0`, `bond0`, `vlan100`, `wg0`, `vrf-blue`). |
| `Kind=` | Рядок | — | Тип пристрою: `bridge`, `bond`, `vlan`, `veth`, `vxlan`, `wireguard`, `dummy`, `macvlan`, `macvtap`, `ipvlan`, `ipvtap`, `vrf`, `tun`, `tap`, `ipip`, `sit`, `gre`, `vti`. |
| `MTUBytes=` | Число | Відсутнє | Розмір MTU створюваного віртуального пристрою. |
| `MACAddress=` | MAC-адреса | Відсутнє | Фіксована MAC-адреса інтерфейсу. |
| `Description=` | Рядок | Відсутнє | Текстовий опис віртуального пристрою. |

#### Спеціалізовані секції за типами `Kind=`

:::tabs
```ini
# Kind=bridge -> Секція [Bridge]
[NetDev]
Name=br0
Kind=bridge

[Bridge]
STP=yes
Priority=32768
ForwardDelaySec=15
HelloTimeSec=2
MaxAgeSec=20
AgeingTimeSec=300
DefaultPVID=1
VLANFiltering=yes
MulticastSnooping=yes
```
```ini
# Kind=bond -> Секція [Bond]
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=802.3ad
MIIMonitorSec=100ms
LACPTransmitRate=fast
TransmitHashPolicy=layer2+3
UpDelaySec=200ms
DownDelaySec=200ms
MinLinks=1
FailOverMACPolicy=none
ARPIntervalSec=0
PrimaryReselectPolicy=always
ResendIGMP=1
```
```ini
# Kind=vlan -> Секція [VLAN]
[NetDev]
Name=vlan100
Kind=vlan

[VLAN]
Id=100
GVRP=no
MVRP=no
LooseBinding=yes
ReorderHeader=yes
```
```ini
# Kind=vxlan -> Секція [VXLAN]
[NetDev]
Name=vxlan42
Kind=vxlan

[VXLAN]
VNI=42
DestinationPort=4789
Remote=192.168.1.200
Local=192.168.1.100
FlowBased=no
```
```ini
# Kind=wireguard -> Секції [WireGuard] та [WireGuardPeer]
[NetDev]
Name=wg0
Kind=wireguard

[WireGuard]
PrivateKeyFile=/etc/wireguard/wg0.key
ListenPort=51820
FireWallMark=51820

[WireGuardPeer]
PublicKey=cmlhbHNlY3VyZXB1YmxpY2tleWZvcndpcmVndWFyZA==
Endpoint=198.51.100.1:51820
AllowedIPs=10.100.0.0/24, 192.168.50.0/24
PersistentKeepalive=25
```
```ini
# Kind=vrf -> Секція [VRF]
[NetDev]
Name=vrf-blue
Kind=vrf

[VRF]
Table=100
```
:::

### 2.4 Специфікація файлів `.network` (Конфігурація L2/L3)

#### Секція `[Match]` у файлах `.network`

Правило зіставлення: усі директиви всередині секції об'єднуються за логічним **І** (AND). Значення, розділені пробілами всередині одного рядка, об'єднуються за логічним **АБО** (OR).

| Директива | Тип | Опис критерію |
|---|---|---|
| `Name=` | Рядок / Glob | Ім'я пристрою (`enp3s0`, `eth*`, `wlan?`, `!lo`). Підтримує заперечення через знак оклику `!`. |
| `MACAddress=` | MAC-адреса | Апаратна адреса канального рівня (`52:54:00:12:34:56`). |
| `PermanentMACAddress=` | MAC-адреса | Постійна заводська MAC-адреса. |
| `Type=` | Рядок | Тип інтерфейсу ядра (`ether`, `wlan`, `bridge`, `bond`, `vlan`, `wireguard`). |
| `Driver=` | Рядок / Glob | Ім'я модуля драйвера ядра (`virtio_net`, `e1000e`, `r8169`). |
| `Path=` | Рядок / Glob | Топологічний шлях на шині PCI/USB (`pci-0000:00:1f.6-*`). |
| `Host=` | Рядок | Мережеве ім'я машини (hostname). |
| `Virtualization=` | Рядок | Тип віртуалізації (`yes`, `no`, `kvm`, `container`, `systemd-nspawn`). |
| `KernelCommandLine=` | Рядок | Наявність аргументу в параметрах запуску ядра. |

#### Секція `[Link]` у файлах `.network`

| Директива | Тип | Замовчування | Опис |
|---|---|---|---|
| `MTUBytes=` | Число | Відсутнє | Розмір MTU для інтерфейсу. |
| `RequiredForOnline=` | `yes`, `no`, `routable`, `carrier`, `degraded` | `yes` | Визначає, чи блокує інтерфейс сервіс `systemd-networkd-wait-online.service` та перехід у `network-online.target`. |
| `RequiredFamilyForOnline=` | `ipv4`, `ipv6`, `both`, `any` | `any` | Яке саме сімейство адрес необхідне для визнання стану `routable`. |
| `Unmanaged=` | `yes`, `no` | `no` | При значенні `yes` демон повністю ігнорує інтерфейс і не змінює жодних параметрів у ядрі. |
| `ActivationPolicy=` | `up`, `down`, `always-up`, `manual`, `bound` | `up` | Політика адміністративного стану лінка при старті демона. |
| `Promiscuous=` | `yes`, `no` | `no` | Переведення інтерфейсу в нерозбірливий режим. |
| `AllMulticast=` | `yes`, `no` | `no` | Прийом усіх багатоадресних пакетів. |

#### Секція `[Network]` у файлах `.network`

| Директива | Тип | Замовчування | Вплив на мережевий стек |
|---|---|---|---|
| `DHCP=` | `yes`, `no`, `ipv4`, `ipv6` | `no` | Управління вбудованим клієнтом DHCP (`yes` активує DHCPv4 та DHCPv6). |
| `IPv6AcceptRA=` | `yes`, `no` | `yes` (якщо DHCP=yes/ipv6) | Прийом та обробка ICMPv6 Router Advertisements для SLAAC. |
| `IPv6SendRA=` | `yes`, `no` | `no` | Розсилка повідомлень ICMPv6 RA у режимі маршрутизатора. |
| `DHCPServer=` | `yes`, `no` | `no` | Запуск вбудованого легковажного DHCPv4-сервера на інтерфейсі. |
| `Address=` | CIDR-нотація | Відсутнє | Статична IP-адреса (`192.168.1.50/24`, `2001:db8::10/64`). Може вказуватися багаторазово. |
| `Gateway=` | IP-адреса | Відсутнє | Адреса шлюзу за замовчуванням (`192.168.1.1`). Демон додає маршрут `0.0.0.0/0` або `::/0`. |
| `DNS=` | Список IP | Відсутнє | Адреси DNS-серверів (`1.1.1.1 8.8.8.8`). Передаються сервісу `systemd-resolved`. |
| `Domains=` | Список доменів | Відсутнє | Домени пошуку DNS. Префікс `~` вказує на пріоритетний домен маршрутизації (Split DNS). |
| `NTP=` | Список хостів/IP | Відсутнє | Адреси серверів синхронізації часу для `systemd-timesyncd`. |
| `Bridge=` | Рядок | Відсутнє | Приєднує поточний інтерфейс як підлеглий порт до зазначеного моста. |
| `Bond=` | Рядок | Відсутнє | Додає поточний інтерфейс до складу групи агрегації каналів Bonding. |
| `VLAN=` | Список рядків | Відсутнє | Імена віртуальних пристроїв VLAN, які ядро прив'язує поверх цього порту. |
| `VRF=` | Рядок | Відсутнє | Прив'язує інтерфейс до таблиці віртуального маршрутизатора VRF. |
| `IPForward=` | `yes`, `no`, `ipv4`, `ipv6` | `no` | Дозволяє транзитну маршрутизацію пакетів (`sysctl net.ipv4.conf.<dev>.forwarding=1`). |
| `IPMasquerade=` | `yes`, `no`, `ipv4`, `ipv6` | `no` | Автоматичне увімкнення трансляції адрес Source NAT (Masquerade) через iptables/nftables. |
| `LinkLocalAddressing=` | `yes`, `no`, `ipv4`, `ipv6` | `ipv6` | Генерація локальних адрес лінка (`169.254.0.0/16` для IPv4 або `fe80::/10` для IPv6). |
| `IPv6PrivacyExtensions=` | `yes`, `no`, `prefer-public` | `no` | Генерація тимчасових приватних адрес SLAAC (RFC 4941). |
| `KeepConfiguration=` | `yes`, `no`, `static`, `dhcp-on-stop`, `dhcp` | `no` | Чи зберігати призначені адреси та маршрути в ядрі при перезапуску чи зупинці демона. |
| `ConfigureWithoutCarrier=` | `yes`, `no` | `no` | Призначати IP-адреси та конфігурацію навіть за відсутності фізичного лінка (NO-CARRIER). |
| `IgnoreCarrierLoss=` | `yes`, `no`, `секунди` | `no` | Затримка перед скиданням налаштувань адреси при короткочасному зникненні лінка. |

#### Секції `[Address]`, `[Route]`, `[RoutingPolicyRule]`, `[BridgeVLAN]`

:::tabs
```ini
# Секція [Address] — розширений контроль адреси
[Address]
Address=10.0.0.15/24
Peer=10.0.0.1/32
Broadcast=10.0.0.255
Scope=global
PreferredLifetimeSec=86400
ValidLifetimeSec=172800
HomeAddress=no
DuplicateAddressDetection=ipv4
```
```ini
# Секція [Route] — статична маршрутизація
[Route]
Destination=10.200.0.0/16
Gateway=192.168.10.254
GatewayOnLink=no
Metric=100
Table=100
Scope=global
PreferredSource=192.168.10.50
Type=unicast
MTUBytes=1420
QuickAck=yes
```
```ini
# Секція [RoutingPolicyRule] — Policy Routing (FIB Rules)
[RoutingPolicyRule]
From=10.200.0.0/16
To=0.0.0.0/0
Table=100
Priority=5000
TypeOfService=0x10
FirewallMark=100
InvertRule=no
```
```ini
# Секція [BridgeVLAN] — тегування портів моста
[BridgeVLAN]
VLAN=20 30 40
PVID=20
EgressUntagged=20
```
:::

#### Секції `[DHCPv4]`, `[DHCPv6]`, `[IPv6AcceptRA]`

| Секція | Директива | Тип | Замовчування | Опис поведінки |
|---|---|---|---|---|
| `[DHCPv4]` | `ClientIdentifier=` | `mac`, `duid`, `duid-only` | `duid` | Формат Option 61 (`mac` — апаратна адреса, `duid` — RFC 4361). |
| `[DHCPv4]` | `UseDNS=` | `yes`, `no` | `yes` | Чи приймати DNS-сервери з DHCP Option 6. |
| `[DHCPv4]` | `UseRoutes=` | `yes`, `no` | `yes` | Чи додавати безкласові маршрути з DHCP Option 121 / 249. |
| `[DHCPv4]` | `UseGateway=` | `yes`, `no` | `yes` | Чи встановлювати маршрут за замовчуванням з DHCP Option 3. |
| `[DHCPv4]` | `RouteMetric=` | Число | `1024` | Фіксована метрика для маршрутів, отриманих через DHCPv4. |
| `[DHCPv4]` | `RouteTable=` | Число | `0` | Номер таблиці маршрутизації ядра для DHCP маршрутів. |
| `[DHCPv4]` | `SendHostname=` | `yes`, `no` | `yes` | Чи передавати системне ім'я хоста у DHCP Option 12. |
| `[DHCPv4]` | `Hostname=` | Рядок | Відсутнє | Явне ім'я хоста для Option 12 замість системного hostname. |
| `[DHCPv4]` | `RequestOptions=` | Список чисел | Відсутнє | Список кодів опцій DHCP для запиту у сервері (Option 55). |
| `[DHCPv4]` | `Anonymize=` | `yes`, `no` | `no` | Увімкнення режиму анонімності RFC 7844 (Anonymity Profiles for DHCP). |
| `[DHCPv4]` | `MaxAttempts=` | Число | `infinity` | Максимальна кількість спроб отримання оренди до переходу у стан fail. |
| `[DHCPv6]` | `WithoutRA=` | `solicit`, `information-request` | Відсутнє | Запуск DHCPv6 без очікування прапорців Managed/Other у ICMPv6 RA. |
| `[DHCPv6]` | `UseDNS=` | `yes`, `no` | `yes` | Чи приймати DNS-сервери з DHCPv6 Option 23. |
| `[DHCPv6]` | `RapidCommit=` | `yes`, `no` | `yes` | Використання швидкого двоетапного обміну Solicit/Reply (RFC 3315). |
| `[IPv6AcceptRA]` | `UseDNS=` | `yes`, `no` | `yes` | Обробка серверів RDNSS (RFC 8106) з ICMPv6 Router Advertisements. |
| `[IPv6AcceptRA]` | `UseDomains=` | `yes`, `no` | `yes` | Обробка доменів пошуку DNSSL з ICMPv6 RA. |
| `[IPv6AcceptRA]` | `RouteMetric=` | Число | `1024` | Метрика маршрутів, отриманих від маршрутизатора через SLAAC. |
| `[IPv6AcceptRA]` | `DHCPv6Client=` | `always`, `auto`, `never` | `auto` | Автоматичний запуск DHCPv6 на основі прапорців M/O у RA. |

#### Секції `[DHCPServer]` та `[DHCPServerStaticLease]` — вбудований DHCPv4-сервер

Підсистема `systemd-networkd` містить вбудований автономний сервер DHCPv4, оптимізований для маршрутизаторів, бездротових точок доступу (AP Hotspot), віртуалізованих середовищ (`systemd-nspawn`, KVM/QEMU) та мостових інтерфейсів. Сервер активується директивою `DHCPServer=yes` у секції `[Network]` відповідного файлу `.network` і працює виключно в межах IPv4-підмережі, призначеної на інтерфейс через параметр `Address=`.

##### Механізм виділення адрес та виявлення колізій

1. **Розрахунок пулу динамічної оренди**:
   * Базовий простір адрес обчислюється на основі статичної IP-адреси та маски підмережі інтерфейсу (наприклад, `192.168.50.1/24`).
   * Початкова адреса пулу зміщується від базової IP на величину `PoolOffset=` (типово `PoolOffset=1`, тобто `192.168.50.2`).
   * Кількість доступних адрес визначається параметром `PoolSize=`. Якщо `PoolSize=0`, пул автоматично охоплює весь залишок адрес підмережі аж до широкомовної адреси `broadcast` (виключаючи IP самого інтерфейсу).
2. **Перевірка унікальності адреси (ARP Probe)**:
   * Перед формуванням повідомлення `DHCPOFFER` сервер надсилає в канальний рівень зондувальний запит ARP Probe (RFC 5227) для перевірки, чи не використовується обрана адреса іншим хостом зі статичною конфігурацією.
   * Якщо на запит надходить відповідь ARP Reply, сервер фіксує колізію, позначає адресу як тимчасово заблоковану та бере наступну вільну IP-адресу з пулу.
3. **Ідентифікація клієнтів та персистентність оренд**:
   * Клієнти ідентифікуються за унікальним ідентифікатором DUID (Option 61) або апаратною MAC-адресою канального рівня.
   * Активні оренди зберігаються в оперативній пам'яті та атомарно скидаються у файли стану `/run/systemd/netif/leases/<ifindex>`. При увімкненому параметрі `PersistLeases=yes` ці записи зчитуються після перезапуску демона, що запобігає перевидачі раніше призначених адрес.

##### Директиви конфігурації секції `[DHCPServer]`

| Директива | Тип | Замовчування | Опис та протокольна дія |
|---|---|---|---|
| `PoolOffset=` | Ціле число | `1` | Зсув початкової IP-адреси пулу відносно власної IP-адреси інтерфейсу. |
| `PoolSize=` | Ціле число | `0` | Кількість адрес у динамічному пулі (`0` — увесь залишок адрес підмережі). |
| `DefaultLeaseTimeSec=` | Час / Секунди | `12h` (`43200s`) | Базовий час оренди адреси, що передається у DHCP Option 51. |
| `MaxLeaseTimeSec=` | Час / Секунди | `24h` (`86400s`) | Максимально дозволений час оренди при індивідуальному запиті клієнта. |
| `EmitDNS=` | `yes`, `no` | `yes` | Чи передавати клієнтам адреси DNS-серверів через DHCP Option 6. |
| `DNS=` | Список IPv4 | Адреса інтерфейсу | Список IP-адрес DNS-серверів для Option 6. За відсутності передається IP поточного інтерфейсу хоста (якщо активний `systemd-resolved`). |
| `EmitNTP=` | `yes`, `no` | `no` | Чи передавати адреси серверів часу через DHCP Option 42. |
| `NTP=` | Список IPv4 | Відсутнє | Список IP-адрес NTP-серверів для Option 42. |
| `EmitRouter=` | `yes`, `no` | `yes` | Чи анонсувати маршрутизатор за замовчуванням через DHCP Option 3. |
| `Router=` | IPv4-адреса | Адреса інтерфейсу | Адреса шлюзу для Option 3 (за замовчуванням — IP локального інтерфейсу). |
| `EmitTimezone=` | `yes`, `no` | `no` | Чи передавати часовий пояс через DHCP Option 100 (POSIX) / Option 101 (TZ String). |
| `Timezone=` | Рядок | Системний timezone | Ідентифікатор часового поясу за базою IANA (наприклад, `Europe/Kyiv`). |
| `EmitSearchDomains=` | `yes`, `no` | `no` | Чи передавати список доменів пошуку через DHCP Option 119. |
| `SearchDomains=` | Список доменів | Відсутнє | Перелік суфіксів пошуку для Option 119 (наприклад, `corp.lan intra.local`). |
| `ServerAddress=` | IPv4-адреса | Адреса інтерфейсу | Явна IP-адреса сервера для поля DHCP Option 54 (Server Identifier). |
| `BootServerAddress=` | IPv4-адреса | Відсутнє | IP-адреса TFTP-сервера мережевого завантаження для Option 66 / поля `siaddr`. |
| `BootServerName=` | Рядок | Відсутнє | Доменне ім'я TFTP-сервера для Option 66. |
| `BootFilename=` | Рядок | Відсутнє | Шлях до завантажувального NBP-образу для Option 67 (наприклад, `pxelinux.0`, `ipxe.efi`). |
| `SendOption=` | `код:тип:дані` | Відсутнє | Передача кастомних опцій DHCP у форматі `SendOption=<code>:<type>:<value>`, де `type` може бути `uint8`, `uint16`, `uint32`, `ipv4address`, `string`, `rfc1035-label`. |
| `SendRawOption=` | `код:hex-байти` | Відсутнє | Передача довільних шістнадцяткових байтів опції у форматі `SendRawOption=240:01020304`. |
| `RelayTarget=` | IPv4-адреса | Відсутнє | Адреса віддаленого DHCP-сервера для пересилання запитів у режимі DHCP Relay Agent (RFC 3046 / Option 82). |
| `PersistLeases=` | `yes`, `no` | `yes` | Чи зберігати базу виданих оренд у каталозі `/run/systemd/netif/leases/` між рестартами демона. |

##### Директиви конфігурації секції `[DHCPServerStaticLease]`

Секція `[DHCPServerStaticLease]` дозволяє закріплювати постійні IP-адреси за конкретними пристроями за їхніми апаратними характеристиками:

| Директива | Тип | Опис та обов'язковість |
|---|---|---|
| `MACAddress=` | MAC-адреса | Фізична апаратна адреса адаптера клієнта (`52:54:00:12:34:56`). |
| `Address=` | IPv4-адреса | Фіксована IP-адреса, що обов'язково належить до підмережі інтерфейсу (`192.168.50.10`). |
| `ClientIdentifier=` | Рядок / DUID | Ідентифікатор клієнта з поля Option 61 (переважає над `MACAddress=`, якщо присутній у запиті). |
| `Hostname=` | Рядок | Фіксоване ім'я хоста, яке призначається клієнту через Option 12. |

##### Приклад шлюзу з налаштованим сервером DHCP та статичними резерваціями

```ini
# /etc/systemd/network/50-gateway-ap.network
[Match]
Name=wlan0

[Network]
Address=192.168.50.1/24
IPForward=yes
IPMasquerade=both
DHCPServer=yes

[DHCPServer]
PoolOffset=20
PoolSize=100
DefaultLeaseTimeSec=8h
MaxLeaseTimeSec=24h
EmitDNS=yes
DNS=192.168.50.1 1.1.1.1
EmitRouter=yes
Router=192.168.50.1
EmitNTP=yes
NTP=192.168.50.1
EmitTimezone=yes
Timezone=Europe/Kyiv
EmitSearchDomains=yes
SearchDomains=ap.local
SendOption=114:string:http://portal.ap.local/login
PersistLeases=yes

# Статична оренда для мережевого принтера
[DHCPServerStaticLease]
MACAddress=00:11:22:33:44:55
Address=192.168.50.10
Hostname=office-printer

# Статична оренда для локального файлового сховища
[DHCPServerStaticLease]
MACAddress=52:54:00:ab:cd:ef
Address=192.168.50.15
Hostname=backup-nas
```

### 2.5 Практичний комплекс конфігурацій systemd-networkd

Нижче наведено зв'язку конфігураційних файлів для реалізації відмовостійкого сервера: два фізичні порти `enp3s0` та `enp3s1` об'єднуються у `bond0` (LACP 802.3ad), поверх якого піднімається тегований віртуальний інтерфейс `vlan20` зі статичною IP-адресою та маршрутизацією.

:::tabs
```ini
# /etc/systemd/network/20-bond0.netdev
[NetDev]
Name=bond0
Kind=bond

[Bond]
Mode=802.3ad
MIIMonitorSec=100ms
LACPTransmitRate=fast
TransmitHashPolicy=layer2+3
```
```ini
# /etc/systemd/network/21-bond-slaves.network
[Match]
Name=enp3s0 enp3s1

[Network]
Bond=bond0
```
```ini
# /etc/systemd/network/22-bond0.network
[Match]
Name=bond0

[Network]
VLAN=vlan20
LinkLocalAddressing=no
```
```ini
# /etc/systemd/network/30-vlan20.netdev
[NetDev]
Name=vlan20
Kind=vlan

[VLAN]
Id=20
```
```ini
# /etc/systemd/network/31-vlan20.network
[Match]
Name=vlan20

[Network]
Address=10.20.0.50/24
Gateway=10.20.0.1
DNS=1.1.1.1 8.8.8.8
Domains=corp.internal
IPv6AcceptRA=no
```
:::

### 2.6 Інтерфейс утиліти `networkctl` та матриці скінченного автомата

Утиліта `networkctl` відображає внутрішній стан інтерфейсів у системному демоні `systemd-networkd` та надсилає команди керування.

| Команда | Опис операції |
|---|---|
| `networkctl list [шаблон]` | Виводить зведену таблицю всіх інтерфейсів, їхніх типів та станів. |
| `networkctl status [пристрій]` | Детальний звіт по інтерфейсу: зіставлений `.network` файл, адреси, шлюзи, DNS, маршрути. |
| `networkctl up <пристрій>` | Переводить інтерфейс у стан `UP` на канальному рівні. |
| `networkctl down <пристрій>` | Переводить інтерфейс у стан `DOWN`. |
| `networkctl renew <пристрій>` | Ініціює процедуру поновлення оренди адреси DHCPv4/DHCPv6. |
| `networkctl forcerenew <пристрій>` | Примусове перезапитування оренди DHCP. |
| `networkctl reconfigure <пристрій>` | Повторний розбір `.network` файлів і повне переналаштування інтерфейсу через Netlink. |
| `networkctl reload` | Перечитує всі файли конфігурацій без скидання стану працюючих інтерфейсів. |
| `networkctl lldp [пристрій]` | Інспектування сусідніх комутаторів за протоколом LLDP. |
| `networkctl edit <файл/пристрій>` | Відкриває конфігураційний файл або drop-in фрагмент у системному редакторі. |
| `networkctl cat <файл/пристрій>` | Друкує вміст активного конфігураційного файлу разом із застосованими drop-in. |
| `networkctl mask <пристрій>` | Блокує керування зазначеним пристроєм демоном systemd-networkd. |
| `networkctl monitor` | Постійний потік подій зміни станів інтерфейсів у реальному часі. |

#### Скінченний автомат: Operational State та Setup State

Кожен інтерфейс у `systemd-networkd` одночасно характеризується двома станами: **Operational State** (фізичний/канальний стан зв'язку) та **Setup State** (стан застосування конфігурації демоном).

##### 1. Матриця станів Operational State

| Стан | Опис фізичного та канального рівня |
|---|---|
| `missing` | Пристрій було фізично вилучено з системи або видалено з ядра. |
| `off` | Інтерфейс перебуває в адміністративному стані `DOWN` (прапорець `IFF_UP` знято). |
| `no-carrier` | Інтерфейс адміністративно `UP`, проте фізичний кабель відключений (`IFF_RUNNING` знято). |
| `dormant` | Фізичний лінк є, проте триває протокольне узгодження канального рівня L2 (802.1X EAP або LACP). |
| `carrier-degraded` | Агрегована група (Bond/Bridge) втратила частину надлишкових портів, але зберігає працездатність. |
| `carrier` | Фізичний лінк L2 повністю активний, але адресація L3 ще не налаштована або відсутній маршрут. |
| `enslaved` | Інтерфейс успішно підключено як підлеглий порт до моста (Bridge) або агрегації (Bond). |
| `routable` | Інтерфейс має призначену валідну IP-адресу та активний маршрут для виходу в інші підмережі. |

##### 2. Матриця станів Setup State

| Стан | Опис стану конфігуратора `systemd-networkd` |
|---|---|
| `pending` | Пристрій виявлено ядром, триває пошук зіставленого `.network` файлу за секцією `[Match]`. |
| `unmanaged` | Для пристрою не знайдено жодного `.network` файлу (або виставлено `Unmanaged=yes`). Демон його не чіпає. |
| `configuring` | Демон виконує налаштування: надсилає Netlink-повідомлення, очікує відповіді DHCP або SLAAC. |
| `configured` | Усі директиви конфігураційного файлу успішно застосовані в ядрі. |
| `failed` | Виникла помилка: конфлікт IP-адрес (DAD fail), відхилення Netlink ядром або таймаут DHCP. |

### 2.7 Механіка обробки подій RTNetlink у systemd-networkd

Демон `systemd-networkd` побудований за асинхронною подієвою моделлю поверх бібліотеки `sd-event`. Для безпосереднього зв'язку з мережевим стеком ядра Linux процес відкриває системний неблокуючий сокет Netlink:

```
int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC | SOCK_NONBLOCK, NETLINK_ROUTE);
```

Через структуру `struct sockaddr_nl` демон реєструє підписку на широкомовні мультикаст-групи ядра:
* `RTMGRP_LINK` (`RTNLGRP_LINK`) — створення, видалення та зміна стану інтерфейсів.
* `RTMGRP_IPV4_IFADDR` / `RTMGRP_IPV6_IFADDR` — додавання, оновлення та вилучення IP-адрес і префіксів.
* `RTMGRP_IPV4_ROUTE` / `RTMGRP_IPV6_ROUTE` — зміни у системних таблицях маршрутизації Forwarding Information Base (FIB).
* `RTMGRP_IPV4_RULE` / `RTMGRP_IPV6_RULE` — правила багатотабличної маршрутизації Policy Routing.
* `RTMGRP_NEIGH` — стан записів сусідів ARP та IPv6 Neighbor Discovery.

Файловий дескриптор сокета реєструється в головному циклі подій через виклик `sd_event_add_io()`. Усі вихідні повідомлення ядра обробляються у черзі з перевіркою номерів транзакцій `nlmsg_seq` та асинхронним очікуванням підтверджень `NLMSG_ERROR` (де значення `error == 0` свідчить про успішне виконання операції).

```
   ┌─────────────────────────────────────────────────────────────┐
   │                    Ядро Linux (RTNetlink)                   │
   └───────────────┬─────────────────────────────▲───────────────┘
   (RTM_* події)   │ (Multicast Groups)          │ (RTM_* команди)
                   ▼                             │
   ┌─────────────────────────────────────────────┴───────────────┐
   │             systemd-networkd (sd-event loop)                │
   │                                                             │
   │  ┌─────────────────┐ ┌──────────────────┐ ┌──────────────┐  │
   │  │ Link State FSM  │ │ Address / DAD    │ │ Route Engine │  │
   │  │ (IFLA_CARRIER)  │ │ (IFA_F_*)        │ │ (FIB recalc) │  │
   │  └─────────────────┘ └──────────────────┘ └──────────────┘  │
   └─────────────────────────────────────────────────────────────┘
```

#### 1. Обробка подій канального рівня (`RTM_NEWLINK` / `RTM_DELLINK`)

Кожне повідомлення канального рівня містить заголовок `struct ifinfomsg` та набір атрибутів `IFLA_*` у форматі TLV (Type-Length-Value).

```
struct ifinfomsg {
    unsigned char  ifi_family; /* AF_UNSPEC */
    unsigned short ifi_type;   /* ARPHRD_ETHER, ARPHRD_LOOPBACK тощо */
    int            ifi_index;  /* Унікальний числовий ifindex інтерфейсу */
    unsigned int   ifi_flags;  /* Прапорці IFF_UP, IFF_RUNNING, IFF_LOWER_UP */
    unsigned int   ifi_change; /* Маска змінених прапорців */
};
```

##### Специфікація розбору атрибутів `IFLA_*` у `systemd-networkd`

| Атрибут ядра | Тип даних | Обробка та семантика в демоні |
|---|---|---|
| `IFLA_IFNAME` | Рядок (null-term) | Системне ім'я адаптера (`enp3s0`). Використовується для первинного зіставлення з секцією `[Match] Name=`. |
| `IFLA_ADDRESS` | Бінарний буфер | Апаратна MAC-адреса інтерфейсу. Зіставляється з `[Match] MACAddress=`. |
| `IFLA_OPERSTATE` | Байт (`uint8`) | Фізичний/операційний стан зв'язку: `IF_OPER_UP`, `IF_OPER_DOWN`, `IF_OPER_DORMANT`, `IF_OPER_LOWERLAYERDOWN`. |
| `IFLA_CARRIER` | Байт (`uint8`) | Стан носія: `1` — фізичний сигнал є (Carrier detected), `0` — лінк відсутній (NO-CARRIER). Запускає або зупиняє FSM налаштування L3. |
| `IFLA_LINK` | Ціле (`int32`) | Числовий індекс батьківського пристрою (для саб-інтерфейсів VLAN, MACVLAN, VXLAN). |
| `IFLA_MASTER` | Ціле (`int32`) | Числовий індекс керуючого пристрою (Bridge або Bond), до якого приєднано цей порт. |
| `IFLA_MTU` | Ціле (`uint32`) | Розмір максимального кадру MTU в ядрі. Якщо відрізняється від `MTUBytes=`, демон генерує коригувальне повідомлення. |
| `IFLA_PROMISCUITY` | Ціле (`uint32`) | Лічильник запитів на нерозбірливий режим Promiscuous Mode. |
| `IFLA_LINKINFO` | Вкладені TLV | Описує тип віртуального пристрою. Включає під-атрибути `IFLA_INFO_KIND` (рядок `bridge`, `bond`, `vlan`, `wireguard`, `vrf`) та `IFLA_INFO_DATA` (специфічні бінарні структури налаштувань). |

#### 2. Обробка адресних повідомлень (`RTM_NEWADDR` / `RTM_DELADDR`) та керування префіксами

Адресні повідомлення транспортують структуру `struct ifaddrmsg` та ланцюжок атрибутів `IFA_*`.

```
struct ifaddrmsg {
    unsigned char ifa_family;    /* AF_INET або AF_INET6 */
    unsigned char ifa_prefixlen; /* Довжина маски підмережі (наприклад, 24 або 64) */
    unsigned char ifa_flags;     /* Прапорці IFA_F_* (базові 8 біт) */
    unsigned char ifa_scope;     /* RT_SCOPE_UNIVERSE, RT_SCOPE_LINK, RT_SCOPE_HOST */
    int           ifa_index;     /* ifindex пристрою */
};
```

##### Специфікація розбору атрибутів `IFA_*` та життєвого циклу

| Атрибут | Тип | Опис та роль у системному демоні |
|---|---|---|
| `IFA_ADDRESS` | 4 або 16 байтів | Мережева IP-адреса або префікс підмережі. |
| `IFA_LOCAL` | 4 або 16 байтів | Локальна IP-адреса інтерфейсу (для p2p збігається з адресою вузла). |
| `IFA_BROADCAST` | 4 байти | Широкомовна адреса IPv4 (`192.168.1.255`). |
| `IFA_LABEL` | Рядок | Текстовий аліас інтерфейсу (legacy-сумісність `eth0:0`). |
| `IFA_FLAGS` | Ціле (`uint32`) | Повний 32-бітний набір прапорців розширеного стану адреси в ядрі. |
| `IFA_CACHEINFO` | `struct ifa_cacheinfo` | Часові ліміти адреси: `ifa_prefered` (час у секундах, протягом якого адреса є основною), `ifa_valid` (час повної валідності до видалення), `cstamp`, `tstamp`. |

##### Прапорці стану адрес (`ifa_flags` / `IFA_FLAGS`)

* `IFA_F_PERMANENT` — статична адреса, призначена адміністратором або демоном.
* `IFA_F_SECONDARY` / `IFA_F_TEMPORARY` — тимчасова динамічна адреса розширення конфіденційності SLAAC (RFC 4941).
* `IFA_F_TENTATIVE` — адреса перебуває у процесі перевірки унікальності DAD (Duplicate Address Detection). Стек ядра ще не приймає і не надсилає через неї прикладний трафік.
* `IFA_F_DADFAILED` — виявлено колізію IP-адреси в мережі. Ядро блокує адресу; `systemd-networkd` фіксує перехід інтерфейсу в стан `failed` та ініціює повторне узгодження DHCP або надсилає сигнал аварії.
* `IFA_F_DEPRECATED` — час `ifa_prefered` сплив. Ядро забороняє використовувати цю адресу для нових вихідних з'єднань, але продовжує приймати вхідні пакети для існуючих сесій.
* `IFA_F_NOPREFIXROUTE` — виставляється `systemd-networkd` для запобігання автоматичному створенню ядром локального маршруту підмережі (демон керує маршрутами самостійно).
* `IFA_F_STABLE_PRIVACY` — адреса згенерована за алгоритмом RFC 7217 на основі криптографічного хешу machine-id та префікса маршрутизатора.

#### 3. Механіка перерахунку та оновлення маршрутів (`RTM_NEWROUTE` / `RTM_DELROUTE`)

Маршрутні повідомлення транспортують структуру `struct rtmsg` та атрибути `RTA_*`.

```
struct rtmsg {
    unsigned char rtm_family;   /* AF_INET або AF_INET6 */
    unsigned char rtm_dst_len;  /* Довжина префікса призначення (/0 для default) */
    unsigned char rtm_src_len;  /* Префікс джерела (для Source Routing) */
    unsigned char rtm_tos;      /* Тип обслуговування Type of Service */
    unsigned char rtm_table;    /* Номер таблиці (RT_TABLE_MAIN=254 тощо) */
    unsigned char rtm_protocol; /* Протокол-джерело маршруту */
    unsigned char rtm_scope;    /* RT_SCOPE_UNIVERSE, RT_SCOPE_LINK, RT_SCOPE_HOST */
    unsigned char rtm_type;     /* RTN_UNICAST, RTN_LOCAL, RTN_BLACKHOLE тощо */
    unsigned int  rtm_flags;    /* RTM_F_CLONED, RTM_F_FIB_MATCH */
};
```

##### Протоколи походження маршруту (`rtm_protocol`)

* `RTPROT_KERNEL` (`2`) — автоматичні локальні маршрути підмережі, згенеровані ядром при підйомі лінка.
* `RTPROT_STATIC` (`4`) — маршрути, задані адміністратором у секціях `[Route]` файлів `.network`.
* `RTPROT_DHCP` (`16`) — маршрути, отримані від сервера DHCPv4 (Option 3 та Option 121).
* `RTPROT_RA` (`9`) — маршрути, отримані з префіксів та опцій RIO (Route Information Option) повідомлень ICMPv6 Router Advertisements.

##### Типи маршрутів (`rtm_type`)

* `RTN_UNICAST` (`1`) — стандартний маршрут прямого пересилання через шлюз або інтерфейс.
* `RTN_LOCAL` (`2`) — локальна адреса хоста (трафік замикається на петльовий інтерфейс `lo`).
* `RTN_BLACKHOLE` (`6`) — тихе відкидання пакетів без надсилання сповіщень джерелу (захист від петель маршрутизації).
* `RTN_UNREACHABLE` (`7`) — відкидання пакетів із надсиланням ICMP Destination Unreachable.
* `RTN_PROHIBIT` (`8`) — відкидання пакетів із надсиланням ICMP Destination Communication Administratively Prohibited.

##### Атрибути маршрутизації `RTA_*`

| Атрибут | Тип | Опис та обробка |
|---|---|---|
| `RTA_DST` | IP-адреса | Мережа призначення (якщо відсутня при `rtm_dst_len=0` — маршрут за замовчуванням). |
| `RTA_GATEWAY` | IP-адреса | Адреса наступного вузла (Next Hop Gateway). |
| `RTA_OIF` | Ціле (`int32`) | Числовий ifindex вихідного інтерфейсу. |
| `RTA_PRIORITY` | Ціле (`uint32`) | Метрика маршруту (числове значення пріоритету в FIB). Менше значення має перевагу. |
| `RTA_PREFSRC` | IP-адреса | Переважна IP-адреса джерела (Preferred Source IP) при виборі цього маршруту. |
| `RTA_TABLE` | Ціле (`uint32`) | Номер цільової таблиці маршрутизації (підтримка Policy Routing до 4 мільярдів таблиць). |
| `RTA_METRICS` | Вкладені TLV | Специфічні метрики ядра TCP: `RTAX_MTU`, `RTAX_ADVMSS`, `RTAX_RTT`, `RTAX_CWND`, `RTAX_QUICKACK`. |

#### 4. Динаміка перерахунку таблиць FIB при подіях носія (`IFLA_CARRIER`)

Коли мережевий комутатор або кабель змінює фізичний стан, демон `systemd-networkd` виконує строго визначений каскад дій:

1. **Втрата носія (`IFLA_CARRIER: 1 -> 0`)**:
   * Демон переводить інтерфейс у статус `no-carrier`.
   * **Якщо `IgnoreCarrierLost=no` (дефолт)**: демон негайно видаляє всі маршрути з протоколом `RTPROT_DHCP` та `RTPROT_RA` через системні виклики `RTM_DELROUTE`, скидає оренду DHCP та скасовує таймери поновлення.
   * **Якщо `IgnoreCarrierLost=N` (задано секунди)**: демон запускає асинхронний таймер у `sd-event`. Протягом цього інтервалу адреси та маршрути залишаються в ядрі. Якщо носій відновиться до завершення таймеру, мережеві сесії не перериваються.
2. **Відновлення носія (`IFLA_CARRIER: 0 -> 1`)**:
   * Демон скасовує таймер втрати носія, переводить інтерфейс у стан `carrier` та ініціює перезапуск клієнтів DHCPv4/DHCPv6 та Router Solicitation.
   * Отримавши нові адреси, демон виконує DAD-перевірку, після чого атомарно надсилає в ядро повідомлення `RTM_NEWROUTE` з метрикою `RouteMetric=` та оновлює записи у `systemd-resolved`.

---

## 3. Специфікація декларативного рівня Netplan (YAML v2)

Утиліта `Netplan` є стандартним інструментом декларативної конфігурації мережі в дистрибутивах Ubuntu та Debian. Вона зчитує єдиний опис мережевої топології у форматі YAML з каталогів `/etc/netplan/*.yaml`, `/run/netplan/*.yaml`, `/lib/netplan/*.yaml` і транслює його у нативні файли для обраного бекенду (`renderer`):
* `renderer: networkd` — генерує файли `.network` та `.netdev` у каталозі `/run/systemd/network/`.
* `renderer: NetworkManager` — генерує файли `.nmconnection` у каталозі `/run/NetworkManager/system-connections/`.

### 3.1 Коренева схема специфікації Netplan YAML

Файли конфігурації повинні відповідати версії схеми `version: 2`:

```yaml
network:
  version: 2
  renderer: networkd # або NetworkManager
  ethernets:
    <dev-id>: { ... }
  wifis:
    <dev-id>: { ... }
  bridges:
    <bridge-id>: { ... }
  bonds:
    <bond-id>: { ... }
  vlans:
    <vlan-id>: { ... }
  tunnels:
    <tunnel-id>: { ... }
  vrfs:
    <vrf-id>: { ... }
  dummy-devices:
    <dummy-id>: { ... }
```

### 3.2 Параметри вузлів `ethernets:` та `wifis:`

| Параметр | Тип | Замовчування | Опис та інваріанти |
|---|---|---|---|
| `match:` | Словник | Відсутнє | Правило пошуку фізичного пристрою: `name:` (шаблон імені), `macaddress:` (апаратний MAC), `driver:` (модуль ядра). |
| `set-name:` | Рядок | Відсутнє | Перейменування знайденого пристрою у системне ім'я (вимагає наявності блоку `match:`). |
| `wakeonlan:` | `true`, `false` | `false` | Увімкнення функції Wake-on-LAN (Magic Packet). |
| `mtu:` | Ціле число | `1500` | Розмір MTU у байтах (наприклад, `1500` або `9000`). |
| `optional:` | `true`, `false` | `false` | Якщо `true`, операційна система не очікує переходу інтерфейсу в стан `routable` при завантаженні (не блокує `network-online.target`). |
| `critical:` | `true`, `false` | `false` | Чи є інтерфейс критичним для кореневої файлової системи (NFS/iSCSI root). |
| `dhcp4:` | `true`, `false` | `false` | Увімкнення клієнта DHCPv4. |
| `dhcp6:` | `true`, `false` | `false` | Увімкнення клієнта DHCPv6. |
| `accept-ra:` | `true`, `false` | `true` (якщо dhcp6) | Прийом ICMPv6 Router Advertisements. |
| `dhcp4-overrides:` | Словник | Відсутнє | Перевизначення параметрів DHCPv4: `use-dns:` (`bool`), `use-routes:` (`bool`), `use-gateway:` (`bool`), `route-metric:` (`int`), `send-hostname:` (`bool`), `use-mtu:` (`bool`). |
| `dhcp6-overrides:` | Словник | Відсутнє | Перевизначення параметрів DHCPv6: `use-dns:`, `use-routes:`, `use-gateway:`, `route-metric:`. |
| `addresses:` | Список CIDR | `[]` | Список статичних IPv4 та IPv6 адрес (наприклад, `[192.168.1.50/24, "2001:db8::10/64"]`). |
| `routes:` | Список словників | `[]` | Список статичних маршрутів. Кожен запис: `to:` (CIDR або `default`), `via:` (IP шлюзу), `metric:` (`int`), `table:` (`int`), `on-link:` (`bool`), `scope:` (`global`, `link`, `host`), `type:` (`unicast`, `blackhole`, `unreachable`). |
| `routing-policy:` | Список словників | `[]` | Правила FIB Policy Routing: `from:` (CIDR), `to:` (CIDR), `table:` (`int`), `priority:` (`int`), `mark:` (`int`), `type-of-service:` (`int`). |
| `nameservers:` | Словник | Відсутнє | Блок DNS. Містить списки `addresses:` (IP-адреси резолверів) та `search:` (домени пошуку). |
| `access-points:` *(wifis)* | Словник SSID | Відсутнє | Конфігурація підключень Wi-Fi. Ключ — назва SSID. Внутрішні поля: `password:` (пароль WPA-PSK), `mode:` (`infrastructure`, `ap`, `adhoc`), `bssid:` (MAC), `hidden:` (`bool`), `band:` (`5GHz`, `2.4GHz`), `channel:` (`int`). |
| `auth:` *(wifis)* | Словник | Відсутнє | Розширена автентифікація EAP: `key-management:` (`psk`, `eap`, `owe`), `identity:`, `password:`, `ca-certificate:`, `client-certificate:`, `client-key:`. |

### 3.3 Параметри віртуальних пристроїв у Netplan

#### 1. Мережеві мости (`bridges:`)
* `interfaces:` — список імен інтерфейсів-членів моста (наприклад, `[enp3s0, enp3s1]`).
* `parameters:` — словник параметрів моста ядра:
  * `stp:` — протокол Spanning Tree (`true`/`false`).
  * `forward-delay:` — затримка пересилання в секундах (типово `15` або `0` для віртуалізації).
  * `hello-time:` — інтервал Hello у секундах (типово `2`).
  * `max-age:` — максимальний вік повідомлень STP у секундах (типово `20`).
  * `ageing-time:` — час старіння записів MAC-таблиці в секундах (типово `300`).
  * `priority:` — пріоритет моста STP (ціле число `0..65535`).

#### 2. Агрегація каналів (`bonds:`)
* `interfaces:` — список імен підлеглих портів агрегації.
* `parameters:` — словник налаштувань модуля Bonding:
  * `mode:` — режим: `balance-rr`, `active-backup`, `balance-xor`, `broadcast`, `802.3ad` (LACP), `balance-tlb`, `balance-alb`.
  * `lacp-rate:` — частота контрольних пакетів LACP: `slow` (кожні 30 с) або `fast` (кожні 1 с).
  * `mii-monitor-interval:` — інтервал опитування лінка MII у мілісекундах (типово `100`).
  * `min-links:` — мінімальна кількість активних портів для утримання бонда в робочому стані.
  * `transmit-hash-policy:` — політика розподілу трафіку: `layer2`, `layer2+3`, `layer3+4`, `encap2+3`, `encap3+4`.
  * `up-delay:` / `down-delay:` — затримка реакції на зміну стану лінка в мілісекундах.
  * `primary:` — ім'я пріоритетного порту для режиму `active-backup`.
  * `primary-reselect-policy:` — політика переобрання: `always`, `better`, `failure`.
  * `fail-over-mac-policy:` — політика зміни MAC: `none`, `active`, `follow`.
  * `arp-interval:` — інтервал моніторингу ARP у мілісекундах.
  * `arp-ip-targets:` — список IP-адрес для контрольних ARP-запитів.
  * `arp-validate:` — перевірка ARP-відповідей: `none`, `active`, `backup`, `all`.

#### 3. Віртуальні локальні мережі (`vlans:`)
* `id:` — числовий ідентифікатор VLAN тегу (від `1` до `4094`).
* `link:` — ім'я батьківського базового інтерфейсу (фізичного адаптера, моста або бонда).

#### 4. Тунелі (`tunnels:`)
* `mode:` — тип інкапсуляції: `ipip`, `sit`, `gre`, `vti`, `wireguard`, `vxlan`.
* `local:` — IP-адреса локального кінця тунелю.
* `remote:` — IP-адреса віддаленого кінця тунелю.
* `port:` — порт для VXLAN чи WireGuard.
* `keys:` — криптографічні ключі: `private:`, `public:`.
* `peers:` — список пірів WireGuard (`keys: { public: ... }`, `endpoint:`, `allowed-ips:`, `keepalive:`).

### 3.4 Практичні зразки конфігурацій Netplan

:::tabs
```yaml
# /etc/netplan/01-server-dual-homed.yaml
# Сервер з двома інтерфейсами та маршрутизацією Policy Routing
network:
  version: 2
  renderer: networkd
  ethernets:
    enp3s0:
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
          metric: 100
      nameservers:
        search: [corp.lan]
        addresses: [1.1.1.1, 8.8.8.8]
    enp3s1:
      addresses:
        - 10.50.0.100/24
      routes:
        - to: 10.0.0.0/8
          via: 10.50.0.1
          metric: 200
          table: 150
      routing-policy:
        - from: 10.50.0.100/32
          table: 150
          priority: 3000
```
```yaml
# /etc/netplan/02-kvm-hypervisor-lacp-vlan.yaml
# Гіпервізор: LACP Bond + Bridge + Management VLAN
network:
  version: 2
  renderer: networkd
  ethernets:
    enp4s0f0: {}
    enp4s0f1: {}
  bonds:
    bond0:
      interfaces: [enp4s0f0, enp4s0f1]
      parameters:
        mode: 802.3ad
        lacp-rate: fast
        mii-monitor-interval: 100
        transmit-hash-policy: layer2+3
  bridges:
    br0:
      interfaces: [bond0]
      parameters:
        stp: false
        forward-delay: 0
      dhcp4: false
  vlans:
    vlan100:
      id: 100
      link: br0
      addresses:
        - 172.16.100.10/24
      routes:
        - to: default
          via: 172.16.100.1
      nameservers:
        addresses: [172.16.100.1]
```
```yaml
# /etc/netplan/03-desktop-wifi.yaml
# Робоча станція з NetworkManager рендерером та Wi-Fi WPA3
network:
  version: 2
  renderer: NetworkManager
  wifis:
    wlan0:
      dhcp4: true
      access-points:
        "Office-Employee":
          password: "SecureCompanyPassword"
          mode: infrastructure
          auth:
            key-management: psk
```
:::

### 3.5 Специфікація команд утиліти `netplan`

```bash
# 1. Синтаксична валідація та генерація конфігурацій бекенду у /run/
netplan generate

# 2. Пряме застосування конфігурації (компіляція + перезавантаження бекенду)
netplan apply

# 3. Безпечне тестування конфігурації з автоматичним відкатом
netplan try --timeout 60

# 4. Перегляд поточного зведеного стану інтерфейсів та рендерерів
netplan status
netplan status --all

# 5. Програмне читання та модифікація окремих ключів YAML
netplan get ethernets.enp3s0.addresses
netplan set ethernets.enp3s0.dhcp4=true

# 6. Перегляд активних орендованих адрес DHCP
netplan ip leases enp3s0
```

#### Контракт безпечного тестування: `netplan try`

Команда `netplan try` забезпечує захист від втрати доступу до віддалених серверів через SSH при зміні мережевих налаштувань:

1. Netplan створює резервний знімок поточної робочої конфігурації у тимчасовому каталозі.
2. Новий YAML транслюється та застосовується до активного бекенду (`systemd-networkd` або `NetworkManager`).
3. Запускається таймер зворотного відліку (за замовчуванням `120` секунд, або заданий прапорцем `--timeout <секунди>`).
4. Адміністратор повинен підтвердити збереження змін, натиснувши клавішу `Enter` у терміналі.
5. Якщо SSH-сесія обірвалася через некоректний маршрут чи помилку адресації, або користувач не натиснув `Enter` до завершення таймауту, Netplan автоматично відновлює попередній стан конфігурації та перезавантажує мережевий стек.

---

## 4. Специфікація підсистеми розпізнавання імен systemd-resolved

Сервіс `systemd-resolved` є монопольним системним менеджером конфігурації DNS, що надає локальний кешуючий stub-резолвер на адресі `127.0.0.53:53` та підтримує роздільну маршрутизацію DNS-запитів за доменами (Split DNS), валідацію DNSSEC і шифрування DNS-over-TLS (DoT).

### 4.1 Конфігурація `/etc/systemd/resolved.conf`

Файл конфігурації містить головну секцію `[Resolve]`. Додаткові фрагменти налаштувань зчитуються з каталогу `/etc/systemd/resolved.conf.d/*.conf`.

| Директива | Тип | Замовчування | Опис та семантика |
|---|---|---|---|
| `DNS=` | Список IP | Відсутнє | Список глобальних DNS-серверів через пробіл (IPv4 та IPv6). Підтримує вказівку порту (`1.1.1.1:53` або `1.1.1.1#cloudflare-dns.com` для DoT SNI). |
| `FallbackDNS=` | Список IP | Вбудований список | Резервні DNS-сервери, що використовуються лише тоді, коли жоден інтерфейс не надав власних DNS або глобальний параметр `DNS=` порожній. |
| `Domains=` | Список доменів | Відсутнє | Глобальні домени пошуку. Домени з префіксом `~` позначають домени маршрутизації (Routing Domains). Запис `~.` встановлює глобальний маршрут за замовчуванням. |
| `DNSSEC=` | `yes`, `no`, `allow-downgrade` | `allow-downgrade` | Валідація DNSSEC: `yes` (сувора перевірка, відхилення непідписаних зон), `no` (вимкнено), `allow-downgrade` (перевірка тільки за наявності DNSKEY/DS у зоні). |
| `DNSOverTLS=` | `yes`, `no`, `opportunistic` | `no` | Шифрування DoT (порт 853): `yes` (вимагає обов'язкового TLS, відхиляє plain DNS), `opportunistic` (спроба TLS з відкатом на порт 53). |
| `MulticastDNS=` | `yes`, `no`, `resolve` | `yes` | Підтримка mDNS (RFC 6762, `.local`): `yes` (резолв та анонс), `resolve` (тільки запити), `no` (вимкнено). |
| `LLMNR=` | `yes`, `no`, `resolve` | `yes` | Протокол Link-Local Multicast Name Resolution (RFC 4795): `yes`, `resolve`, `no`. |
| `ReadEtcHosts=` | `yes`, `no` | `yes` | Чи зчитувати локальні статичні записи з файлу `/etc/hosts`. |
| `ResolveUnicastSingleLabel=` | `yes`, `no` | `no` | Чи надсилати односкладові імена хостів без крапки до публічних DNS-серверів. |
| `Cache=` | `yes`, `no`, `no-negative` | `yes` | Локальне кешування відповідей: `yes` (повний кеш), `no` (вимкнено), `no-negative` (не кешувати NXDOMAIN/NODATA). |
| `CacheFromLocalhost=` | `yes`, `no` | `no` | Чи дозволяти кешування відповідей від локальних серверів (`127.0.0.1`). |
| `DNSStubListener=` | `yes`, `no`, `udp`, `tcp` | `yes` | Запуск локального DNS-сервера на петльовій адресі `127.0.0.53:53`. |
| `DNSStubListenerExtra=` | Список IP:Port | Відсутнє | Додаткові адреси та порти для прослуховування локальним stub-резолвером. |
| `StaleRetentionSec=` | Ціле число | `0` | Час у секундах, протягом якого дозволено віддавати застарілі кешовані записи при недоступності апстрім-серверів. |

```ini
# /etc/systemd/resolved.conf.d/corporate-dot.conf
[Resolve]
DNS=1.1.1.1#cloudflare-dns.com 8.8.8.8#dns.google
FallbackDNS=9.9.9.9#dns.quad9.net
Domains=corp.internal ~corp.lan
DNSSEC=allow-downgrade
DNSOverTLS=yes
MulticastDNS=resolve
LLMNR=no
Cache=yes
```

### 4.2 Режими взаємодії з `/etc/resolv.conf`

`systemd-resolved` генерує чотири різні варіанти файлів конфігурації у каталозі `/run/systemd/resolve/`. Системний файл `/etc/resolv.conf` повинен бути символічним посиланням на один із них:

```
/etc/resolv.conf ──► /run/systemd/resolve/stub-resolv.conf (Рекомендований режим)
```

1. **Режим Stub Resolver (`/run/systemd/resolve/stub-resolv.conf`)**:
   * Вміст: рядок `nameserver 127.0.0.53` та актуальний зведений перелік доменів пошуку `search`.
   * Семантика: Усі DNS-запити від бібліотеки glibc надсилаються на локальний сокет `127.0.0.53:53`. `systemd-resolved` здійснює кешування, валідацію DNSSEC та роздільну маршрутизацію (Split DNS). Це **стандартний і рекомендований** режим.
2. **Прямий статичний режим (`/run/systemd/resolve/resolv.conf`)**:
   * Вміст: прямий перелік усіх зовнішніх DNS-серверів з усіх активних інтерфейсів (щонайбільше три сервери glibc).
   * Семантика: Програми оминають локальний кеш 127.0.0.53 і звертаються напряму до апстрім-серверів. Використовується для сумісності з ПЗ усередині контейнерів/chroot, де петльова адреса `127.0.0.53` недоступна.
3. **Статичний користувацький файл (`/etc/resolv.conf`)**:
   * Семантика: Звичайний файл, не є сімлінком. `systemd-resolved` зчитує з нього DNS-сервери і використовує їх як глобальні апстріми.

### 4.3 Роздільна маршрутизація запитів (Split DNS)

При наявності кількох мережевих адаптерів (наприклад, Ethernet `enp3s0` та VPN `wg0`) `systemd-resolved` спрямовує DNS-запити за правилами прив'язки доменів:

* Домен без префікса `~` (наприклад, `Domains=corp.internal`): додається до суфіксів пошуку відносних імен (Search Domain) та реєструється як домен маршрутизації.
* Домен із префіксом `~` (наприклад, `Domains=~corp.internal`): використовується **виключно для маршрутизації** (Routing Domain) і не додається до суфіксів пошуку в `/etc/resolv.conf`.
* Домен `~.` (Routing Domain для кореня DNS): позначає інтерфейс як шлюз за замовчуванням для всіх неспецифікованих DNS-запитів.
* Якщо надійшов запит на ім'я `db.corp.internal`, `systemd-resolved` знаходить найдовший збіг суфікса серед усіх зареєстрованих Routing Domains і надсилає запит виключно на DNS-сервери інтерфейсу `wg0`.

### 4.4 Інтерфейс утиліти `resolvectl`

Утиліта `resolvectl` (раніше `systemd-resolve`) є головним CLI-інструментом взаємодії з демоном `systemd-resolved`.

```bash
# 1. Резолвінг доменного імені або зворотної PTR-адреси
resolvectl query kernel.org
resolvectl query 192.168.1.1

# 2. Перегляд глобального стану та конфігурації для кожного інтерфейсу
resolvectl status
resolvectl status wg0

# 3. Динамічне призначення DNS-серверів на конкретний інтерфейс у runtime
resolvectl dns wg0 10.200.0.1 10.200.0.2

# 4. Призначення доменів пошуку та доменів маршрутизації (Split DNS)
resolvectl domain wg0 "~corp.internal" "~corp.lan"

# 5. Увімкнення/вимкнення маршруту DNS за замовчуванням на інтерфейсі
resolvectl default-route wg0 yes

# 6. Динамічне керування DNSSEC та DNS-over-TLS для інтерфейсу
resolvectl dnssec wg0 allow-downgrade
resolvectl dnsovertls wg0 yes

# 7. Скидання локального кешу DNS
resolvectl flush-caches

# 8. Скидання профілю відстеження характеристик серверів (EDNS/DoT probe cache)
resolvectl reset-server-features

# 9. Перегляд статистики транзакцій, кешу та валідації DNSSEC
resolvectl statistics

# 10. Моніторинг потоку DNS-запитів у реальному часі
resolvectl monitor
```

### 4.5 Специфікація та механізми валідації DNSSEC у systemd-resolved

Демон `systemd-resolved` реалізує повноцінний валідуючий резолвер (Security-Aware Stub Resolver) відповідно до стандартів RFC 4033, RFC 4034, RFC 4035 та RFC 6840. Він забезпечує криптографічну перевірку автентичності джерела та цілісності відповідей DNS за допомогою асиметричної криптографії та ланцюжка цифрових підписів.

#### 1. Якорі довіри (Trust Anchors) та конфігураційні каталоги

Валідація починається з наявності хоча б одного абсолютного довіреного відкритого ключа — якоря довіри (Trust Anchor):

* **Вбудований кореневий якір**: Демон скомпільований із зашитим ключем підпису ключів KSK (Key Signing Key) кореневої зони DNS (`.`). Підтримується механізм автоматичного оновлення кореневих ключів RFC 5011.
* **Каталог `/etc/dnssec-trust-anchors.d/`**:
  * Файли `*.positive` — користувацькі позитивні якорі довіри для внутрішніх підписаних доменів або ізольованих інтранет-зон. Рядки мають стандартний синтаксис ресурсних записів `DS` або `DNSKEY`:
    ```
    corp.internal. IN DS 12345 8 2 49FD087E8DA68EBE87EF3CD934F475F2531DE0B8B2E3FE5BDEFF9B7F7EB4725E
    ```
  * Файли `*.negative` — негативні якорі довіри (Negative Trust Anchors, NTA). Визначають доменні суфікси, для яких валідація DNSSEC примусово відключається (наприклад, внутрішні домени `.corp` або зони перехоплення Captive Portal):
    ```
    corp.internal
    intranet.local
    ```

#### 2. Протокольний ланцюжок автентифікації (Authentication Chain)

Для кожного запитуваного доменного імені `systemd-resolved` виконує рекурсивну перевірку криптографічних підписів знизу вгору:

```
  [ Коренева зона "." ] ──► Root KSK (Вбудований Trust Anchor)
           │ (Підписує запис DS дочірньої зони)
           ▼
  [ Зона TLD ".com" ]  ──► DS record ──► DNSKEY (KSK) ──► DNSKEY (ZSK)
           │ (Підписує запис DS дочірньої зони)
           ▼
  [ Зона "example.com" ]─► DS record ──► DNSKEY (KSK) ──► DNSKEY (ZSK)
                                                               │
                                                               ▼
                                               RRSIG ──► RRset (A: 93.184.216.34)
```

1. **Запит із бітом DO**: Резолвер надсилає запит з увімкненим бітом `DO=1` (DNSSEC OK) в EDNS0 OPT RR, сигналізуючи авторитетним серверам про необхідність повернення записів `RRSIG`.
2. **Верифікація RRset**: Сервер повертає набір записів `RRset` та його цифровий підпис `RRSIG`. Резолвер витягує `DNSKEY` зони та перевіряє валідність підпису `RRSIG` за допомогою відкритого ключа підпису зони ZSK (Zone Signing Key).
3. **Верифікація ZSK через KSK**: Підпис набору `DNSKEY` перевіряється ключем підпису ключів KSK (Key Signing Key).
4. **Зв'язок із батьківською зоною**: Резолвер запитує запис `DS` (Delegation Signer) у батьківській зоні. Значення `DS` містить криптографічний дайджест (SHA-256 або SHA-384) дочірнього ключа KSK. Резолвер обчислює хеш від KSK і звіряє його з `DS`, а підпис `DS` перевіряє ключем батьківської зони.
5. **Фіксація результату**: Процедура повторюється до досягнення кореневого якоря довіри.

#### 3. Доведення неіснування записів: NSEC проти NSEC3

Критичною частиною DNSSEC є надання криптографічного доказу того, що запитане ім'я або тип запису дійсно **не існують** у зоні (відповіді `NXDOMAIN` або `NODATA`), без необхідності динамічного генерування підписів на авторитетних серверах у реальному часі.

##### Механізм NSEC (RFC 4034)

Запис `NSEC` (Next Secure) зв'язує всі існуючі доменні імена в зоні у канонічно відсортований циклічний список.

```
alpha.example.com.   IN NSEC beta.example.com.   A TXT RRSIG NSEC
beta.example.com.    IN NSEC gamma.example.com.  A AAAA RRSIG NSEC
```

* **Доведення NXDOMAIN**: Якщо клієнт запитує `baker.example.com`, сервер повертає запис `alpha.example.com. NSEC beta.example.com.` разом із його `RRSIG`. Оскільки ім'я `baker` за алфавітом лежить у закритому інтервалі `(alpha, beta)`, резолвер отримує математичний доказ відсутності імені.
* **Доведення NODATA**: Якщо клієнт запитує `MX` для `beta.example.com`, сервер повертає NSEC для `beta`, де в бітовій карті типів (`Type Bit Maps`) присутні `A`, `AAAA`, але відсутній біт `MX`.
* **Вразливість (Zone Walking)**: Зловмисник може послідовно запитувати імена між межами NSEC і за лічені секунди повністю викачати повну топологію всіх внутрішніх імен зони.

##### Механізм NSEC3 (RFC 5155)

`NSEC3` усуває вразливість Zone Walking шляхом заміни відкритих імен їхніми криптографічними хешами з додаванням солі та ітерацій: `H = SHA1(Name + Salt)`.

```
2T7B8MG...example.com. IN NSEC3 1 0 10 AABBCCDDEEFF 4U8C9NH... A AAAA RRSIG
```

| Поле NSEC3 | Розмір / Тип | Опис та семантика |
|---|---|---|
| `Hash Algorithm` | 1 байт (`uint8`) | Алгоритм хешування (`1` = SHA-1). |
| `Flags` | 1 байт (`uint8`) | Прапорці. Біт 0 (`0x01`) — прапорець `Opt-Out`. |
| `Iterations` | 2 байти (`uint16`) | Кількість додаткових раундів хешування (типово від 0 до 50). |
| `Salt Length` | 1 байт (`uint8`) | Довжина байтів солі. |
| `Salt` | Байти | Випадкова послідовність байтів для запобігання атакам за райдужними таблицями. |
| `Next Hashed Owner Name` | Base32Hex | Хеш наступного існуючого доменного імені у лексикографічному порядку хеш-простору. |
| `Type Bit Maps` | Змінна | Бітова карта типів ресурсних записів, наявних для даного хешу. |

* **Алгоритм валідації NXDOMAIN у systemd-resolved**:
  1. Резолвер хешує запитане ім'я `QNAME` з сіллю та ітераціями, отриманими в NSEC3.
  2. Знаходить **Covering NSEC3 Record**, чий інтервал `[Hashed Owner, Next Hashed Owner]` покриває хеш `QNAME`.
  3. Перевіряє **Closest Encloser Proof**: знаходить NSEC3, що точно відповідає хешу найдовшого існуючого суфікса (батьківського домену).
  4. Перевіряє **Wildcard Denial**: перевіряє NSEC3, що покриває хеш гіпотетичного підстановочного запису `*.closest_encloser`, доводячи, що запис не може бути згенерований через wildcard.
* **Прапорець Opt-Out (RFC 5155 §6)**:
  Дозволяє авторитетним серверам TLD (наприклад, `.com`) не генерувати NSEC3-записи для непідписаних дочірніх делегувань. `systemd-resolved` перевіряє, що відсутність `DS` для непідписаної зони потрапляє в інтервал NSEC3 з увімкненим прапорцем Opt-Out, і коректно переводить статус домену в `insecure`.

#### 4. Матриця станів валідації DNSSEC

| Стан валідації | Опис внутрішнього стану резолвера | Поведінка щодо застосунку |
|---|---|---|
| `authenticated` (`Secure`) | Ланцюжок довіри успішно пройдено до активного Trust Anchor. Усі RRSIG валідні. | Відповідь повертається з прапорцем `AD=1` (Authenticated Data) у DNS-заголовку. |
| `insecure` | Доведено, що домен або його батьківська зона не використовує DNSSEC (підтверджено валідним доказом відсутності DS). | Відповідь повертається з прапорцем `AD=0`. |
| `bogus` (`Validation Failed`) | Виявлено криптографічну невідповідність: прострочений RRSIG, невалідний дайджест DS, відсутність підпису в підписаній зоні. | Якщо `DNSSEC=yes` або `allow-downgrade` (за наявності DS), запит блокується й клієнту повертається помилка `SERVFAIL` (RCODE 2). |
| `indeterminate` | Не вдалося встановити статус через мережеву недоступність апстріму або відсутність підтримки EDNS0. | Залежить від режиму: при `DNSSEC=yes` блокується (`SERVFAIL`), при `allow-downgrade` пропускається. |

---

### 4.6 Специфікація та протокольний стек DNS-over-TLS (DoT)

Підсистема `systemd-resolved` підтримує шифрування DNS-трафіку за протоколом DNS-over-TLS (DoT) відповідно до стандартів RFC 7858 та RFC 8310.

```
┌────────────────────────────────────────────────────────┐
│              systemd-resolved Stub (127.0.0.53:53)     │
└───────────────────────────┬────────────────────────────┘
                            │ (Внутрішній роутинг)
                            ▼
┌────────────────────────────────────────────────────────┐
│           DoT Engine (OpenSSL / GnuTLS TLS 1.3)        │
│  - SNI Verification (#hostname)                        │
│  - Connection Reuse / Pipelining                       │
│  - Session Resumption (TLS Tickets)                    │
│  - EDNS0 Padding (RFC 7830 / RFC 8467)                 │
└───────────────────────────┬────────────────────────────┘
                            │ TLS по TCP:853
                            ▼
┌────────────────────────────────────────────────────────┐
│            Апстрім DoT Резолвер (1.1.1.1 / 8.8.8.8)    │
└────────────────────────────────────────────────────────┘
```

#### 1. Синтаксис конфігурації адрес та автентифікація SNI

Для запобігання атакам класу Man-in-the-Middle (MitM) шифрування DoT вимагає обов'язкової автентифікації імені віддаленого сервера:

* **Формат запису**: `<IP-адреса>#<TLS-ім'я-хоста>`
  ```ini
  DNS=1.1.1.1#cloudflare-dns.com 8.8.8.8#dns.google 2606:4700:4700::1111#cloudflare-dns.com
  ```
* Символ `#` відокремлює IP-адресу транспорту від доменного імені, яке передається у розширенні TLS Server Name Indication (SNI) під час TLS ClientHello та зіставляється з полем `Subject Alternative Name` (SAN dNSName) сертифіката X.509 сервера.

#### 2. Режими роботи `DNSOverTLS=`

| Режим | Специфікація поведінки (RFC 8310) | Дії при збої шифрування |
|---|---|---|
| `yes` | **Strict Privacy Profile**: Вимагає виключно зашифрованого каналу TLS на порт 853. Виконує повну перевірку ланцюжка сертифікатів через системне сховище CA (`/etc/ssl/certs/ca-certificates.crt`). | Якщо порт 853 заблоковано, сертифікат прострочено або ім'я SNI не збігається, запит негайно завершується помилкою. Відкат на відкритий порт 53 суворо заборонено. |
| `opportunistic` | **Opportunistic Privacy Profile**: Намагається встановити DoT-з'єднання на порт 853. | Якщо з'єднання відхилено (TCP RST), виник таймаут або сертифікат не пройшов перевірку, резолвер фіксує сервер як обмежений у внутрішньому probe-кеші та прозоро відкочується на стандартний DNS (порт 53 UDP/TCP). Періодично виконує фонові probe-спроби для повернення на TLS. |
| `no` | Шифрування DoT вимкнено. Усі запити надсилаються на порт 53 UDP/TCP. | — |

#### 3. Оптимізація сесій та захист від аналізу трафіку

* **Мультиплексування (Pipelining) та Connection Reuse**: Демон утримує постійні відкриті TCP/TLS з'єднання до налаштованих апстрімів. Усі паралельні DNS-запити від локальних процесів надсилаються через єдиний сокет з унікальними ідентифікаторами `Transaction ID` без очікування відповіді на попередній пакет, що нівелює затримку на рукостискання TLS (0-RTT / 1-RTT).
* **TLS Session Resumption**: Використовуються механізми TLS Session Tickets (RFC 5077) та TLS 1.3 Pre-Shared Key (PSK), що дозволяє миттєво відновлювати зашифровану сесію при рестарті з'єднання без виконання повної фази асиметричного обміну ключами.
* **Вирівнювання довжини повідомлень (EDNS0 Padding, RFC 7830 / RFC 8467)**:
  Розмір DNS-запитів та відповідей корелює з довжиною запитуваних доменних імен. Зловмисник, що прослуховує зашифрований канал, може ідентифікувати відвідувані сайти за точним розміром пакетів.
  `systemd-resolved` додає опцію EDNS0 Padding (код опції `12`), доповнюючи розмір кожного вихідного блоку нульовими байтами до фіксованих меж:
  * Запити вирівнюються блоками по **128 байтів**.
  * Відповіді вирівнюються блоками по **468 байтів**.

---

## 5. Специфікація класичного ifupdown (`/etc/network/interfaces`) та resolvconf

Комплекс утиліт `ifupdown` (`ifup`, `ifdown`, `ifquery`) є історичним стандартом для дистрибутивів Debian та Ubuntu. Конфігурація мережі описується у файлі `/etc/network/interfaces` та фрагментах у каталозі `/etc/network/interfaces.d/*`.

Утиліти фіксують стан інтерфейсів у системному файлі статусу `/run/network/ifstate` і блокують паралельні виклики через lock-файл `/run/network/.ifstate.lock`.

### 5.1 Глобальні строфи та директиви включення

| Директива | Синтаксис | Призначення |
|---|---|---|
| `source` | `source /etc/network/interfaces.d/*` | Включає конфігураційні файли за зазначеним шляхом або glob-шаблоном. |
| `source-directory` | `source-directory /etc/network/interfaces.d` | Рекурсивно підключає всі валідні файли з каталогу (ігноруючи резервні копії з тильдою `~` та крапками). |
| `auto` | `auto eth0 eth1` | Позначає інтерфейси, які автоматично піднімаються при завантаженні системи або при виклику `ifup -a`. |
| `allow-hotplug` | `allow-hotplug eth0` | Інтерфейс піднімається асинхронно демоном `udev` при виявленні події появи апаратного пристрою в ядрі. |
| `mapping` | `mapping eth0 script /usr/local/bin/map-script` | Динамічне зіставлення фізичного інтерфейсу з логічним профілем. |

### 5.2 Строфа визначення інтерфейсу `iface`

```
iface <логічне-ім'я> <сімейство-адрес> <метод>
```

* **Сімейство адрес (`address family`)**: `inet` (IPv4) або `inet6` (IPv6).
* **Методи конфігурації (`method`)**:
  * `static` — статичне призначення IP-адрес і параметрів підмережі.
  * `dhcp` — отримання параметрів через зовнішній DHCP-клієнт (`dhclient`, `udhcpc`, `dhcpcd`).
  * `manual` — інтерфейс переводиться в стан `UP` (`ip link set dev <dev> up`), але стек L3 не налаштовується (застосовується для підлеглих портів Bridge/Bond).
  * `loopback` — спеціальний метод для петльового пристрою `lo`.
  * `ppp` — підключення через Point-to-Point Protocol (PPPoE).
  * `wpa` — конфігурація Wi-Fi через зовнішній файл `wpa_supplicant.conf`.

#### Опції методів `static` та `dhcp`

| Опція | Метод | Опис |
|---|---|---|
| `address` | `static` | IP-адреса вузла (`192.168.1.50` або `192.168.1.50/24`). |
| `netmask` | `static` | Маска підмережі у десятковому форматі (`255.255.255.0`). Не потрібна, якщо префікс вказано в `address`. |
| `gateway` | `static` | IP-адреса шлюзу за замовчуванням (`192.168.1.1`). |
| `broadcast` | `static` | Широкомовна адреса підмережі (`192.168.1.255`). |
| `metric` | `static`, `dhcp` | Метрика для доданого маршруту за замовчуванням. |
| `mtu` | `static`, `dhcp` | Розмір максимального кадру MTU. |
| `scope` | `static` | Рівень досяжності адреси (`global`, `link`, `host`). |
| `pointopoint` | `static` | IP-адреса віддаленого вузла для з'єднань точка-точка. |
| `hwaddress` | `static`, `dhcp` | Підміна апаратної MAC-адреси інтерфейсу (`hwaddress ether 52:54:00:12:34:56`). |
| `hostname` | `dhcp` | Рядок імені хоста, що передається у DHCP Option 12. |
| `client` | `dhcp` | Ідентифікатор клієнта для DHCP Option 61. |
| `dns-nameservers` | `static` | Список DNS-серверів через пробіл (передається у `resolvconf`). |
| `dns-search` | `static` | Список доменів пошуку DNS (передається у `resolvconf`). |

### 5.3 Життєвий цикл та хук-директиви

`ifupdown` надає можливість виконувати довільні системні команди та скрипти на чотирьох фазах життєвого циклу інтерфейсу:

```
                  ┌─────────────────────────────────────┐
                  │          ifup <interface>           │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │   pre-up <команда>  │  (Лінк ще DOWN)
                          └──────────┬──────────┘
                                     │ (якщо exit code == 0)
                                     ▼
                          ┌─────────────────────┐
                          │ Конфігурація L2/L3  │  (ip link set up, dhclient/ip addr)
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │  post-up / up <cmd> │  (Інтерфейс активний і готовий)
                          └─────────────────────┘

                  ┌─────────────────────────────────────┐
                  │         ifdown <interface>          │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ pre-down / down     │  (Перед зняттям адрес/зупинкою)
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ Зняття адрес ядра   │  (ip addr flush, ip link set down)
                          └──────────┬──────────┘
                                     │
                                     ▼
                          ┌─────────────────────┐
                          │ post-down <команда> │  (Лінк повністю зупинено)
                          └─────────────────────┘
```

Якщо команда у директиві `pre-up` завершується з ненульовим кодом повернення, `ifup` негайно перериває виконання і не налаштовує інтерфейс.

#### Змінні оточення всередині хук-скриптів

Під час виконання директив `pre-up`, `post-up`, `down`, `post-down` та скриптів у каталогах `/etc/network/if-*.d/` утиліта `ifupdown` експортує змінні оточення:
* `$IFACE` — системне фізичне ім'я інтерфейсу (наприклад, `eth0`).
* `$LOGICAL` — логічне ім'я профілю з'єднання.
* `$ADDRFAM` — сімейство адрес (`inet` або `inet6`).
* `$METHOD` — активний метод (`static`, `dhcp`, `manual`).
* `$MODE` — режим дії (`start` для `ifup`, `stop` для `ifdown`).
* `$PHASE` — поточна фаза виконання (`pre-up`, `post-up`, `pre-down`, `post-down`).
* `$VERBOSITY` — рівень деталізації (`1`, якщо увімкнено прапорець `-v`, інакше `0`).

### 5.4 Інтерфейс утиліти `resolvconf`

Пакет `resolvconf` є посередником між динамічними клієнтами (DHCP, VPN, PPP) або статичним `ifupdown` та файлом `/etc/resolv.conf`:

* Кожен сервіс реєструє свої DNS-налаштування шляхом надсилання рядків формату `resolv.conf` у стандартний ввід команди `resolvconf -a <інтерфейс.протокол>`:
  ```bash
  printf "nameserver 1.1.1.1\nsearch corp.lan\n" | /sbin/resolvconf -a eth0.inet
  ```
* При зупинці інтерфейсу фрагмент видаляється:
  ```bash
  /sbin/resolvconf -d eth0.inet
  ```
* Демон зберігає фрагменти у каталозі `/run/resolvconf/interface/`, об'єднує їх відповідно до пріоритетів файлу `/etc/resolvconf.conf` та атомарно оновлює кінцевий файл `/etc/resolv.conf`.

### 5.5 Практичні зразки конфігурації `/etc/network/interfaces`

:::tabs
```ini
# /etc/network/interfaces — Базовий сервер зі статичною адресацією та DNS
auto lo
iface lo inet loopback

# Автоматичний підйом основного порту WAN
auto eth0
iface eth0 inet static
    address 198.51.100.50/24
    gateway 198.51.100.1
    dns-nameservers 1.1.1.1 8.8.8.8
    dns-search corp.internal
    pre-up /sbin/iptables -F
    post-up /sbin/ip route add 10.0.0.0/8 via 198.51.100.254 dev eth0
    pre-down /sbin/ip route del 10.0.0.0/8 via 198.51.100.254 dev eth0

# IPv6 конфігурація для того самого порту
iface eth0 inet6 static
    address 2001:db8:1::50/64
    gateway 2001:db8:1::1
    dns-nameservers 2606:4700:4700::1111
```
```ini
# /etc/network/interfaces — Сервер віртуалізації (Bridge + VLAN 802.1Q)
auto lo
iface lo inet loopback

# Базовий фізичний інтерфейс переводиться в режим manual
auto eth0
iface eth0 inet manual

# Створення саб-інтерфейсу VLAN 100
auto eth0.100
iface eth0.100 inet manual
    vlan-raw-device eth0

# Мережевий міст поверх VLAN для віртуальних машин
auto br100
iface br100 inet static
    address 172.16.100.10/24
    gateway 172.16.100.1
    bridge_ports eth0.100
    bridge_stp off
    bridge_fd 0
    bridge_maxwait 0
```
:::

---

## 6. Зведена матриця операцій між мережевими підсистемами

| Завдання адміністрування | NetworkManager (`nmcli`) | systemd-networkd (`networkctl`) | Netplan (`netplan`) | systemd-resolved (`resolvectl`) | ifupdown (`ifup`/`ifdown`) |
|---|---|---|---|---|---|
| **Головний конфігураційний каталог** | `/etc/NetworkManager/system-connections/` | `/etc/systemd/network/` | `/etc/netplan/` | `/etc/systemd/resolved.conf.d/` | `/etc/network/interfaces` |
| **Формат файлів** | INI / Keyfile (`.nmconnection`) | INI / Unit-подібний (`.network`, `.netdev`, `.link`) | YAML (`.yaml`) | INI (`.conf`) | Плоский текст / строфи `iface` |
| **Перевірка загального статусу** | `nmcli general status` | `networkctl status` | `netplan status` | `resolvectl status` | — |
| **Список пристроїв та станів** | `nmcli device status` | `networkctl list` | `netplan status` | `resolvectl status` | `ifquery --list` / `cat /run/network/ifstate` |
| **Детальна інспекція порту** | `nmcli device show <dev>` | `networkctl status <dev>` | — | `resolvectl status <dev>` | `ifquery <dev>` |
| **Підйом інтерфейсу** | `nmcli connection up <id>` | `networkctl up <dev>` | — | — | `ifup <iface>` |
| **Зупинка інтерфейсу** | `nmcli connection down <id>` | `networkctl down <dev>` | — | — | `ifdown <iface>` |
| **Застосування змін без перезавантаження** | `nmcli connection reload && nmcli device reapply <dev>` | `networkctl reload && networkctl reconfigure <dev>` | `netplan apply` | `systemctl reload systemd-resolved` | `ifdown <iface> && ifup <iface>` |
| **Безпечне тестування (Safe Fallback)** | — | — | `netplan try --timeout N` | — | — |
| **Поновлення оренди DHCP** | `nmcli device reapply <dev>` | `networkctl renew <dev>` | — | — | `dhclient -r <iface> && dhclient <iface>` |
| **Діагностика DNS та доменів** | `nmcli device show <dev>` | `networkctl status <dev>` | — | `resolvectl query <host>` | `cat /etc/resolv.conf` |
| **Скидання кешу DNS** | — | — | — | `resolvectl flush-caches` | — |
| **Моніторинг подій у реальному часі** | `nmcli monitor` | `networkctl monitor` | — | `resolvectl monitor` | — |

---

## 7. Взаємодія кількох мережевих стеків на одному хості та стратегії міграції

Сучасні дистрибутиви Linux нерідко містять одночасно кілька активних менеджерів мережі: наприклад, серверну підсистему `systemd-networkd`, сервіс віртуалізації Docker/Containerd (що керує власними мостами та veth-парами через внутрішні Netlink-виклики), десктопний стек `NetworkManager` для Wi-Fi/VPN та залишки класичного комплексу `ifupdown`.

### 7.1 Проблема конкуренції стеків за Netlink та розмежування зон відповідальності

Ядро Linux не має механізму ексклюзивного блокування мережевих інтерфейсів за окремим процесом. Будь-який демон із системним привілеєм `CAP_NET_ADMIN` має право додавати або видаляти IP-адреси, змінювати MTU, виставляти прапорці лінка та переписувати маршрути у FIB через сокет `NETLINK_ROUTE`.

Якщо два різні демони одночасно намагаються керувати одним фізичним або віртуальним адаптером, виникає стан конкурентної гонки (Race Condition / Split-Brain):
1. Демон А призначає IP-адресу `192.168.1.50/24` та шлюз за замовчуванням `192.168.1.1`.
2. Демон Б отримує асинхронне сповіщення `RTM_NEWADDR` через Netlink, розпізнає невідому адресу як чужорідну й надсилає `RTM_DELADDR` та `RTM_DELROUTE`.
3. Демон А фіксує несанкціоноване видалення адреси й повторно надсилає `RTM_NEWADDR`.
4. Виникає безперервний цикл перемикання станів (Flapping), що призводить до повного колапсу мережевого зв'язку, деградації продуктивності CPU та розриву сокетів TCP.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Ядро Linux (FIB & Links)                        │
└───────────────────▲────────────────────────────────▲───────────────────┘
                    │ (RTM_NEWADDR / RTM_NEWROUTE)   │ (RTM_DELADDR)
                    │                                │
        ┌───────────┴───────────┐        ┌───────────┴───────────┐
        │    NetworkManager     │        │   systemd-networkd    │
        │  (Керує Wi-Fi / VPN)  │        │  (Керує Ethernet/LAN) │
        └───────────────────────┘        └───────────────────────┘
                    ▲                                ▲
                    │                                │
            [unmanaged-devices]               [Unmanaged=yes]
         (ігнорує eth0, br0, bond0)        (ігнорує wlan0, wg0)
```

#### Механізми виключення інтерфейсів у NetworkManager

Щоб заборонити `NetworkManager` втручатися в роботу інтерфейсів, якими керує `systemd-networkd`, KVM або Docker, використовуються три взаємодоповнюючі механізми:

##### 1. Декларативне правило в `NetworkManager.conf`

У каталозі `/etc/NetworkManager/conf.d/` створюється файл `99-unmanaged-devices.conf`:

```ini
# /etc/NetworkManager/conf.d/99-unmanaged-devices.conf
[keyfile]
# Перелік шаблонів інтерфейсів через крапку з комою
unmanaged-devices=interface-name:enp3s0;interface-name:enp3s1;interface-name:br*;interface-name:veth*;mac:52:54:00:12:34:56;type:bridge;type:bond
```

* Підтримувані селектори: `interface-name:<glob>`, `mac:<XX:XX:XX:XX:XX:XX>`, `type:<технологія>`, `except:interface-name:<виняток>`.

##### 2. Правило системного менеджера udev

Правила udev позначають пристрій спеціальною змінною оточення `NM_UNMANAGED` у момент його появи в ядрі до того, як NetworkManager спробує його налаштувати:

```udev
# /etc/udev/rules.d/99-networkmanager-unmanaged.rules
SUBSYSTEM=="net", ACTION=="add", ENV{INTERFACE}=="veth*", ENV{NM_UNMANAGED}="1"
SUBSYSTEM=="net", ACTION=="add", ENV{INTERFACE}=="docker*", ENV{NM_UNMANAGED}="1"
SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="52:54:00:aa:bb:cc", ENV{NM_UNMANAGED}="1"
```

##### 3. Динамічне переведення через D-Bus API у runtime

```bash
# Примусове відключення керування пристроєм через busctl
busctl set-property org.freedesktop.NetworkManager \
    /org/freedesktop/NetworkManager/Devices/1 \
    org.freedesktop.NetworkManager.Device Managed b false
```

#### Механізми виключення інтерфейсів у systemd-networkd

##### 1. Декларативна директива `Unmanaged=yes`

У каталозі `/etc/systemd/network/` створюється файл із найвищим пріоритетом (найменший числовий префікс), що зіставляється з виключеними пристроями:

```ini
# /etc/systemd/network/00-unmanaged.network
[Match]
Name=wlan* wwan* virbr* docker* veth*

[Link]
Unmanaged=yes
```

##### 2. Блокування через CLI `networkctl mask`

Команда `networkctl mask <інтерфейс>` створює тимчасовий конфігураційний файл у каталозі періоду виконання `/run/systemd/network/10-netif-<інтерфейс>.network` із директивою `Unmanaged=yes`, миттєво припиняючи будь-яку активність демона на цьому порті:

```bash
networkctl mask wlan0
```

##### 3. Правило udev для systemd-networkd

```udev
# /etc/udev/rules.d/99-networkd-unmanaged.rules
SUBSYSTEM=="net", ACTION=="add", ENV{INTERFACE}=="wlan*", ENV{SYSTEMD_NETWORKD_UNMANAGED}="1"
```

#### Захист від флапінгу та збереження конфігурації при збоях

У змішаних та високошвидкісних мережах критично важливо правильно налаштувати поведінку демона при тимчасових апаратних розривах та рестартах сервісів:

##### Директива `IgnoreCarrierLost=` (Захист від затримок Spanning Tree)

Коли мережевий кабель підключається до керованого комутатора, протоколи Spanning Tree (IEEE 802.1D STP / 802.1w RSTP) перевіряють порт на наявність петель комутації, утримуючи його у стані Listening/Learning протягом 15–30 секунд. Без додаткових директив `systemd-networkd` фіксує подію `IFLA_CARRIER: 0` і негайно видаляє всі IP-адреси та шлюзи з ядра.

```ini
# /etc/systemd/network/10-eth0.network
[Match]
Name=eth0

[Network]
Address=192.168.10.50/24
Gateway=192.168.10.1
# Утримувати IP-адреси та маршрути в ядрі протягом 15 секунд після втрати лінка
IgnoreCarrierLost=15s
```

* Значення `IgnoreCarrierLost=yes` повністю забороняє демону знімати налаштування при фізичному відключенні кабелю (стан `NO-CARRIER`).

##### Директива `KeepConfiguration=` (Безшовне оновлення та перезапуск демонів)

За замовчуванням (`KeepConfiguration=no`) при зупинці або перезавантаженні сервісу `systemd-networkd.service` (наприклад, під час оновлення системних пакетів через `apt upgrade`) демон надсилає Netlink-запити на видалення всіх створених ним IP-адрес і маршрутів, що призводить до миттєвого розриву активних SSH-з'єднань.

| Значення `KeepConfiguration=` | Поведінка при рестарті/зупинці демона |
|---|---|
| `no` | Повне очищення: демон видаляє всі адреси, маршрути та правила Policy Routing. |
| `yes` | Повне збереження: усі адреси, маршрути та оренди DHCP залишаються в ядрі недоторканними. Новий екземпляр демона перехоплює їх без скидання лінка. |
| `static` | Зберігаються лише статично налаштовані адреси та маршрути; динамічні оренди DHCP видаляються. |
| `dhcp-on-stop` | Демон не надсилає серверу пакет DHCP Release, зберігаючи призначену динамічну адресу в ядрі. |

---

### 7.2 Покроковий алгоритм міграції з legacy ifupdown на Netplan / systemd-networkd / NetworkManager

Міграція робочого сервера зі застарілого комплексу `ifupdown` (`/etc/network/interfaces`) на сучасний декларативний стек вимагає суворого дотримання послідовності дій, аби уникнути блокування віддаленого доступу через SSH (Zero-Downtime Migration).

#### 1. Таблиця трансляції конфігураційних конструкцій

| Конструкція `/etc/network/interfaces` | Аналог у Netplan (`.yaml`) | Аналог у `systemd-networkd` (`.network` / `.netdev`) |
|---|---|---|
| `auto eth0` + `iface eth0 inet static` | `ethernets.eth0.addresses: [IP/MASK]` | `[Match] Name=eth0` + `[Network] Address=IP/MASK` |
| `gateway 192.168.1.1` | `ethernets.eth0.routes: [{to: default, via: 192.168.1.1}]` | `[Network] Gateway=192.168.1.1` |
| `iface eth0 inet dhcp` | `ethernets.eth0.dhcp4: true` | `[Network] DHCP=ipv4` |
| `dns-nameservers 1.1.1.1 8.8.8.8` | `ethernets.eth0.nameservers.addresses: [1.1.1.1, 8.8.8.8]` | `[Network] DNS=1.1.1.1 8.8.8.8` |
| `dns-search corp.lan` | `ethernets.eth0.nameservers.search: [corp.lan]` | `[Network] Domains=corp.lan` |
| `auto eth0.100` + `vlan-raw-device eth0` | `vlans.vlan100: {id: 100, link: eth0}` | `30-vlan100.netdev` (`[VLAN] Id=100`) + `VLAN=vlan100` у файлі батьківського порту |
| `auto br0` + `bridge_ports eth0 eth1` | `bridges.br0.interfaces: [eth0, eth1]` | `20-br0.netdev` (`Kind=bridge`) + `Bridge=br0` у файлах портів |
| `bond-master bond0` + `bond-mode 802.3ad` | `bonds.bond0.parameters.mode: 802.3ad` | `20-bond0.netdev` (`Kind=bond`, `Mode=802.3ad`) + `Bond=bond0` у файлах портів |
| `post-up ip route add ...` | `ethernets.eth0.routes: [...]` | Секція `[Route]` у відповідному `.network` файлі |

#### 2. Покроковий протокол безшовної міграції на живому сервері

```
 [Крок 1: Підготовка] ──► Створення Netplan YAML / networkd units (KeepConfiguration=yes)
          │
          ▼
 [Крок 2: Валідація]  ──► Синтаксична перевірка без застосування (netplan generate)
          │
          ▼
 [Крок 3: Пасивація]  ──► ifdown --no-act (зняття прапорців ifstate без flush адрес)
          │
          ▼
 [Крок 4: Вимкнення]  ──► systemctl disable --now networking.service
          │
          ▼
 [Крок 5: Активація]  ──► systemctl enable --now systemd-networkd systemd-resolved
          │
          ▼
 [Крок 6: DNS-сімлінк]──► ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
          │
          ▼
 [Крок 7: Контроль]   ──► networkctl status && resolvectl status && ip route show
```

##### Командна реалізація процедури:

```bash
# КРОК 1. Створення нової цільової конфігурації Netplan
cat <<'EOF' > /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 198.51.100.50/24
      routes:
        - to: default
          via: 198.51.100.1
      nameservers:
        search: [corp.internal]
        addresses: [1.1.1.1, 8.8.8.8]
EOF

# КРОК 2. Валідація синтаксису та генерація runtime-файлів systemd-networkd
netplan generate

# КРОК 3. Увімкнення утримання конфігурації у згенерованих файлах
# Гарантує, що старт networkd не скине поточну активну SSH-сесію
mkdir -p /etc/systemd/network/10-netplan-eth0.network.d/
cat <<'EOF' > /etc/systemd/network/10-netplan-eth0.network.d/override.conf
[Network]
KeepConfiguration=yes
EOF

# КРОК 4. Пасивація ifupdown без скидання адрес у ядрі Linux
# Прапорець --no-act оновлює /run/network/ifstate, не виконуючи ip addr flush
ifdown --no-act -a

# КРОК 5. Зупинка, вимкнення та маскування застарілих unit-файлів
systemctl stop networking.service ifupdown-wait-online.service
systemctl disable networking.service ifupdown-wait-online.service
systemctl mask networking.service

# КРОК 6. Запуск та активація сучасного стека systemd
systemctl enable --now systemd-networkd.service
systemctl enable --now systemd-resolved.service

# КРОК 7. Атомарне перемикання системного резолвера DNS
ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf

# КРОК 8. Інспекція стану та підтвердження стабільності
networkctl status eth0
resolvectl status
ip route show
```

---

## 8. Специфікація діагностики, журналювання та низькорівневого трасування мережевих демонів (Debugging & Tracing Reference)

Діагностика мережевих демонів вимагає комплексного аналізу на трьох рівнях:
1. **Рівень системних журналів та внутрішніх кінцевих автоматів** (`journalctl`, `systemd-analyze`, `nmcli general logging`).
2. **Рівень канального протокольного виявлення сусідів** (IEEE 802.1AB LLDP через `networkctl lldp` та `nmcli device lldp`).
3. **Рівень реального часу та системних шин** (`networkctl monitor`, `nmcli monitor`, `resolvectl monitor`, перехоплення `NETLINK_ROUTE` та подій `udev`).

### 8.1 Журналювання та динамічне налагодження через `journalctl` та D-Bus API

#### 1. systemd-networkd та systemd-resolved: рівні журналювання та динамічне керування

За замовчуванням сервіси `systemd-networkd` та `systemd-resolved` записують повідомлення рівня `info` та вище. Для виявлення проблем з узгодженням DHCP, таймаутами DAD або помилками валідації DNSSEC рівень деталізації перемикається у режим `debug`.

##### Встановлення рівня журналу через змінні оточення (постійна конфігурація)

У каталозі `/etc/systemd/system/systemd-networkd.service.d/` створюється drop-in файл `10-debug.conf`:

```ini
# /etc/systemd/system/systemd-networkd.service.d/10-debug.conf
[Service]
Environment=SYSTEMD_LOG_LEVEL=debug
Environment=SYSTEMD_LOG_LOCATION=yes
```

* `SYSTEMD_LOG_LEVEL=debug`: активує вивід детальних повідомлень Netlink-транзакцій, кроків FSM та парсингу опцій DHCP.
* `SYSTEMD_LOG_LOCATION=yes`: додає до кожного рядка журналу ім'я вихідного C-файлу та номер рядка у коді systemd (наприклад, `src/network/networkd-link.c:1245`), що критично для точної діагностики.

##### Динамічне перемикання рівня журналу без перезапуску сервісів (Runtime)

Зміна рівня журналу на льоту здійснюється за допомогою утиліти `systemd-analyze` або прямими викликами D-Bus методів через `busctl`:

:::tabs
```bash
# 1. Керування через systemd-analyze
systemd-analyze set-log-level systemd-networkd debug
systemd-analyze set-log-level systemd-resolved debug

# Повернення до стандартного рівня
systemd-analyze set-log-level systemd-networkd info
```
```bash
# 2. Керування через системну шину D-Bus (busctl)
# Для systemd-networkd (інтерфейс org.freedesktop.network1.Manager)
busctl call org.freedesktop.network1 \
    /org/freedesktop/network1 \
    org.freedesktop.network1.Manager \
    SetLogLevel s "debug"

# Для systemd-resolved (інтерфейс org.freedesktop.resolve1.Manager)
busctl call org.freedesktop.resolve1 \
    /org/freedesktop/resolve1 \
    org.freedesktop.resolve1.Manager \
    SetLogLevel s "debug"
```
:::

##### Вибірка та фільтрація повідомлень через `journalctl`

```bash
# Потоковий моніторинг networkd з монотонним системним таймстампом
journalctl -u systemd-networkd.service -f -o short-monotonic --no-pager

# Спільний перегляд журналів networkd та resolved у форматі ISO-часу
journalctl -u systemd-networkd.service -u systemd-resolved.service -f -o short-iso

# Фільтрація повідомлень networkd щодо конкретного мережевого інтерфейсу
journalctl -u systemd-networkd.service _KERNEL_DEVICE=+net:enp3s0 -f
```

#### 2. NetworkManager: динамічна система доменного журналювання

`NetworkManager` використовує дворівневу модель журналювання: глобальний рівень важливості (`level`) та перелік функціональних підсистем (`domains`).

##### Команди інспектування та керування журналами (`nmcli general logging`)

```bash
# 1. Перегляд поточного рівня та активних доменів журналювання
nmcli general logging

# 2. Увімкнення глобального максимального налагодження (DEBUG для всіх доменів)
nmcli general logging level DEBUG domains ALL

# 3. Вибіркове включення рівня TRACE для критичних модулів (Ethernet, IPv4, DHCP)
nmcli general logging level TRACE domains CORE,ETHER,IP4,DHCP4

# 4. Налагодження виключно бездротового стека та Wi-Fi автентифікації
nmcli general logging level DEBUG domains WIFI,SUPPLICANT

# 5. Повернення до стандартного рівня
nmcli general logging level INFO domains DEFAULT
```

##### Специфікація доменів журналювання NetworkManager

| Домен журналювання | Підсистема та охоплені процеси |
|---|---|
| `PLATFORM` | Взаємодія з ядром Linux через сокети Netlink, ethtool та sysfs. |
| `CORE` | Головний цикл подій, менеджер станів пристроїв, ініціалізація сервісу. |
| `DEVICE` | Скінченний автомат життєвого циклу мережевих адаптерів (FSM станів `CONFIG`, `IP_CONFIG`). |
| `HW` | Апаратні операції канального рівня, зчитування EEPROM, конфігурація MAC. |
| `ETHER` | Специфіка провідних адаптерів Ethernet 802.3. |
| `WIFI` | Бездротові адаптери 802.11, сканування ефіру, роумінг. |
| `SUPPLICANT` | D-Bus обмін із зовнішнім демоном `wpa_supplicant`. |
| `IP4` / `IP6` | Налаштування IPv4/IPv6 адрес, шлюзів, обробка SLAAC та ICMPv6 Router Advertisements. |
| `DHCP4` / `DHCP6` | Внутрішній або зовнішній DHCP-клієнт, розбір опцій та фаз оренди (DORA). |
| `ROUTE` | Оновлення таблиць маршрутизації ядра FIB та правил Policy Routing. |
| `DNS` | Формування конфігурації DNS та взаємодія з `systemd-resolved` / `resolvconf`. |
| `VPN` | Керування дочірніми процесами VPN-плагінів (WireGuard, OpenVPN, StrongSwan). |
| `SETTINGS` | Зчитування, валідація та запис Keyfile-профілів у `/etc/NetworkManager/system-connections/`. |

```bash
# Зчитування виводу журналу NetworkManager
journalctl -u NetworkManager.service -f -o cat
```

---

### 8.2 Інспектування топології канального рівня та протоколу LLDP

Протокол виявлення канального рівня (Link Layer Discovery Protocol, LLDP, стандартизований у IEEE 802.1AB) дозволяє мережевим адаптерам пасивно отримувати інформацію про фізичний порт комутатора, ім'я шасі, PVID VLAN та можливості пристрою без надсилання IP-трафіку. Кадри LLDP транслюються комутатором кожні 30 секунд на зарезервовану групову MAC-адресу `01:80:C2:00:00:0E` з EtherType `0x88CC`.

#### 1. Структура TLV кадру LLDP

| Тип TLV | Назва | Вміст та семантика |
|---|---|---|
| `TLV 1` | Chassis ID | Апаратний ідентифікатор комутатора (MAC-адреса, ім'я шасі або локальний ID). |
| `TLV 2` | Port ID | Фізичний ідентифікатор порту комутатора (наприклад, `GigabitEthernet1/0/24`, `eth0`, `Slot 1 Port 4`). |
| `TLV 3` | Time To Live (TTL) | Час у секундах, протягом якого інформація вважається валідною (типово `120s`). |
| `TLV 4` | Port Description | Текстовий коментар адміністратора до порту на комутаторі (наприклад, `Trunk-to-Server-Rack-B`). |
| `TLV 5` | System Name | Системне мережеве ім'я (hostname) комутатора (наприклад, `sw-core-01.corp`). |
| `TLV 6` | System Description | Назва моделі комутатора, версія прошивки/ОС (Cisco IOS, JunOS, Arista EOS). |
| `TLV 7` | System Capabilities | Бітова маска можливостей: `Bridge`, `Router`, `WLAN AP`, `Repeater`, `Telephone`. |
| `TLV 8` | Management Address | IPv4/IPv6 адреса керування комутатором для доступу через SSH/SNMP. |
| `TLV 127` | Org Specific | Організаційні розширення: IEEE 802.1 Port VLAN ID (PVID), IEEE 802.3 Link Aggregation, MTU. |

#### 2. Інспектування LLDP у `systemd-networkd` (`networkctl lldp` та `status`)

Для активації прийому LLDP у файлі `.network` відповідного інтерфейсу виставляється директива `LLDP=yes` (або `LLDP=routers-only`) у секції `[Network]`.

```bash
# Перегляд переліку сусідніх комутаторів, виявлених за протоколом LLDP
networkctl lldp enp3s0
```

```
LINK             CHASSIS ID        SYSTEM NAME               PORT ID                  PORT DESCRIPTION
enp3s0           52:54:00:ee:ff:01 sw-core-leaf01.corp.lan   GigabitEthernet1/0/12    Trunk to Server SRV-01

Neighbor: 52:54:00:ee:ff:01
  Chassis ID: 52:54:00:ee:ff:01 (MAC address)
  System Name: sw-core-leaf01.corp.lan
  System Description: Cisco IOS Software, C3750E Software (C3750E-UNIVERSALK9-M), Version 15.0(2)SE
  Port ID: GigabitEthernet1/0/12 (Interface name)
  Port Description: Trunk to Server SRV-01
  System Capabilities: Bridge, Router
  Enabled Capabilities: Bridge
  Management Address: 10.0.0.254 (IPv4)
  Port VLAN ID: 100
```

```bash
# Комплексна перевірка стану адаптера, зв'язаного файлу та адресації
networkctl status enp3s0
```

```
● 2: enp3s0
       Link File: /usr/lib/systemd/network/99-default.link
    Network File: /etc/systemd/network/10-enp3s0.network
            Type: ether
           State: routable (configured)
    Online state: online
            Path: pci-0000:00:1f.6
          Driver: e1000e
          Vendor: Intel Corporation
            HW Address: 52:54:00:12:34:56
             MTU: 1500 (min: 68, max: 9216)
           Speed: 1Gbps
          Duplex: full
         Address: 192.168.10.50 (DHCPv4 via 192.168.10.1)
                  2001:db8:1::50
                  fe80::5054:ff:fe12:3456
         Gateway: 192.168.10.1 (Intel Corporation)
             DNS: 1.1.1.1
                  8.8.8.8
  Search Domains: corp.internal
            DHCP: DHCPv4 client lease acquired (T1: 6h, T2: 10.5h, Expiration: 12h)
```

#### 3. Інспектування LLDP у `NetworkManager` (`nmcli device lldp`)

У NetworkManager обробка LLDP активується параметром `lldp=1` (тільки прийом) або `lldp=2` (прийом та збереження) у секції `[connection]` профілю.

```bash
# Перегляд отриманих LLDP-сусідів для пристрою
nmcli device lldp list ifname enp3s0
```

---

### 8.3 Моніторинг потоку подій у реальному часі (Real-Time Event Streaming)

Консольні монітори дозволяють спостерігати за системними подіями безперервно у реальному часі, фіксуючи кожну зміну стану зв'язку або D-Bus транзакцію.

#### 1. Монітор `networkctl monitor` (systemd-networkd)

Утиліта підключається до системного циклу `sd-event` і транслює потокові зміни `OperationalState` та `SetupState` для всіх інтерфейсів ядра:

```bash
networkctl monitor
```

```
Timestamp              Index Link            OperationalState  SetupState
Sat 2026-08-29 17:15:01    2 enp3s0          no-carrier        configuring
Sat 2026-08-29 17:15:03    2 enp3s0          carrier           configuring
Sat 2026-08-29 17:15:04    2 enp3s0          routable          configured
Sat 2026-08-29 17:18:20    5 wg0             carrier           configuring
Sat 2026-08-29 17:18:21    5 wg0             routable          configured
```

#### 2. Монітор `nmcli monitor` (NetworkManager)

Перехоплює всі події, що генеруються об'єктами `org.freedesktop.NetworkManager` на шині D-Bus:

```bash
nmcli monitor
```

```
enp3s0: connection activating (prepare) -> profile 'Office-Wired'
enp3s0: connection activating (configuring)
enp3s0: connection activating (ip-config)
enp3s0: connection activated
NetworkManager: state is now CONNECTED_GLOBAL
Connectivity is now FULL
```

#### 3. Монітор `resolvectl monitor` (systemd-resolved)

Показує повний потік внутрішніх транзакцій системного резолвера: кожне ім'я, що розпізнається, обраний апстрім-сервер, затримка відповіді RTT та прапорці безпеки:

```bash
resolvectl monitor
```

```
[Transaction 124] Querying: kernel.org (Type: A)
  Server: 1.1.1.1:853 (TLS / DoT)
  Response: 93.184.216.34 (TTL: 300s, RTT: 14.2ms)
  Flags: authenticated (DNSSEC valid), confidential (DoT encrypted)

[Transaction 125] Querying: internal-nas.corp.lan (Type: A)
  Routing Domain: ~corp.lan -> Interface: wg0
  Server: 10.200.0.1:53 (Plain UDP)
  Response: 10.200.0.50 (TTL: 3600s, RTT: 2.1ms)
  Flags: insecure (No DNSSEC)
```

---

### 8.4 Низькорівневе трасування ядра: udev та RTNetlink

Якщо поведінка мережевого демона свідчить про розбіжність між простором користувача та ядром, використовуються прямі точки трасування підсистем Linux:

```bash
# 1. Трасування подій менеджера пристроїв udev (гаряче підключення, зміна атрибутів)
udevadm monitor --subsystem-match=net --property

# 2. Прямий моніторинг мультикаст-повідомлень RTNetlink ядра Linux
# Фіксує всі команди RTM_NEWLINK, RTM_NEWADDR, RTM_NEWROUTE в момент їх виконання
ip monitor link address route
```


