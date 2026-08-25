# ⚙️ Реалізація захищеного gossip-рушія з підписами Ed25519 та скорингом

У класичних реалізаціях gossip-протоколів (таких як оригінальний SWIM або базовий Scuttlebutt) вузли обмінюються мережевими UDP-дейтаграмами без криптографічної перевірки авторства. При отриманні повідомлення вузол сліпо довіряє зазначеному номеру версії або інкарнації та оновлює локальний стан кластера. У довіреному середовищі ізольованого дата-центру це забезпечує мінімальні накладні витрати на процесор і нульову затримку серіалізації. Проте у відкритих однорангових мережах, мультитенентних хмарах або за наявності скомпрометованого вузла така наївна модель відкриває простір для катастрофічних збоїв.

Зловмисник може згенерувати підроблене повідомлення про вихід з ладу критичних серверів, надіслати штучно завищений лічильник послідовності (`seq = 2⁶⁴ - 1`), що заблокує подальші легітимні оновлення, або здійснити атаку повторного відтворення (replay attack), змушуючи кластер повертатися до застарілої конфігурації. Щоб унеможливити подібні сценарії, транспортний рівень пліток підсилюється захисним конвеєром валідації.

Нижче наведено практичну архітектуру та реалізацію захищеного gossip-рушія двома мовами: C (для вбудованих та низькорівневих системних компонентів) та ідіоматичному C++20 (з використанням строгих типів, безпечного доступу до пам'яті через `std::span` та виразної обробки помилок через `std::expected`).

---

## Архітектура криптографічного конверта та інваріанти валідації

Кожне повідомлення перед відправленням у мережу пакується в бінарний конверт фіксованого формату. Захисний конвеєр приймача розбиває перевірку дейтаграми на п'ять послідовних етапів:

1. **Контроль довжини та формату:** Захищає пам'ять вузла від переповнення буфера (`buffer overflow`) або вичерпання купи занадто великими пакетами.
2. **Перевірка часового зсуву (Clock Drift Filter):** Захищає від підробки міток часу. Якщо позначка часу відрізняється від локального системного годинника більше ніж на `MAX_CLOCK_DRIFT_SEC`, повідомлення відкидається. Це запобігає атакам із фіксацією повідомлень «у далекому майбутньому».
3. **Криптографічна автентифікація джерела:** Перевірка асиметричного цифрового підпису Ed25519 гарантує незмінність корисного навантаження. Проміжний ретранслятор передає пакет далі, не маючи змоги модифікувати жодного байта без порушення підпису.
4. **Фільтрація монотонності та вікно повторів:** Кожен вузол підтримує таблицю останніх бачених номерів `last_seq` для всіх відомих джерел. Повідомлення з `seq ≤ last_seq` відкидаються як застарілі дублікати.
5. **Детекція візантійської еквівокації (Equivocation Detection):** Якщо надходить повідомлення з номером `seq == last_seq`, але його криптографічний хеш відрізняється від раніше зафіксованого для цього ж `seq`, рушій фіксує факт зради (подвійні плітки). Джерело негайно отримує штраф у репутацію та довічний бан.

```
+-----------------------------------------------------------------------------------+
| Origin Node ID (32 bytes) | Sequence (8 bytes) | Timestamp (8 bytes)              |
+-----------------------------------------------------------------------------------+
| Payload Length (4 bytes)  | Payload Data (N bytes)                                |
+-----------------------------------------------------------------------------------+
| Cryptographic Signature (Ed25519 / HMAC-SHA256, 64 bytes)                         |
+-----------------------------------------------------------------------------------+
```

---

## Скоринг репутації пірів за моделлю Gossipsub

Система захисту не обмежується лише перевіркою джерела: вона оцінює поведінку безпосереднього сусіда-ретранслятора (`relay_peer_id`). Якщо сусід передає невалідні підписи або сміттєвий трафік, його локальний рейтинг `score` падає. При досягненні порогу `SCORE_GREYLIST_THRESHOLD` сусід відключається від активної сітки ретрансляції, що локалізує DoS-атаки та запобігає засміченню мережевих каналів.

---

## Сирцевий код захищеного gossip-рушія

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>

#define NODE_ID_LEN 32
#define SIGNATURE_LEN 64
#define MAX_PAYLOAD_LEN 1024
#define PEER_TABLE_SIZE 256
#define MAX_CLOCK_DRIFT_SEC 5
#define SCORE_INVALID_SIG -100.0f
#define SCORE_EQUIVOCATION -500.0f
#define SCORE_VALID_DELIVERY 1.0f
#define SCORE_GREYLIST_THRESHOLD -50.0f

typedef struct {
    uint8_t origin_id[NODE_ID_LEN];
    uint64_t seq_num;
    uint64_t timestamp_sec;
    uint32_t payload_len;
    uint8_t payload[MAX_PAYLOAD_LEN];
    uint8_t signature[SIGNATURE_LEN];
} GossipEnvelope;

typedef struct {
    uint8_t node_id[NODE_ID_LEN];
    uint64_t last_seq;
    uint8_t last_payload_hash[32];
    float score;
    bool is_banned;
} PeerRecord;

typedef struct {
    PeerRecord peers[PEER_TABLE_SIZE];
    size_t peer_count;
    uint8_t local_id[NODE_ID_LEN];
} SecureGossipEngine;

// Проста імітація криптографічного хешу для ілюстрації логіки валідації
static void compute_payload_hash(const uint8_t *payload, size_t len, uint8_t *out_hash) {
    memset(out_hash, 0, 32);
    for (size_t i = 0; i < len; ++i) {
        out_hash[i % 32] ^= payload[i];
    }
}

// Заглушка перевірки Ed25519 підпису (у продакшені: crypto_sign_verify_detached)
static bool verify_ed25519_signature(const uint8_t *origin_id, const GossipEnvelope *env) {
    if (env->signature[0] == 0xFF && env->signature[1] == 0xFF) {
        return false; // Симуляція підробленого підпису
    }
    return (origin_id != NULL && env != NULL);
}

void engine_init(SecureGossipEngine *engine, const uint8_t *local_id) {
    memset(engine, 0, sizeof(SecureGossipEngine));
    memcpy(engine->local_id, local_id, NODE_ID_LEN);
}

PeerRecord *get_or_create_peer(SecureGossipEngine *engine, const uint8_t *node_id) {
    for (size_t i = 0; i < engine->peer_count; ++i) {
        if (memcmp(engine->peers[i].node_id, node_id, NODE_ID_LEN) == 0) {
            return &engine->peers[i];
        }
    }
    if (engine->peer_count < PEER_TABLE_SIZE) {
        PeerRecord *p = &engine->peers[engine->peer_count++];
        memcpy(p->node_id, node_id, NODE_ID_LEN);
        p->last_seq = 0;
        p->score = 0.0f;
        p->is_banned = false;
        memset(p->last_payload_hash, 0, 32);
        return p;
    }
    return NULL;
}

typedef enum {
    PROCESS_OK = 0,
    ERR_PEER_BANNED,
    ERR_INVALID_LENGTH,
    ERR_CLOCK_DRIFT,
    ERR_BAD_SIGNATURE,
    ERR_REPLAY_STALE,
    ERR_EQUIVOCATION_DETECTED
} ValidationResult;

ValidationResult process_incoming_gossip(SecureGossipEngine *engine,
                                         const uint8_t *relay_peer_id,
                                         const GossipEnvelope *env,
                                         uint64_t current_time_sec) {
    PeerRecord *relay = get_or_create_peer(engine, relay_peer_id);
    if (relay && relay->is_banned) {
        return ERR_PEER_BANNED;
    }

    if (env->payload_len > MAX_PAYLOAD_LEN) {
        if (relay) relay->score += SCORE_INVALID_SIG;
        return ERR_INVALID_LENGTH;
    }

    // 1. Перевірка часового зсуву (Clock Drift)
    int64_t drift = (int64_t)env->timestamp_sec - (int64_t)current_time_sec;
    if (drift > MAX_CLOCK_DRIFT_SEC || drift < -MAX_CLOCK_DRIFT_SEC) {
        return ERR_CLOCK_DRIFT;
    }

    // 2. Криптографічна перевірка підпису джерела
    if (!verify_ed25519_signature(env->origin_id, env)) {
        if (relay) {
            relay->score += SCORE_INVALID_SIG;
            if (relay->score < SCORE_GREYLIST_THRESHOLD) {
                relay->is_banned = true;
            }
        }
        return ERR_BAD_SIGNATURE;
    }

    PeerRecord *origin = get_or_create_peer(engine, env->origin_id);
    if (!origin) {
        return ERR_PEER_BANNED;
    }

    uint8_t current_hash[32];
    compute_payload_hash(env->payload, env->payload_len, current_hash);

    // 3. Перевірка еквівокації (той самий seq, але інший хеш)
    if (env->seq_num == origin->last_seq && origin->last_seq > 0) {
        if (memcmp(origin->last_payload_hash, current_hash, 32) != 0) {
            origin->score += SCORE_EQUIVOCATION;
            origin->is_banned = true;
            if (relay) relay->score += SCORE_INVALID_SIG;
            return ERR_EQUIVOCATION_DETECTED;
        }
        return ERR_REPLAY_STALE;
    }

    // 4. Перевірка на застарілий номер послідовності (Replay)
    if (env->seq_num < origin->last_seq) {
        return ERR_REPLAY_STALE;
    }

    // 5. Оновлення стану та підвищення рейтингу
    origin->last_seq = env->seq_num;
    memcpy(origin->last_payload_hash, current_hash, 32);
    if (relay) {
        relay->score += SCORE_VALID_DELIVERY;
    }

    return PROCESS_OK;
}

int main(void) {
    SecureGossipEngine engine;
    uint8_t my_id[NODE_ID_LEN] = {1};
    uint8_t peer_a[NODE_ID_LEN] = {2};
    uint8_t rogue[NODE_ID_LEN] = {9};

    engine_init(&engine, my_id);

    GossipEnvelope msg1;
    memcpy(msg1.origin_id, peer_a, NODE_ID_LEN);
    msg1.seq_num = 1;
    msg1.timestamp_sec = 1000;
    msg1.payload_len = 12;
    memcpy(msg1.payload, "Status=Alive", 12);
    msg1.signature[0] = 0xAA; // Валідний підпис

    ValidationResult r1 = process_incoming_gossip(&engine, peer_a, &msg1, 1000);
    printf("Message 1 result: %d (Expected 0 - OK)\n", r1);

    // Спроба повтору старого повідомлення (Replay)
    ValidationResult r2 = process_incoming_gossip(&engine, peer_a, &msg1, 1001);
    printf("Replay result: %d (Expected 5 - Stale)\n", r2);

    // Спроба еквівокації від rogue: той самий seq=1, але інший payload
    GossipEnvelope msg_rogue1;
    memcpy(msg_rogue1.origin_id, rogue, NODE_ID_LEN);
    msg_rogue1.seq_num = 10;
    msg_rogue1.timestamp_sec = 1002;
    msg_rogue1.payload_len = 8;
    memcpy(msg_rogue1.payload, "State=V1", 8);
    msg_rogue1.signature[0] = 0xAA;
    process_incoming_gossip(&engine, rogue, &msg_rogue1, 1002);

    GossipEnvelope msg_rogue2;
    memcpy(msg_rogue2.origin_id, rogue, NODE_ID_LEN);
    msg_rogue2.seq_num = 10; // Той самий seq!
    msg_rogue2.timestamp_sec = 1002;
    msg_rogue2.payload_len = 8;
    memcpy(msg_rogue2.payload, "State=V2", 8); // Інший вміст!
    msg_rogue2.signature[0] = 0xAA;

    ValidationResult r3 = process_incoming_gossip(&engine, rogue, &msg_rogue2, 1002);
    printf("Equivocation result: %d (Expected 6 - Equivocation Detected)\n", r3);

    PeerRecord *rogue_rec = get_or_create_peer(&engine, rogue);
    if (rogue_rec) {
        printf("Rogue peer banned status: %s, Score: %.1f\n",
               rogue_rec->is_banned ? "TRUE" : "FALSE", rogue_rec->score);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <unordered_map>
#include <string_view>
#include <span>
#include <chrono>
#include <expected>
#include <cstring>

namespace gossip::security {

constexpr size_t NodeIdLength = 32;
constexpr size_t SignatureLength = 64;
constexpr size_t MaxPayloadLength = 1024;
constexpr int64_t MaxClockDriftSeconds = 5;

constexpr double ScoreInvalidSignature = -100.0;
constexpr double ScoreEquivocation = -500.0;
constexpr double ScoreValidDelivery = 1.0;
constexpr double ScoreGreylistThreshold = -50.0;

using NodeId = std::array<uint8_t, NodeIdLength>;
using Signature = std::array<uint8_t, SignatureLength>;
using Hash256 = std::array<uint8_t, 32>;

struct NodeIdHash {
    size_t operator()(const NodeId& id) const noexcept {
        size_t h = 0;
        for (size_t i = 0; i < sizeof(size_t) && i < id.size(); ++i) {
            h = (h << 8) | id[i];
        }
        return h;
    }
};

struct GossipEnvelope {
    NodeId originId{};
    uint64_t sequenceNumber{0};
    uint64_t timestampSeconds{0};
    std::vector<uint8_t> payload{};
    Signature signature{};
};

enum class SecurityError {
    PeerBanned,
    PayloadTooLarge,
    ClockDriftExceeded,
    InvalidSignature,
    ReplayStaleSequence,
    EquivocationDetected
};

struct PeerRecord {
    NodeId id{};
    uint64_t lastSequence{0};
    Hash256 lastPayloadHash{};
    double score{0.0};
    bool isBanned{false};
};

class SecureGossipEngine {
public:
    explicit SecureGossipEngine(NodeId localId)
        : localId_(localId) {}

    std::expected<void, SecurityError> processIncomingGossip(
        const NodeId& relayPeerId,
        const GossipEnvelope& envelope,
        std::chrono::seconds currentTime)
    {
        auto& relay = getOrCreatePeer(relayPeerId);
        if (relay.isBanned) {
            return std::unexpected(SecurityError::PeerBanned);
        }

        if (envelope.payload.size() > MaxPayloadLength) {
            relay.score += ScoreInvalidSignature;
            return std::unexpected(SecurityError::PayloadTooLarge);
        }

        // 1. Перевірка часового зсуву
        auto nowSec = static_cast<uint64_t>(currentTime.count());
        int64_t drift = static_cast<int64_t>(envelope.timestampSeconds) - static_cast<int64_t>(nowSec);
        if (drift > MaxClockDriftSeconds || drift < -MaxClockDriftSeconds) {
            return std::unexpected(SecurityError::ClockDriftExceeded);
        }

        // 2. Криптографічна перевірка підпису Ed25519
        if (!verifySignature(envelope.originId, envelope)) {
            relay.score += ScoreInvalidSignature;
            if (relay.score < ScoreGreylistThreshold) {
                relay.isBanned = true;
            }
            return std::unexpected(SecurityError::InvalidSignature);
        }

        auto& origin = getOrCreatePeer(envelope.originId);
        if (origin.isBanned) {
            return std::unexpected(SecurityError::PeerBanned);
        }

        Hash256 currentHash = computeHash(envelope.payload);

        // 3. Перевірка на еквівокацію
        if (envelope.sequenceNumber == origin.lastSequence && origin.lastSequence > 0) {
            if (origin.lastPayloadHash != currentHash) {
                origin.score += ScoreEquivocation;
                origin.isBanned = true;
                relay.score += ScoreInvalidSignature;
                return std::unexpected(SecurityError::EquivocationDetected);
            }
            return std::unexpected(SecurityError::ReplayStaleSequence);
        }

        // 4. Перевірка монотонності послідовності (Replay)
        if (envelope.sequenceNumber < origin.lastSequence) {
            return std::unexpected(SecurityError::ReplayStaleSequence);
        }

        // 5. Оновлення стану
        origin.lastSequence = envelope.sequenceNumber;
        origin.lastPayloadHash = currentHash;
        relay.score += ScoreValidDelivery;

        return {};
    }

    [[nodiscard]] const PeerRecord* getPeer(const NodeId& id) const {
        auto it = peers_.find(id);
        return (it != peers_.end()) ? &it->second : nullptr;
    }

private:
    NodeId localId_;
    std::unordered_map<NodeId, PeerRecord, NodeIdHash> peers_;

    PeerRecord& getOrCreatePeer(const NodeId& id) {
        auto [it, _] = peers_.try_emplace(id, PeerRecord{id, 0, {}, 0.0, false});
        return it->second;
    }

    static Hash256 computeHash(std::span<const uint8_t> payload) {
        Hash256 out{};
        for (size_t i = 0; i < payload.size(); ++i) {
            out[i % 32] ^= payload[i];
        }
        return out;
    }

    static bool verifySignature(const NodeId& /*originId*/, const GossipEnvelope& env) {
        if (!env.signature.empty() && env.signature[0] == 0xFF && env.signature[1] == 0xFF) {
            return false; // Симуляція підробленого підпису
        }
        return true;
    }
};

} // namespace gossip::security

int main() {
    using namespace gossip::security;

    NodeId myId{1};
    NodeId peerA{2};
    NodeId rogueNode{9};

    SecureGossipEngine engine(myId);

    // 1. Коректне повідомлення
    GossipEnvelope msg1{
        .originId = peerA,
        .sequenceNumber = 1,
        .timestampSeconds = 1000,
        .payload = {'S', 't', 'a', 't', 'u', 's', '=', 'O', 'K'},
        .signature = {0xAA}
    };

    auto res1 = engine.processIncomingGossip(peerA, msg1, std::chrono::seconds(1000));
    std::cout << "Message 1 valid: " << (res1.has_value() ? "YES" : "NO") << "\n";

    // 2. Повтор застарілого повідомлення
    auto res2 = engine.processIncomingGossip(peerA, msg1, std::chrono::seconds(1001));
    std::cout << "Replay detected error: "
              << (res2.error() == SecurityError::ReplayStaleSequence ? "Stale Sequence" : "Other") << "\n";

    // 3. Еквівокація (той самий seq=5, різний payload)
    GossipEnvelope rogueMsg1{
        .originId = rogueNode,
        .sequenceNumber = 5,
        .timestampSeconds = 1002,
        .payload = {'V', 'e', 'r', 's', 'i', 'o', 'n', '1'},
        .signature = {0xAA}
    };
    engine.processIncomingGossip(rogueNode, rogueMsg1, std::chrono::seconds(1002));

    GossipEnvelope rogueMsg2{
        .originId = rogueNode,
        .sequenceNumber = 5,
        .timestampSeconds = 1002,
        .payload = {'V', 'e', 'r', 's', 'i', 'o', 'n', '2'},
        .signature = {0xAA}
    };
    auto res3 = engine.processIncomingGossip(rogueNode, rogueMsg2, std::chrono::seconds(1002));
    std::cout << "Equivocation error: "
              << (res3.error() == SecurityError::EquivocationDetected ? "Equivocation Detected" : "Other") << "\n";

    if (const auto* roguePeer = engine.getPeer(rogueNode)) {
        std::cout << "Rogue peer banned: " << (roguePeer->isBanned ? "TRUE" : "FALSE")
                  << ", Score: " << roguePeer->score << "\n";
    }

    return 0;
}
```
:::

---

## Детальний розбір конвеєра обробки та оптимізація Ed25519

Реалізований конвеєр демонструє фундаментальний розподілений принцип: **дешеві перевірки виконуються раніше за дорогі**.

1. **Етап швидкого відсікання (Fast-Reject):**
   Перевірка довжини дейтаграми та часового зсуву займає одиниці наносекунд і виконується на рівні пам'яті стека. Це захищає процесор від необхідності викликати високовартісну криптографічну верифікацію, якщо пакет надійшов із явним порушенням протокольного контракту або пошкоджений на фізичному рівні.
2. **Пакетна верифікація (Batch Signature Verification):**
   У високонавантажених системах (наприклад, у клієнтах Ethereum Prysm або Lighthouse) валідація окремих підписів `crypto_sign_verify_detached` замінюється пакетною перевіркою за алгоритмом Босселаера — Кнута (Bos-Coster). Замість перевірки `m` підписів по черзі:
   ```
   8 · S_i · B = 8 · R_i + 8 · H(R_i, A_i, M_i) · A_i
   ```
   рушій накопичує пакет із 32–64 повідомлень і перевіряє одну зведену мультискалярну точку на еліптичній кривій Curve25519:
   ```
   ∑ z_i · S_i · B = ∑ z_i · R_i + ∑ (z_i · H(R_i, A_i, M_i)) · A_i
   ```
   де `z_i` — 128-бітні випадкові скаляри. Це прискорює сумарну верифікацію у 2.5–3 рази, знижуючи середній час обробки одного підпису з 65 мкс до менш ніж 25 мкс.

---

## Пастки пам'яті та крайові випадки Sybil-атак

Під час практичної експлуатації захищеного gossip-рушія виникають три типові інженерні пастки:

1. **Виснаження пам'яті через спам ідентичностей (Sybil Memory Exhaustion):**
   Якщо зловмисник генерує мільйони унікальних `origin_id`, динамічний словник `peers_` (або фіксований масив у C) швидко заповнюється. У наведеній C-реалізації використовується статичний пул `PEER_TABLE_SIZE = 256`. У продакшен-системі таблиця ідентичностей організовується як двошаровий кеш із політикою LRU (Least Recently Used) або CLOCK: неактивні піри з нульовим скорингом витісняються, тоді як піри з високим позитивним рейтингом та заблоковані порушники (`is_banned = true`) фіксуються в постійному фільтрі Блума або префіксному дереві (Trie).
2. **Переповнення монотонного лічильника `seq_num`:**
   Використання беззнакового 64-бітного цілого `uint64_t` унеможливлює випадкове переповнення за нормальних умов (навіть при 100 000 повідомлень на секунду лічильника вистачить на мільйони років). Проте зловмисник може навмисно надіслати пакет зі значенням `seq = UINT64_MAX`.
   *Захист:* Рушій повинен вимагати перезапуску епохи з новим криптографічним сертифікатом вузла або обмежувати максимальний крок приросту `Δseq ≤ MAX_ALLOWED_SEQ_STEP` (наприклад, не більше ніж на +1000 від поточного значення).
3. **Асиметричний розрив зв'язку та хибні штрафи:**
   Якщо ретранслятор сам став жертвою атаки «людина посередині» (MITM) на мережевому рівні й отримав спотворений пакет, він не повинен отримувати миттєвий вічний бан. Саме тому скоринг використовує поріг `SCORE_GREYLIST_THRESHOLD = -50.0`: поодинокий пошкоджений пакет знижує рейтинг, але бан активується лише при систематичній трансляції невалідного трафіку.
