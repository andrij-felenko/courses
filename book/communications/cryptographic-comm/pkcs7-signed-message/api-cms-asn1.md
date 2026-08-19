# Специфікація ASN.1 та DER-структур PKCS#7 і CMS

Конструкція Cryptographic Message Syntax (CMS, RFC 5652) та її попередник PKCS#7 (RFC 2315) спираються на формальну граматику ASN.1 (Abstract Syntax Notation One) за правилами двійкового кодування DER (Distinguished Encoding Rules). Кожен криптографічний конверт є двійковим деревом елементів типу «тег — довжина — значення» (Tag-Length-Value, TLV), де кожен вузол однозначно декларує свій тип, клас простору імен, довжину вкладеного тіла в байтах та алгоритми криптографічної обробки.

Нижче наведено повну структурну специфікацію ASN.1-модуля `CryptographicMessageSyntax2004`, розширені структури для шифрування `EnvelopedData`, параметри RSA-PSS (RFC 4055), відповіді протоколу OCSP (RFC 5940), бітові маски розширень сертифікатів X.509 v3, спеціалізовані типи Microsoft Authenticode, таблиці числових ідентифікаторів об'єктів (OID), алгоритм кодування OID у двійковий формат, побайтовий розбір шістнадцяткового дампу та правила канонічної серіалізації DER.

---

### Двійкова анатомія ASN.1 DER: класи тегів та кодування довжин

Кожен елемент у потоці DER починається з одного або кількох байтів ідентифікатора типу (Identifier Octet):

```
 7   6   5   4   3   2   1   0  (Біти першого байта тегу)
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ Клас  │P/C│    Номер тегу     │
└───┴───┴───┴───┴───┴───┴───┴───┘
```

- **Клас тегу (Біти 7–6):**
  - `00` — **Universal:** стандартні загальносистемні типи ASN.1 (наприклад, `INTEGER = 0x02`, `OCTET STRING = 0x04`, `OBJECT IDENTIFIER = 0x06`, `SEQUENCE = 0x30`, `SET = 0x31`).
  - `01` — **Application:** типи, специфічні для конкретного прикладного стандарту.
  - `10` — **Context-Specific:** контекстні поля всередині структур (позначаються в ASN.1 як `[0]`, `[1]`, `[2]`). Наприклад, поле `certificates [0]` у `SignedData` має байт `0xA0` (`10` Context-Specific + `1` Constructed + `00000` Tag 0).
  - `11` — **Private:** типи, визначені конкретною організацією або підприємством.
- **Прапорець структури P/C (Біт 5):**
  - `0` — **Primitive:** неподільне значення (наприклад, сирі байти `OCTET STRING` або ціле число `INTEGER`).
  - `1` — **Constructed:** складене значення, всередині якого знаходяться інші вкладені TLV-елементи (`SEQUENCE`, `SET` або явні контекстні обгортки `EXPLICIT`).
- **Номер тегу (Біти 4–0):** Якщо номер тегу менший за 31, він записується безпосередньо у біти 4–0. Якщо номер `>= 31`, біти 4–0 заповнюються одиницями (`11111`), а сам номер кодується у наступних октетах у форматі змінної довжини VLQ (Base-128).

#### Кодування довжини (Length Octets) у DER
Правила DER (на відміну від BER) забороняють використання невизначеної довжини (Indefinite Length `0x80 ... 0x00 0x00`). Довжина повинна бути закодована у мінімально можливій кількості октетів:

1. **Коротка форма (Short Form, довжина 0–127 байтів):** кодується одним байтом `0xLL`, де біт 7 дорівнює `0`, а біти 6–0 містять довжину (наприклад, `0x20` = 32 байти).
2. **Довга форма (Long Form, довжина 128 байтів і більше):** перший байт має встановлений біт 7 (`0x80 + N`), де число `N` (від 1 до 126) задає кількість наступних байтів, що містять точну довжину у форматі big-endian (без провідних нулів). Наприклад, довжина 1024 байти (`0x0400`) кодується трьома байтами: `0x82 0x04 0x00`.

