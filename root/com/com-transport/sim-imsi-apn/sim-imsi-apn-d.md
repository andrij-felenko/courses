# SIM, IMSI, APN: як пристрій входить у мережу оператора

<preknowlist>
- [Покоління: від GSM до 5G і що з них лишилося пристроям](root:com-transport/pokolinnia) — еволюція архітектури радіодоступу та ядра мережі від комутації каналів до автономного пакетного ядра.
- [Комутація каналів проти комутації пакетів](root:com-transport/circuit-vs-packet-switching) — фундаментальні відмінності між виділеним фізичним трактом та дейтаграмною передачею даних.
- [IP-маршрутизація](root:com-transport/ip-routing) — просування пакетів у мережах за префіксами адрес та таблицями маршрутизації.
- [Транспортні протоколи TCP і UDP](root:com-transport/tcp-vs-udp) — встановлення надійного потокового з'єднання проти дейтаграмного протоколу без встановлення з'єднання.
- [Джерело ентропії (TRNG)](root:sf-security/entropy-source) — генерація непередбачуваних випадкових чисел для криптографічних протоколів.
</preknowlist>

Коли автономний контролер або мобільний термінал подає живлення на вбудований стільниковий модем, радіомодуль не може просто вийти в ефір і надіслати IP-пакет у бік найближчої базової станції. Стільникова інфраструктура побудована за принципом нульової довіри до радіообладнання: ефір загальнодоступний, радіосигнали можуть перехоплюватися або імітуватися зловмисниками, а ресурси базових станцій і магістральних маршрутизаторів оператора вимагають суворого обліку та білінгу.

Щоб пристрій отримав можливість маршрутизувати трафік у глобальний інтернет або ізольовану корпоративну мережу, він повинен подолати чотири послідовні бар'єри:
1. Апаратно довести свою автентичність криптографічному центру мережі без передачі секретного ключа у відкритий ефір.
2. Повідомити оператору глобальні ідентифікатори абонента та визначити права на обслуговування в домашній мережі або в роумінгу.
3. Вказати логічну точку входу (**APN**) для вибору цільового шлюзу пакетних даних.
4. Узгодити параметри сесії (**PDP-контекст**), отримати мережеву адресу (IPv4/IPv6) та підняти інкапсульований тунель крізь опорну мережу оператора.

---

### Апаратна та файлова архітектура смарт-карти SIM/UICC

Фізична SIM-карта (англ. *Subscriber Identity Module*) є повноцінним захищеним мікрокомп'ютером особливого класу — смарт-картою стандарту **UICC** (*Universal Integrated Circuit Card*, стандарти ETSI TS 102 221 та 3GPP TS 31.102). 

Кристал UICC містить 8-, 16- або 32-бітний мікроконтролер із гарвардською або модифікованою фон-нейманівською архітектурою, захищене апаратне ядро з криптографічним співпроцесором (AES, 3DES, SHA, RSA, ECC), генератор випадкових чисел (TRNG), невеликий обсяг оперативної пам'яті (RAM, 8–32 КБ) для виконання обчислень та енергонезалежну пам'ять (Flash/EEPROM, 64–512 КБ), у якій зберігається операційна система смарт-карти (наприклад, Java Card OS), аплети та файлова система.

