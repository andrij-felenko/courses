# 📋 Криптопідсистема ядра: типи перетворень, шаблони, прапорці

Це контракт звернення до криптопідсистеми Linux: які є типи перетворення й яким набором викликів працює кожен, повний перелік готових шаблонів із синтаксисом імені, що насправді означають аргументи `type`/`mask` — і що каже кожне поле запису в `/proc/crypto`. Довідка потрібна тому, що вся домовленість тримається на рядку з ім'ям алгоритму й парі чисел: помилка в них не ловиться компілятором і проявляється або як `-ENOENT` при виділенні, або — гірше — як мовчазний добір не тієї реалізації.

Підписи взято з `include/crypto/` ядра 6.x; де інтерфейс з'явився недавно, версію вказано окремо.

## Типи перетворення

Тип визначає **форму** операції, а не алгоритм: він каже, чи є ключ, чи є початковий вектор, чи операція розпадається на кроки й чи результат може прийти пізніше. Тип реалізації видно в `/proc/crypto` полем `type`, і брати її треба саме тим `crypto_alloc_*`, що відповідає цьому рядку.

| Тип | Заголовок | Форма операції | Запит |
| --- | --- | --- | --- |
| `skcipher` | `<crypto/skcipher.h>` | симетричний шифр із режимом; вхід і вихід — списки сегментів | так |
| `lskcipher` | `<crypto/skcipher.h>` | те саме на суцільних буферах, без запиту й колбека (ядро 6.7) | ні |
| `cipher` | `<crypto/internal/cipher.h>` | рівно один блок під ключем; шар для шаблонів, не для споживачів | ні |
| `shash` | `<crypto/hash.h>` | геш, завжди синхронний, дані звичайним вказівником | ні, дескриптор |
| `ahash` | `<crypto/hash.h>` | геш зі списком сегментів; за ним може стояти залізо | так |
| `aead` | `<crypto/aead.h>` | шифрування разом з автентичністю | так |
| `akcipher` | `<crypto/akcipher.h>` | асиметричне шифрування (RSA) | так |
| `sig` | `<crypto/sig.h>` | підпис і перевірка підпису; синхронний | ні |
| `kpp` | `<crypto/kpp.h>` | узгодження спільного ключа (DH, ECDH) | так |
| `rng` | `<crypto/rng.h>` | детермінований генератор із перезасіванням | ні |
| `acomp` | `<crypto/acompress.h>` | стиснення й розтиснення | так |
| `scomp` | — | синхронна реалізація стиснення; споживач її не бачить і виділяє `acomp` | — |

Два рядки потребують пояснення. `cipher` живе в теці `internal` навмисно: блоковий шифр без режиму — не робочий інструмент, і виклик потрібен лише тому коду, що надбудовує режим. А `sig` відокремили від `akcipher` восени 2024 року (комміт «crypto: akcipher — Drop sign/verify operations»): підпис і шифрування відкритим ключем — різні операції з різними розмірами входу, тож сьогодні `akcipher` уміє тільки шифрувати.

## Виділення й ключ

| Тип | Виділити | Дати ключ |
| --- | --- | --- |
| `skcipher` | `crypto_alloc_skcipher(name, type, mask)` | `crypto_skcipher_setkey(tfm, key, keylen)` |
| `lskcipher` | `crypto_alloc_lskcipher(name, type, mask)` | `crypto_lskcipher_setkey(tfm, key, keylen)` |
| `cipher` | `crypto_alloc_cipher(name, type, mask)` | `crypto_cipher_setkey(tfm, key, keylen)` |
| `shash` | `crypto_alloc_shash(name, type, mask)` | `crypto_shash_setkey(...)` — лише для ключових, як `hmac` |
| `ahash` | `crypto_alloc_ahash(name, type, mask)` | `crypto_ahash_setkey(...)` — так само |
| `aead` | `crypto_alloc_aead(name, type, mask)` | `crypto_aead_setkey(...)` **плюс** `crypto_aead_setauthsize(tfm, authsize)` |
| `akcipher` | `crypto_alloc_akcipher(name, type, mask)` | `crypto_akcipher_set_pub_key` / `..._set_priv_key(tfm, key, keylen)` |
| `sig` | `crypto_alloc_sig(name, type, mask)` | `crypto_sig_set_pubkey` / `crypto_sig_set_privkey` |
| `kpp` | `crypto_alloc_kpp(name, type, mask)` | `crypto_kpp_set_secret(tfm, buf, len)` — свій закритий параметр |
| `rng` | `crypto_alloc_rng(name, type, mask)` | `crypto_rng_reset(tfm, seed, slen)` — засівання, `seedsize` байтів |
| `acomp` | `crypto_alloc_acomp(name, type, mask)` | ключа немає |