---

### Загальна оболонка ContentInfo

Усі типи повідомлень у CMS обов'язково упаковуються в універсальну зовнішню структуру `ContentInfo`. Вона відіграє роль поліморфного контейнера, що повідомляє десеріалізатору, який саме криптографічний тип розташовано всередині:

```asn1
ContentInfo ::= SEQUENCE {
    contentType        ContentType,
    content            [0] EXPLICIT ANY DEFINED BY contentType
}

ContentType ::= OBJECT IDENTIFIER
```

Двійковий тег поля `content` маркується як `[0] EXPLICIT` (байт `0xA0` у шістнадцятковому представленні), що дозволяє парсеру однозначно відокремити метадані заголовка від корисного навантаження до початку його розбору.

#### Стандартні OID типів вмісту

| Назва типу | Об'єктний ідентифікатор (OID) | ASN.1 визначення вмісту | Призначення |
| :--- | :--- | :--- | :--- |
| `id-data` | `1.2.840.113549.1.7.1` | `OCTET STRING` | Неструктурований масив сирих байтів (payload). |
| `id-signedData` | `1.2.840.113549.1.7.2` | `SignedData` | Дані з одним або кількома цифровими підписами. |
| `id-envelopedData` | `1.2.840.113549.1.7.3` | `EnvelopedData` | Зашифровані дані з ключами для списку одержувачів. |
| `id-digestedData` | `1.2.840.113549.1.7.5` | `DigestedData` | Дані, захищені лише контрольним дайджестом. |
| `id-encryptedData` | `1.2.840.113549.1.7.6` | `EncryptedData` | Дані, зашифровані спільним симетричним ключем. |
| `id-ct-authData` | `1.2.840.113549.1.9.16.1.2` | `AuthenticatedData` | Дані з кодом автентичності повідомлення (MAC). |
| `id-ct-authEnvelopedData` | `1.2.840.113549.1.9.16.1.23` | `AuthEnvelopedData` | Дані, захищені шифруванням AEAD (RFC 5083). |

---

### Структура SignedData

Коли поле `contentType` містить OID `id-signedData`, поле `content` розгортається в послідовність `SignedData`. Це головна структура для захисту цілісності, автентифікації автора та транспортування супутнього ланцюга сертифікатів:

```asn1
SignedData ::= SEQUENCE {
    version             CMSVersion,
    digestAlgorithms    DigestAlgorithmIdentifiers,
    encapContentInfo    EncapsulatedContentInfo,
    certificates        [0] IMPLICIT CertificateSet OPTIONAL,
    crls                [1] IMPLICIT RevocationInfoChoices OPTIONAL,
    signerInfos         SignerInfos
}

CMSVersion ::= INTEGER { v0(0), v1(1), v2(2), v3(3), v4(4), v5(5) }

DigestAlgorithmIdentifiers ::= SET OF AlgorithmIdentifier

AlgorithmIdentifier ::= SEQUENCE {
    algorithm           OBJECT IDENTIFIER,
    parameters          ANY DEFINED BY algorithm OPTIONAL
}

EncapsulatedContentInfo ::= SEQUENCE {
    eContentType        ContentType,
    eContent            [0] EXPLICIT OCTET STRING OPTIONAL
}

CertificateSet ::= SET OF CertificateChoices

CertificateChoices ::= CHOICE {
    certificate         Certificate,          -- X.509 v3 сертифікат (RFC 5280)
    extendedCertificate [0] IMPLICIT ExtendedCertificate, -- Застаріле з PKCS#7
    v1AttrCert          [1] IMPLICIT AttributeCertificateV1,
    v2AttrCert          [2] IMPLICIT AttributeCertificateV2,
    other               [3] IMPLICIT OtherCertificateFormat
}

RevocationInfoChoices ::= SET OF RevocationInfoChoice

RevocationInfoChoice ::= CHOICE {
    crl                 CertificateList,      -- X.509 CRL (RFC 5280)
    other               [1] IMPLICIT OtherRevocationInfoFormat
}

SignerInfos ::= SET OF SignerInfo
```