```
                    Зовнішній інтерфейс ISO/IEC 7816-3
          (Контакти: VCC, GND, RST, CLK, I/O, VPP/SWP)
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Смарт-карта UICC (Universal Integrated Circuit Card)                   │
│                                                                        │
│  ┌──────────────────────┐  ┌────────────────────────────────────────┐  │
│  │ Контролер I/O (UART) │  │ Захищене ядро CPU (ARM SecurCore / 8051)│  │
│  └──────────┬───────────┘  └───────────────────┬────────────────────┘  │
│             │                                  │                       │
│  ┌──────────▼───────────┐  ┌───────────────────▼────────────────────┐  │
│  │ Оперативна RAM       │  │ Апаратний криптопроцесор (AES, TRNG)   │  │
│  │ (Тимчасові змінні)   │  │ (Захист від DPA, SPA та Fault Injection)│  │
│  └──────────────────────┘  └───────────────────┬────────────────────┘  │
│                                                │                       │
│  ┌─────────────────────────────────────────────▼────────────────────┐  │
│  │ Енергонезалежна пам'ять Flash / EEPROM                            │  │
│  │ ┌──────────────────────────────────────────────────────────────┐ │  │
│  │ │ Секретний ключ Ki (128/256 бітів) — АПАРАТНО НЕ ЧИТАЄТЬСЯ    │ │  │
│  │ ├──────────────────────────────────────────────────────────────┤ │  │
│  │ │ Файлова система: MF (3F00) ──> ADF_USIM ──> EF_IMSI, EF_LOCI │ │  │
│  │ └──────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

Фізичний інтерфейс зв'язку між модемом і картою стандартизовано за стандартом **ISO/IEC 7816-3**. Обмін даними відбувається через послідовний напівдуплексний асинхронний канал (контакт `I/O`) за допомогою командно-відповідних пакетів **APDU** (*Application Protocol Data Unit*).

#### Ієрархія файлової системи ETSI/3GPP

Файлова система карти організована у вигляді дерева каталогів та файлів, де кожен об'єкт ідентифікується 2-байтним шістнадцятковим числом (File ID):

![Ієрархічна структура файлової системи UICC](/root/com/com-transport/sim-imsi-apn/img/uicc-file-system.svg)
*Ієрархічна організація файлів на смарт-карті UICC. Кореневий каталог MF містить службові таблиці реєстрації та веде до спеціалізованих каталогів додатків ADF_USIM і DF_TELECOM з елементарними файлами ідентифікації та налаштувань.*

1. **MF (Master File, ID: `3F00`):** корінь файлової системи, аналог кореневого каталогу `/` в Unix.
2. **DF (Dedicated File):** проміжний каталог, що групує файли певної функціональності. Наприклад, `DF_TELECOM` (`7F10`) містить загальні телекомунікаційні служби (телефонна книга, SMS), а історичний `DF_GSM` (`7F20`) містив файли для мереж 2G.
3. **ADF (Application Dedicated File):** спеціалізований каталог повноцінного телекомунікаційного застосунка. У сучасних мережах LTE та 5G цим застосунком є **ADF_USIM** (Universal SIM Application, AID `A0000000871002...`).
4. **EF (Elementary File):** кінцеві файли даних, що безпосередньо зберігають параметри.

За внутрішньою структурою елементарні файли (EF) поділяються на три типи:
* **Transparent (Прозорі):** неструктурований масив байтів із прямим доступом за зміщенням (Offset) та довжиною. У такому форматі зберігаються `EF_ICCID` (`2FE2`) та `EF_IMSI` (`6F07`).
* **Linear Fixed (Лінійні фіксовані):** послідовність записів однакової фіксованої довжини з індексацією від 1 до N. Застосовуються для списків контактів (`EF_ADN`, `6F3A`) та сховища SMS-повідомлень (`EF_SMS`, `6F3C`).
* **Cyclic (Циклічні):** кільцевий буфер фіксованих записів, де запис нового елемента автоматично витісняє найстаріший. Використовуються для журналу останніх викликів або лічильників вартості.

#### Захищений апаратний анклав та ключ `Ki`

У захищеній зоні EEPROM, доступ до якої заблоковано на рівні мікрокоду карти для будь-яких зовнішніх команд зчитування, зберігається головний криптографічний секрет абонента — **ключ `Ki`** (*Individual Subscriber Authentication Key*). Ключ має довжину 128 бітів (у 3G/4G) або 256 бітів (у 5G TUAK).

Копія цього ключа зберігається виключно в апаратному центрі автентифікації домашнього оператора (**AuC**, *Authentication Centre*, у складі баз даних HSS/UDM). За жодних обставин ключ `Ki` не може бути прочитаний через контакти карти: контролер UICC виконує криптографічні перетворення виключно всередині кристала й видає назовні лише результат обчислення функцій. 

Кристали смарт-карт оснащуються фізичним захистом від зондування мікроманіпуляторами, сенсорами виявлення перепадів напруги, тактової частоти та лазерного опромінення (захист від *Fault Injection Attacks*), а також схемами маскування енергоспоживання для нейтралізації атак за сторонніми каналами (DPA/SPA — *Differential/Simple Power Analysis*).

---

### Глобальні ідентифікатори: ICCID та IMSI

У процесі ідентифікації та входу в мережу використовуються два фундаментальні ідентифікатори різного призначення: апаратний номер фізичного чипа (**ICCID**) та логічний ідентифікатор мобільного абонента (**IMSI**).

```
Ідентифікатори термінала та підписки:
┌────────────────────────────────────────────────────────────────────────┐
│ ICCID (Integrated Circuit Card ID, ITU-T E.118) — 19-20 цифр           │
│ [ 89 ] [ 380 ] [ 01 ] [ 1234567890 ] [ 4 ]                             │
│   │      │       │           │         └─ Контрольна сума Луна (Luhn)  │
│   │      │       │           └─────────── Індивідуальний номер карти   │
│   │      │       └─────────────────────── Код оператора-емітента       │
│   │      └─────────────────────────────── Телефонний код країни (380)  │
│   └────────────────────────────────────── MII: 89 = Телекомунікації    │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ IMSI (International Mobile Subscriber Identity, ITU-T E.212) — до 15 ц.│
│ [ 255 ] [ 01 ] [ 1234567890 ]                                          │
│    │      │           └────────────────── MSIN: Номер абонента в мережі│
│    │      └────────────────────────────── MNC: Код мобільної мережі    │
│    └───────────────────────────────────── MCC: Мобільний код країни    │
│ └──────────────────── PLMN-ідентифікатор ────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

#### ICCID (Integrated Circuit Card Identifier)

Стандартизований рекомендацією **ITU-T E.118**, номер ICCID є постійним серійним номером фізичної смарт-карти або чипа. Він наноситься лазером на пластиковий корпус карти та записується у файл `EF_ICCID` (`2FE2`).

Структура ICCID (до 20 десяткових цифр):
* **MII (Major Industry Identifier, 2 цифри):** значення `89` резервує карту за галуззю телекомунікацій.
* **Country Code (1–3 цифри):** міжнародний телефонний код країни за стандартом ITU-T E.164 (наприклад, `380` для України, `1` для США, `49` для Німеччини).
* **Issuer Identifier (1–4 цифри):** код оператора зв'язку, що випустив карту.
* **Individual Account Identification:** унікальний серійний номер чипа, згенерований виробником.
* **Checksum (1 цифра):** контрольний розряд, розрахований за класичним алгоритмом Луна (*Luhn algorithm*).

ICCID не використовується для маршрутизації викликів або пакетного трафіку в стільниковій мережі. Його призначення — облік на складі, логістичне прив'язування чипа до контракту в BSS/CRM оператора та ідентифікація апаратного кристала при віддаленій ініціалізації.

#### IMSI (International Mobile Subscriber Identity)

Номер IMSI стандартизовано рекомендацією **ITU-T E.212** і є головним маршрутизованим ідентифікатором підписки абонента у світовій стільниковій інфраструктурі. Він зберігається у файлі `EF_IMSI` (`6F07`) всередині каталогу `ADF_USIM`.

Структура IMSI складається з трьох числових блоків загальною довжиною не більше 15 цифр:
1. **MCC (Mobile Country Code, 3 цифри):** код країни розташування мережі (наприклад, `255` — Україна, `262` — Німеччина, `310` — США).
2. **MNC (Mobile Network Code, 2 або 3 цифри):** код конкретного оператора всередині країни (наприклад, `255 01` — Vodafone UA, `255 03` — Kyivstar, `255 06` — lifecell).
3. **MSIN (Mobile Subscription Identification Number, до 10 цифр):** унікальний ідентифікатор абонентського запису в базі даних конкретного оператора.

