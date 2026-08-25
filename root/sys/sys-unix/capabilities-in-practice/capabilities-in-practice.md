# Можливості на практиці: базовий огляд

<preknowlist>
- [Можливості (capabilities) замість всесильного root](root:sys-unix/capabilities)
- [Systemd: модель і юніти](root:sys-unix/systemd-model)
</preknowlist>

Є два основні шляхи надати непривілейованій програмі окремі права (можливості) без використання `root`: через файлові атрибути або через менеджер служб (Systemd).

## Файлові можливості

Утилітами `setcap` і `getcap` (пакунок `libcap2-bin` у Debian та Ubuntu, `libcap` у Fedora) можна закріпити дозвіл прямо за виконуваним файлом.

```bash
== Bash
sudo setcap cap_net_bind_service=ep /usr/bin/my-web-server
getcap /usr/bin/my-web-server
```

Суфікс `=ep` означає, що можливість відразу стає дозволеною (permitted) та діючою (effective). Важливо пам'ятати, що ці налаштування лежать у розширених атрибутах (`xattr`), тому звичайне копіювання (`cp` без прапорця `--preserve=xattr`) їх не перенесе — без можливостей лишиться саме копія, оригінал не змінюється.

## Навколишні можливості через Systemd

Сучасний підхід для серверних служб — уникати модифікації файлів. Замість цього Systemd може запустити процес зі звичайними правами, але передати йому потрібну можливість через так званий **навколишній набір (ambient capabilities)**.

```ini
== Systemd Unit
[Service]
ExecStart=/opt/myapp/server
User=myappuser
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```

Це значно спрощує розгортання та оновлення програмного забезпечення. Для тестування таких сценаріїв у командному рядку можна використовувати утиліту `capsh`.
