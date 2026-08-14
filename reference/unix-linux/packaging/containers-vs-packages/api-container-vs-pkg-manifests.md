# 📋 Порівняльний довідник маніфестів: DEB/RPM проти OCI Spec

Цей довідник містить детальний порівняльний аналіз та специфікацію маніфестів, структур даних, схем JSON та керуючих файлів метаданих, що використовуються в системних пакунках дистрибутивів Linux (Debian `.deb` та Red Hat `.rpm`), а також у специфікаціях Open Container Initiative (OCI Image Specification та OCI Runtime Specification). Документ призначено для розробників системних інструментів, пакетних менеджерів та контейнерних рушіїв.

---

## 1. Архітектурне порівняння специфікацій

Системні пакунки описують компоненти, що інтегруються у спільне середовище хоста, тоді як OCI-специфікації декларують автономні шари файлової системи та параметри виклику примітивів ізоляції ядра.

| Параметр специфікації | Debian Package (`control`) | Red Hat Package (`.spec`) | OCI Image Spec (`image-spec`) | OCI Runtime Spec (`runtime-spec`) |
| :--- | :--- | :--- | :--- | :--- |
| **Формат декларації** | Key-Value Text (`822-style`) | Macro Specfile Text | JSON Schema (`application/json`) | JSON Schema (`config.json`) |
| **Об'єкт опису** | Архів бінарних файлів та скриптів | Сценарій збирання та метадані | Незмінний шар rootfs + конфіг | Специфікація запуску процесу |
| **Ідентифікація версії** | Epoch:Version-Revision | Version-Release | SHA-256 Digest (Content Addressed) | JSON ociVersion field |
| **Модель залежностей** | Граф сумісності (`Depends`) | Граф сумісності (`Requires`) | Незмінний стек шарів (Layer Stack) | Специфікація Namespaces/Cgroups |
| **Модель розгортання** | Запис у спільний FHS | Запис у спільний FHS | Монтування OverlayFS `lowerdir` | Створення `clone()` з прапорцями |
| **Верифікація цілісності** | `md5sums` / GPG Signature | RPM Header Signature (GPG) | SHA-256 layer diff_ids / digests | OCI Digest validation |

---

## 2. Специфікація маніфесту системного пакунка Debian (`control`)

Маніфест `control` розташований усередині архіву метаданих `control.tar.xz` у пакунку `.deb`. Він розпізнається системним менеджером `dpkg` та високорівневим інструментом `apt` для побудови графу залежностей і перевірки конфліктів усередині дистрибутива.

### Формат декларації полів Debian Control (RFC 822)
Текстовий формат опису базується на стандарті RFC 822 і складається з пар "ключ: значення", розділених двокрапкою. Поля опису мають суворі правила семантики:

```ini
Package: nginx
Version: 1.24.0-2ubuntu1
Architecture: amd64
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Installed-Size: 2840
Depends: libc6 (>= 2.34), libpcre2-8-0 (>= 10.39), libssl3 (>= 3.0.0), zlib1g (>= 1:1.1.4)
Pre-Depends: init-system-helpers (>= 1.54)
Recommends: nginx-module-image-filter, nginx-module-xslt
Suggests: nginx-doc
Provides: httpd, httpd-cgi
Conflicts: nginx-full, nginx-light
Breaks: nginx-common (<< 1.24.0-2ubuntu1)
Replaces: nginx-common (<< 1.24.0-2ubuntu1)
Section: web
Priority: optional
Description: high performance web server and reverse proxy server
 Nginx is a web server that can also be used as a reverse proxy,
 load balancer, mail proxy and HTTP cache.
```

### Детальна семантика полів управління залежностями
Формат Debian підтримує багатшу семантику графу залежностей у порівнянні з іншими пакетними менеджерами:
- **`Package`:** Унікальний системний ідентифікатор пакунка в репозиторії. Дозволяє використовувати лише нижній регістр ASCII, цифри, дефіси та крапки.
- **`Version`:** Семантична версія у форматі `[Epoch:]Upstream_Version[-Debian_Revision]`. Поле `Epoch` (число з двокрапкою) скасовує стандартне порівняння версій і застосовується при зміні схеми нумерації версій розробником.
- **`Depends`:** Жорсткі необхідні залежності. Системний менеджер `dpkg` відмовиться конфігурувати пакунок, якщо в системі відсутні зазначені компоненти потрібних версій. Дозволяється логічне АБО через вертикальну риску (наприклад, `default-mta | mail-transport-agent`).
- **`Pre-Depends`:** Критичні перед-залежності. Вони мають бути не лише розпаковані, але й повністю зконфігуровані в системі *до початку розпакування* корисного навантаження поточного пакунка. Використовується для інструментів ініціалізації та базових системних бібліотек.
- **`Recommends`:** Сильні рекомендації. Інструмент `apt` встановлює ці пакунки за замовчуванням, якщо користувач явно не скасував цю опцію прапорцем `--no-install-recommends`.
- **`Suggests`:** Допоміжні пакунки, які розширюють функціональність, але не є обов'язковими для базової роботи.
- **`Provides`:** Оголошення віртуальних пакунків (наприклад, `httpd`), що дозволяє іншим програмам задовольняти залежності альтернативними реалізаціями веб-серверів.
- **`Conflicts` / `Breaks`:** Обмеження сумісності. Поле `Breaks` вказує, що встановлення цього пакунка зламає вказані версії інших пакунків, вимагаючи їхнього оновлення. Поле `Conflicts` забороняє одночасне співіснування пакунків на диску.
- **`Replaces`:** Дозволяє перезаписувати файли інших пакунків при переході файлів між пакетами під час рефакторингу.

