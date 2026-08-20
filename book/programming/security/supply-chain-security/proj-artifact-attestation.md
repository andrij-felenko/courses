# ⚙️ Практика побудови конвеєра перевірки атестацій та підпису артефактів

У виробничих розподілених системах безпека розгортання вимагає наявності швидкого, автономного інструмента верифікації, який може бути безпосередньо інтегрований у контролер допуску Kubernetes (Admission Controller), системну утиліту розгортання або передпусковий хук на цільовому сервері. Головне завдання такого інструмента — перехопити бінарний артефакт або образ контейнера безпосередньо перед його виконанням, обчислити його криптографічний дайджест SHA-256, розпакувати атестацію походження у форматі in-toto, перевірити цифровий підпис та оцінити відповідність параметрів збирання корпоративним політикам безпеки.

Створення автономного верифікатора вимагає ретельного дотримання криптографічних гарантій. Недостатньо просто перевірити наявність цифрового підпису: необхідно переконатися, що підпис накладено на конкретний вміст атестації, суб'єкт атестації суворо відповідає бінарному файлу на диску, а параметри компілятора та ідентифікатор раннера збігаються з дозволеними корпоративними стандартами.

Нижче наведено повну реалізацію верифікатора атестацій SLSA Provenance v1.0, яка демонструє покрокову перевірку цілісності артефакту, зіставлення гешу з суб'єктом атестації та верифікацію цифрового підпису за стандартом ECDSA (NIST P-256).

---

### Архітектура процесу перевірки атестації

Процес верифікації артефакту складається з п'яти обов'язкових кроків, які мають виконуватися в суворій послідовності без можливості обходу проміжних етапів:

```
                  [ Бінарний артефакт (app.bin) ]
                                 │
                                 ▼ (Крок 1)
                     [ Обчислення SHA-256 гешу ]
                                 │
 [ Атестація: attestation.json ] │
               │                 │
               ▼ (Крок 2)        ▼
     [ Розбір конверта ] ◄───────┴──► [ Крок 3: Звірка гешу суб'єкта ]
     [ in-toto Envelope]                  (subject.digest.sha256)
               │                                     │
               ▼ (Крок 4)                            ▼
     [ Перевірка ECDSA підпису ]            [ Збіг підтверджено ]
     [ через відкритий ключ    ]                     │
               │                                     │
               ▼ (Крок 5)                            │
     [ Оцінка політики SLSA L3 ] ◄───────────────────┘
     [ builder.id + source.uri ]
               │
               ▼
      [ Вердикт: ДОЗВОЛЕНО / ВІДХИЛЕНО ]
```

1. **Обчислення гешу артефакту**: Потокове зчитування вхідного бінарного файлу блоками фіксованого розміру для мінімізації навантаження на оперативну пам'ять та генерація криптографічного відбитка SHA-256;
2. **Розбір конверта in-toto**: Десеріалізація структури JSON, декодування корисного навантаження (Base64) та перевірка типу предиката (`https://slsa.dev/provenance/v1`);
3. **Звірка суб'єкта (*Subject Matching*)**: Перевірка того, що обчислений геш артефакту байт-у-байт збігається зі значенням `subject[0].digest.sha256` у тілі атестації;
4. **Криптографічна валідація підпису**: Перевірка підпису корисного навантаження за відкритим ключем авторизованого центру збирання або ланцюжком сертифікатів;
5. **Оцінка правил безпеки**: Перевірка того, що артефакт зібрано довіреним раннером (`builder.id`), з офіційного репозиторію (`externalParameters.source`) та з дозволеної релізної гілки без несанкціонованих прапорців налагодження.

---

### Реалізація верифікатора

:::tabs
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <span>
#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <memory>
#include <expected>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/pem.h>

// Структура розібраної атестації SLSA v1.0
struct SlsaProvenance {
    std::string subject_name;
    std::string subject_sha256;
    std::string builder_id;
    std::string source_uri;
    std::string source_commit;
};

