# 📋 Інтерфейс атестації SPDM у ядрі Linux та sysfs

Підсистема PCI ядра Linux надає експонований поверхневий інтерфейс користувацького простору та системного адміністрування для моніторингу, керування та перевірки стану атестації SPDM периферійних пристроїв PCIe.

## Структура файлової системи sysfs

Для кожного PCIe-пристрою, що підтримує розширену можливість Data Object Exchange (DOE Capability ID `0x002E`) та протокол CMA, ядро створює каталог атестації у стандартній ієрархії sysfs:

```
/sys/bus/pci/devices/0000:03:00.0/attestation/
├── state
├── version
├── responder_capabilities
├── certificates/
│   ├── slot0
│   └── slot1
├── measurements/
│   ├── manifest
│   └── raw
└── ide/
    ├── status
    └── stream_id
```

### Атрибути стану та конфігурації

Кожен файл у каталозі `attestation/` надає конкретний тип даних для програмного моніторингу або автоматизованого аудіту безпеки системними демонами.

- `state`: Продукує поточний криптографічний стан пристрою в підсистемі `cma.c`. Повертає одне із фіксованих текстових значень:
  - `unauthenticated`: Пристрій виявлено на шині, але сесію атестації ще не розпочато або вона знаходиться на етапі узгодження алгоритмів.
  - `authenticated`: Завершено перевірку ланцюжка сертифікатів та підписів Challenge, володіння приватним ключем підтверджено.
  - `measurement_passed`: Успішно вилучено криптографічні хеші прошивки, і вони повністю збіглися з еталонними маніфестами цілісності.
  - `failed`: Пристрій не пройшов криптографічну перевірку (підроблений підпис, розбіжність хешів або неопознаний Root CA).
  - `revoked`: Сертифікат пристрою знаходиться у списку відкликання (CRL / OCSP).

- `version`: Відображає узгоджену версію специфікації SPDM (наприклад, `1.1`, `1.2` або `1.3`). Читання атрибута виконує внутрішнє звернення до збереженого контексту `struct pci_spdm_state`.

- `responder_capabilities`: 32-бітне шістнадцяткове число, що відображає бітові прапорці апаратної підтримки Responder. Повертає значення регістра `CAPABILITIES` пристрою:
  - `Bit 0 (CERT_CAP)`: Пристрій здатен надавати ланцюжок сертифікатів X.509.
  - `Bit 1 (CHAL_CAP)`: Підтримка виклику Challenge-Response для автентифікації ідентичності.
  - `Bit 2 (MEAS_CAP)`: Підтримка надання криптографічних вимірювань прошивки.
  - `Bit 3 (MEAS_FRESH_CAP)`: Пристрій підтримує згенероване свіже вимірювання за запитом із Nonce.
  - `Bit 4 (ENCRYPT_CAP)`: Здатність шифрувати кадр-повідомлення SPDM.
  - `Bit 5 (MAC_CAP)`: Підтримка обчислення та додавання коду автентифікації MAC.
  - `Bit 6 (KEY_EX_CAP)`: Підтримка встановлення захищеної сесії з виведенням ключів для PCIe IDE.

- `certificates/slot0` та `certificates/slot1`: Бінарні атрибути sysfs (`sysfs_bin_attr`), що містять DER-закодований ланцюжок сертифікатів X.509 ASN.1. Зчитування здійснюється побуферно з урахуванням зсуву `off` та розміру `count`. Читання атрибута повертає сировий потік байтів, який можна передавати безпосередньо у криптографічні бібліотеки типу OpenSSL або GnuTLS для перевірки дерева довіри.

- `measurements/manifest`: Текстовий або бінарний документ Reference Integrity Manifest (RIM), що описує очікувані значення прошивки пристрою.

- `measurements/raw`: Бінарний масив даних, що містить зчитаний від Responder дайджест вимірювань та підпис ECDSA/RSA над ним.

- `ide/status`: Стан канального шифрування PCIe IDE. Текстовий атрибут, що повертає `disabled`, `link_ide_active` або `selective_ide_active`.

- `ide/stream_id`: Числовий атрибут, що визначає ідентифікатор селективного потоку IDE Stream ID, закріплений за цим BDF.

## Механізм бінарних атрибутів sysfs у ядрі

Створення бінарних атрибутів у `attestation/` виконується підсистемою PCI через внутрішній ядерний виклики `sysfs_create_bin_file()`. Оскільки ланцюжок сертифікатів X.509 або бінарні маніфести цілісності RIM можуть перевищувати стандартний розмір однієї сторінки пам'яті `PAGE_SIZE` (4096 байтів), підсистема ядра реалізує спеціальні обробники читання `read()` зі складеною буферизацією:

```c
/* Приклад внутрішньої структури бінарного атрибута sysfs у drivers/pci/pcie/cma.c */
static ssize_t spdm_cert_read(struct file *filp, struct kobject *kobj,
                              struct bin_attribute *bin_attr,
                              char *buf, loff_t off, size_t count)
{
    struct pci_dev *pdev = to_pci_dev(kobj_to_dev(kobj));
    struct pci_spdm_state *spdm = pdev->spdm_state;

    if (!spdm || !spdm->cert_chain)
        return -ENODATA;

    if (off >= spdm->cert_chain_len)
        return 0;

    if (off + count > spdm->cert_chain_len)
        count = spdm->cert_chain_len - off;

    memcpy(buf, spdm->cert_chain + off, count);
    return count;
}
```

Така організація дозволяє користувацьким інструментам зчитувати бінарні сертифікати через стандартні системні виклики `read()` або утиліти типу `cat` та `hexdump` без ризику обрізання криптографічних даних.

## Регістри апаратного поштового ящика PCIe DOE

Комунікація SPDM у ядрі Linux здійснюється через стандартний поштовий ящик DOE (Data Object Exchange). Регістри розташовані в PCI Extended Configuration Space починаючи від базового зсуву Capability Header.

| Зсув регістру | Назва регістра | Права доступу | Опис та бітова маска |
| :--- | :--- | :--- | :--- |
| `+0x00` | `DOE Header` | `Read-Only` | Extended Capability Header ID `0x002E`, версія структури та зсув наступної можливості. |
| `+0x04` | `DOE Status` | `Read-Clear` | Регістр стану готовності поштового ящика та обробки переривань. |
| `+0x08` | `DOE Control` | `Read-Write` | Регістр керування передачею даних, генерації переривань та скидання. |
| `+0x0C` | `DOE Read Data` | `Read-Only` | 32-бітний FIFO-вікно зчитування відповідей від периферійного пристрою. |
| `+0x10` | `DOE Write Data`| `Write-Only` | 32-бітний FIFO-вікно запису запитів від ядра операційної системи. |

### Деталізація бітів Status та Control регістрів

- **Status Register (`+0x04`)**:
  - `Bit 0 (DOE Data Out Ready)`: Прапорець встановлюється пристроєм, коли у FIFO Read Mailbox з'явилася повна відповідь, готова до зчитування хостом.
  - `Bit 1 (DOE Busy)`: Прапорець встановлюється пристроєм на час обробки отриманого запиту та вирахування криптографічних підписів. Запис у Write Mailbox при активному `DOE Busy` викликає апаратну помилку.
  - `Bit 2 (DOE Error)`: Свідчить про помилку протоколу (невалідний заголовок DOE, непідтримуваний Vendor ID або збій таймауту).
  - `Bit 31 (DOE Interrupt Status)`: Індикація згенерованого переривання MSI-X про зміну стану поштового ящика.

- **Control Register (`+0x08`)**:
  - `Bit 0 (DOE Abort)`: Запис одиниці примусово перериває поточну операцію поштового ящика та скидає стан FIFO.
  - `Bit 1 (DOE Go)`: Сигнал пристрою про те, що хост завершив запис кадру запиту у Write Mailbox і пристрій повинен розпочати обробку.
  - `Bit 2 (DOE Interrupt Enable)`: Дозволяє генерацію MSI-X переривань при зміні прапорця `DOE Data Out Ready`.

## Ядерний C-API для внутрішніх драйверів

Усередині ядра Linux підсистема PCI надає розробникам низку функцій C-API для роботи з поштовими ящиками DOE та атестацією SPDM (визначаються в заголовкових файлах `<linux/pci-doe.h>` та `<linux/pci-cma.h>`):

```c
/* Структура стану поштового ящика DOE */
struct pci_doe_mb;

/* Ініціалізація та пошук поштового ящика DOE для вказаного пристрою */
struct pci_doe_mb *pci_find_doe_mailbox(struct pci_dev *pdev, u16 vendor_id, u8 type);

/* Синхронний обмін пакетами через поштовий ящик DOE */
int pci_doe_exchange(struct pci_doe_mb *doe_mb, 
                     const void *request, size_t req_len,
                     void *response, size_t resp_len);

/* Перевірка підтримки конкретного протоколу (наприклад, CMA / SPDM) */
bool pci_doe_supports_prot(struct pci_doe_mb *doe_mb, u16 vendor_id, u8 type);
```