#### Семантика полів SignedData

1. **`version` (CMSVersion):** Синтаксична версія структури. Значення обчислюється автоматично залежно від використовуваних полів:
   - `v1` (1) — якщо всі підписувачі використовують `IssuerAndSerialNumber`, сертифікати є стандартними X.509, а `encapContentInfo.eContentType` дорівнює `id-data`.
   - `v3` (3) — якщо хоча б один підписувач використовує `SubjectKeyIdentifier` або `eContentType` відрізняється від `id-data`.
   - `v4` (4) — якщо присутні атрибутні сертифікати версії 2 (`v2AttrCert`).
   - `v5` (5) — якщо використовуються сторонні формати сертифікатів або списків відкликання (`other`).
2. **`digestAlgorithms`:** Множина ідентифікаторів алгоритмів гешування, які використовують автори для формування підписів. Дозволяє верифікатору наперед ініціалізувати обчислювальні конвеєри гешів (наприклад, SHA-256 та SHA-384) під час однопрохідного потокового читання.
3. **`encapContentInfo`:** Опис та вміст підписаних даних:
   - `eContentType` — OID типу внутрішніх даних (`id-data` або довільний специфічний OID застосунку).
   - `eContent` — опціональне поле з корисним навантаженням. Якщо поле присутнє, підпис є **вбудованим (attached)**. Якщо поле пропущене (`NULL`), підпис є **відокремленим (detached)**, а самі дані передаються чи зберігаються окремо.
4. **`certificates`:** Опціональний набір сертифікатів X.509 v3, необхідних для побудови повного ланцюга довіри від кінцевого сертифіката підписувача до довіреного кореневого центру (Root CA).
5. **`crls`:** Опціональний набір списків відкликання сертифікатів (CRL) або відповідей протоколу OCSP, дійсних на момент формування підпису.
6. **`signerInfos`:** Множина блоків із підписами окремих підписувачів. CMS дозволяє кільком незалежним особам або сервісам підписувати одне й те саме повідомлення (наприклад, розробник коду та служба безпеки репозиторію).

---

### Параметри алгоритму RSA-PSS у структурі AlgorithmIdentifier (RFC 4055)

Коли підпис генерується алгоритмом RSASSA-PSS (OID `1.2.840.113549.1.1.8`), поле `parameters` послідовності `AlgorithmIdentifier` містить детальну конфігурацію маскування:

```asn1
RSASSA-PSS-params ::= SEQUENCE {
    hashAlgorithm      [0] AlgorithmIdentifier DEFAULT sha1Identifier,
    maskGenAlgorithm   [1] AlgorithmIdentifier DEFAULT mgf1SHA1Identifier,
    saltLength         [2] INTEGER DEFAULT 20,
    trailerField       [3] INTEGER DEFAULT 1
}
```

У сучасних криптографічних профілях CMS для SHA-256 поле `saltLength` встановлюється в 32 (що відповідає довжині дайджесту SHA-256), а `maskGenAlgorithm` вказує на функцію MGF1 з ідентифікатором SHA-256.

---

### Інтеграція відповідей протоколу OCSP у поле crls (RFC 5940)

Стандарт RFC 5940 дозволяє вбудовувати відповіді онлайн-перевірки статусу сертифікатів (Online Certificate Status Protocol, OCSP) прямо в поле `crls` структури `SignedData`. Це усуває потребу виконання онлайн-запитів верифікатором:

```asn1
OtherRevocationInfoFormat ::= SEQUENCE {
    otherRevInfoFormat      OBJECT IDENTIFIER,
    otherRevInfo            ANY DEFINED BY otherRevInfoFormat
}

-- Для OCSP відповідей OID = id-ri-ocsp-response (1.3.6.1.5.5.7.48.1.1)
OCSPResponse ::= SEQUENCE {
    responseStatus          OCSPResponseStatus,
    responseBytes       [0] EXPLICIT ResponseBytes OPTIONAL
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
    tbsResponseData         ResponseData,
    signatureAlgorithm      AlgorithmIdentifier,
    signature               BIT STRING,
    certs               [0] EXPLICIT SEQUENCE OF Certificate OPTIONAL
}
```

