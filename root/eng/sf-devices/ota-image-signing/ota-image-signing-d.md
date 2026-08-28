# Підписаний образ і захист від відкату

<preknowlist>
- [OTA-слоти та подвійний образ](root:sf-devices/ota-slots) — поділ флеш-пам'яті на активний і пасивний банки, механіка безпечного перемикання.
- [Secure boot і шифрування Flash](root:sf-security/firmware-secure-boot) — апаратний корінь довіри, різниця між автентичністю коду та таємністю даних.
- [Хеш і цифровий підпис](root:sf-security/hash-and-digital-signature) — математичний принцип пари відкритий/закритий ключ та автентифікація повідомлень.
- [Криптографічні хеш-функції](root:sf-security/cryptographic-hash) — властивості односторонніх функцій, стійкість до колізій і дайджест SHA-256.
- [Таблиця розділів у мікроконтролерах](root:sys-fw/partition-table) — розбиття адресної карти Flash на bootloader, app-слоти та NVS.
</preknowlist>

Коли промисловий контролер автоматики, розумний електролічильник чи польотний контролер дрона отримує файл нової прошивки через мережу, саме лише шифрування каналу зв'язку (TLS) не гарантує безпеки системи. Якщо зловмисник скомпрометує хмарний сервер оновлень, виконає підміну DNS-відповідей або перехопить трафік на корпоративному проксі-сервері, пристрій слухняно отримає та запише у Flash ворожий двійковий код. Захищений транспортний канал завершується в мережевому стеку; щойно байти лягли на флеш-пам'ять, захист з'єднання перестає існувати.

Транспортний протокол TLS автентифікує виключно *серверне з'єднання*, а не *автора двійкового коду*. Якщо прошивка не містить криптографічного підпису автора, будь-який суб'єкт, що контролює точку доставки або має локальний доступ до шини SPI чи інтерфейсу налагодження (SWD/JTAG), може записати в мікроконтролер модифікований бінарник. Ба більше: якщо застосувати симетричну схему автентифікації (наприклад, перевірку за спільним секретним ключем HMAC або паролем), виникає фатальна проблема масштабування. Зловмиснику достатньо розібрати один-єдиний екземпляр пристрою з партії у сто тисяч штук, випаяти мікросхему пам'яті й вичитати спільний ключ — після цього вся лінійка обладнання стає беззахисною перед генерацією підроблених оновлень.

Асиметрична криптографія докорінно змінює баланс сил. Закритий ключ (*Private Key*) ніколи не потрапляє на пристрої й зберігається виключно на захищеному складальному сервері виробника (усередині апаратного модуля безпеки, HSM). Пристрій несе у своїй пам'яті лише відкритий ключ (*Public Key*), за допомогою якого він може математично перевірити справжність підпису, але не здатний згенерувати підпис самостійно. Навіть якщо нападник повністю вичитає всю пам'ять мікроконтролера до останнього байта, він отримає лише відкритий ключ, який не дає жодної змоги підписати підроблений образ.

Ще підступнішою є загроза відкату версії коду — так звана атака зниження версії (*англ. downgrade attack* або *replay attack*). Припустімо, виробник випустив прошивку версії 1.0. Через пів року в її мережевому парсері виявили критичну вразливість переповнення буфера, яка дозволяє віддалене виконання довільного коду. Розробники терміново виправили дефект, зібрали версію 2.0 і розіслали її на всі пристрої. Зловмисник, що прагне захопити контроль над обладнанням, не створює власного шкідливого коду: він бере старий бінарний файл версії 1.0, який колись офіційно підписав сам виробник. Якщо завантажувач мікроконтролера перевіряє виключно валідність криптографічного підпису, версія 1.0 успішно пройде перевірку. Пристрій відкотиться на вразливу версію, і нападник миттєво застосує відомий експлойт.

Надійна система оновлення прошивки (*англ. Over-The-Air Update, OTA*) вимагає одночасного розв'язання двох незалежних завдань: доведення **автентичності автора** (цифровий підпис гарантує, що жоден байт не змінено сторонніми особами) та доведення **свіжості версії** (апаратний захист від відкату унеможливлює повторне встановлення застарілих вразливих образів).

![Апаратний ланцюг довіри від OTP eFuse до коду застосунку](/root/eng/sf-devices/ota-image-signing/img/chain-of-trust.svg)
*Апаратний ланцюг довіри: незмінне масковане ROM перевіряє завантажувач другого рівня за хешем ключа в OTP eFuse, а завантажувач верифікує цифровий підпис та лічильник свіжості прошивки застосунку.*

### Ланцюг довіри: від спаленого eFuse до образу застосунку

У комп'ютерній системі довіра не може виникати з програми, яку можна змінити або переписати. Якщо код, який здійснює перевірку підпису, сам зберігається у звичайній перезаписуваній флеш-пам'яті без апаратного контролю, нападник із доступом до шини SPI чи інтерфейсу налагодження (SWD/JTAG) може замінити цей код на функцію, яка завжди повертає успіх.

Основою безпечного запуску є **апаратний корінь довіри** (*англ. Root of Trust, RoT*). Він складається з двох компонентів, інтегрованих безпосередньо в кристал мікроконтролера на етапі виробництва кремнієвої пластини:

1. **Масковане первинне ROM (Primary Boot ROM):** енергонезалежна пам'ять, металізована на фаб-заводі. Її вміст є фізичною топологією кремнієвих транзисторів кристала. Її неможливо модифікувати жодними електричними сигналами чи програмними командами. Саме сюди апаратний лічильник команд процесора (`PC`) вказує після зняття сигналу скидання (`RESET`).
2. **Одноразово програмовані мікрозапобіжники (OTP eFuses):** матриця мікроскопічних полікремнієвих або металевих перемичок, які під дією підвищеної напруги пропалюються, незворотно змінюючи свій стан із логічного `0` на `1`. Спалений запобіжник неможливо повернути в початковий стан жодними програмними командами чи фізичним перепрограмуванням Flash.

Зберігати повний відкритий ключ виробника (наприклад, 256 або 512 бітів) у матриці eFuse буває надто марнотратно для кремнієвої площі мікроконтролерів. Тому інженери застосовують криптографічний компроміс: у блок eFuse пропалюють **SHA-256 дайджест відкритого ключа виробника** (Root Public Key Digest, 32 байти).

Коли живлення подається на чип, масковане ROM зчитує завантажувач другого рівня (*англ. Second Stage Bootloader*, наприклад MCUboot) із зовнішньої або внутрішньої Flash. У тіло завантажувача вбудовано відкритий ключ виробника. Первинне ROM виконує такі строго регламентовані кроки:
- зчитує відкритий ключ вендора, вбудований у двійковий образ завантажувача;
- обчислює апаратним криптографічним блоком SHA-256 хеш від цього відкритого ключа;
- зчитує 32-байтний еталонний дайджест із блоку OTP eFuse мікроконтролера;
- порівнює отриманий дайджест із еталоном за алгоритмом постійного часу (*Constant-Time Compare*), щоб уникнути атак витоку часу;
- якщо дайджести збіглися байт-у-байт, ROM використовує цей відкритий ключ для валідації цифрового підпису всього двійкового блоку завантажувача;
- за умови успішної криптографічної перевірки керування передається у завантажувач другого рівня.

Щоб запобігти апаратним атакам збою живлення (*Fault Injection / Voltage Glitching*), коли нападник за допомогою короткочасного імпульсу просідання напруги намагається змусити процесор пропустити умовну інструкцію переходу `BNE` (Branch if Not Equal), якісний код ROM-завантажувачів містить подвійні надлишкові перевірки (*Redundant State Variables*) та випадкові затримки.

Тепер завантажувач другого рівня стає довіреною ланкою. Він бере на себе валідацію власне образу застосунку (*Application Image*), що зберігається в основному або вторинному слоті оновлення. Жодна інструкція не передається на виконання центральному процесору, доки її цілісність, авторство та актуальність не підтверджені попередньою ланкою ланцюга.

### Анатомія підписаного образу: стандарт MCUboot

Звичайний виконуваний двійковий файл (`.bin`), отриманий після лінкування компілятором `objcopy`, містить лише сирий машинний код і константи. Такий файл не несе інформації про версію, тип цільової архітектури, зміщення точки входу, дайджести цілісності чи криптографічні підписи. Для організації безпечного завантаження відкритий стандарт **MCUboot** загортає скомпільований код у структурований контейнер.

Образ MCUboot складається з чотирьох обов'язкових зон, розміщених у Flash строго послідовно:

```text
+-------------------------------------------------------------+
| Заголовок образу: Image Header (32 байти)                   |
+-------------------------------------------------------------+
| Виконуваний двійковий код: Vector Table + Code + Constants  |
+-------------------------------------------------------------+
| Захищені дескриптори: Protected TLV Area (Magic 0x6908)     |
+-------------------------------------------------------------+
| Трейлер підпису: Non-Protected TLV Area (Magic 0x6907)      |
+-------------------------------------------------------------+
```

![Анатомія підписаного двійкового образу MCUboot](/root/eng/sf-devices/ota-image-signing/img/mcuboot-image-layout.svg)
*Структура контейнера образу MCUboot: заголовок фіксованого розміру, виконуваний код програми, зона захищених метаданих TLV та кінцевий трейлер цифрового підпису.*

Перші 32 байти займає фіксований заголовок `image_header`. Він містить магічне число `0x96f3b83d`, яке дозволяє завантажувачу миттєво визначити наявність валідного образу в секторі Flash, адресу завантаження `ih_load_addr`, розмір заголовка `ih_hdr_size` (зміщення до виконуваного коду для правильного вирівнювання вектора переривань `VTOR`), сумарний розмір корисного коду `ih_img_size` та 8-байтну структуру семантичної версії `ih_ver` (`major.minor.revision.build`).

Одразу після виконуваного коду програми розміщується зона захищених метаданих — **Protected TLV** (*Type-Length-Value*). Ця область починається власним заголовком `image_tlv_info` із магічним числом `0x6908`. Усі записи всередині цієї зони (наприклад, `IMAGE_TLV_SEC_CNT` — 32-бітний апаратний лічильник захисту від відкату версії) **обов'язково входять до криптографічного хешу образу**. Це означає, що нападник не може підправити номер версії або лічильник безпеки в бінарнику: будь-яка модифікація хоча б одного біта у Protected TLV зробить підпис недійсним.