Комбінація `MCC + MNC` формує унікальний глобальний ідентифікатор мережі **PLMN ID** (*Public Land Mobile Network Identifier*).

#### Двійкове пакування BCD у файлі `EF_IMSI`

У файлі `EF_IMSI` дані зберігаються у двійково-десятковому форматі (**Packed BCD**, *Binary Coded Decimal*) з перестановкою напівбайтів (Nibbles), що мінімізує обсяг сховища.

Структура 9-байтного запису `EF_IMSI`:
* **Байт 0:** Довжина даних IMSI (кількість значущих байтів).
* **Байт 1:** Молодший напівбайт (Bits 0..3) містить прапорець парності та першу цифру IMSI; старший напівбайт (Bits 4..7) містить другу цифру.
* **Байти 2..8:** Кожна пара цифр записується у зворотному порядку напівбайтів (`Digit N+1 || Digit N`). Якщо кількість цифр непарна, невикористаний напівбайт заповнюється значенням `0xF`.

```
Приклад кодування IMSI "255011234567890" (15 цифр):
Байт 0: 0x08 (довжина 8 байтів)
Байт 1: 0x52 (Bits 0..3: прапорець/цифра 2, Bits 4..7: цифра 5)
Байт 2: 0x05 (цифра 5, цифра 0)
Байт 3: 0x11 (цифра 1, цифра 1)
Байт 4: 0x32 (цифра 2, цифра 3)
Байт 5: 0x54 (цифра 4, цифра 5)
Байт 6: 0x76 (цифра 6, цифра 7)
Байт 7: 0x98 (цифра 8, цифра 9)
Байт 8: 0xF0 (цифра 0, напівбайт заповнення 0xF)
```

#### Роумінг та маршрутизація: HPLMN проти VPLMN

Коли модем вмикає радіоприймач, він сканує доступні частотні канали та зчитує системну інформацію (System Information Blocks, SIB), яку транслюють довколишні базові станції. У блоці SIB1 станція передає свій `PLMN ID` (`MCC + MNC`).

Модем порівнює отриманий PLMN ID з даними власної карти:
* Якщо `MCC + MNC` збігаються з домашнім ідентифікатором карти, мережа визначається як **HPLMN** (*Home PLMN*).
* Якщо ідентифікатори відрізняються, термінал переходить у режим роумінгу у гостьовій мережі **VPLMN** (*Visited PLMN*).

Гостьова базова станція та вузол керування мобільністю (MME у LTE або SGSN у 3G) виділяють блок `MCC + MNC` з надісланого терміналом IMSI і за міжнародними сигнальними маршрутами (протоколи Diameter або SS7/MAP через шлюзи IPX/GRX) звертаються до домашнього сервера HSS оператора-емітента карти. Гостьова мережа не володіє ключем `Ki` — вона лише запитує у домашньої мережі разові вектори автентифікації.

---

### Криптографічний механізм автентифікації: 3GPP AKA та Milenage

В історичних мережах 2G GSM застосовувалася одностороння автентифікація (алгоритми COMP128): мережа перевіряла справжність термінала, але термінал не мав можливості перевірити, чи є базова станція справжньою. Це створювало критичну вразливість перед фальшивими базовими станціями (*IMSI-Catchers*, комплекси Stingray), які могли примусово знизити шифрування до нульового (A5/0) і перехоплювати трафік.

Починаючи з покоління 3G UMTS і в усіх наступних стандартах (4G LTE, 5G NR), впроваджено протокол **3GPP AKA** (*Authentication and Key Agreement*, 3GPP TS 33.102), який реалізує **взаємну автентифікацію**: термінал підтверджує свої права оператору, а оператор доводить терміналу, що він володіє ключем `Ki` та автентичним лічильником послідовності `SQN`.

![Процедура взаємної автентифікації 3GPP AKA та генерація ключів](/root/com/com-transport/sim-imsi-apn/img/aka-milenage-auth.svg)
*Послідовність сигналізації протоколу 3GPP AKA. Центр HSS генерує 5-елементний вектор автентифікації, термінал верифікує токен AUTN всередині апаратного ядра USIM та повертає відгук RES, одночасно виробляючи сесійні ключі шифрування CK та контролю цілісності IK.*

Криптографічною основою протоколу AKA є алгоритмічний набір **Milenage** (3GPP TS 35.205 / TS 35.206), побудований на блочному шифрі AES-128. Повний математичний розбір функцій `f1..f5`, обчислення масок та правила ресинхронізації лічильників винесено в окремий [алгоритмічний розбір Milenage та протоколу AKA](root:com-transport/sim-imsi-apn/math-milenage-aka.md).

#### Етапи процедури AKA

1. **Запит реєстрації (Attach Request):** модем передає свій IMSI (або тимчасовий псевдонім TMSI/GUTI) вузлу MME/SGSN.
2. **Отримання вектора автентифікації:** MME звертається до домашнього HSS. Центр AuC/HSS генерує 128-бітне псевдовипадкове число `RAND`, бере поточне значення лічильника послідовності `SQN` і запускає функції Milenage на базі секретного ключа `Ki`:
   * Функція `f1` обчислює 64-бітний код автентифікації мережі `MAC-A = f1(Ki, SQN, RAND, AMF)`.
   * Функція `f5` генерує 48-бітний ключ анонімності `AK = f5(Ki, RAND)`, який маскує лічильник: `SQN ⊕ AK`.
   * Формується токен мережі `AUTN = (SQN ⊕ AK) || AMF || MAC-A`.
   * Функції `f2`, `f3`, `f4` обчислюють очікувану відповідь `XRES` та 128-бітні сесійні ключі шифрування `CK` і контролю цілісності `IK`.
   * Кортеж `(RAND, AUTN, XRES, CK, IK)` передається назад вузлу MME.