Верифікатор отримує підписану відповідь OCSP-сервера, перевіряє підпис сервера відкликань та переконується, що сертифікат підписувача мав статус `GOOD` на момент генерації повідомлення. Це забезпечує повну автономність аудиту в закритих промислових мережах.

---

### Структура SignerInfo та ідентифікація підписувача

Кожен елемент множини `SignerInfos` описує цифровий підпис одного конкретного суб'єкта:

```asn1
SignerInfo ::= SEQUENCE {
    version             CMSVersion,
    sid                 SignerIdentifier,
    digestAlgorithm     DigestAlgorithmIdentifier,
    signedAttrs         [0] IMPLICIT SignedAttributes OPTIONAL,
    signatureAlgorithm  SignatureAlgorithmIdentifier,
    signature           SignatureValue,
    unsignedAttrs       [1] IMPLICIT UnsignedAttributes OPTIONAL
}

SignerIdentifier ::= CHOICE {
    issuerAndSerialNumber   IssuerAndSerialNumber,
    subjectKeyIdentifier    [0] SubjectKeyIdentifier
}

IssuerAndSerialNumber ::= SEQUENCE {
    issuer              Name,
    serialNumber        CertificateSerialNumber
}

SubjectKeyIdentifier ::= OCTET STRING

SignedAttributes ::= SET SIZE (1..MAX) OF Attribute

UnsignedAttributes ::= SET SIZE (1..MAX) OF Attribute

Attribute ::= SEQUENCE {
    attrType            OBJECT IDENTIFIER,
    attrValues          SET OF ANY DEFINED BY attrType
}

SignatureValue ::= OCTET STRING
```

#### Способи ідентифікації підписувача (`SignerIdentifier`)