Усі вони повертають вказівник, який перевіряють через `IS_ERR()`: `-ENOENT` означає «такого імені немає й скласти його нема з чого», `-ENOMEM` — брак пам'яті. Виклик має право заснути (може знадобитися завантажити модуль і прогнати самоперевірку), тому кличуть його лише з контексту процесу. Перевірити наявність, нічого не виділяючи, дають `crypto_has_skcipher`, `crypto_has_ahash`, `crypto_has_aead` та їхні побратими з тими самими `type`/`mask`. Звільняють парним `crypto_free_*`, ключ у `tfm` живе до звільнення.

## Одна операція

Типи з запитом мають однакову послідовність: виділити запит, прив'язати колбек, описати дані, викликати роботу.

```c
/* skcipher */
req = skcipher_request_alloc(tfm, GFP_KERNEL);
skcipher_request_set_callback(req, flags, compl, data);
skcipher_request_set_crypt(req, src_sg, dst_sg, cryptlen, iv);
err = crypto_skcipher_encrypt(req);          /* або crypto_skcipher_decrypt */

/* ahash: або одним махом, або init → update… → final */
ahash_request_set_crypt(req, src_sg, result, nbytes);
err = crypto_ahash_digest(req);              /* finup = update + final */

/* aead: асоційовані дані й корисне навантаження — в одному списку */
aead_request_set_ad(req, assoclen);
aead_request_set_crypt(req, src_sg, dst_sg, cryptlen, iv);
err = crypto_aead_encrypt(req);

/* akcipher */
akcipher_request_set_crypt(req, src_sg, dst_sg, src_len, dst_len);
err = crypto_akcipher_encrypt(req);

/* kpp: вхід і вихід задають окремо */
kpp_request_set_input(req, in_sg, in_len);
kpp_request_set_output(req, out_sg, out_len);
err = crypto_kpp_generate_public_key(req);   /* потім _compute_shared_secret */

/* acomp */
acomp_request_set_params(req, src_sg, dst_sg, slen, dlen);
err = crypto_acomp_compress(req);            /* або crypto_acomp_decompress */
```

Типи без запиту синхронні за побудовою — там нема чого чекати:

```c
SHASH_DESC_ON_STACK(desc, tfm);
desc->tfm = tfm;
crypto_shash_init(desc);
crypto_shash_update(desc, data, len);
crypto_shash_final(desc, out);
crypto_shash_tfm_digest(tfm, data, len, out);      /* те саме одним викликом */

crypto_lskcipher_encrypt(tfm, src, dst, len, siv); /* суцільні буфери, siv — вектор */
crypto_cipher_encrypt_one(tfm, dst, src);          /* рівно blocksize байтів */

crypto_sig_sign(tfm, src, slen, dst, dlen);
crypto_sig_verify(tfm, src, slen, digest, dlen);   /* ненуль = підпис не збігся */
crypto_rng_get_bytes(tfm, out, len);
```

Розкладка даних для `aead` — єдина, де легко помилитися. Список джерела містить `assoclen` байтів асоційованих даних, а одразу за ними — текст; при шифруванні в приймачі має бути місце ще й на тег (`cryptlen + authsize`), при розшифруванні `cryptlen` **уже включає тег**. Про сам режим, у якому частину даних лише автентифікують, є стаття [автентифіковане шифрування](topic:communications/authenticated-encryption) — там про те, чому тег рахують і від відкритого заголовка, і від шифротексту.

## Готові шаблони

Шаблон — це код режиму чи обгортки, який приймає інший алгоритм за іменем. Кома в дужках розділяє аргументи, порядок значущий.