3. **Виклик термінала (Authentication Request):** MME надсилає модему пару `(RAND, AUTN)`.
4. **Апаратне обчислення в USIM:** модем транслює `RAND` та `AUTN` у карту командою APDU `AUTHENTICATE`. Карта обчислює `AK`, знімає маску з лічильника `SQN`, розраховує свій `XMAC` і порівнює його з `MAC-A`.
   * Якщо `XMAC ≠ MAC-A`, карта відхиляє мережу (*MAC Failure* — спроба перехоплення фальшивою станцією).
   * Якщо `SQN` застарілий, карта генерує токен ресинхронізації `AUTS` (*Synch Failure*).
   * При успіху карта обчислює `RES`, `CK`, `IK` і повертає `RES` модему.
5. **Верифікація відповіді:** модем передає `RES` вузлу MME. MME порівнює `RES` з `XRES`. При збігу взаємна автентифікація вважається завершеною, а ключі `CK` та `IK` завантажуються в апаратні прискорювачі шифрування радіотракту.

---

### Програмні профілі та архітектура eSIM / eUICC

Зі зростанням вимог до мініатюризації пристроїв інтернету речей (IoT), герметичності корпусів та потреби віддаленої зміни оператора без заміни пластикової карти було розроблено стандарт **eSIM** (архітектура **eUICC**, специфікації GSMA SGP.02 для M2M та GSMA SGP.22 для споживчих пристроїв Consumer RSP).

Чип eUICC є незнімною мікросхемою у формфакторі MFF2 (5×6 мм) або WLCSP, припаяною безпосередньо на друковану плату пристрою. Головна відмінність eUICC від класичної UICC полягає у здатності безпечно зберігати **декілька незалежних операторських профілів** і перемикати їх за програмною командою.

![Архітектура дистанційного завантаження профілів eSIM](/root/com/com-transport/sim-imsi-apn/img/esim-rsp-architecture.svg)
*Архітектура GSMA SGP.22 Remote SIM Provisioning. Віддалені сервери SM-DP+ та SM-DS взаємодіють із локальним помічником LPA на пристрої для криптографічно захищеного завантаження операторських профілів у внутрішні домени безпеки eUICC.*

#### Компоненти архітектури Remote SIM Provisioning (RSP)

1. **eUICC (Embedded UICC):** апаратний крипточип, який має глобальний унікальний ідентифікатор **EID** (32 цифри). Внутрішній простір eUICC поділено на домени безпеки:
   * **ECASD (eUICC Controlling Authority Security Domain):** кореневий домен, що містить сертифікати довіри GSMA Root CI та заводські приватні ключі чипа для верифікації сертифікатів серверів.
   * **ISD-R (Issuer Security Domain Root):** системний домен, що відповідає за створення нових контейнерів, завантаження, активацію, деактивацію та видалення профілів.
   * **ISD-P (Issuer Security Domain Profile):** ізольований захищений контейнер, всередині якого розміщується окремий операторський профіль зі своєю файловою системою, ключем `Ki` та аплетом USIM. У кожен момент часу активним може бути лише один профіль ISD-P (або декілька при підтримці Multiple Enabled Profiles, MEP).
2. **LPA (Local Profile Assistant):** програмний компонент на хості або всередині модема (LPAd), що керує інтерфейсом завантаження:
   * **LPD (Profile Download):** здійснює HTTPS/TLS з'єднання із сервером завантаження;
   * **LDS (Discovery Service Client):** періодично опитує сервер сповіщень SM-DS;
   * **LUI (Local User Interface):** взаємодіє з користувачем або приймає команди сканування QR-коду (рядок activation code).
3. **SM-DP+ (Subscription Manager Data Preparation +):** сервер оператора, що генерує зашифрований пакет профілю (**BPP**, *Bound Profile Package*), підписаний власним сертифікатом і зашифрований на відкритому ключі конкретного чипа eUICC.
4. **SM-DS (Subscription Manager Discovery Server):** глобальний маршрутизатор сповіщень GSMA, де оператор реєструє наявність готового профілю для вказаного EID.

Завдяки наскрізному асиметричному шифруванню (PKI) пакет BPP розшифровується виключно всередині домену ISD-R цільового кристала eUICC: ні хост-процесор пристрою, ні проміжний інтернет-провайдер не мають доступу до ключів `Ki` та параметрів профілю.

---

### Точка доступу APN: шлюз у зовнішні мережі

Після того як термінал успішно зареєструвався в соті й пройшов взаємну автентифікацію, він перебуває у стані радіозв'язку, але не має доступу до IP-маршрутизації. Для передачі пакетних даних необхідно вказати точку доступу — **APN** (*Access Point Name*).

APN — це текстовий рядок, структурований за правилами доменних імен DNS (RFC 1035 / 3GPP TS 23.003), який ідентифікує пакетний шлюз (**PGW** у 4G LTE, **UPF** у 5G, **GGSN** у 2G/3G) та визначає правила маршрутизації й ізоляції трафіку.

```
Структура повного FQDN APN:
[ internet.kyivstar.net ] . [ mnc003.mcc255.gprs ]
           │                               │
           │                               └─ Operator Identifier (Опціонально)
           └───────────────────────────────── Network Identifier (Обов'язково)
```

1. **Network Identifier (NI):** обов'язкова частина, що визначає цільову зовнішню мережу (наприклад, `internet`, `ims`, `mms`, `iot.telekom.de`, `vpn.company.corp`).
2. **Operator Identifier (OI):** опціональний суфікс виду `mnc<MNC>.mcc<MCC>.gprs`, який однозначно визначає приналежність до конкретного оператора. Якщо термінал передає лише `internet`, вузол MME автоматично підставляє домашній OI для резолвінгу IP-адреси шлюзу через внутрішній DNS оператора.