// RAII обгортки для коректного звільнення ресурсів OpenSSL
struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const { if (ctx) EVP_MD_CTX_free(ctx); }
};
using ScopedMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

struct EvpPkeyDeleter {
    void operator()(EVP_PKEY* pkey) const { if (pkey) EVP_PKEY_free(pkey); }
};
using ScopedPkey = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;

// 1. Потокове обчислення SHA-256 гешу файлу на диску
std::expected<std::string, std::string> calculate_sha256(std::string_view filepath) {
    std::ifstream file(std::string(filepath), std::ios::binary);
    if (!file.is_open()) {
        return std::unexpected("Неможливо відкрити цільовий файл артефакту");
    }

    ScopedMdCtx ctx(EVP_MD_CTX_new());
    if (!ctx || EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) != 1) {
        return std::unexpected("Помилка ініціалізації контексту EVP_MD");
    }

    std::vector<char> buffer(65536);
    while (file.read(buffer.data(), buffer.size()) || file.gcount() > 0) {
        if (EVP_DigestUpdate(ctx.get(), buffer.data(), file.gcount()) != 1) {
            return std::unexpected("Помилка обчислення проміжного гешу");
        }
    }

    unsigned char hash[EVP_MAX_MD_SIZE];
    unsigned int length = 0;
    if (EVP_DigestFinal_ex(ctx.get(), hash, &length) != 1) {
        return std::unexpected("Помилка фіналізації гешу");
    }

    std::ostringstream ss;
    for (unsigned int i = 0; i < length; ++i) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hash[i]);
    }
    return ss.str();
}

// 2. Декодування Base64 рядка
std::expected<std::string, std::string> base64_decode(std::string_view input) {
    std::vector<unsigned char> output(input.size());
    int len = EVP_DecodeBlock(output.data(), 
                              reinterpret_cast<const unsigned char*>(input.data()), 
                              static_cast<int>(input.size()));
    if (len < 0) {
        return std::unexpected("Помилка декодування Base64 корисного навантаження");
    }
    
    // Коригування padding символів '='
    int pad = 0;
    if (input.ends_with("==")) pad = 2;
    else if (input.ends_with("=")) pad = 1;

    return std::string(reinterpret_cast<char*>(output.data()), len - pad);
}

// 3. Перевірка цифрового підпису ECDSA над payload
bool verify_ecdsa_signature(std::string_view payload, 
                            std::string_view signature_b64, 
                            std::string_view public_key_pem) {
    auto sig_raw = base64_decode(signature_b64);
    if (!sig_raw) return false;

    BIO* bio = BIO_new_mem_buf(public_key_pem.data(), static_cast<int>(public_key_pem.size()));
    if (!bio) return false;

    ScopedPkey pkey(PEM_read_bio_PUBKEY(bio, nullptr, nullptr, nullptr));
    BIO_free(bio);
    if (!pkey) return false;

    ScopedMdCtx ctx(EVP_MD_CTX_new());
    if (!ctx) return false;

    if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, pkey.get()) != 1) {
        return false;
    }

    if (EVP_DigestVerifyUpdate(ctx.get(), payload.data(), payload.size()) != 1) {
        return false;
    }

    int rc = EVP_DigestVerifyFinal(ctx.get(), 
                                   reinterpret_cast<const unsigned char*>(sig_raw->data()), 
                                   sig_raw->size());
    return rc == 1;
}

// 4. Політика оцінки відповідності параметрів збирання
bool evaluate_policy(const SlsaProvenance& prov, 
                     std::string_view expected_builder, 
                     std::string_view expected_repo) {
    if (prov.builder_id != expected_builder) {
        std::cerr << "[ВІДМОВА] Недовірений Builder ID: " << prov.builder_id 
                  << " (очікувався: " << expected_builder << ")\n";
        return false;
    }
    if (prov.source_uri != expected_repo) {
        std::cerr << "[ВІДМОВА] Невідповідність репозиторію джерела: " << prov.source_uri 
                  << " (очікувався: " << expected_repo << ")\n";
        return false;
    }
    return true;
}