| Шаблон | Синтаксис | Що дає на виході |
| --- | --- | --- |
| `ecb` | `ecb(aes)` | skcipher без зчеплення; сам по собі не вживають |
| `cbc` | `cbc(aes)` | зчеплення блоків, `ivsize` = `blocksize` |
| `ctr` | `ctr(aes)` | лічильник; `blocksize` стає 1, `chunksize` лишається 16 |
| `rfc3686` | `rfc3686(ctr(aes))` | той самий CTR із розкладкою nonce за RFC 3686 (IPsec) |
| `cts` | `cts(cbc(aes))` | крадіжка шифротексту для довжин, не кратних блоку |
| `xts` | `xts(aes)` | твік-режим для дискових секторів; ключ подвійної довжини |
| `lrw` | `lrw(aes)` | старіший твік-режим |
| `xctr`, `hctr2`, `adiantum` | `adiantum(xchacha12,aes)` | широкоблокові режими для файлових систем на залізі без AES |
| `essiv` | `essiv(cbc(aes),sha256)`, `essiv(authenc(hmac(sha256),cbc(aes)),sha256)` | початковий вектор, породжений гешем із номера сектора |
| `hmac` | `hmac(sha256)` | код автентичності на базі гешу, тип `shash`/`ahash` |
| `cmac`, `xcbc` | `cmac(aes)` | код автентичності на базі блокового шифру |
| `gcm` | `gcm(aes)`, розгорнуто `gcm_base(ctr(aes),ghash)` | AEAD із лічильником і множенням у полі |
| `rfc4106` | `rfc4106(gcm(aes))` | GCM із розкладкою ESP: 4 байти солі в кінці ключа, 8 байтів IV |
| `rfc4543` | `rfc4543(gcm(aes))` | GMAC: усе лише автентифікується, нічого не шифрується |
| `ccm` | `ccm(aes)`, розгорнуто `ccm_base(ctr(aes),cbcmac(aes))` | AEAD для заліза без множника |
| `rfc4309` | `rfc4309(ccm(aes))` | CCM із розкладкою ESP |
| `rfc7539` | `rfc7539(chacha20,poly1305)`, `rfc7539esp(chacha20,poly1305)` | AEAD без блокового шифру |
| `authenc` | `authenc(hmac(sha256),cbc(aes))` | шифрування плюс окремий MAC, старий розклад IPsec |
| `authencesn` | `authencesn(hmac(sha1),cbc(aes))` | те саме з розширеним номером послідовності |
| `seqiv`, `echainiv` | `seqiv(rfc4106(gcm(aes)))` | породження початкового вектора з лічильника |
| `cryptd` | `cryptd(__xts-aes-aesni)` | переносить виконання у робочу чергу |
| `pcrypt` | `pcrypt(rfc4106-gcm-aesni)` | розкидає AEAD-запити по ядрах через `padata` |

Аргументом шаблону може бути й **драйверне** ім'я — саме так збирають `cryptd(__…)` і `pcrypt(…)` навколо конкретної реалізації. Про `hmac` як конструкцію є окрема стаття: [HMAC і коди автентичності повідомлень](topic:communications/hmac).

## Аргументи type і mask

Кожен `crypto_alloc_*` бере ще два числа. Правило добору одне:

```
реалізація підходить ⟺ (cra_flags ^ type) & mask == 0
```

Тобто **`mask` каже, які біти взагалі перевіряти, а `type` — якими вони мають бути**. Свої біти типу перетворення підставляє сам виклик, тож споживачеві лишаються прапорці властивостей.

| `type`, `mask` | Що вимагає |
| --- | --- |
| `0`, `0` | будь-яка реалізація, найвища за пріоритетом |
| `0`, `CRYPTO_ALG_ASYNC` | тільки синхронна: біт має бути нульовим |
| `CRYPTO_ALG_ASYNC`, `CRYPTO_ALG_ASYNC` | тільки асинхронна |
| `0`, `CRYPTO_ALG_ALLOCATES_MEMORY` | реалізація не сміє виділяти пам'ять під час операції |
| `CRYPTO_ALG_INTERNAL`, `CRYPTO_ALG_INTERNAL` | дістатися внутрішньої реалізації |