#### Маршрутизація: Публічний інтернет проти корпоративного VRF

Залежно від конфігурації APN у профілі підписки HSS, шлюз PGW/UPF направляє трафік користувача за одним із двох принципово різних маршрутів:

```
                  ┌────────────┐   APN: "internet"   ┌────────────────────────┐
                  │            ├────────────────────>│ Глобальний Інтернет    │
                  │  Шлюз PGW  │ (Динамічний CGNAT)  │ (Публічні адреси)      │
[ Мобільний UE ] ─┤    UPF     ├─────────────────────┼────────────────────────┤
                  │   (SGi)    │   APN: "corp.iot"   │ Корпоративний VPN / VRF│
                  │            ├────────────────────>│ (Ізольований L3 контур,│
                  │            │ (Статичні IP/IPsec) │  без доступу ззовні)   │
                  └────────────┘                     └────────────────────────┘
```

* **Публічний APN (Default Internet):** шлюз PGW виділяє модему динамічну приватну IP-адресу з пулу CGNAT (RFC 6598, префікс `100.64.0.0/10` або `10.0.0.0/8`) і виконує трансляцію адрес у публічний інтернет. Вхідні з'єднання ззовні блокуються міжмережевим екраном оператора.
* **Корпоративний приватний APN (Private APN / VPN):** трафік термінала термінується в ізольованій таблиці віртуальної маршрутизації (**VRF**, *Virtual Routing and Forwarding*) або передається безпосередньо в корпоративний дата-центр через заздалегідь піднятий тунель IPsec чи виділений L2/L3 MPLS VPN канал.
  * Пристроям призначаються статичні або фіксовані адреси з корпоративного адресного простору.
  * Дозволяється двостороння пряма адресація: сервер диспетчеризації може ініціювати TCP/UDP з'єднання до IoT-датчика без сторонніх NAT-проксі.
  * Трафік фізично ізольований від загального інтернету, що усуває загрозу DDoS-атак та сканування портів ззовні.

---

### Активація PDP-контексту та створення тунелів GTP

Для створення сесії передачі даних модем надсилає запит на активацію контексту протоколу пакетних даних — **PDP-контексту** (*Packet Data Protocol Context*, у термінології LTE — *EPS Bearer*, у 5G — *PDU Session*).

![Активація PDP-контексту: сигналізація GTP-C та тракт даних GTP-U](/root/com/com-transport/sim-imsi-apn/img/pdp-context-activation.svg)
*Розподіл сигнальної площини та площини передачі пакетів під час активації PDP-контексту. Протокол GTP-C узгоджує параметри тунелювання між MME, SGW та PGW, після чого відкривається тунель GTP-U з ідентифікаторами TEID для передачі користувацького IP-трафіку.*

#### Послідовність сигналізації створення сесії

1. Модем надсилає повідомлення сигналізації бездротового рівня NAS: `Activate PDP Context Request` (у 3G) або `PDN Connectivity Request` (у LTE). Запит містить числовий номер контексту (`cid`), тип протоколу (`IPv4`, `IPv6` або `IPv4v6`), назву `APN` та контейнер параметрів `PCO` (*Protocol Configuration Options*).
2. Вузол керування MME отримує запит, перевіряє права абонента в базі HSS і за допомогою внутрішнього DNS оператора знаходить IP-адресу найближчого шлюзу PGW, що обслуговує цей APN.
3. MME надсилає повідомлення протоколу керування **GTP-C** (*GPRS Tunneling Protocol Control Plane*, 3GPP TS 29.274) `Create Session Request` до шлюзу обслуговування SGW, а той транслює його до PGW.
4. PGW резервує для абонента IP-адресу, виділяє ідентифікатор кінцевої точки тунелю **TEID** (*Tunnel Endpoint Identifier*) для прийому трафіку користувача та повертає `Create Session Response` з адресами DNS-серверів та значенням MTU в блоці PCO.
5. Між базовою станцією eNodeB та SGW (інтерфейс `S1-U`), а також між SGW та PGW (інтерфейс `S5/S8`) підіймається тунель протоколу площини користувача **GTP-U** (порт UDP `2152`).

Кожен IP-пакет, згенерований операційною системою пристрою, обгортається модемом і базовою станцією в заголовок GTP-U, що містить призначений `TEID`, та передається магістральними маршрутизаторами оператора як стандартна UDP-дейтаграма. Шлюз PGW знімає заголовки GTP/UDP і спрямовує чистий вихідний IP-пакет у бік підключеної мережі APN (інтерфейс `SGi`).

#### Default Bearer проти Dedicated Bearer

* **Default Bearer (Канал за замовчуванням):** створюється автоматично під час первинної активації PDP-контексту. Він залишається активним протягом усього часу перебування пристрою в мережі, забезпечує доставку пакетів за принципом найкращих зусиль (*Best Effort*) і не гарантує мінімальної пропускної здатності.
* **Dedicated Bearer (Виділений вторинний канал):** створюється динамічно за ініціативою мережі поверх наявного Default Bearer для специфічного трафіку, що вимагає суворих параметрів якості обслуговування (**QoS**). Визначається класом обслуговування **QCI** (*QoS Class Identifier* у LTE) або **5QI** (у 5G). Використовується для передачі голосу високої чіткості (**VoLTE**, QCI=1 з гарантованим бітрейтом GBR та пріоритетною затримкою < 100 мс) або відеоконференцій (QCI=2).

---

### Програмне керування модемом через стек AT-команд

Керування процесом ініціалізації SIM, конфігурації профілів APN та активації PDP-контекстів з боку мікроконтролера або хост-системи виконується через асинхронний послідовний порт (UART, USB CDC-ACM або PCIe virtual serial) за допомогою стандартизованих команд 3GPP TS 27.007.