---

## 3. Специфікація маніфесту системного пакунка RPM (`.spec`)

Файл специфікації `.spec` визначає повний інструктаж для утиліти `rpmbuild`. На відміну від статичного `control` файлу Debian, RPM specfile описує як інструкції збирання з вихідного коду, так і метадані підсумкового бінарного пакунка.

### Структура та макроси RPM Specfile
Специфікація RPM широко використовує макроси системних шляхів FHS (`%{_bindir}`, `%{_libdir}`, `%{_sysconfdir}`, `%{_unitdir}`), що забезпечує портативність збирання між різними дистрибутивами (RHEL, Fedora, openSUSE):

```spec
Name:           nginx
Version:        1.24.0
Release:        2%{?dist}
Summary:        A high performance web server and reverse proxy server

License:        BSD-2-Clause
URL:            https://nginx.org/
Source0:        https://nginx.org/download/%{name}-%{version}.tar.gz

BuildRequires:  gcc, make, libpcre2-devel, openssl-devel, zlib-devel
Requires:       libpcre2-8.so.0()(64bit), libssl.so.3()(64bit), systemd

%description
Nginx is a web server that can also be used as a reverse proxy,
load balancer, mail proxy and HTTP cache.

%prep
%autosetup

%build
%configure --with-http_ssl_module
%make_build

%install
%make_install

%files
%{_sbindir}/nginx
%{_sysconfdir}/nginx/nginx.conf
%{_unitdir}/nginx.service
%doc README

%changelog
* Fri Aug 14 2026 Maintainer <maintainer@example.com> - 1.24.0-2
- Security rebuild for OpenSSL 3.0
```

Специфікація RPM розрізняє залежності збирання (`BuildRequires`) та залежності виконання (`Requires`). Під час збирання утиліта `rpmbuild` аналізує зкомпільовані бінарні файли ELF за допомогою `ldd` / `readelf` і автоматично додає залежності від динамічних бібліотек на основі їхніх назв SONAME та архітектурних розширень `(64bit)`.

### Керуючі скрипти та гачки (Triggers) в RPM
Файл специфікації дозволяє оголошувати сценарії оболонки shell, що виконуються у визначені моменти транзакції інсталятора:
- **`%pre` / `%post`:** Скрипти підготовки та післяінсталяційної конфігурації.
- **`%preun` / `%postun`:** Скрипти зупинки та післявидалення.
- **`%pretrans` / `%posttrans`:** Скрипти, що виконуються суворо до початку або після завершення всієї пакетної транзакції інсталятора `dnf`.
- **`%triggerin` / `%triggerun`:** Динамічні гачки, які активуються при встановленні або видаленні суміжних пакунків-партнерів.

---

## 4. Специфікація OCI Image Manifest (`image-spec`)

Специфікація OCI Image Manifest декларує структуру образу контейнера у форматі JSON. Вона зв'язує конфігураційний файл образу з масивом шарів файлової системи (tarballs), ідентифікованих за вмістом через хеші SHA-256 (Content Addressable Storage).