Сценарій взаємодії ядерного драйвера з пристроєм виглядає так:
1. Під час функції `probe()` драйвер закликає `pci_find_doe_mailbox(pdev, PCI_DVSEC_VENDOR_ID_PCA, PCI_DOE_DATA_OBJECT_TYPE_CMA)`.
2. Якщо поштовий ящик знайдено, драйвер формує заголовок кадру CMA і передає його у `pci_doe_exchange()`.
3. Функція `pci_doe_exchange()` самостійно блокує м'ютекс поштового ящика, записує 32-бітні слова в `DOE Write Data`, активує `DOE Go` і переходить у стан очікування (sleep on completion) до отримання переривання від пристрою.

При виконанні обміну пакетами `pci_doe_exchange()` перевіряє поведінку апаратного забезпечення на випадок зависання Responder. Якщо пристрій не піднімає прапорець `DOE Data Out Ready` протягом 1000 мс, функція перериває очікування, записує одиницю у біт `DOE Abort` регістра `DOE Control` і повертає код помилки `-ETIMEDOUT`.

## Правила udev та підсистема безпеки SELinux

Для інтеграції стану атестації SPDM із демонами управління вузлом центрів обробки даних використовуються підсистеми `udev` та `SELinux` / `AppArmor`.

Приклад правила `udev` (`/etc/udev/rules.d/99-pci-spdm.rules`), що автоматично запускає утиліти перевірки або надсилає сповіщення у syslog при виявленні некоректного стану пристрою:

```text
# Автоматичний аналіз стану SPDM атестації при додаванні PCIe пристрою
ACTION=="add", SUBSYSTEM=="pci", ATTR{attestation/state}=="failed", \
    RUN+="/usr/bin/logger -p daemon.crit 'ALERT: PCIe device %k failed SPDM attestation! System compromised.'"

# Автоматичний запуск демона верифікації для успішно атестованих пристроїв
ACTION=="add", SUBSYSTEM=="pci", ATTR{attestation/state}=="measurement_passed", \
    RUN+="/usr/bin/spdm_verifier_cpp /sys/bus/pci/devices/%k/attestation"
```

З точки зору контекстів безпеки SELinux, доступ до каталогу `/sys/bus/pci/devices/.../attestation/` обмежується семантикою метки `sysfs_pci_attestation_t`. Зчитування бінарних сертифікатів та вимірювань дозволено тільки привілейованим демонам аудіту (наприклад, `auditd` або `tpm2-daemon`), що виключає можливість несанкціонованого вилучення інформації про структуру прошивок неавторизованими користувацькими процесами.

## Аналіз діагностичних повідомлень ядра dmesg

Діагностика процесу атестації під час завантаження системи або підключення нового пристрою доступна через системний журнал `dmesg`.

Приклад журналювання успішної атестації пристрою:
```text
[    2.415902] pci 0000:03:00.0: DOE capability found at offset 0x180 (ArrayList ID: 0x002E)
[    2.418201] pci 0000:03:00.0: SPDM 1.2 Negotiated: Hash=SHA-384, Asym=ECDSA-P384, DHE=SECP384R1
[    2.441093] pci 0000:03:00.0: Certificate chain validated against system keyring (Root CA: Intel Device Root)
[    2.465811] pci 0000:03:00.0: Measurements match RIM (Digest: 8a7f90e4b2... verification passed)
[    2.478901] pci 0000:03:00.0: PCIe IDE Selective Stream 0 enabled (AES-256-GCM encryption active)
```

Приклад журналювання відмови в атестації через недійсний підпис або підробку вимірювань:
```text
[    2.510239] pci 0000:04:00.0: SPDM Challenge Auth Failed: Invalid ECDSA signature from device
[    2.512991] pci 0000:04:00.0: CMA attestation failed with error -EKEYREJECTED
[    2.515410] pci 0000:04:00.0: Driver probe denied by SPDM policy; device isolated via IOMMU
```

## Трасування подій та dynamic debug

Для глибокого відлагодження процедури обміну SPDM-повідомленнями у розробницьких середовищах використовується механізм ядерного динамічного логування `dynamic_debug`.

Активація трасування регістрів DOE та викликів `libspdm`:
```bash
echo "file drivers/pci/doe.c +p" > /sys/kernel/debug/dynamic_debug/control
echo "file drivers/pci/pcie/cma.c +p" > /sys/kernel/debug/dynamic_debug/control
```

Після активації у системному логу з'являються детальні трасування бінарного навантаження кожного 32-бітного слова, записаного або зчитаного з поштового ящика DOE, що дозволяє інженерам діагностувати апаратні збої периферійних мікроконтролерів.