Детальний опис усіх параметрів команд, форматів відповідей та числових кодів помилок `+CME ERROR` наведено в окремому [довіднику інтерфейсу AT-команд для PDP](root:com-transport/sim-imsi-apn/api-at-cellular-pdp.md).

#### Машина станів ініціалізації з'єднання

Надійна реалізація модемного драйвера повинна базуватися на детермінованій машині станів (FSM), яка послідовно проходить кроки підготовки:

```
[ Стан 0: Очікування готовності модема (AT -> OK) ]
                       │
                       ▼
[ Стан 1: Перевірка та розблокування SIM (AT+CPIN? -> READY) ]
                       │
                       ▼
[ Стан 2: Опитування реєстрації в мережі (AT+CEREG? -> stat=1 або 5) ]
                       │
                       ▼
[ Стан 3: Запис профілю APN (AT+CGDCONT=1,"IP","internet.apn") ]
                       │
                       ▼
[ Стан 4: Активація PDP-контексту (AT+CGACT=1,1) ]
                       │
                       ▼
[ Стан 5: Зчитування виділеної IP-адреси (AT+CGPADDR=1) ]
                       │
                       ▼
[ Стан 6: З'єднання встановлено (DATA_ROUTING_ACTIVE) ]
```

Нижче наведено практичну реалізацію модуля керування модемом мовами C та ідіоматичним C++20. Модуль реалізує повний цикл ініціалізації SIM, очікування реєстрації в мережі, конфігурації APN, активації PDP-контексту та зчитування виділеної IP-адреси з надійним синтаксичним аналізом відповідей та обробкою таймаутів.