Наприкінці двійкового файлу знаходиться незахищений трейлер метаданих — **TLV Trailer** із магічним числом `0x6907`. У ньому зберігаються результати криптографічних обчислень:
- `IMAGE_TLV_SHA256` (тип `0x0010`): 32-байтний еталонний дайджест SHA-256, розрахований над масивом `[Image Header + Payload Code + Protected TLVs]`;
- `IMAGE_TLV_KEYHASH` (тип `0x0001`): 32-байтний хеш відкритого ключа підписувача (дозволяє системі підтримувати кілька ключів і швидко знаходити потрібний публічний ключ у пам'яті);
- `IMAGE_TLV_ECDSA256` (тип `0x0022`) або `IMAGE_TLV_ED25519` (тип `0x0024`): безпосередньо 64 байти двійкового цифрового підпису.

Повний перелік типів дескрипторів, прапорців та форматів двійкових структур детально наведено у довіднику [специфікація двійкового формату MCUboot та типів TLV](root:sf-devices/ota-image-signing/api-mcuboot-format.md).

### Криптографія підпису: ECDSA (secp256r1) проти Ed25519

Для цифрового підпису образів прошивки у вбудованих системах класичний алгоритм RSA (наприклад, RSA-2048 чи RSA-4096) поступово виходить із ужитку. Причина полягає в розмірі ключів і підписів: підпис RSA-3072 займає 384 байти, а відкритий ключ разом із модулем — сотні байтів. Крім того, математичні операції піднесення до степеня за модулем вимагають значного обсягу оперативної пам'яті (SRAM) для розміщення великих чисел (*bignum*), чого в мікроконтролерах із 32–64 КБ RAM часто бракує.

Сучасні вбудовані платформи базуються на криптографії на еліптичних кривих (*Elliptic Curve Cryptography, ECC*). Два головні алгоритми в індустрії — це **ECDSA** (на кривій NIST P-256 / secp256r1) та **Ed25519** (EdDSA на скрученій кривій Едвардса Curve25519).

```text
+----------------------+--------------------------+--------------------------+
| Властивість          | ECDSA (secp256r1)        | Ed25519 (Curve25519)     |
+----------------------+--------------------------+--------------------------+
| Розмір ключа (PubKey)| 64 байти (x, y)          | 32 байти (стиснута Y)    |
| Розмір підпису       | 64 байти (r, s)          | 64 байти (R, S)          |
| Рівень стійкості     | ~128 біт                 | ~128 біт                 |
| Генерація випадкового| Вимагає ідеального TRNG  | Детермінована (RFC 8032) |
| числа k при підписі  | (Повтор k = злив ключа!) | Не залежить від RNG      |
| Стійкість до атак по | Залежить від реалізації  | Повні закони додавання,  |
| сторонніх каналах    | (є особливі точки)       | сталий час за замовчанням|
| Апаратне прискорення | Є в більшості чипів      | З'являється в нових MCU  |
|                      | (STM32 PKA, ESP32 ECC)   | (ESP32-C6, NRF5340)      |
+----------------------+--------------------------+--------------------------+
```

Принципова різниця між ними полягає у формуванні підпису та вимогах до обчислювальної стабільності.

**ECDSA (NIST P-256):** крива короткої форми Вейєрштрасса `y² = x³ - 3x + b (mod p)`. Алгоритм підпису вимагає генерації одноразового таємного числа `k` (*nonce*) для кожного підпису. Якщо генератор випадкових чисел (*TRNG*) на складальному сервері збійне і згенерує однакове `k` для двох різних версій прошивки, зловмисник, знаючи два підписи `(r, s₁)`, `(r, s₂)`, елементарною алгебраїчною дією обчислює приватний ключ виробника:

```
d = (s₁·h₂ - s₂·h₁) ÷ (r·(s₂ - s₁)) (mod n)
```

Навіть незначний статистичний перекіс у генераторі випадкових чисел (наприклад, якщо один чи два старших біти числа `k` завжди дорівнюють нулю) дозволяє відновити закритий ключ за допомогою решітчастих алгоритмів розв'язання задачі прихованого числа (Hidden Number Problem). Щоб усунути цей ризик для ECDSA, застосовують стандарт RFC 6979, де `k` обчислюється детерміновано через HMAC від приватного ключа та хешу прошивки.

**Ed25519:** схема цифрового підпису Едвардса на кривій `-x² + y² = 1 - (121665/121666)·x²·y²` над полем `2²⁵⁵ - 19`. Алгоритм Ed25519 детермінований за своєю конструкцією: замість випадкового числа `k` використовується криптографічний хеш SHA-512 від секретного зерна та самого повідомлення. У ньому немає виняткових точок (додавання точок працює за єдиною універсальною формулою для будь-яких координат), що гарантує захист від атак за часом виконання (*timing side-channel attacks*) без спеціальних програмних уповільнювачів. Крім того, верифікація Ed25519 у чистому C на процесорах ARM Cortex-M4 виконується надзвичайно швидко навіть без апаратних криптоакселераторів.

Принцип верифікації для обох алгоритмів підпорядковується парадигмі **Hash-then-Sign**:
1. Завантажувач зчитує весь образ блоками (наприклад, по 512 або 4096 байтів) і оновлює контекст SHA-256.
2. Отриманий 32-байтний дайджест звіряється з полем `IMAGE_TLV_SHA256`.
3. Функція криптографічної верифікації приймає відкритий ключ вендора, 32-байтний хеш і 64-байтний підпис. Якщо результат повертає `VALID`, автентичність образу доведено.

### Апаратний захист від відкату: монотонні лічильники eFuse

Перевірки одного лише криптографічного підпису недостатньо для захисту пристрою від атак класу *Downgrade*. Якщо виробник підписав версію 1.0, цей підпис залишається математично валідним вічно. Щоб заборонити пристрою повертатися до застарілих версій, застосовують **механізм захисту від відкату** (*Anti-Rollback Protection*).

![Захист від відкату за допомогою апаратного лічильника eFuse](/root/eng/sf-devices/ota-image-signing/img/anti-rollback-efuse.svg)
*Механізм блокування відкату: при встановленні v2 перевіряється умова Image Sec ≥ eFuse NV. Після успіху eFuse пропалюється до значення 2. Подальша спроба підсунути стару підписану прошивку v1 блокується завантажувачем.*

#### Семантична версія проти лічильника безпеки

У заголовку образу присутня семантична версія `ih_ver` (`Major.Minor.Patch.Build`). Проте використовувати семантичну версію для апаратного блокування відкату неприпустимо з двох причин:
- Ресурс одноразових запобіжників eFuse на кристалі суворо обмежений (зазвичай від 32 до 128 бітів на весь життєвий цикл виробу).
- Не кожне оновлення прошивки виправляє критичні вразливості безпеки. Якщо реліз містить лише косметичне виправлення графічного інтерфейсу (наприклад, версія 1.0.1 замість 1.0.0), спалювати апаратний запобіжник безглуздо — це позбавить користувача можливості відкотитися на 1.0.0 у разі незначних багів.

Для цього стандарт MCUboot вводить окреме поле в захищеній зоні TLV — **монотонний лічильник безпеки** (`IMAGE_TLV_SEC_CNT`). Цей лічильник інкрементується розробниками **тільки тоді**, коли нове оновлення закриває критичну діру в безпеці або змінює схему шифрування, роблячи запуск усіх попередніх бінарників небезпечним для системи.

#### Унітарне кодування в eFuse (Thermometer Coding)

У звичайній флеш-пам'яті чи RAM число 4 записується як `0x00000004`. Але у Flash зловмисник може переписати сектор назад. У кристалі мікроконтролера регістр eFuse є односпрямованим: біт із `0` можна перевести в `1`, але повернути `1` назад у `0` неможливо.

Тому лічильник безпеки в eFuse представляють у вигляді унітарного коду (*термометричного кодування*):

```text
Лічильник безпеки = 0:  0b0000_0000_0000_0000 (0 бітів пропалено)
Лічильник безпеки = 1:  0b0000_0000_0000_0001 (1 біт пропалено)
Лічильник безпеки = 2:  0b0000_0000_0000_0011 (2 біти пропалено)
Лічильник безпеки = 3:  0b0000_0000_0000_0111 (3 біти пропалено)
Лічильник безпеки = N:  N молодших бітів встановлено в 1
```

Кількість одиничних бітів у регістрі eFuse позначає поточний мінімально допустимий рівень безпеки пристрою (`HW_SEC_CNT`). Деякі сучасні мікроконтролери (наприклад, лінійки STM32H5/H7 із блоком Secure User Flash або ESP32-S3 з блоком eFuse Controller) мають вбудовані апаратні схеми контролю парності та коди корекції помилок (ECC), які гарантують надійне зчитування навіть при деградації кремнію з часом.

Завантажувач під час старту порівнює значення з образу та регістру чипа:

```
Image_Security_Counter >= Hardware_eFuse_Counter
```

Якщо образ має лічильник менший, ніж поточне значення в апаратному eFuse, завантажувач негайно перериває процес, маркує слот як недійсний і переходить у режим аварійного відновлення.

#### Залізне правило пропалювання запобіжників

> ⚠️ **Критичне правило безпеки:** Ніколи не пропалюйте апаратний eFuse під час завантаження або первинного запису образу у пасивний слот!
> Якщо спалити eFuse до значення `2` одразу після копіювання нової прошивки, а нова прошивка виявиться аварійною (наприклад, впадає в `HardFault` на першій секунді через несумісність із ревізією заліза), мікроконтролер більше **не зможе повернутися на стару робочу версію 1**, бо її `Security Counter = 1` буде заблоковано щойно спаленим eFuse. Пристрій перетвориться на «цеглину».
>
> Апаратний eFuse пропалюється **виключно з коду самого нового застосунку**, лише після того, як нова прошивка успішно запустилася, пройшла початкове самотестування периферії, зв'язалася із сервером і підтвердила свою працездатність викликом `boot_set_confirmed()`.

### Двоетапна атомарна прошивка та A/B Swap

Безпечне оновлення вимагає не лише криптографічної перевірки, а й відмовостійкої заміни образу в умовах раптового зникнення живлення. У мікроконтролерах без блоку керування пам'яттю (MMU) код виконується безпосередньо з Flash за фіксованими фізичними адресами (*Execute-In-Place, XIP*).

MCUboot організовує Flash у вигляді трьох ключових розділів:
1. **Первинний слот (Slot 0 / Primary):** розташований за фіксованою адресою виконання (наприклад, `0x08020000`). Процесор завжди завантажується та виконує код із цього слота.
2. **Вторинний слот (Slot 1 / Secondary):** пасивний розділ такого самого розміру. Сюди фоновий мережевий процес OTA записує новий підписаний файл образу.
3. **Розділ підкачки (Scratch Partition):** невеликий розділ розміром в один флеш-сектор (наприклад, 4 або 32 КБ), який використовується як транзакційний буфер для атомарного посекторного обміну (*Swap*) між Slot 0 та Slot 1.

![Життєвий цикл оновлення та двоетапний пробний старт з відкатом](/root/eng/sf-devices/ota-image-signing/img/dual-slot-swap.svg)
*Життєвий цикл A/B оновлення: завантаження у Slot 1, перевірка підпису, своп у Slot 0, тестовий старт під наглядом Watchdog. Успіх — закріплення та пропалювання eFuse; збій — автоматичний зворотний своп на старий робочий образ.*

Механізм двоетапного перемикання гарантує безперервність роботи:

1. **Завантаження та попередній аудит:** Застосунок приймає пакети оновлення по Wi-Fi/LTE і пише їх у Slot 1. Поточна прошивка у Slot 0 продовжує безперебійно керувати об'єктом.
2. **Валідація образу завантажувачем:** Пристрій ініціює перезавантаження. MCUboot перевіряє цілісність, SHA-256 хеш, цифровий підпис і лічильник безпеки образу в Slot 1. Якщо підпис недійсний — Slot 1 стирається, а старий Slot 0 запускається без змін.
3. **Атомарний своп (Image Swap using Scratch):** Завантажувач посекторно міняє місцями вміст Slot 0 та Slot 1 через буфер Scratch:
   - Сектор N зі Slot 0 копіюється у розділ Scratch.
   - Сектор N зі Slot 1 записується на місце сектора N у Slot 0.
   - Дані зі Scratch записуються у сектор N розділу Slot 1.
   - Оновлюється статусний маркер кроку в трейлері слота.
   Навіть якщо живлення вимкнеться посеред копіювання, метадані в кінці секторів дозволяють завантажувачу після рестарту завершити транзакцію з точного місця обриву.
4. **Пробний запуск (Trial Boot):** Завантажувач передає керування новому образу в Slot 0, виставляючи статус `TESTING`. Одночасно активується апаратний сторожовий таймер (*Hardware Watchdog*).
5. **Розгалуження результату:**
   - **Сценарій успіху:** Новий образ запускається, перевіряє життєздатність датчиків та зв'язку, після чого викликає функцію `mcuboot_mark_confirmed()`. Прапорець `Image OK` записується у трейлер слота. Образ стає постійним. Якщо `Security Counter` у новому образі вищий за апаратний eFuse, застосунок викликає драйвер захищеного пропалювання eFuse.
   - **Сценарій аварії:** Якщо новий образ містить фатальну помилку, зависає або викликає паніку ядра до підтвердження, спрацьовує сторожовий таймер Watchdog і скидає процесор. Під час наступного старту MCUboot бачить статус `TESTING` без позначки `Image OK`. Завантажувач констатує збій і автоматично виконує зворотний своп (*Revert Swap*), повертаючи перевірену стару версію зі Slot 1 у Slot 0.

### Повна реалізація криптографічного перевізника образу та анти-відкату

Наведений нижче модуль демонструє повний цикл низькорівневого розбору двійкового образу: перевірку магічних чисел, захист від переповнення розмірів, поблокове обчислення SHA-256, пошук обов'язкових TLV-дескрипторів, верифікацію лічильника безпеки проти апаратного eFuse та перевірку підпису ECDSA/Ed25519.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define IMAGE_MAGIC                 0x96f3b83dU
#define IMAGE_TLV_PROT_INFO_MAGIC   0x6908U
#define IMAGE_TLV_INFO_MAGIC        0x6907U

#define IMAGE_TLV_KEYHASH           0x0001U
#define IMAGE_TLV_SHA256            0x0010U
#define IMAGE_TLV_ECDSA256          0x0022U
#define IMAGE_TLV_ED25519           0x0024U
#define IMAGE_TLV_SEC_CNT           0x0050U

/* Заголовок образу MCUboot (32 байти) */
typedef struct __attribute__((packed)) {
    uint32_t ih_magic;
    uint32_t ih_load_addr;
    uint16_t ih_hdr_size;
    uint16_t ih_protect_tlv_size;
    uint32_t ih_img_size;
    uint32_t ih_flags;
    uint8_t  ver_major;
    uint8_t  ver_minor;
    uint16_t ver_revision;
    uint32_t ver_build_num;
    uint32_t _pad1;
} image_header_t;

/* Заголовок блоку TLV метаданих (4 байти) */
typedef struct __attribute__((packed)) {
    uint16_t it_magic;
    uint16_t it_tlv_tot;
} image_tlv_info_t;

/* Запис окремого TLV елемента (4 байти + дані) */
typedef struct __attribute__((packed)) {
    uint16_t it_type;
    uint16_t it_len;
} image_tlv_t;

typedef enum {
    VERIFY_OK = 0,
    ERR_INVALID_MAGIC,
    ERR_IMAGE_TOO_LARGE,
    ERR_TLV_CORRUPTED,
    ERR_SEC_COUNTER_DOWNGRADE,
    ERR_HASH_MISMATCH,
    ERR_SIGNATURE_INVALID,
    ERR_KEY_NOT_FOUND
} verify_status_t;

/* Зовнішні криптографічні інтерфейси платформи */
extern void sha256_init(void *ctx);
extern void sha256_update(void *ctx, const uint8_t *data, size_t len);
extern void sha256_final(void *ctx, uint8_t out_hash[32]);

extern bool crypto_verify_signature(uint16_t sig_type,
                                   const uint8_t *pubkey, size_t pubkey_len,
                                   const uint8_t hash[32],
                                   const uint8_t *sig, size_t sig_len);

extern uint32_t hw_efuse_read_sec_counter(void);
extern bool hw_efuse_burn_sec_counter(uint32_t new_val);

/* Головна функція повної верифікації двійкового образу */
verify_status_t verify_image_security(const uint8_t *raw_flash, size_t flash_boundary) {
    if (flash_boundary < sizeof(image_header_t)) {
        return ERR_INVALID_MAGIC;
    }

    const image_header_t *hdr = (const image_header_t *)raw_flash;
    if (hdr->ih_magic != IMAGE_MAGIC) {
        return ERR_INVALID_MAGIC;
    }

    /* Безпечна перевірка меж образу */
    uint32_t total_payload_offset = (uint32_t)hdr->ih_hdr_size + hdr->ih_img_size;
    uint32_t protected_tlv_sz = hdr->ih_protect_tlv_size;

    if (total_payload_offset + protected_tlv_sz > flash_boundary) {
        return ERR_IMAGE_TOO_LARGE;
    }

    uint32_t img_sec_counter = 0;
    bool sec_counter_present = false;

    /* 1. Обробка захищених TLV (Protected TLV), якщо вони є */
    if (protected_tlv_sz > 0) {
        if (protected_tlv_sz < sizeof(image_tlv_info_t)) {
            return ERR_TLV_CORRUPTED;
        }

        const uint8_t *p_tlv_raw = raw_flash + total_payload_offset;
        const image_tlv_info_t *p_info = (const image_tlv_info_t *)p_tlv_raw;

        if (p_info->it_magic != IMAGE_TLV_PROT_INFO_MAGIC || p_info->it_tlv_tot != protected_tlv_sz) {
            return ERR_TLV_CORRUPTED;
        }

        size_t off = sizeof(image_tlv_info_t);
        while (off + sizeof(image_tlv_t) <= protected_tlv_sz) {
            const image_tlv_t *item = (const image_tlv_t *)(p_tlv_raw + off);
            if (off + sizeof(image_tlv_t) + item->it_len > protected_tlv_sz) {
                return ERR_TLV_CORRUPTED;
            }

            if (item->it_type == IMAGE_TLV_SEC_CNT && item->it_len == sizeof(uint32_t)) {
                memcpy(&img_sec_counter, p_tlv_raw + off + sizeof(image_tlv_t), sizeof(uint32_t));
                sec_counter_present = true;
            }
            off += sizeof(image_tlv_t) + item->it_len;
        }
    }

    /* 2. Апаратна перевірка захисту від відкату (Anti-Rollback) */
    uint32_t hw_counter = hw_efuse_read_sec_counter();
    if (sec_counter_present && (img_sec_counter < hw_counter)) {
        return ERR_SEC_COUNTER_DOWNGRADE;
    }

    /* 3. Обчислення SHA-256 хешу: Header + Payload + Protected TLVs */
    uint8_t calculated_hash[32];
    uint8_t sha_ctx[256]; /* Необхідний розмір контексту криптобібліотеки */

    sha256_init(sha_ctx);
    /* Хешуємо заголовок, тіло програми та захищені метадані */
    size_t signed_area_len = total_payload_offset + protected_tlv_sz;
    sha256_update(sha_ctx, raw_flash, signed_area_len);
    sha256_final(sha_ctx, calculated_hash);

    /* 4. Розбір незахищеного трейлера підпису (Non-Protected TLV Trailer) */
    size_t trailer_offset = signed_area_len;
    if (trailer_offset + sizeof(image_tlv_info_t) > flash_boundary) {
        return ERR_TLV_CORRUPTED;
    }

    const uint8_t *trailer_raw = raw_flash + trailer_offset;
    const image_tlv_info_t *t_info = (const image_tlv_info_t *)trailer_raw;

    if (t_info->it_magic != IMAGE_TLV_INFO_MAGIC) {
        return ERR_TLV_CORRUPTED;
    }

    if (trailer_offset + t_info->it_tlv_tot > flash_boundary) {
        return ERR_IMAGE_TOO_LARGE;
    }

    const uint8_t *expected_hash = NULL;
    const uint8_t *signature = NULL;
    size_t signature_len = 0;
    uint16_t sig_type = 0;

    size_t t_off = sizeof(image_tlv_info_t);
    while (t_off + sizeof(image_tlv_t) <= t_info->it_tlv_tot) {
        const image_tlv_t *item = (const image_tlv_t *)(trailer_raw + t_off);
        if (t_off + sizeof(image_tlv_t) + item->it_len > t_info->it_tlv_tot) {
            return ERR_TLV_CORRUPTED;
        }

        const uint8_t *val = trailer_raw + t_off + sizeof(image_tlv_t);
        if (item->it_type == IMAGE_TLV_SHA256 && item->it_len == 32) {
            expected_hash = val;
        } else if (item->it_type == IMAGE_TLV_ECDSA256 || item->it_type == IMAGE_TLV_ED25519) {
            sig_type = item->it_type;
            signature = val;
            signature_len = item->it_len;
        }
        t_off += sizeof(image_tlv_t) + item->it_len;
    }

    if (!expected_hash || !signature) {
        return ERR_TLV_CORRUPTED;
    }

    /* Порівняння хешу за сталий час (Constant-Time Compare) */
    uint8_t diff = 0;
    for (size_t i = 0; i < 32; ++i) {
        diff |= (calculated_hash[i] ^ expected_hash[i]);
    }
    if (diff != 0) {
        return ERR_HASH_MISMATCH;
    }

    /* 5. Криптографічна верифікація цифрового підпису відкритим ключем */
    extern const uint8_t g_vendor_public_key[];
    extern const size_t g_vendor_public_key_len;

    if (!crypto_verify_signature(sig_type, g_vendor_public_key, g_vendor_public_key_len,
                                calculated_hash, signature, signature_len)) {
        return ERR_SIGNATURE_INVALID;
    }

    return VERIFY_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <string_view>
#include <algorithm>

namespace mcuboot {

inline constexpr uint32_t ImageMagic = 0x96f3b83dU;
inline constexpr uint16_t ProtectedTlvMagic = 0x6908U;
inline constexpr uint16_t NonProtectedTlvMagic = 0x6907U;

enum class TlvType : uint16_t {
    KeyHash   = 0x0001U,
    Sha256    = 0x0010U,
    EcdsaP256 = 0x0022U,
    Ed25519   = 0x0024U,
    SecCount  = 0x0050U
};

enum class VerifyError {
    InvalidMagic,
    ImageOutOfBounds,
    CorruptedTlvStructure,
    SecurityCounterDowngrade,
    HashMismatch,
    SignatureInvalid,
    MissingSignatureOrHash
};

#pragma pack(push, 1)
struct ImageHeader {
    uint32_t magic;
    uint32_t load_addr;
    uint16_t hdr_size;
    uint16_t protect_tlv_size;
    uint32_t img_size;
    uint32_t flags;
    uint8_t  ver_major;
    uint8_t  ver_minor;
    uint16_t ver_revision;
    uint32_t ver_build_num;
    uint32_t pad;
};

struct TlvInfo {
    uint16_t magic;
    uint16_t total_len;
};

struct TlvItem {
    uint16_t type;
    uint16_t len;
};
#pragma pack(pop)

/* Абстрактні апаратні залежності */
struct CryptoDriver {
    virtual void sha256_start() = 0;
    virtual void sha256_update(std::span<const uint8_t> data) = 0;
    virtual std::array<uint8_t, 32> sha256_finish() = 0;

    virtual bool verify_sig(TlvType type, std::span<const uint8_t> pubkey,
                            const std::array<uint8_t, 32>& hash,
                            std::span<const uint8_t> signature) = 0;

    virtual uint32_t read_hw_security_counter() = 0;
    virtual bool burn_hw_security_counter(uint32_t new_val) = 0;
    virtual ~CryptoDriver() = default;
};

class ImageVerifier {
public:
    explicit ImageVerifier(CryptoDriver& crypto, std::span<const uint8_t> root_pubkey) noexcept
        : crypto_{crypto}, root_pubkey_{root_pubkey} {}

    [[nodiscard]] std::expected<uint32_t, VerifyError>
    verify(std::span<const uint8_t> flash_image) noexcept {
        if (flash_image.size() < sizeof(ImageHeader)) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        const auto* hdr = reinterpret_cast<const ImageHeader*>(flash_image.data());
        if (hdr->magic != ImageMagic) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        const size_t total_payload_offset = static_cast<size_t>(hdr->hdr_size) + hdr->img_size;
        const size_t protected_tlv_sz = hdr->protect_tlv_size;

        if (total_payload_offset + protected_tlv_sz > flash_image.size()) {
            return std::unexpected(VerifyError::ImageOutOfBounds);
        }

        uint32_t img_sec_counter = 0;
        bool has_sec_counter = false;

        // 1. Парсинг захищених метаданих Protected TLV
        if (protected_tlv_sz > 0) {
            if (protected_tlv_sz < sizeof(TlvInfo)) {
                return std::unexpected(VerifyError::CorruptedTlvStructure);
            }

            auto prot_slice = flash_image.subspan(total_payload_offset, protected_tlv_sz);
            const auto* p_info = reinterpret_cast<const TlvInfo*>(prot_slice.data());

            if (p_info->magic != ProtectedTlvMagic || p_info->total_len != protected_tlv_sz) {
                return std::unexpected(VerifyError::CorruptedTlvStructure);
            }

            size_t offset = sizeof(TlvInfo);
            while (offset + sizeof(TlvItem) <= protected_tlv_sz) {
                const auto* item = reinterpret_cast<const TlvItem*>(prot_slice.data() + offset);
                if (offset + sizeof(TlvItem) + item->len > protected_tlv_sz) {
                    return std::unexpected(VerifyError::CorruptedTlvStructure);
                }

                if (static_cast<TlvType>(item->type) == TlvType::SecCount && item->len == sizeof(uint32_t)) {
                    std::copy_n(prot_slice.data() + offset + sizeof(TlvItem),
                                sizeof(uint32_t),
                                reinterpret_cast<uint8_t*>(&img_sec_counter));
                    has_sec_counter = true;
                }
                offset += sizeof(TlvItem) + item->len;
            }
        }

        // 2. Апаратна перевірка захисту від відкату (Anti-Rollback)
        const uint32_t hw_sec_cnt = crypto_.read_hw_security_counter();
        if (has_sec_counter && img_sec_counter < hw_sec_cnt) {
            return std::unexpected(VerifyError::SecurityCounterDowngrade);
        }

        // 3. Обчислення SHA-256 над Header + Payload + Protected TLVs
        crypto_.sha256_start();
        const size_t signed_len = total_payload_offset + protected_tlv_sz;
        crypto_.sha256_update(flash_image.subspan(0, signed_len));
        const auto calc_hash = crypto_.sha256_finish();

        // 4. Парсинг трейлера TLV підпису
        const size_t trailer_offset = signed_len;
        if (trailer_offset + sizeof(TlvInfo) > flash_image.size()) {
            return std::unexpected(VerifyError::CorruptedTlvStructure);
        }

        auto trailer_slice = flash_image.subspan(trailer_offset);
        const auto* t_info = reinterpret_cast<const TlvInfo*>(trailer_slice.data());

        if (t_info->magic != NonProtectedTlvMagic || trailer_offset + t_info->total_len > flash_image.size()) {
            return std::unexpected(VerifyError::CorruptedTlvStructure);
        }

        std::span<const uint8_t> expected_hash;
        std::span<const uint8_t> signature;
        TlvType sig_type{};

        size_t t_off = sizeof(TlvInfo);
        while (t_off + sizeof(TlvItem) <= t_info->total_len) {
            const auto* item = reinterpret_cast<const TlvItem*>(trailer_slice.data() + t_off);
            if (t_off + sizeof(TlvItem) + item->len > t_info->total_len) {
                return std::unexpected(VerifyError::CorruptedTlvStructure);
            }

            auto val_span = trailer_slice.subspan(t_off + sizeof(TlvItem), item->len);
            auto type = static_cast<TlvType>(item->type);

            if (type == TlvType::Sha256 && item->len == 32) {
                expected_hash = val_span;
            } else if (type == TlvType::EcdsaP256 || type == TlvType::Ed25519) {
                sig_type = type;
                signature = val_span;
            }
            t_off += sizeof(TlvItem) + item->len;
        }

        if (expected_hash.empty() || signature.empty()) {
            return std::unexpected(VerifyError::MissingSignatureOrHash);
        }

        // Порівняння за сталий час
        uint8_t diff = 0;
        for (size_t i = 0; i < 32; ++i) {
            diff |= (calc_hash[i] ^ expected_hash[i]);
        }
        if (diff != 0) {
            return std::unexpected(VerifyError::HashMismatch);
        }

        // 5. Перевірка цифрового підпису відкритим ключем
        if (!crypto_.verify_sig(sig_type, root_pubkey_, calc_hash, signature)) {
            return std::unexpected(VerifyError::SignatureInvalid);
        }

        return img_sec_counter;
    }

private:
    CryptoDriver& crypto_;
    std::span<const uint8_t> root_pubkey_;
};

} // namespace mcuboot
```
:::

Код на C реалізує строго детермінований аналіз без використання динамічної пам'яті (`malloc`), що критично для завантажувачів у режимі жорсткої нестачі SRAM. Варіант на C++ використовує безпечні діапазони `std::span` та тип результату `std::expected` (C++23) для унеможливлення виходу за межі буфера та надійного повернення помилок без використання механізму винятків.

> 🔧 **Навіщо це.** Якщо ви розробляєте підключений пристрій комерційного чи промислового рівня, безпечний OTA-завантажувач — це ваш страховий поліс. Підпис гарантує, що жоден зловмисник не перетворить партію контролерів на ботнет. Апаратний eFuse лічильник гарантує, що пристрій не вдасться повернути до старої версії із закритими дірами. А двоетапний A/B Swap із пробним запуском та сторожовим таймером гарантує, що навіть за збою живлення чи помилки в новому коді прилад самостійно повернеться до робочого стану без виїзду сервісної бригади з програматором.

### Підсумок

Криптографічний захист прошивки у вбудованих системах тримається на чотирьох взаємопов'язаних засадах:
1. **Апаратний якір довіри (Root of Trust):** Масковане первинне ROM звіряє відкритий ключ завантажувача з незмінним дайджестом, зашитим у кристалі в блоці OTP eFuse.
2. **Цифровий підпис (ECDSA / Ed25519):** Завантажувач MCUboot обчислює SHA-256 хеш від заголовка, корисного коду програми та захищених метаданих TLV, після чого математично підтверджує автентичність образу за допомогою публічного ключа виробника.
3. **Апаратний захист від відкату (Anti-Rollback):** Монотонний лічильник безпеки в захищеному блоці TLV звіряється з апаратним eFuse лічильником чипа, унеможливлюючи повернення до старих вразливих релізів.
4. **Атомарний A/B Swap і пробний запуск:** Новий образ тестується під наглядом сторожового таймера Watchdog; апаратний eFuse пропалюється лише після повного успіху самодіагностики, а в разі зависання завантажувач миттєво відкочує систему на попередню робочу прошивку.