| Прапорець алгоритму | Значення | Зміст |
| --- | --- | --- |
| `CRYPTO_ALG_ASYNC` | `0x00000080` | має право повернути `-EINPROGRESS` і покликати колбек |
| `CRYPTO_ALG_INTERNAL` | `0x00002000` | видно лише тому, хто спитав явно; так ховають реалізації, що самі по собі не годяться |
| `CRYPTO_ALG_ALLOCATES_MEMORY` | `0x00010000` | під час операції виділяє пам'ять |
| `CRYPTO_ALG_KERN_DRIVER_ONLY` | `0x00001000` | роботу робить залізо, недосяжне з простору користувача напряму |
| `CRYPTO_ALG_TESTED` | `0x00000400` | самоперевірку пройдено; це і є поле `selftest` |

> 🔧 **Навіщо це.** `CRYPTO_ALG_ALLOCATES_MEMORY` виглядає дрібницею, доки шифрування не опиниться на шляху вивільнення пам'яті: [dm-crypt](topic:unix-linux/dm-crypt) пише сторінки під тиском, і реалізація, яка в цю мить попросить пам'ять, замкне систему на собі. Тому пристроєві відображення ставлять цей біт у `mask`, лишаючи в `type` нуль, — і свідомо беруть повільнішу реалізацію, яка нічого не просить.

## Прапорці запиту й коди повернення

Перший аргумент після запиту в `*_request_set_callback` — прапорці саме цієї операції.

| Прапорець | Значення | Зміст |
| --- | --- | --- |
| `CRYPTO_TFM_REQ_MAY_SLEEP` | `0x00000200` | виклик відбувається там, де спати вільно |
| `CRYPTO_TFM_REQ_MAY_BACKLOG` | `0x00000400` | при заповненій черзі стати в чергу очікування, а не отримати відмову |
| `CRYPTO_TFM_REQ_FORBID_WEAK_KEYS` | `0x00000100` | відхиляти слабкі ключі (значуще для DES) |
| `CRYPTO_TFM_REQ_ON_STACK` | `0x00000800` | запит лежить у стеку виклику |

| Повернення | Що сталося |
| --- | --- |
| `0` | зроблено, результат уже на місці |
| `-EINPROGRESS` | прийнято, колбек буде згодом |
| `-EBUSY` з `MAY_BACKLOG` | стало в чергу очікування, колбек буде |
| `-EBUSY` без `MAY_BACKLOG` | відкинуто, повторювати самому |
| `-EBADMSG` | лише `crypto_aead_decrypt`: тег не збігся, вихід не вживати |
| `-EINVAL` | не сходяться довжини — ключа, вектора, буфера |

Пастка тут одна, і вона в колбеку: запит, який поклали в чергу очікування, отримує **два** виклики колбека — спершу з `-EINPROGRESS` у мить, коли він вийшов з черги й пішов у роботу, і потім із власне результатом. Готовий колбек `crypto_req_done` це враховує, і саме тому його тіло починається з перевірки:

```c
void crypto_req_done(void *data, int err)
{
        struct crypto_wait *wait = data;

        if (err == -EINPROGRESS)
                return;

        wait->err = err;
        complete(&wait->completion);
}
```

Власний колбек, який цієї перевірки не має, розбудить того, хто чекає, зарано — і буфер розберуть посеред роботи.

## Запис у /proc/crypto

Спільні поля йдуть для будь-якого типу.

| Поле | Що означає |
| --- | --- |
| `name` | узагальнене ім'я — те, що просить споживач |
| `driver` | ім'я саме цієї реалізації; ним просять її і тільки її |
| `module` | звідки вона прийшла; `kernel` — вбудована в образ |
| `priority` | вага при доборі, більше — краще; за домовленістю переносний код на C має 100, оптимізовані під архітектуру — сотні, окремі рушії — ще вище |
| `refcnt` | скільки живих перетворень і вкладень тримають алгоритм; поки не нуль, модуль не вивантажиться |
| `selftest` | `passed` — тестові вектори пройдено; `unknown` — ще ні, і споживачеві реалізацію не віддадуть |
| `internal` | `yes` — реалізацію дістане лише той, хто спитав про неї явно |
| `fips` | з'являється лише в режимі FIPS |
| `type` | тип перетворення; він і визначає, яким `crypto_alloc_*` її брати |

Решта полів залежить від типу.