:::tabs
```c
/* modem_controller.c — Повна C-реалізація ініціалізації PDP-контексту */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/select.h>

#define MODEM_BUFFER_SIZE 1024
#define DEFAULT_TIMEOUT_MS 5000

typedef struct {
    int serial_fd;
    char assigned_ip[64];
    int last_cme_error;
} modem_t;

static bool serial_write(int fd, const char *cmd) {
    size_t len = strlen(cmd);
    ssize_t written = write(fd, cmd, len);
    return (written == (ssize_t)len);
}

static bool wait_for_response(int fd, char *buffer, size_t max_len, int timeout_ms) {
    size_t total_read = 0;
    memset(buffer, 0, max_len);

    while (timeout_ms > 0) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(fd, &read_fds);

        struct timeval tv;
        tv.tv_sec = timeout_ms / 1000;
        tv.tv_usec = (timeout_ms % 1000) * 1000;

        int res = select(fd + 1, &read_fds, NULL, NULL, &tv);
        if (res > 0 && FD_ISSET(fd, &read_fds)) {
            ssize_t n = read(fd, buffer + total_read, max_len - total_read - 1);
            if (n > 0) {
                total_read += (size_t)n;
                buffer[total_read] = '\0';
                if (strstr(buffer, "\r\nOK\r\n") != NULL || strstr(buffer, "\r\nERROR\r\n") != NULL ||
                    strstr(buffer, "+CME ERROR:") != NULL) {
                    return true;
                }
            }
        } else {
            break; /* Таймаут */
        }
        timeout_ms -= 50;
    }
    return (total_read > 0);
}

bool modem_send_cmd(modem_t *modem, const char *cmd, char *out_resp, size_t out_max, int timeout_ms) {
    char full_cmd[256];
    snprintf(full_cmd, sizeof(full_cmd), "%s\r\n", cmd);

    if (!serial_write(modem->serial_fd, full_cmd)) {
        return false;
    }

    char local_buf[MODEM_BUFFER_SIZE];
    bool ok = wait_for_response(modem->serial_fd, local_buf, sizeof(local_buf), timeout_ms);
    if (!ok) {
        return false;
    }

    if (out_resp && out_max > 0) {
        strncpy(out_resp, local_buf, out_max - 1);
        out_resp[out_max - 1] = '\0';
    }

    if (strstr(local_buf, "\r\nOK\r\n") != NULL) {
        return true;
    }

    char *err_pos = strstr(local_buf, "+CME ERROR: ");
    if (err_pos) {
        modem->last_cme_error = atoi(err_pos + 12);
    }
    return false;
}

bool modem_init_pdp(modem_t *modem, const char *apn, const char *pdp_type) {
    char response[MODEM_BUFFER_SIZE];

    /* 1. Перевірка базової реакції модема */
    if (!modem_send_cmd(modem, "AT", response, sizeof(response), 1000)) {
        return false;
    }

    /* 2. Увімкнення розширеного звітування про помилки (+CME ERROR) */
    modem_send_cmd(modem, "AT+CMEE=1", NULL, 0, 1000);

    /* 3. Перевірка готовності SIM-карти */
    if (!modem_send_cmd(modem, "AT+CPIN?", response, sizeof(response), 3000)) {
        return false;
    }
    if (strstr(response, "+CPIN: READY") == NULL) {
        return false; /* SIM заблокована або відсутня */
    }

    /* 4. Очікування реєстрації в мережі LTE (CEREG stat=1 або stat=5) */
    bool registered = false;
    for (int attempts = 0; attempts < 15; attempts++) {
        if (modem_send_cmd(modem, "AT+CEREG?", response, sizeof(response), 2000)) {
            if (strstr(response, ",1") != NULL || strstr(response, ",5") != NULL) {
                registered = true;
                break;
            }
        }
        sleep(1);
    }
    if (!registered) {
        return false; /* Реєстрацію не отримано */
    }

    /* 5. Конфігурація PDP-контексту cid=1 */
    char cgdcont_cmd[256];
    snprintf(cgdcont_cmd, sizeof(cgdcont_cmd), "AT+CGDCONT=1,\"%s\",\"%s\"", pdp_type, apn);
    if (!modem_send_cmd(modem, cgdcont_cmd, response, sizeof(response), 3000)) {
        return false;
    }

    /* 6. Активація PDP-контексту cid=1 */
    if (!modem_send_cmd(modem, "AT+CGACT=1,1", response, sizeof(response), 10000)) {
        return false;
    }

    /* 7. Зчитування призначеної IP-адреси */
    if (modem_send_cmd(modem, "AT+CGPADDR=1", response, sizeof(response), 3000)) {
        char *ip_start = strstr(response, "+CGPADDR: 1,\"");
        if (ip_start) {
            ip_start += 13;
            char *ip_end = strchr(ip_start, '\"');
            if (ip_end) {
                size_t ip_len = (size_t)(ip_end - ip_start);
                strncpy(modem->assigned_ip, ip_start, ip_len);
                modem->assigned_ip[ip_len] = '\0';
                return true;
            }
        }
    }
    return false;
}
```
```cpp
/* modem_controller.cpp — Ідіоматична C++20 реалізація контролера з'єднання */
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <chrono>
#include <thread>
#include <format>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/select.h>

namespace cellular {

enum class ModemError {
    SerialIoError,
    Timeout,
    SimNotReady,
    RegistrationFailed,
    PdpActivationFailed,
    InvalidResponse
};

class SerialPort {
public:
    explicit SerialPort(std::string_view device_path) {
        fd_ = ::open(device_path.data(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    }

    ~SerialPort() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;
    SerialPort(SerialPort&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SerialPort& operator=(SerialPort&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }

    bool write_command(std::string_view command) const {
        if (fd_ < 0) return false;
        std::string payload = std::format("{}\r\n", command);
        ssize_t written = ::write(fd_, payload.data(), payload.size());
        return written == static_cast<ssize_t>(payload.size());
    }

    std::optional<std::string> read_response(std::chrono::milliseconds timeout) const {
        if (fd_ < 0) return std::nullopt;
        std::string buffer;
        buffer.resize(1024);
        size_t total_read = 0;
        auto remaining_time = timeout;

        while (remaining_time.count() > 0) {
            fd_set read_fds;
            FD_ZERO(&read_fds);
            FD_SET(fd_, &read_fds);

            struct timeval tv{};
            tv.tv_sec = std::chrono::duration_cast<std::chrono::seconds>(remaining_time).count();
            tv.tv_usec = (remaining_time.count() % 1000) * 1000;

            int res = ::select(fd_ + 1, &read_fds, nullptr, nullptr, &tv);
            if (res > 0 && FD_ISSET(fd_, &read_fds)) {
                ssize_t n = ::read(fd_, buffer.data() + total_read, buffer.size() - total_read - 1);
                if (n > 0) {
                    total_read += static_cast<size_t>(n);
                    std::string_view current_view(buffer.data(), total_read);
                    if (current_view.contains("\r\nOK\r\n") || current_view.contains("\r\nERROR\r\n") ||
                        current_view.contains("+CME ERROR:")) {
                        buffer.resize(total_read);
                        return buffer;
                    }
                }
            } else {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
            remaining_time -= std::chrono::milliseconds(50);
        }
        return (total_read > 0) ? std::make_optional(buffer.substr(0, total_read)) : std::nullopt;
    }

private:
    int fd_{-1};
};

struct PdpSession {
    std::string ip_address;
    int cid{1};
    std::string apn;
};

class ModemController {
public:
    explicit ModemController(SerialPort port) : port_(std::move(port)) {}

    std::expected<PdpSession, ModemError> activate_data_session(std::string_view apn, std::string_view pdp_type = "IP") {
        if (!port_.is_open()) {
            return std::unexpected(ModemError::SerialIoError);
        }

        /* 1. Перевірка AT */
        if (!exec_command("AT", std::chrono::milliseconds(1000))) {
            return std::unexpected(ModemError::Timeout);
        }

        exec_command("AT+CMEE=1", std::chrono::milliseconds(1000));

        /* 2. Перевірка SIM */
        auto pin_resp = exec_command("AT+CPIN?", std::chrono::milliseconds(3000));
        if (!pin_resp || !pin_resp->contains("+CPIN: READY")) {
            return std::unexpected(ModemError::SimNotReady);
        }

        /* 3. Очікування реєстрації LTE */
        bool registered = false;
        for (int i = 0; i < 15; ++i) {
            auto reg_resp = exec_command("AT+CEREG?", std::chrono::milliseconds(2000));
            if (reg_resp && (reg_resp->contains(",1") || reg_resp->contains(",5"))) {
                registered = true;
                break;
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        if (!registered) {
            return std::unexpected(ModemError::RegistrationFailed);
        }

        /* 4. Задання PDP Context */
        std::string set_pdp_cmd = std::format("AT+CGDCONT=1,\"{}\",\"{}\"", pdp_type, apn);
        if (!exec_command(set_pdp_cmd, std::chrono::milliseconds(3000))) {
            return std::unexpected(ModemError::PdpActivationFailed);
        }

        /* 5. Активація Context */
        if (!exec_command("AT+CGACT=1,1", std::chrono::milliseconds(10000))) {
            return std::unexpected(ModemError::PdpActivationFailed);
        }

        /* 6. Зчитування IP */
        auto ip_resp = exec_command("AT+CGPADDR=1", std::chrono::milliseconds(3000));
        if (ip_resp) {
            std::string_view resp_view{*ip_resp};
            auto pos = resp_view.find("+CGPADDR: 1,\"");
            if (pos != std::string_view::npos) {
                auto start = pos + 13;
                auto end = resp_view.find('\"', start);
                if (end != std::string_view::npos) {
                    PdpSession session;
                    session.cid = 1;
                    session.apn = std::string(apn);
                    session.ip_address = std::string(resp_view.substr(start, end - start));
                    return session;
                }
            }
        }
        return std::unexpected(ModemError::InvalidResponse);
    }

private:
    std::optional<std::string> exec_command(std::string_view cmd, std::chrono::milliseconds timeout) {
        if (!port_.write_command(cmd)) {
            return std::nullopt;
        }
        auto resp = port_.read_response(timeout);
        if (resp && resp->contains("OK")) {
            return resp;
        }
        return std::nullopt;
    }

    SerialPort port_;
};

} // namespace cellular
```
:::