// Головна процедура аудиту артефакту
int verify_artifact(std::string_view artifact_path, 
                    const SlsaProvenance& prov, 
                    std::string_view payload_json, 
                    std::string_view signature_b64, 
                    std::string_view public_key_pem) {
    std::cout << "[1/4] Обчислення контрольного гешу артефакту: " << artifact_path << "...\n";
    auto digest = calculate_sha256(artifact_path);
    if (!digest) {
        std::cerr << "[ПОМИЛКА] " << digest.error() << "\n";
        return 1;
    }
    std::cout << "      Отримано SHA-256: " << *digest << "\n";

    std::cout << "[2/4] Звірка дайджесту з суб'єктом атестації...\n";
    if (*digest != prov.subject_sha256) {
        std::cerr << "[ВІДХИЛЕНО] Геш артефакту (" << *digest 
                  << ") не збігається з атестацією (" << prov.subject_sha256 << ")!\n";
        return 2;
    }
    std::cout << "      Геші збігаються. Цілісність файлу підтверджена.\n";

    std::cout << "[3/4] Перевірка цифрового підпису атестації...\n";
    if (!verify_ecdsa_signature(payload_json, signature_b64, public_key_pem)) {
        std::cerr << "[ВІДХИЛЕНО] Недійсний цифровий підпис атестації!\n";
        return 3;
    }
    std::cout << "      Криптографічний підпис дійсний.\n";

    std::cout << "[4/4] Оцінка правил політики SLSA L3...\n";
    if (!evaluate_policy(prov, 
                         "https://github.com/actions/runner/slsa-builder-generic@v2", 
                         "git+https://github.com/enterprise/payment-gateway")) {
        std::cerr << "[ВІДХИЛЕНО] Порушення правил безпеки походження!\n";
        return 4;
    }

    std::cout << "[УСПІХ] Артефакт повністю верифіковано. Допущено до виконання.\n";
    return 0;
}
```
```go
package main

import (
	"crypto"
	"crypto/ecdsa"
	"crypto/sha256"
	"crypto/x509"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"encoding/pem"
	"errors"
	"fmt"
	"io"
	"os"
)

// InTotoEnvelope описує універсальну структуру підписаного контейнера
type InTotoEnvelope struct {
	PayloadType string          `json:"payloadType"`
	Payload     string          `json:"payload"`
	Signatures  []SignatureMeta `json:"signatures"`
}

type SignatureMeta struct {
	KeyID string `json:"keyid"`
	Sig   string `json:"sig"`
}

// SLSAStatement описує структуру корисного навантаження SLSA Provenance v1.0
type SLSAStatement struct {
	Type          string          `json:"_type"`
	Subject       []SubjectMeta   `json:"subject"`
	PredicateType string          `json:"predicateType"`
	Predicate     SLSAPredicateV1 `json:"predicate"`
}

type SubjectMeta struct {
	Name   string            `json:"name"`
	Digest map[string]string `json:"digest"`
}

type SLSAPredicateV1 struct {
	BuildDefinition struct {
		BuildType          string `json:"buildType"`
		ExternalParameters struct {
			Source struct {
				URI    string `json:"uri"`
				Digest struct {
					GitCommit string `json:"gitCommit"`
				} `json:"digest"`
			} `json:"source"`
		} `json:"externalParameters"`
	} `json:"buildDefinition"`
	RunDetails struct {
		Builder struct {
			ID string `json:"id"`
		} `json:"builder"`
	} `json:"runDetails"`
}

// 1. Обчислення SHA-256 артефакту
func calculateSHA256(filePath string) (string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	h := sha256.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", err
	}
	return hex.EncodeToString(h.Sum(nil)), nil
}

