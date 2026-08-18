# 📋 Специфікація структури X.509 v3 та розширень ASN.1

Сертифікат відкритого ключа стандарту **X.509 версії 3** (визначений у специфікації IETF RFC 5280 та рекомендації ITU-T X.509) являє собою стандартизовану структуру даних, яка зв'язує відкритий ключ з ідентифікатором його власника (доменним ім'ям, організацією або фізичною особою) за допомогою цифрового підпису засвідчувального центру. 

На бінарному рівні сертифікат описується мовою абстрактного синтаксису **ASN.1** (англ. *Abstract Syntax Notation One*) та серіалізується за канонічними правилами розрізнення **DER** (англ. *Distinguished Encoding Rules*). Для текстового зберігання та передавання протоколами прикладної пошти чи конфігураціями вебсерверів бінарний DER-масив упаковується у формат **PEM** (англ. *Privacy-Enhanced Mail*).

Нижче наведено повну структурну специфікацію полів, правила кодування ASN.1 DER, таблиці ідентифікаторів об'єктів (OID) та реєстр критичних розширень X.509 v3.

---

### 1. Двійкове кодування ASN.1 DER: формат «Тег — Довжина — Значення» (TLV)

Канонічні правила DER вимагають однозначного бінарного кодування кожного елемента за тріадою **TLV** (англ. *Tag-Length-Value*):

```
+----------+--------------------------+------------------------------+
| Тег (T)  | Довжина значення (L)     | Тіло значення (V)            |
| 1 байт   | 1 байт або 1 + N байтів  | L байтів корисного навантаж. |
+----------+--------------------------+------------------------------+
```

#### Таблиця універсальних тегів ASN.1

| Шістнадцятковий тег | Назва типу ASN.1 | Призначення у сертифікаті X.509 |
|---|---|---|
| `0x30` | `SEQUENCE` (конструйований) | Впорядкований список полів (контейнер сертифіката, TBS, розширення) |
| `0x31` | `SET` (конструйований) | Невпорядкована множина (частина Distinguished Name) |
| `0x02` | `INTEGER` (примітивний) | Серійний номер сертифіката, номер версії, параметри RSA |
| `0x03` | `BIT STRING` (примітивний) | Значення цифрового підпису, відкритий ключ, маска Key Usage |
| `0x04` | `OCTET STRING` (примітивний) | Бінарні дані (значення розширень, геші ключів SKI/AKI) |
| `0x05` | `NULL` (примітивний) | Порожній параметр алгоритму підпису |
| `0x06` | `OBJECT IDENTIFIER (OID)` | Унікальний ієрархічний числовий ідентифікатор алгоритму чи розширення |
| `0x0C` | `UTF8String` (примітивний) | Текстові назви сучасних полів суб'єкта та видавця |
| `0x13` | `PrintableString` (примітивний) | ASCII-підмножина тексту (країна C, організація O) |
| `0x16` | `IA5String` (примітивний) | ASCII-рядок для доменних імен у розширенні SAN та адрес URL |
| `0x17` | `UTCTime` (примітивний) | Час у форматі `YYMMDDHHMMSSZ` (для дат до 2050 року) |
| `0x18` | `GeneralizedTime` (примітивний) | Час у форматі `YYYYMMDDHHMMSSZ` (для дат після 2049 року) |

#### Правила кодування довжини (Length Octets)

- **Коротка форма (Short Form):** якщо довжина корисного навантаження `L < 128` байтів, байт довжини містить число `L` у діапазоні `0x00–0x7F` (старший біт `0`).
- **Довга форма (Long Form):** якщо `L ≥ 128` байтів, перший байт має встановлений старший біт (`0x80 | N`), де `N` — кількість наступних байтів, що кодують число `L` у форматі Big-Endian.
  - Наприклад, довжина 256 байтів (`0x0100`) записується двома байтами: `0x82 0x01 0x00` (де `0x82` вказує на 2 байти довжини, що слідують далі).

---

### 2. Специфікація модуля ASN.1 для сертифіката X.509 v3

Повна синтаксична схема структури сертифіката згідно з RFC 5280:

```asn1
Certificate ::= SEQUENCE {
    tbsCertificate          TBSCertificate,
    signatureAlgorithm      AlgorithmIdentifier,
    signatureValue          BIT STRING
}

TBSCertificate ::= SEQUENCE {
    version         [0]  EXPLICIT Version DEFAULT v1,
    serialNumber         CertificateSerialNumber,
    signature            AlgorithmIdentifier,
    issuer               Name,
    validity             Validity,
    subject              Name,
    subjectPublicKeyInfo SubjectPublicKeyInfo,
    issuerUniqueID  [1]  IMPLICIT UniqueIdentifier OPTIONAL, -- Заборонено в RFC 5280
    subjectUniqueID [2]  IMPLICIT UniqueIdentifier OPTIONAL, -- Заборонено в RFC 5280
    extensions      [3]  EXPLICIT Extensions OPTIONAL        -- Обов'язково для v3
}

Version ::= INTEGER { v1(0), v2(1), v3(2) }

CertificateSerialNumber ::= INTEGER

Validity ::= SEQUENCE {
    notBefore       Time,
    notAfter        Time
}

Time ::= CHOICE {
    utcTime         UTCTime,
    generalTime     GeneralizedTime
}

SubjectPublicKeyInfo ::= SEQUENCE {
    algorithm            AlgorithmIdentifier,
    subjectPublicKey     BIT STRING
}

AlgorithmIdentifier ::= SEQUENCE {
    algorithm            OBJECT IDENTIFIER,
    parameters           ANY DEFINED BY algorithm OPTIONAL
}

Extensions ::= SEQUENCE SIZE (1..MAX) OF Extension

Extension ::= SEQUENCE {
    extnID      OBJECT IDENTIFIER,
    critical    BOOLEAN DEFAULT FALSE,
    extnValue   OCTET STRING
}
```

---

### 3. Опис полів структури TBSCertificate

Блок `TBSCertificate` (англ. *To Be Signed*) містить усі авторизаційні дані, над якими обчислюється криптографічний геш для підпису видавця.

#### Поля та їхні вимоги валідації:

1. **`version` (Контекстний тег `[0]`):**
   Для сертифікатів версії 3 кодується як ціле число `2` (`0x02 0x01 0x02`). Якщо поле відсутнє, сертифікат вважається застарілою версією v1, у якій заборонено використання розширень.
2. **`serialNumber` (`INTEGER`):**
   Унікальний додатний цілочисельний номер, призначений засвідчувальним центром для цього сертифіката. Максимальна довжина становить 20 байтів (160 бітів). Відповідно до правил CA/Browser Forum, серійний номер зобов'язаний містити щонайменше 64 біти криптографічно стійкої ентропії для захисту від атак колізій геш-функцій.
3. **`signature` (`AlgorithmIdentifier`):**
   Ідентифікатор алгоритму підпису видавця. Мусить **побайтово збігатися** із зовнішнім полем `Certificate.signatureAlgorithm`. Невідповідність цих двох полів є критичною помилкою валідації.
4. **`issuer` (`Name` — послідовність RDN):**
   Відмітне ім'я засвідчувального центру, що створив підпис. Складається з елементів `RelativeDistinguishedName` (наприклад, `C=UA, O=State CA, CN=Root CA`). Повинно побайтово або канонічно відповідати полю `Subject` сертифіката видавця.
5. **`validity` (`Validity`):**
   Часовий інтервал чинності сертифіката:
   - `notBefore`: момент часу, раніше якого сертифікат є недійсним.
   - `notAfter`: момент часу, після якого сертифікат втрачає чинність.
   - Для сертифікатів TLS, випущених після 1 вересня 2020 року, максимальний строк дії обмежений 398 днями.