### OCI Image Index JSON Schema (`application/vnd.oci.image.index.v1+json`)
OCI Image Index (також відомий як мульти-архітектурний маніфест) дозволяє одному тегу образу в реєстрі посилатися на різні реалізації під процесорні архітектури `amd64`, `arm64`, `riscv64`:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.index.v1+json",
  "manifests": [
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 714,
      "digest": "sha256:e69d12366c54129c158b2d192e544a6242b314a500f2083430b2b6d34b5c4646",
      "platform": {
        "architecture": "amd64",
        "os": "linux"
      }
    },
    {
      "mediaType": "application/vnd.oci.image.manifest.v1+json",
      "size": 714,
      "digest": "sha256:4b152d8e404b8b6e6f98103c80a0684f88421379c29d0092c4b8b9816556e01a",
      "platform": {
        "architecture": "arm64",
        "os": "linux"
      }
    }
  ]
}
```

### OCI Image Manifest JSON Schema (`application/vnd.oci.image.manifest.v1+json`)
Окремий маніфест описує конкретну збірку під цільову платформу та посилається на конфігураційний об'єкт і списки шарів файлової системи:

```json
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": "sha256:4b152d8e404b8b6e6f98103c80a0684f88421379c29d0092c4b8b9816556e01a",
    "size": 1472
  },
  "layers": [
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:72115655fc9a9096181f33f6707883b27b9c9f28ecb34a5d898516d24f0c436b",
      "size": 2814020
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:a4128f731c34a26e8316c026e6d19472e39e559ef17e657c9df94689c10a4023",
      "size": 78120
    },
    {
      "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
      "digest": "sha256:c2974916a24911d7e2f5b68df7265a6c1e5d76d49826f9876f9202a0a20a4b77",
      "size": 1042050
    }
  ],
  "annotations": {
    "org.opencontainers.image.title": "My Custom Application",
    "org.opencontainers.image.version": "1.0.0",
    "org.opencontainers.image.created": "2026-08-14T12:00:00Z"
  }
}
```

### OCI Image Configuration JSON Schema
Конфігураційний об'єкт образу описує середовище виконання контейнера: цільову архітектуру, змінні оточення, робочий каталог та список незмінних diff_ids для розпакування усередині OverlayFS:

```json
{
  "architecture": "amd64",
  "os": "linux",
  "config": {
    "User": "1001",
    "ExposedPorts": {
      "8080/tcp": {}
    },
    "Env": [
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "APP_ENV=production"
    ],
    "Entrypoint": [
      "/usr/bin/app-binary"
    ],
    "WorkingDir": "/app"
  },
  "rootfs": {
    "type": "layers",
    "diff_ids": [
      "sha256:d8a2307849156b6b7f320b9e81c0340d859b12a8398b1e4c9f1388031d234856",
      "sha256:e647585090f7193952f5209f987a20c388277a1130d22081d683786196238b68",
      "sha256:f1240c571c322b7a95610d7a6e11802958319d6778f65421c609618f5e08b292"
    ]
  }
}
```

Відмінність між `digest` у маніфесті та `diff_id` у конфігурації полягає в тому, що `digest` обчислюється від стиснутого архіву `.tar.gz` (для мережевого передавання), а `diff_id` — від незмінної розпакованої тар-архівації після застосування шару до файлової системи.

---

## 5. Специфікація OCI Runtime Specification (`config.json`)

Специфікація `config.json` згенерована низкоривневим рушієм (runc, crun) описує конфігурацію системних викликів ядра для створення примітивів ізоляції (namespaces, cgroups, capabilities, seccomp).

### Повний приклад OCI Runtime Configuration
Цей файл підготовано контейнерним рушієм перед системним викликом `clone()`:

```json
{
  "ociVersion": "1.0.2",
  "process": {
    "terminal": false,
    "user": {
      "uid": 1000,
      "gid": 1000
    },
    "args": [
      "/usr/bin/app-binary"
    ],
    "env": [
      "PATH=/usr/local/bin:/usr/bin:/bin"
    ],
    "cwd": "/app",
    "capabilities": {
      "bounding": [
        "CAP_NET_BIND_SERVICE"
      ],
      "effective": [
        "CAP_NET_BIND_SERVICE"
      ],
      "permitted": [
        "CAP_NET_BIND_SERVICE"
      ]
    }
  },
  "root": {
    "path": "rootfs",
    "readonly": true
  },
  "mounts": [
    {
      "destination": "/proc",
      "type": "proc",
      "source": "proc"
    },
    {
      "destination": "/dev",
      "type": "tmpfs",
      "source": "tmpfs",
      "options": ["nosuid", "strictatime", "mode=755", "size=65536k"]
    }
  ],
  "linux": {
    "namespaces": [
      { "type": "pid" },
      { "type": "network" },
      { "type": "ipc" },
      { "type": "uts" },
      { "type": "mount" },
      { "type": "user" }
    ],
    "resources": {
      "memory": {
        "limit": 536870912
      },
      "cpu": {
        "shares": 1024,
        "quota": 100000,
        "period": 100000
      }
    }
  }
}
```

---

## 6. Утиліти діагностики та інспекції маніфестів

Для перевірки вмісту маніфестів без розпакування системних артефактів використовуються такі системні команди у консолі:

### Перевірка системних пакунків Debian та RPM
Для аналізу метаданих пакетів використовуються утиліти `dpkg-deb` та `rpm`:
```bash
# Перегляд метаданих та залежностей пакунка .deb
dpkg-deb -I package.deb control

# Список усіх файлів усередині пакунка .deb
dpkg-deb -c package.deb

# Перегляд заголовків та метаданих пакунка .rpm
rpm -qpi package.rpm

# Перегляд списку файлів усередині пакунка .rpm
rpm -qpl package.rpm
```

### Інспекція контейнерних образів OCI
Для аналізу OCI-маніфестів у реєстрах або на локальному диску використовуються інструменти `skopeo` та `umoci`:
```bash
# Перегляд OCI Manifest JSON без завантаження всього образу
skopeo inspect docker://registry.example.com/app:v1.0

# Розпакування OCI образу у стандартний OCI Bundle каталогу config.json
umoci unpack --image app:v1.0 bundle_dir
```