- **`IssuerAndSerialNumber` (Класичний PKCS#7):** Однозначно зв'язує підпис із сертифікатом через пару «Distinguished Name (DN) видавця + унікальний серійний номер сертифіката». Цей спосіб підтримується всіма застарілими клієнтами S/MIME, але стає недійсним у разі перевипуску або поновлення сертифіката тим самим CA.
- **`SubjectKeyIdentifier` (CMS / RFC 5652):** Ідентифікує підписувача за 160- або 256-бітним гешем його відкритого ключа (розширення X.509 SKI). Дозволяє оновлювати сертифікати за умови збереження тієї самої пари ключів без порушення перевірки старих підписів.

---

### Підписані та непідписані атрибути

Якщо поле `signedAttrs` присутнє, криптографічний підпис `signature` обчислюється **не від корисного навантаження `eContent`**, а від канонічного DER-представлення всієї множини `signedAttrs`.

```
Дані (eContent) ───► SHA-256 ───► H_data
                                     │
                ┌────────────────────┘
                ▼
        [messageDigest: H_data]
        [contentType:   id-data] ───► DER SET OF (0x31) ───► SHA-256 ───► H_attr ───► RSA_Sign(H_attr)
        [signingTime:   2026.. ]                                                          │
                                                                                          ▼
                                                                                   SignatureValue
```

#### Обов'язкові підписані атрибути

Коли підписувач додає поле `signedAttrs`, стандарт RFC 5652 вимагає обов'язкової наявності двох атрибутів:

1. **`id-contentType` (`1.2.840.113549.1.9.3`):**
   ```asn1
   ContentTypeAttributeValue ::= OBJECT IDENTIFIER
   ```
   Мусить точно збігатися зі значенням `encapContentInfo.eContentType`. Це унеможливлює атаку підміни типу вмісту (наприклад, інтерпретацію підписаного бінарного коду як простого тексту).

2. **`id-messageDigest` (`1.2.840.113549.1.9.4`):**
   ```asn1
   MessageDigestAttributeValue ::= OCTET STRING
   ```
   Містить дайджест вихідного відкритого тексту `eContent`, обчислений за алгоритмом `digestAlgorithm`. Завдяки цьому атрибут створює криптографічний міст між тілом повідомлення та підписом атрибутів.

#### Додаткові підписані атрибути

- **`id-signingTime` (`1.2.840.113549.1.9.5`):** Заявляє локальний час створення підпису у форматі `UTCTime` (для років до 2049) або `GeneralizedTime`:
  ```asn1
  SigningTime ::= Time
  Time ::= CHOICE {
      utcTime             UTCTime,
      generalTime         GeneralizedTime
  }
  ```
  Формат `UTCTime` кодує дату як `YYMMDDHHMMSSZ` (двозначний рік). Правило RFC 5280 вимагає, щоб дати з `YY >= 50` інтерпретувалися як 1950–1999 роки, а дати з `YY < 50` — як 2000–2049 роки. Для 2050 року і пізніше стандарт зобов'язує використовувати `GeneralizedTime` (`YYYYMMDDHHMMSSZ`).
- **`id-aa-cmsAlgorithmProtection` (`1.2.840.113549.1.9.52`, RFC 6211):** Захищає від атак зниження криптографічної стійкості (Algorithm Downgrade Attacks). Фіксує точні ідентифікатори алгоритмів гешування та підпису:
  ```asn1
  CMSAlgorithmProtection ::= SEQUENCE {
      digestAlgorithm         DigestAlgorithmIdentifier,
      signatureAlgorithm  [1] SignatureAlgorithmIdentifier OPTIONAL,
      macAlgorithm        [2] MessageAuthenticationCodeAlgorithm OPTIONAL
  }
  ```

#### Непідписані атрибути (UnsignedAttributes)

Непідписані атрибути додаються до структури `SignerInfo` після генерації підпису. Вони не захищені первинним підписом `SignatureValue`, але можуть нести власний криптографічний захист:

- **`id-countersignature` (`1.2.840.113549.1.9.6`):** Контрпідпис (завірення). Значенням атрибута є ще одна повноцінна структура `SignerInfo`, у якій поле `signedAttrs.messageDigest` містить дайджест від байтів первинного підпису `SignatureValue`. Застосовується для багаторівневого візування документів або підтвердження нотаріусом.
- **`id-aa-timeStampToken` (`1.2.840.113549.1.9.16.2.14`, RFC 3161):** Криптографічний штамп часу від довіреного сервера TSA (Time Stamping Authority). Значенням є повний автономний контейнер `ContentInfo` типу `SignedData`, виданий TSA над гешем первинного підпису `SignatureValue`. Доводить, що підпис існував до моменту відкликання або закінчення терміну дії сертифіката.

---

### Розширення сертифікатів X.509 v3 для підпису коду та пошти

Під час верифікації CMS перевіряється відповідність сертифіката підписувача його цільовому призначенню через розширення X.509 v3:

1. **`KeyUsage` (OID `2.5.29.15`):** бітова маска, що обмежує операції з ключем:
   - `digitalSignature (0)` — **обов'язковий прапорець** для підписів `SignedData`.
   - `nonRepudiation (1)` — доказ авторства без можливості відмови.
   - `keyEncipherment (2)` — обов'язковий для одержувачів у `EnvelopedData` (Key Transport).
   - `keyAgreement (4)` — обов'язковий для протоколів ECDH у `EnvelopedData` (Key Agreement).
2. **`ExtendedKeyUsage` (OID `2.5.29.37`):** список OID допустимих сценаріїв використання:
   - `id-kp-codeSigning` (`1.3.6.1.5.5.7.3.3`) — підпис виконуваного коду та прошивок.
   - `id-kp-emailProtection` (`1.3.6.1.5.5.7.3.4`) — захист електронної пошти S/MIME.
   - `id-kp-timeStamping` (`1.3.6.1.5.5.7.3.8`) — підпис штампів часу серверами TSA.

---

### Структури захищеного конверта EnvelopedData

Коли потрібно забезпечити конфіденційність повідомлення для групи одержувачів, CMS використовує структуру `EnvelopedData`:

```asn1
EnvelopedData ::= SEQUENCE {
    version                 CMSVersion,
    originatorInfo      [0] IMPLICIT OriginatorInfo OPTIONAL,
    recipientInfos          RecipientInfos,
    encryptedContentInfo    EncryptedContentInfo,
    unprotectedAttrs    [1] IMPLICIT UnprotectedAttributes OPTIONAL
}

RecipientInfos ::= SET SIZE (1..MAX) OF RecipientInfo

RecipientInfo ::= CHOICE {
    ktri        KeyTransRecipientInfo,      -- Асиметричне шифрування (RSA)
    kari    [1] KeyAgreeRecipientInfo,      -- Узгодження ключів (ECDH)
    kekri   [2] KEKRecipientInfo,           -- Спільний симетричний KEK
    pwri    [3] PasswordRecipientInfo,      -- Ключ на основі пароля (PBKDF2)
    ori     [4] OtherRecipientInfo
}

KeyTransRecipientInfo ::= SEQUENCE {
    version                 CMSVersion,
    rid                     RecipientIdentifier,
    keyEncryptionAlgorithm  KeyEncryptionAlgorithmIdentifier,
    encryptedKey            EncryptedKey
}

EncryptedContentInfo ::= SEQUENCE {
    contentType                 ContentType,
    contentEncryptionAlgorithm  ContentEncryptionAlgorithmIdentifier,
    encryptedContent        [0] IMPLICIT EncryptedContent OPTIONAL
}
```

Контейнер `EnvelopedData` генерує одноразовий випадковий симетричний ключ (Content Encryption Key, CEK, наприклад AES-256), шифрує ним корисне навантаження `encryptedContentInfo`, а сам ключ CEK шифрує окремо для кожного одержувача через `RecipientInfo`. Одержувач розшифровує свій блок `encryptedKey` власним приватним ключем та отримує доступ до спільного відкритого тексту.

---

### Структури AuthenticatedData та AuthEnvelopedData

Стандарти RFC 5652 та RFC 5083 розширюють можливості CMS підтримкою симетричних кодів автентичності (MAC) та режимів автентифікованого шифрування AEAD:

```asn1
AuthenticatedData ::= SEQUENCE {
    version                 CMSVersion,
    originatorInfo      [0] IMPLICIT OriginatorInfo OPTIONAL,
    recipientInfos          RecipientInfos,
    macAlgorithm            MessageAuthenticationCodeAlgorithm,
    digestAlgorithm     [1] DigestAlgorithmIdentifier OPTIONAL,
    encapContentInfo        EncapsulatedContentInfo,
    authAttrs           [2] IMPLICIT AuthAttributes OPTIONAL,
    mac                     MessageAuthenticationCode,
    unauthAttrs         [3] IMPLICIT UnauthAttributes OPTIONAL
}

AuthEnvelopedData ::= SEQUENCE {
    version                 CMSVersion,
    originatorInfo      [0] IMPLICIT OriginatorInfo OPTIONAL,
    recipientInfos          RecipientInfos,
    authEncryptedContentInfo EncryptedContentInfo,
    authAttrs           [1] IMPLICIT AuthAttributes OPTIONAL,
    mac                     MessageAuthenticationCode,
    unauthAttrs         [2] IMPLICIT UnauthAttributes OPTIONAL
}
```

В `AuthEnvelopedData` використовується єдиний примітив AEAD (наприклад, AES-GCM або ChaCha20-Poly1305), де поле `authAttrs` передається як асоційовані нешифровані автентифіковані дані (Additional Authenticated Data, AAD), а обчислений тег автентифікації записується у поле `mac`.

---

### Структури Microsoft Authenticode у CMS

Підпис виконуваних файлів Windows PE (Portable Executable) за стандартом Authenticode інкапсулює структуру `SignedData`, у якій поле `encapContentInfo.eContentType` містить спеціалізований OID `SPC_INDIRECT_DATA_OBJID` (`1.3.6.1.4.1.311.2.1.4`), а тіло розгортається у структури:

```asn1
SpcIndirectDataContent ::= SEQUENCE {
    data                    SpcAttributeTypeAndOptionalValue,
    messageDigest           DigestInfo
}

SpcAttributeTypeAndOptionalValue ::= SEQUENCE {
    type                    OBJECT IDENTIFIER, -- SPC_PE_IMAGE_DATAOBJ (1.3.6.1.4.1.311.2.1.15)
    value                   ANY DEFINED BY type
}

SpcPeImageData ::= SEQUENCE {
    flags                   SpcPeImageFlagsType,
    file                    SpcLink
}

SpcSpOpusInfo ::= SEQUENCE {
    programName         [0] EXPLICIT SpcString OPTIONAL,
    moreInfo            [1] EXPLICIT SpcLink OPTIONAL
}
```

Поле `DigestInfo` містить хеш образу виконуваного файлу PE, обчислений за спеціальним алгоритмом Authenticode (з виключенням контрольної суми заголовка PE та самої таблиці сертифікатів безпеки).

---

### Алгоритм двійкового кодування OID у DER

Кожен числовий ідентифікатор `OID` (наприклад, `1.2.840.113549.1.7.1`) кодується у DER за спеціальним двійковим алгоритмом:

1. **Перші дві цифри (`X.Y`):** об'єднуються в єдиний перший байт за формулою:
   ```
   Byte[0] = X · 40 + Y
   ```
   Для OID, що починається з `1.2`, перший байт завжди дорівнює: `1 · 40 + 2 = 42 = 0x2A`.
2. **Усі наступні числа (`Z`):** кодуються у форматі змінної довжини Base-128 (Variable-Length Quantity). Кожне число розбивається на 7-бітні блоки. У всіх байтах, крім останнього, найстарший біт 7 встановлюється в `1`, а в останньому байті — в `0`.

**Приклад розбору числа `840` (`0x0348`):**
- Двійкове представлення: `0000011 1001000₂`.
- Перший 7-бітний блок (`0000011₂ = 3`) зі встановленим бітом 7: `0x80 | 0x03 = 0x86`.
- Другий 7-бітний блок (`1001000₂ = 72`): `0x48`.
- Результат кодування `840`: два байти `0x86 0x48`.

---

### Побайтовий аналіз бінарного DER-дампу ContentInfo

Нижче наведено шістнадцятковий дамп реального заголовка CMS `ContentInfo` з типом `SignedData`:

```
30 82 03 40          -- SEQUENCE (Довжина 0x0340 = 832 байти)
   06 09             -- OBJECT IDENTIFIER (Довжина 9 байтів)
      2A 86 48 86 F7 0D 01 07 02 -- 1.2.840.113549.1.7.2 (id-signedData)
   A0 82 03 31       -- [0] EXPLICIT (Контекстний тег розгортання content)
      30 82 03 2D    -- SEQUENCE (SignedData, довжина 813 байтів)
         02 01 03    -- INTEGER 3 (version = v3)
         31 0D       -- SET OF DigestAlgorithmIdentifiers (13 байтів)
            30 0B    -- SEQUENCE (AlgorithmIdentifier)
               06 09 -- OBJECT IDENTIFIER (id-sha256: 2.16.840.1.101.3.4.2.1)
                  60 86 48 01 65 03 04 02 01
```

Кожен байт у цьому дампі підпорядкований строгому математичному синтаксису DER, що унеможливлює неоднозначне тлумачення полів або зміщення вказівників пам'яті під час десеріалізації.

---

### Таблиця криптографічних OID для CMS

| Об'єктний ідентифікатор (OID) | Назва в RFC / OpenSSL | Призначення в структурі |
| :--- | :--- | :--- |
| `1.2.840.113549.1.1.1` | `rsaEncryption` | Алгоритм відкритого ключа RSA |
| `1.2.840.113549.1.1.11` | `sha256WithRSAEncryption` | Підпис PKCS#1 v1.5 RSA з дайджестом SHA-256 |
| `1.2.840.113549.1.1.8` | `id-RSASSA-PSS` | Стійкий підпис RSA-PSS (RFC 8017) |
| `1.2.840.10045.4.3.2` | `ecdsa-with-SHA256` | Підпис на еліптичних кривих ECDSA |
| `1.3.101.112` | `id-Ed25519` | Підпис EdDSA над кривою Curve25519 (RFC 8410) |
| `2.16.840.1.101.3.4.2.1` | `id-sha256` | Функція гешування SHA-256 (256 бітів) |
| `2.16.840.1.101.3.4.2.2` | `id-sha384` | Функція гешування SHA-384 (384 біти) |
| `2.16.840.1.101.3.4.2.3` | `id-sha512` | Функція гешування SHA-512 (512 бітів) |
| `1.2.840.113549.1.9.3` | `id-contentType` | Підписаний атрибут: тип корисного навантаження |
| `1.2.840.113549.1.9.4` | `id-messageDigest` | Підписаний атрибут: дайджест payload |
| `1.2.840.113549.1.9.5` | `id-signingTime` | Підписаний атрибут: час формування підпису |
| `1.2.840.113549.1.9.52` | `id-aa-cmsAlgorithmProtection` | Підписаний атрибут: захист алгоритмів |
| `1.2.840.113549.1.9.6` | `id-countersignature` | Непідписаний атрибут: додатковий підпис |
| `1.2.840.113549.1.9.16.2.14` | `id-aa-timeStampToken` | Непідписаний атрибут: штамп часу RFC 3161 |
| `1.3.6.1.4.1.311.2.1.4` | `SPC_INDIRECT_DATA_OBJID` | Тип контенту Authenticode у PE-файлах |
| `1.3.6.1.4.1.311.2.1.12` | `SPC_SP_OPUS_INFO_OBJID` | Метадані програми Authenticode (ім'я/URL) |
| `1.3.6.1.5.5.7.48.1.1` | `id-ri-ocsp-response` | Інформація про відкликання через OCSP |
| `1.3.6.1.5.5.7.3.3` | `id-kp-codeSigning` | Розширення X.509: дозвіл на підпис коду |
| `1.3.6.1.5.5.7.3.4` | `id-kp-emailProtection` | Розширення X.509: захист пошти S/MIME |

---

### Канонічні правила кодування DER для SignedAttributes

Формування та перевірка підпису над множиною `SignedAttributes` вимагають суворого дотримання канонічних правил DER (X.690). Будь-яке порушення правил детермінізму змінює байти повідомлення й робить криптографічний підпис недійсним:

1. **Заміна тегу при гешуванні:** В описі ASN.1 поле `signedAttrs` оголошено як `[0] IMPLICIT SignedAttributes`. У закодованому потоці воно має контекстний тег `0xA0`. Проте перед обчисленням гешу `H_attr` для накладання цифрового підпису перший байт тегу **обов'язково замінюється на стандартний універсальний тег `0x31` (`SET OF`)**.
2. **Лексикографічне сортування SET OF:** Елементи множини `SET OF Attribute` у DER повинні бути відсортовані за зростанням їхніх закодованих октетів (побайтове беззнакове порівняння). Якщо атрибут `id-contentType` має менше або коротше закодоване значення, ніж `id-messageDigest`, він зобов'язаний розташовуватися першим у бінарному масиві.
3. **Строгість представлення булевих значень (BOOLEAN):** Значення `TRUE` у DER обов'язково кодується байтом `0xFF` (на відміну від BER, де дозволено будь-який ненульовий байт від `0x01` до `0xFF`).
4. **Мінімальність цілих чисел (INTEGER):** Цілі числа повинні бути закодовані у мінімальній кількості октетів. Заборонено додавати зайві байти `0x00` на початку, якщо тільки найстарший біт першого байта не встановлений у `1` (байт `0x00` додається лише для позначення додатного числа в доповняльному коді).