6. **`subject` (`Name`):**
   Відмітне ім'я суб'єкта (власника відкритого ключа). Для кінцевих серверних сертифікатів поле `subject` може бути порожнім, якщо ідентифікація здійснюється через розширення `SubjectAlternativeName` (у цьому випадку SAN зобов'язане мати прапорець `critical = TRUE`).
7. **`subjectPublicKeyInfo` (`SubjectPublicKeyInfo`):**
   Містить відкритий ключ та ідентифікатор його типу. Для ключів RSA — це структура `RSAPublicKey` (модуль `n` та експонента `e`), для еліптичних кривих — стиснена чи нестиснена точка кривої.
8. **`extensions` (Контекстний тег `[3]`):**
   Послідовність розширень стандарту v3, що визначають обмеження використання ключа, альтернативні доменні імена та шляхи перевірки статусу.

---

### 4. Реєстр криптографічних ідентифікаторів об'єктів (OID)

Ідентифікатори OID (англ. *Object Identifier*) — це глобально унікальні числові послідовності, організовані у вигляді дерева.

| Алгоритм / Призначення | Текстовий ідентифікатор ASN.1 | Числовий OID |
|---|---|---|
| RSA Encryption | `rsaEncryption` | `1.2.840.113549.1.1.1` |
| RSA з SHA-256 | `sha256WithRSAEncryption` | `1.2.840.113549.1.1.11` |
| RSA з SHA-384 | `sha384WithRSAEncryption` | `1.2.840.113549.1.1.12` |
| RSA з SHA-512 | `sha512WithRSAEncryption` | `1.2.840.113549.1.1.13` |
| RSA-PSS підпис | `id-RSASSA-PSS` | `1.2.840.113549.1.1.10` |
| Відкритий ключ EC | `id-ecPublicKey` | `1.2.840.10045.2.1` |
| Крива NIST P-256 | `secp256r1` (prime256v1) | `1.2.840.10045.3.1.7` |
| Крива NIST P-384 | `secp384r1` | `1.3.132.0.34` |
| ECDSA з SHA-256 | `ecdsa-with-SHA256` | `1.2.840.10045.4.3.2` |
| ECDSA з SHA-384 | `ecdsa-with-SHA384` | `1.2.840.10045.4.3.3` |
| Підпис Ed25519 | `id-Ed25519` | `1.3.101.112` |
| Ключовий обмін X25519 | `id-X25519` | `1.3.101.110` |
| Геш-функція SHA-256 | `id-sha256` | `2.16.840.1.101.3.4.2.1` |

#### Специфікація параметрів схеми RSA-PSS (RFC 4055)
Якщо алгоритм підпису визначено як `id-RSASSA-PSS`, поле `parameters` містить вкладену структуру параметрів маскування та солі:

```asn1
RSASSA-PSS-params ::= SEQUENCE {
    hashAlgorithm      [0] HashAlgorithm      DEFAULT sha1Identifier,
    maskGenAlgorithm   [1] MaskGenAlgorithm   DEFAULT mgf1SHA1Identifier,
    saltLength         [2] INTEGER            DEFAULT 20,
    trailerField       [3] TrailerField       DEFAULT trailerFieldBC
}
```

Для сучасних підписів TLS 1.3 `hashAlgorithm` та `maskGenAlgorithm` встановлюються у `id-sha256` (`2.16.840.1.101.3.4.2.1`) з алгоритмом генерації маски `MGF1`, а довжина солі `saltLength` дорівнює довжині виходу геш-функції (32 байти для SHA-256).

---

### 5. Специфікація стандартних і критичних розширень X.509 v3

Кожне розширення сертифіката містить три поля: ідентифікатор `extnID` (OID), логічний прапорець критичності `critical` (`BOOLEAN`) та байтовий рядок значення `extnValue` (`OCTET STRING`), всередині якого закодовано власну DER-структуру конкретного розширення.

> **Правило критичності (Criticality Rule):** якщо програма перевірки зустрічає розширення з прапорцем `critical = TRUE`, призначення якого вона не підтримує або семантику якого не може виконати, вона **зобов'язана відхилити сертифікат як недійсний**. Якщо `critical = FALSE`, невідоме розширення можна безпечно ігнорувати.

#### 5.1. Basic Constraints (Базові обмеження)
- **OID:** `2.5.29.19` (`id-ce-basicConstraints`)
- **Критичність:** Зобов'язане бути `TRUE` для сертифікатів CA; для кінцевих вузлів рекомендовано `TRUE` або `FALSE`.
- **Синтаксис ASN.1:**
```asn1
BasicConstraints ::= SEQUENCE {
    cA                  BOOLEAN DEFAULT FALSE,
    pathLenConstraint   INTEGER (0..MAX) OPTIONAL
}
```
- **Семантика полів:**
  - `cA`: логічний прапорець. Якщо `TRUE`, сертифікат належить засвідчувальному центру і має право підписувати інші сертифікати. Якщо `FALSE`, сертифікат належить кінцевому суб'єкту (Leaf / End-Entity).
  - `pathLenConstraint`: максимальна кількість проміжних центрів сертифікації, які можуть слідувати за цим сертифікатом у валідному ланцюгу довіри. Якщо `pathLenConstraint = 0`, цей CA має право видавати виключно кінцеві сертифікати (`cA = FALSE`), але не може підписувати інші проміжні центри.

#### 5.2. Key Usage (Призначення ключів)
- **OID:** `2.5.29.15` (`id-ce-keyUsage`)
- **Критичність:** Зазвичай `TRUE`.
- **Синтаксис ASN.1:**
```asn1
KeyUsage ::= BIT STRING {
    digitalSignature        (0),
    nonRepudiation          (1),
    keyEncipherment         (2),
    dataEncipherment        (3),
    keyAgreement            (4),
    keyCertSign             (5),
    cRLSign                 (6),
    encipherOnly            (7),
    decipherOnly            (8)
}
```
- **Вимоги до встановлення бітів:**
  - Для центрів сертифікації (CA) обов'язково встановлюються біти `keyCertSign` (5) та `cRLSign` (6).
  - Для серверних сертифікатів TLS з алгоритмом ECDSA встановлюється біт `digitalSignature` (0).
  - Для серверних сертифікатів RSA зі статичним шифруванням ключів (застарілий TLS RSA handshake) встановлювався `keyEncipherment` (2). У сучасному TLS 1.3 використовується виключно `digitalSignature` (для підпису повідомлень Handshake CertificateVerify).

#### 5.3. Extended Key Usage (Розширене призначення ключів)
- **OID:** `2.5.29.37` (`id-ce-extKeyUsage`)
- **Критичність:** Може бути `TRUE` або `FALSE`.
- **Синтаксис ASN.1:**
```asn1
ExtKeyUsageSyntax ::= SEQUENCE SIZE (1..MAX) OF KeyPurposeId
KeyPurposeId ::= OBJECT IDENTIFIER
```
- **Стандартні ідентифікатори призначення:**
  - `id-kp-serverAuth` (`1.3.6.1.5.5.7.3.1`): автентифікація вебсервера TLS.
  - `id-kp-clientAuth` (`1.3.6.1.5.5.7.3.2`): клієнтська автентифікація mTLS.
  - `id-kp-codeSigning` (`1.3.6.1.5.5.7.3.3`): підпис виконуваного коду та прошивок.
  - `id-kp-emailProtection` (`1.3.6.1.5.5.7.3.4`): шифрування та підпис електронної пошти S/MIME.

#### 5.4. Subject Alternative Name (SAN, Альтернативне ім'я суб'єкта)
- **OID:** `2.5.29.17` (`id-ce-subjectAltName`)
- **Критичність:** `FALSE` (якщо поле `Subject` не порожнє) або `TRUE` (якщо `Subject` порожній).
- **Синтаксис ASN.1:**
```asn1
SubjectAltName ::= GeneralNames
GeneralNames ::= SEQUENCE SIZE (1..MAX) OF GeneralName

GeneralName ::= CHOICE {
    otherName           [0] AnotherName,
    rfc822Name          [1] IA5String,
    dNSName             [2] IA5String,
    x400Address         [3] ORAddress,
    directoryName       [4] Name,
    ediPartyName        [5] EDIPartyName,
    uniformResourceIdentifier [6] IA5String,
    iPAddress           [7] OCTET STRING,
    registeredID        [8] OBJECT IDENTIFIER
}
```
- **Правила валідації вебдоменів:**
  - Сучасні клієнти (браузери, бібліотеки OpenSSL, curl) виконують перевірку доменного імені **виключно через записи `dNSName` у розширенні SAN**. Зіставлення за полем `Subject.CommonName` (CN) повністю вилучено зі стандартів (RFC 6125, RFC 9110).
  - Шаблонні імена (Wildcard): запис виду `*.example.com` покриває рівно один рівень піддоменів (`api.example.com`, `shop.example.com`), але не покриває кореневий домен `example.com` та багаторівневі піддомени (`v1.api.example.com`).

#### 5.5. Authority Key Identifier (AKI) та Subject Key Identifier (SKI)
- **AKI OID:** `2.5.29.35` (`id-ce-authorityKeyIdentifier`)
- **SKI OID:** `2.5.29.14` (`id-ce-subjectKeyIdentifier`)
- **Синтаксис ASN.1:**
```asn1
AuthorityKeyIdentifier ::= SEQUENCE {
    keyIdentifier             [0] KeyIdentifier OPTIONAL,
    authorityCertIssuer       [1] GeneralNames OPTIONAL,
    authorityCertSerialNumber [2] CertificateSerialNumber OPTIONAL
}

SubjectKeyIdentifier ::= KeyIdentifier
KeyIdentifier ::= OCTET STRING
```
- **Призначення:** Поле `SubjectKeyIdentifier` містить 160-бітний або 256-бітний SHA-геш відкритого ключа поточного сертифіката. Сертифікат-нащадок записує цей самий геш у своє поле `AuthorityKeyIdentifier.keyIdentifier`. Це дозволяє програмі перевірки однозначно та швидко знаходити сертифікат батьківського видавця серед десятків встановлених у системі проміжних сертифікатів.

#### 5.6. Authority Information Access (AIA)
- **OID:** `1.3.6.1.5.5.7.1.1` (`id-pe-authorityInfoAccess`)
- **Критичність:** Завжди `FALSE`.
- **Синтаксис ASN.1:**
```asn1
AuthorityInfoAccessSyntax ::= SEQUENCE SIZE (1..MAX) OF AccessDescription

AccessDescription ::= SEQUENCE {
    accessMethod          OBJECT IDENTIFIER,
    accessLocation        GeneralName
}
```
- **Методи доступу:**
  - `id-ad-ocsp` (`1.3.6.1.5.5.7.48.1`): HTTP URL-адреса служби OCSP Responder для онлайн-перевірки статусу відкликання цього сертифіката.
  - `id-ad-caIssuers` (`1.3.6.1.5.5.7.48.2`): HTTP URL-адреса для автоматичного завантаження відсутнього сертифіката проміжного засвідчувального центру (AIA Chaining).

#### 5.8. Name Constraints (Обмеження простору імен)
- **OID:** `2.5.29.30` (`id-ce-nameConstraints`)
- **Критичність:** Завжди `TRUE`.
- **Синтаксис ASN.1:**
```asn1
NameConstraints ::= SEQUENCE {
    permittedSubtrees       [0]     GeneralSubtrees OPTIONAL,
    excludedSubtrees        [1]     GeneralSubtrees OPTIONAL
}

GeneralSubtrees ::= SEQUENCE SIZE (1..MAX) OF GeneralSubtree
GeneralSubtree ::= SEQUENCE {
    base                    GeneralName,
    minimum         [0]     BaseDistance DEFAULT 0,
    maximum         [1]     BaseDistance OPTIONAL
}
BaseDistance ::= INTEGER (0..MAX)
```
- **Призначення:** Дозволяє обмежити юрисдикцію проміжного засвідчувального центру виключно певним доменом (наприклад, дозволити випуск сертифікатів лише для `.gov.ua` та заборонити для всіх інших TLD). Якщо проміжний CA з таким розширенням підпише сертифікат для домену поза дозволеним деревом `permittedSubtrees`, клієнт відхилить такий сертифікат як недійсний.

- **Алгоритм перевірки:**
  1. Клієнт видобуває всі імена суб'єкта з розширення `SubjectAlternativeName` та поля `Subject.CommonName`.
  2. Кожне видобуте доменне або поштове ім'я зіставляється з кожним елементом списку `excludedSubtrees`: якщо знайдено хоча б один збіг, валідація негайно переривається з фатальною помилкою `X509_V_ERR_NAME_CONSTRAINTS_EXCLUDED`.
  3. Якщо список `permittedSubtrees` задано, кожне ім'я сертифіката зобов'язане належати щонайменше до одного з дозволених піддерев; відсутність збігу породжує помилку `X509_V_ERR_NAME_CONSTRAINTS_NOT_PERMITTED`.
  4. Обмеження застосовуються кумулятивно вздовж усього ланцюга: кожен наступний CA може лише звужувати дозволений простір імен, але не розширювати його.

---

### 6. Побайтний розбір структури ASN.1 DER на живому прикладі

Для розуміння того, як бінарний парсер розбирає сертифікат, розглянемо перші 40 байтів реального DER-потоку сертифіката сервера:

```
30 82 04 86 30 82 03 6e a0 03 02 01 02 02 10 4a 9f ...
```

1. **`0x30` (`SEQUENCE`):** кореневий контейнер `Certificate`.
2. **`0x82 0x04 0x86` (Довжина):** довга форма довжини (2 байти), що вказує на `0x0486` = 1158 байтів загального розміру сертифіката.
3. **`0x30` (`SEQUENCE`):** перший вкладений елемент — контейнер `TBSCertificate`.
4. **`0x82 0x03 0x6e` (Довжина):** довжина блоку `TBSCertificate` становить `0x036e` = 878 байтів.
5. **`0xa0 0x03` (Контекстний тег `[0]`):** ядрове поле `version` (довжина 3 байти).
6. **`0x02 0x01 0x02` (`INTEGER`):** тип ціле число, довжина 1 байт, значення `0x02` (версія v3).
7. **`0x02 0x10` (`INTEGER`):** наступне поле `serialNumber` — ціле число довжиною 16 байтів (`0x10`), за яким слідують 16 байтів унікального серійного номера: `4a 9f ...`.

Парсер крокує деревом TLV за зміщеннями, використовуючи довжини внутрішніх блоків для прямого доступу до відкритих ключів та розширень без необхідності перекодовувати дані.

---

### 6. Специфікація списків відкликання (CRL v2, RFC 5280)

Список відкликаних сертифікатів (англ. *Certificate Revocation List, CRL*) публікується засвідчувальним центром у бінарному форматі ASN.1 DER:

```asn1
CertificateList ::= SEQUENCE {
    tbsCertList          TBSCertList,
    signatureAlgorithm   AlgorithmIdentifier,
    signatureValue       BIT STRING
}

TBSCertList ::= SEQUENCE {
    version                 Version OPTIONAL, -- Якщо присутнє, мусить бути v2 (значення 1)
    signature               AlgorithmIdentifier,
    issuer                  Name,
    thisUpdate              Time,
    nextUpdate              Time OPTIONAL,
    revokedCertificates     SEQUENCE OF SEQUENCE {
        userCertificate         CertificateSerialNumber,
        revocationDate          Time,
        crlEntryExtensions      Extensions OPTIONAL
    } OPTIONAL,
    crlExtensions           [0] EXPLICIT Extensions OPTIONAL
}
```

#### Стандартні коди причин відкликання (`CRLReason`, OID `2.5.29.21`):
| Числовий код | Назва переліку ASN.1 | Опис причини анулювання |
|---|---|---|
| `0` | `unspecified` | Не вказано конкретну причину |
| `1` | `keyCompromise` | Доведено або підозрюється витік закритого ключа суб'єкта |
| `2` | `cACompromise` | Скомпрометовано закритий ключ самого засвідчувального центру |
| `3` | `affiliationChanged` | Зміна назви організації, домену чи звільнення співробітника |
| `4` | `superseded` | Сертифікат достроково замінено на новий |
| `5` | `cessationOfOperation` | Припинення роботи сервісу або вебсайту |
| `6` | `certificateHold` | Тимчасове призупинення дії (може бути знято пізніше) |

---

### 7. Специфікація протоколу онлайн-статусу сертифікатів (OCSP, RFC 6960)

Протокол OCSP обмінюється бінарними DER-повідомленнями через транспорт HTTP за допомогою методів `POST` (з MIME-типом `application/ocsp-request`) або `GET` (де запит кодується в URL через Base64).

#### Схема запиту `OCSPRequest`:
```asn1
OCSPRequest ::= SEQUENCE {
    tbsRequest                  TBSRequest,
    optionalSignature   [0]     EXPLICIT Signature OPTIONAL
}

TBSRequest ::= SEQUENCE {
    version             [0]     EXPLICIT Version DEFAULT v1,
    requestorName       [1]     EXPLICIT GeneralName OPTIONAL,
    requestList                 SEQUENCE OF Request,
    requestExtensions   [2]     EXPLICIT Extensions OPTIONAL
}

Request ::= SEQUENCE {
    reqCert                     CertID,
    singleRequestExtensions [0] EXPLICIT Extensions OPTIONAL
}

CertID ::= SEQUENCE {
    hashAlgorithm       AlgorithmIdentifier,
    issuerNameHash      OCTET STRING, -- Геш від DER-рядка поля Issuer
    issuerKeyHash       OCTET STRING, -- Геш від відкритого ключа видавця
    serialNumber        CertificateSerialNumber
}
```

#### Схема відповіді `OCSPResponse`:
```asn1
OCSPResponse ::= SEQUENCE {
    responseStatus         OCSPResponseStatus,
    responseBytes      [0] EXPLICIT ResponseBytes OPTIONAL
}

OCSPResponseStatus ::= ENUMERATED {
    successful            (0),
    malformedRequest      (1),
    internalError         (2),
    tryLater              (3),
    sigRequired           (5),
    unauthorized          (6)
}

BasicOCSPResponse ::= SEQUENCE {
    tbsResponseData      ResponseData,
    signatureAlgorithm   AlgorithmIdentifier,
    signature            BIT STRING,
    certs            [0] EXPLICIT SEQUENCE OF Certificate OPTIONAL
}

ResponseData ::= SEQUENCE {
    version              [0] EXPLICIT Version DEFAULT v1,
    responderID              ResponderID,
    producedAt               GeneralizedTime,
    responses                SEQUENCE OF SingleResponse,
    responseExtensions   [1] EXPLICIT Extensions OPTIONAL
}

SingleResponse ::= SEQUENCE {
    certID                       CertID,
    certStatus                   CertStatus,
    thisUpdate                   GeneralizedTime,
    nextUpdate           [0]     EXPLICIT GeneralizedTime OPTIONAL,
    singleExtensions     [1]     EXPLICIT Extensions OPTIONAL
}

CertStatus ::= CHOICE {
    good        [0]     IMPLICIT NULL,
    revoked     [1]     IMPLICIT RevokedInfo,
    unknown     [2]     IMPLICIT UnknownInfo
}

RevokedInfo ::= SEQUENCE {
    revocationTime              GeneralizedTime,
    revocationReason    [0]     EXPLICIT CRLReason OPTIONAL
}
```

---

### 8. Специфікація запиту на випуск сертифіката (CSR / PKCS#10, RFC 2986)

Перед отриманням сертифіката відкритого ключа користувач або вебсервер генерує пару ключів локально і створює запит на сертифікацію **PKCS#10** (англ. *Certificate Signing Request, CSR*):

```asn1
CertificationRequest ::= SEQUENCE {
    certificationRequestInfo CertificationRequestInfo,
    signatureAlgorithm       AlgorithmIdentifier,
    signature                BIT STRING
}

CertificationRequestInfo ::= SEQUENCE {
    version       INTEGER { v1(0) },
    subject       Name,
    subjectPKInfo SubjectPublicKeyInfo,
    attributes    [0] Attributes
}
```

- Поле `signature` містить цифровий підпис суб'єкта, обчислений його **власним закритим ключем** над `CertificationRequestInfo`.
- Це слугує математичним підтвердженням володіння (Proof of Possession, PoP): засвідчувальний центр перевіряє підпис через відкритий ключ `subjectPKInfo` і гарантує, що заявник справді володіє відповідним таємним ключем, а не намагається випустити сертифікат на чужий публічний ключ.

---

### 9. Текстовий формат інкапсуляції PEM

Формат PEM (RFC 7468) кодує бінарні DER-байти у друковані ASCII-символи за допомогою алгоритму Base64 з обрамленням спеціальними мітками заголовка та кінця.

```
-----BEGIN CERTIFICATE-----
MIICljCCAX6gAwIBAgIUQ9v5K2n1X8q4m... (рядки Base64 строго по 64 символи)
...
-----END CERTIFICATE-----
```

#### Вимоги до оформлення PEM-файлів:
1. **Префікс та суфікс:** рядок `-----BEGIN CERTIFICATE-----` на початку та `-----END CERTIFICATE-----` наприкінці. Для запитів CSR використовується `-----BEGIN CERTIFICATE REQUEST-----`, а для закритих ключів RSA чи EC — `-----BEGIN PRIVATE KEY-----` (PKCS#8). Між дефісами та назвою типу заборонені пробіли.
2. **Переноси рядків:** бінарний масив Base64 повинен розбиватися на рядки довжиною рівно 64 символи (допускається до 76 символів). Як роздільник рядка підтримується як UNIX-формат LF (`\n`), так і Windows CRLF (`\r\n`).
3. **Ланцюг сертифікатів (Full Chain):** при налаштуванні вебсерверів (Nginx, Apache, Envoy) у файл сертифіката записуються кілька PEM-блоків поспіль у строгому порядку:
   - 1-й блок: кінцевий сертифікат сервера (Leaf Certificate).
---

### 10. Суміжні формати контейнерів: PKCS#12 (.p12 / .pfx) та PKCS#7 (.p7b / CMS)

Окрім плоских PEM/DER сертифікатів, у мережевих службах та системному адмініструванні застосовуються спеціалізовані криптографічні контейнери:

#### 10.1. PKCS#12 (Personal Information Exchange Syntax, RFC 7292)
Контейнер PKCS#12 (файли з розширенням `.p12` або `.pfx`) призначений для захищеного зберігання та транспортування **повного криптографічного комплекту**: закритого ключа сервера, його кінцевого сертифіката та всіх проміжних сертифікатів засвідчувальних центрів в одному зашифрованому бінарному файлі.

- **Синтаксис верхнього рівня:** `PFX ::= SEQUENCE { version INTEGER {v3(3)}, authSafe ContentInfo, macData MacData OPTIONAL }`
- **Захист:** Закриті ключі шифруються симетричним алгоритмом (AES-256-CBC або застарілим 3DES) під паролем користувача за допомогою функції формування ключа PBKDF2 (Password-Based Key Derivation Function 2) або алгоритму PKCS#12 KDF.
- **Цілісність:** Контейнер містить структуру `MacData` (HMAC-SHA256), яка захищає вміст від несанкціонованої модифікації.

#### 10.2. PKCS#7 / CMS (Cryptographic Message Syntax, RFC 5652)
Формат PKCS#7 (файли `.p7b` або `.p7c`) являє собою бінарну або загорнуту в PEM структуру `SignedData`, яка містить виключно **ланцюги відкритих сертифікатів та списки відкликання (CRL)** без таємних ключів:

```asn1
SignedData ::= SEQUENCE {
    version          INTEGER,
    digestAlgorithms DigestAlgorithmIdentifiers,
    encapContentInfo EncapsulatedContentInfo,
    certificates [0] IMPLICIT CertificateSet OPTIONAL,
    crls         [1] IMPLICIT RevocationInfoChoices OPTIONAL,
    signerInfos      SignerInfos
}
```

- Використовується в операційних системах Windows для імпорту повних наборів сертифікатів засвідчувальних центрів та в поштовому стандарті S/MIME для передавання підписаних листів. Поле `certificates` містить повний набір сертифікатів, необхідних клієнту для побудови ланцюга довіри до кореневого якоря.