// 2. Перевірка підпису ECDSA над декодованим корисним навантаженням
func verifySignature(payload []byte, sigBase64 string, pubKeyPEM []byte) error {
	block, _ := pem.Decode(pubKeyPEM)
	if block == nil {
		return errors.New("помилка парсингу PEM блоку публічного ключа")
	}

	pub, err := x509.ParsePKIXPublicKey(block.Bytes)
	if err != nil {
		return err
	}

	ecdsaPub, ok := pub.(*ecdsa.PublicKey)
	if !ok {
		return errors.New("ключ не є валідним ECDSA публічним ключем")
	}

	sigBytes, err := base64.StdEncoding.DecodeString(sigBase64)
	if err != nil {
		return err
	}

	h := sha256.Sum256(payload)
	if !ecdsa.VerifyASN1(ecdsaPub, h[:], sigBytes) {
		return errors.New("криптографічний підпис не відповідає даним")
	}
	return nil
}

// Головна функція верифікації
func VerifyArtifactPipeline(artifactPath string, envelopeBytes []byte, pubKeyPEM []byte) error {
	// Крок 1: Обчислення гешу цільового бінарника
	actualDigest, err := calculateSHA256(artifactPath)
	if err != nil {
		return fmt.Errorf("помилка читання артефакту: %w", err)
	}

	// Крок 2: Розбір конверта in-toto
	var env InTotoEnvelope
	if err := json.Unmarshal(envelopeBytes, &env); err != nil {
		return fmt.Errorf("невалідний JSON конверта in-toto: %w", err)
	}

	rawPayload, err := base64.StdEncoding.DecodeString(env.Payload)
	if err != nil {
		return fmt.Errorf("помилка декодування Base64 payload: %w", err)
	}

	// Крок 3: Перевірка підпису
	if len(env.Signatures) == 0 {
		return errors.New("відсутні цифрові підписи в конверті")
	}
	if err := verifySignature(rawPayload, env.Signatures[0].Sig, pubKeyPEM); err != nil {
		return fmt.Errorf("помилка перевірки підпису: %w", err)
	}

	// Крок 4: Розбір та зіставлення предикату SLSA
	var stmt SLSAStatement
	if err := json.Unmarshal(rawPayload, &stmt); err != nil {
		return fmt.Errorf("помилка парсингу SLSA Statement: %w", err)
	}

	if len(stmt.Subject) == 0 || stmt.Subject[0].Digest["sha256"] != actualDigest {
		return fmt.Errorf("геш артефакту (%s) не збігається з гешем атестації (%s)",
			actualDigest, stmt.Subject[0].Digest["sha256"])
	}

	// Крок 5: Перевірка відповідності правилам безпеки
	const expectedBuilder = "https://github.com/actions/runner/slsa-builder-generic@v2"
	const expectedSource = "git+https://github.com/enterprise/payment-gateway"

	if stmt.Predicate.RunDetails.Builder.ID != expectedBuilder {
		return fmt.Errorf("недовірений збирач: %s", stmt.Predicate.RunDetails.Builder.ID)
	}
	if stmt.Predicate.BuildDefinition.ExternalParameters.Source.URI != expectedSource {
		return fmt.Errorf("недозволене джерело: %s", stmt.Predicate.BuildDefinition.ExternalParameters.Source.URI)
	}

	fmt.Println("[УСПІХ] Артефакт успішно верифіковано. SLSA гарантії підтверджено.")
	return nil
}
```
:::

---

### Детальний розбір механізмів та інваріантів перевірки

#### 1. Звірка контрольних сум: захист від підміни бінарних файлів
Перший етап захищає від атаки підміни бінарного файлу легітимною чужою атестацією. Навіть якщо зловмисник візьме валідний підписаний документ `provenance.json` від іншого офіційного релізу, поле `subject[0].digest.sha256` міститиме унікальний відбиток того конкретного бінарника. Якщо поточний виконуваний файл має хоча б один змінений байт (наприклад, унаслідок підміни на рівні файлової системи чи мережевого перехоплення), функція порівняння гешів негайно зупиняє виконання зі статусом відмови.

Потокова обробка файлу через буфер фіксованого розміру (64 КБ) у функції `calculate_sha256` гарантує стабільне споживання пам'яті незалежно від того, чи перевіряється невеликий системний бінарний файл розміром 2 МБ, чи багатогігабайтний образ диска.

#### 2. Канонізація JSON та перевірка цифрового підпису
Критична пастка під час роботи з криптографічними підписами над JSON-структурами полягає в тому, що форматування JSON (пробіли, перенесення рядків, порядок ключів) може змінюватися серіалізаторами без зміни змісту. Якщо підписати JSON-рядок напряму, зміна порядку полів у парсері іншого середовища призведе до невалідності підпису.

Конверт in-toto вирішує цю проблему за допомогою Base64 кодування поля `payload`. Підпис накладається безпосередньо на вихідний масив байтів `payload`, що усуває будь-яку неоднозначність інтерпретації пробілів і порядку ключів. Під час перевірки валідатор передає в OpenSSL `EVP_DigestVerifyUpdate` точно той самий масив байтів, який було декодовано з Base64.

#### 3. Керування пам'яттю та безпека ресурсів OpenSSL
При роботі з криптографічною бібліотекою OpenSSL на C++ критично важливо уникати витоків ресурсів і подвійного звільнення пам'яті. У прикладі використано патерн RAII за допомогою `std::unique_ptr` із власними делетерами `EvpMdCtxDeleter` та `EvpPkeyDeleter`. Це гарантує, що контексти `EVP_MD_CTX` та структури ключів `EVP_PKEY` будуть коректно очищені за будь-яких умов виходу з функції, включно з виникненням помилок чи винятків у проміжних операціях.

Використання сучасного типу повернення `std::expected<std::string, std::string>` у стандарті C++23 дає змогу виразно передавати або успішний результат обчислення, або зрозуміле повідомлення про помилку без необхідності використання сирих кодів повернення чи неконтрольованих винятків.

#### 4. Перевірка контекстних тверджень (Claims Verification)
Перевірка підпису доводить лише те, що атестація була сформована власником закритого ключа. Головне рішення про допуск до виконання ухвалюється функцією оцінки політик (`evaluate_policy`):
- Вона вимагає, щоб `builder.id` відповідав саме захищеному конвеєру збирання, а не локальному налагоджувальному скрипту;
- Вона перевіряє, що URI вихідного коду належить офіційному репозиторію компанії, виключаючи збирання з форків розробників;
- За необхідності політика може додатково перевіряти наявність обов'язкових прапорців оптимізації компілятора та відсутність прапорців налагодження (*debug symbols*) у виробничому бінарнику.

---

### Тестування та перевірка на крайових випадках

Під час впровадження верифікатора в конвеєр розгортання слід провести автоматичне тестування на чотирьох негативних сценаріях:

1. **Тест на зміну байта (*Bit-flip Attack*)**: Модифікація одного байта у скомпільованому бінарному файлі. Очікуваний результат: відхилення на Кроці 2 (невідповідність гешу суб'єкта).
2. **Тест на модифікацію метаданих (*Tampered Provenance*)**: Зміна URI репозиторію всередині JSON-атестації без оновлення підпису. Очікуваний результат: відхилення на Кроці 3 (помилка верифікації ECDSA).
3. **Тест на чужий ключ (*Unauthorized Signer*)**: Підпис валідної атестації ключем, згенерованим іншим відділом або стороннім сервісом. Очікуваний результат: відхилення на Кроці 3 (публічний ключ корпоративного довіреного центру не збігається).
4. **Тест на збирання з форку (*Unauthorized Branch/Repo*)**: Успішне збирання та підпис артефакту на легітимному раннері, але з форку розробника `github.com/attacker/payment-gateway`. Очікуваний результат: відхилення на Кроці 4 (порушення політики `source.uri`).