| Тип | Додає |
| --- | --- |
| `cipher` | `blocksize`, `min keysize`, `max keysize` |
| `skcipher` | `async`, `blocksize`, `min keysize`, `max keysize`, `ivsize`, `chunksize`, `walksize`, `statesize` |
| `shash` | `blocksize`, `digestsize` |
| `ahash` | `async`, `blocksize`, `digestsize` |
| `aead` | `async`, `blocksize`, `ivsize`, `maxauthsize`, `geniv` |
| `rng` | `seedsize` |
| `akcipher`, `sig`, `kpp`, `acomp`, `scomp` | нічого, крім рядка `type` |
| `larval` | `flags : 0x…` — запис ще будується, алгоритму поки немає |

| Поле | Що означає |
| --- | --- |
| `async` | `yes` — результат може прийти колбеком |
| `blocksize` | природна порція алгоритму; у режимів, які поводяться як потокові (`ctr`), тут `1` |
| `min keysize`, `max keysize` | межі довжини ключа в байтах; у `xts` обидві вдвічі більші, бо ключів там два |
| `ivsize` | довжина початкового вектора, який чекає `*_set_crypt` |
| `chunksize` | найменша порція, яку алгоритм здатен обробити самостійно; у `ctr(aes)` це 16 при `blocksize` 1, і різати дані можна лише по її межі — крім останнього шматка |
| `walksize` | найбільша порція, яку реалізація хоче дістати суцільною; кратна `chunksize` і більша за неї там, де код молотить кілька блоків паралельно векторними інструкціями |
| `statesize` | розмір стану, який дають вивантажити й завантажити назад, щоб продовжити з середини |
| `digestsize` | довжина готового гешу |
| `maxauthsize` | найбільший тег, який прийме `crypto_aead_setauthsize` |
| `geniv` | генератор початкового вектора; майже завжди `<none>` — залишок від давнього способу робити IPsec |
| `seedsize` | скільки байтів засіву бере `crypto_rng_reset` |

Ці ж числа доступні з коду: `crypto_skcipher_ivsize()`, `crypto_skcipher_blocksize()`, `crypto_ahash_digestsize()`, `crypto_aead_authsize()`, `crypto_akcipher_maxsize()`, `crypto_kpp_maxsize()`, `crypto_rng_seedsize()` — саме ними, а не сталими в коді, і визначають розміри буферів.

## Найкоротший робочий виклик

```c
struct crypto_aead *tfm;
struct aead_request *req;
DECLARE_CRYPTO_WAIT(wait);
struct scatterlist sg[3];
int err;

tfm = crypto_alloc_aead("gcm(aes)", 0, 0);
if (IS_ERR(tfm))
        return PTR_ERR(tfm);

err = crypto_aead_setkey(tfm, key, 32);            /* AES-256 */
if (!err)
        err = crypto_aead_setauthsize(tfm, 16);    /* тег 16 байтів */
if (err)
        goto out_free_tfm;

req = aead_request_alloc(tfm, GFP_KERNEL);
if (!req) {
        err = -ENOMEM;
        goto out_free_tfm;
}

sg_init_table(sg, 3);
sg_set_buf(&sg[0], ad,   ad_len);     /* лише автентифікується */
sg_set_buf(&sg[1], data, data_len);   /* шифрується на місці */
sg_set_buf(&sg[2], tag,  16);         /* сюди ляже тег */

aead_request_set_callback(req,
        CRYPTO_TFM_REQ_MAY_BACKLOG | CRYPTO_TFM_REQ_MAY_SLEEP,
        crypto_req_done, &wait);
aead_request_set_ad(req, ad_len);
aead_request_set_crypt(req, sg, sg, data_len, iv);

err = crypto_wait_req(crypto_aead_encrypt(req), &wait);
```

Розшифрування відрізняється трьома дрібницями: тег має вже лежати в списку джерела, `cryptlen` дорівнює `data_len + 16`, а `-EBADMSG` означає, що дані підроблені й вихідний буфер треба викинути цілком, не дивлячись у нього.

Буфери `ad`, `data`, `tag` мусять походити з пам'яті, придатної для DMA — не зі стека й не з `vmalloc`; чому саме так, розібрано в довідці про [DMA і відображення буферів у ядрі](topic:unix-linux/dma-and-buffers). Ключі для `kpp` беруть не звідси, а з протоколу узгодження — [обмін ключами Діффі — Геллмана](topic:algorithms/diffie-hellman); засів для `rng` — з системного джерела випадковості, про яке є стаття [криптографічний генератор випадкових чисел](topic:algorithms/csprng).