---

### Діагностика типових несправностей при вході пристрою в мережу

У процесі експлуатації вбудованих терміналів (IoT-трекери, промислові контролери, телеметричні шлюзи) інженери стикаються з відмовами з'єднання, локалізація яких вимагає аналізу відповідей модема на кожному кроці протоколу:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Дерево діагностики стільникового з'єднання:                           │
│                                                                        │
│ 1. [ AT+CPIN? ] ────────> Не READY ─────> Апаратна помилка слота / PIN │
│        │                                                               │
│        ▼ READY                                                         │
│ 2. [ AT+CSQ / CESQ ] ───> RSSI < 5 ─────> Проблема антени / Зона тіні  │
│        │                                                               │
│        ▼ Сигнал є                                                      │
│ 3. [ AT+CEREG? ] ───────> stat=3 ───────> Реєстрацію відхилено (HSS)  │
│        │                                                               │
│        ▼ stat=1 або 5                                                  │
│ 4. [ AT+CGACT=1,1 ] ────> CME ERROR 149 > Помилка автентифікації APN   │
│        │             ───> CME ERROR 133 > APN не входить у підписку    │
│        ▼ OK                                                            │
│ 5. [ AT+CGPADDR=1 ] ────> IP отримано ──> Проблема DNS або MTU         │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Відмови ініціалізації SIM (`+CPIN: NOT INSERTED` або `+CME ERROR: 10`):**
   * *Причина:* окиснення контактів тримача, механічна вібрація в транспорті, просідання напруги живлення карти під час передачі струмового імпульсу або некоректний рівень напруги (сучасні карти працюють при 1.8 В, застарілі — при 3.0 В).
   * *Дія:* перевірка ліній живлення SIM VCC осцилографом, використання напаюваних чипів eUICC/MFF2 для вібронавантажених систем.
2. **Відхилення реєстрації в соті (`+CEREG: 0,3` — Registration Denied):**
   * *Причина:* операторська база HSS заблокувала абонента через несплату, закінчення терміну дії контракту або заборону роумінгу в цій локації; пристрій внесено до чорного списку обладнання EIR за недійсний IMEI.
   * *Дія:* зчитування коду причини відхилення (*Reject Cause*) через команду `AT+CEER` (Extended Error Report).
3. **Помилка активації PDP-контексту (`+CME ERROR: 133` — Service option not subscribed):**
   * *Причина:* помилка в імені APN. Якщо оператор вимагає `iot.kyivstar.net`, а в конфігурації вказано стандартний `internet`, PGW відхиляє створення GTP-тунелю.
4. **Помилка автентифікації APN (`+CME ERROR: 149` — PDP authentication failure):**
   * *Причина:* невідповідність протоколу перевірки пароля (сервер вимагає CHAP, а модем надіслав PAP) або помилка в рядках логіна/пароля в командах `AT+CGAUTH` / `AT$QCPDPP`.
5. **Проблема MTU Blackhole при передачі великих TCP-пакетів:**
   * *Причина:* інкапсуляція призначених для абонента пакетів усередину тунелю GTP-U додає оверхед транспортних заголовків зовнішньої мережі оператора. Складовими цього оверхеду є зовнішній заголовок IPv4 (20 байтів; або 40 байтів для IPv6), транспортний заголовок UDP на порт 2152 (8 байтів) та базовий заголовок протоколу GTP-U (8 байтів; за наявності опційних полів розширення Sequence Number чи Extension Header додається ще 4 байти):

```text
# Розрахунок мінімального оверхеду GTP-U тунелю (IPv4 + UDP + GTP-U):
20 + 8 + 8 = 36 байтів

# Ефективний розмір MTU для корисного навантаження (Standard Ethernet MTU 1500):
1500 - 36 = 1464 байти
```

     З урахуванням можливих опцій заголовків, додаткового шифрування PDCP/IPsec або транспорту IPv6 сумарний оверхед може сягати 40–80 байтів, через що ефективний розмір MTU стільникового каналу зменшується з 1500 до `1420–1460` байтів. Якщо хост намагається передавати пакети розміром 1500 байтів із встановленим прапорцем DF (*Don't Fragment*), а проміжні вузли блокують повідомлення ICMP `Fragmentation Needed`, сесія зависає при спробі передачі великих порцій даних.
   * *Дія:* примусове обмеження MTU на локальному мережевому інтерфейсі термінала до `1420` байтів або активація механізму TCP MSS Clamping (`MSS = 1380`).

---

### Підсумок

Процес підключення пристрою до мережі оператора є строго детермінованим криптографічним та мережевим протоколом:
* Смарт-карта UICC виступає захищеним апаратним сховищем секретного ключа `Ki` та обчислювальним анклавом для алгоритмічного набору Milenage.
* Номер ICCID ідентифікує кремнієвий чип у логістичних базах, тоді як номер IMSI є глобальною маршрутизованою адресою абонента для ініціалізації взаємної автентифікації 3GPP AKA між терміналом та домашнім HSS.
* Технологія eSIM / eUICC перетворює апаратні профілі на зашифровані програмні контейнери, дозволяючи оновлювати підписки по повітрю (RSP) зі збереженням криптографічної ізоляції.
* Рядок APN виконує роль маршрутного покажчика до цільового пакетного шлюзу PGW/UPF, розподіляючи потоки між публічним інтернетом та ізольованими корпоративними контурами VRF.
* Активація PDP-контексту розгортає тунелі GTP-U площини користувача, виділяє IP-адресу й сервери DNS та переводить модем у стан активного обміну мережевими пакетами.
