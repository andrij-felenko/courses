# ⚙️ Практична реалізація рушія Jupiter OT: клієнт-серверна синхронізація тексту

Спільне редагування тексту в реальному часі без затримок інтерфейсу вимагає суворого розподілу обов'язків між клієнтом і сервером. Людина не терпить затримки введення: натискання клавіші повинно миттєво змінювати текст на екрані, ще до того, як пакет із даними полетить мережею до сервера. Одночасно система мусить гарантувати, що чужі правки, зроблені паралельно, не зламають локальний текст і не знищать непідтверджені зміни автора.

У цій роботі реалізовано повнофункціональний симулятор архітектури Jupiter для операцій вставки (`Insert`) та видалення (`Delete`) символів мовами C та C++.

## Архітектурний поділ та протокол взаємодії

Система спирається на зіркоподібну топологію, де всі клієнти спілкуються виключно через центральний сервер-серіалізатор:

1. **Сервер (Jupiter Server):**
   - Зберігає канонічний стан документа та монотонно зростаючий лічильник ревізій `revision` (`0, 1, 2, ...`).
   - Веде журнал застосованих операцій `history`.
   - Приймає від клієнтів операції із зазначенням базової ревізії клієнта `client_rev`.
   - Якщо `client_rev < server_rev`, сервер послідовно трансформує вхідну операцію проти всіх записів у журналі від `client_rev` до `server_rev`.
   - Застосовує трансформовану операцію до канонічного тексту, додає її в `history` і розсилає трансляцію (broadcast) іншим клієнтам.

2. **Клієнт (Jupiter Client):**
   - Зберігає локальну копію документа та номер останньої відомої серверної ревізії `server_revision`.
   - Реалізує трипозиційний автомат станів для керування буферизацією локальних дій.
   - Застосовує власні операції до тексту негайно, але надсилає на сервер не більше однієї операції за раз.

## Три стани клієнтського автомата

Клієнтський рушій перемикається між трьома станами:

```
[ SYNCHRONIZED ]
       │
       │  локальна дія: надіслати op, in_flight = op
       ▼
[ AWAITING_CONFIRM ] ──────── локальна дія ────────► [ AWAITING_CONFIRM_WITH_BUFFER ]
       │                                                       │
       │  отримано ACK                                         │  отримано ACK:
       │  in_flight = noop                                     │  надіслати buffer, in_flight = buffer
       ▼                                                       ▼
[ SYNCHRONIZED ] ◄────────────────────────────────── [ AWAITING_CONFIRM ]
```

1. **`SYNCHRONIZED` (Синхронізовано):**
   - Буфер порожній, жодних непідтверджених операцій у польоті немає.
   - Коли користувач друкує, клієнт застосовує дію локально, зберігає її в `in_flight`, надсилає на сервер і переходить у `AWAITING_CONFIRM`.
   - Якщо надходить чужа операція з сервера, вона безпосередньо застосовується до локального тексту.

2. **`AWAITING_CONFIRM` (Очікування підтвердження):**
   - Операція `in_flight` летить мережею. Клієнт чекає підтвердження від сервера.
   - Якщо користувач друкує новий символ, він застосовується до локального екрана, зберігається в змінній `buffer`, і клієнт переходить у `AWAITING_CONFIRM_WITH_BUFFER`.
   - Якщо надходить чужа операція `srv_op`, клієнт обчислює пару `(srv_op', in_flight') = transform_pair(srv_op, in_flight)`. Трансформована `srv_op'` застосовується до локального тексту, а `in_flight` оновлюється новим значенням `in_flight'`.

3. **`AWAITING_CONFIRM_WITH_BUFFER` (Очікування з буфером):**
   - Одна дія в польоті (`in_flight`), а наступні дії користувача накопичені в локальному `buffer`.
   - Коли надходить підтвердження ACK від сервера, попередня дія вважається зафіксованою. Клієнт бере дію з `buffer`, робить її новою `in_flight`, відправляє на сервер і повертається в стан `AWAITING_CONFIRM`.
   - Якщо приходить чужа операція `srv_op`, вона проходить подвійну трансформацію: спершу крізь `in_flight`, потім крізь `buffer`. Після цього фінальна `srv_op''` застосовується до тексту, а змінні `in_flight` і `buffer` відповідно оновлюються.

## Повна реалізація мовами C та C++

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

#define MAX_DOC_LEN 256
#define MAX_LOG_LEN 128

typedef enum {
    OP_INSERT,
    OP_DELETE,
    OP_NOOP
} OpType;

typedef struct {
    OpType type;
    int pos;
    char ch;
    int client_id;
} Operation;

/* Створення операцій */
Operation op_insert(int pos, char ch, int client_id) {
    Operation op;
    op.type = OP_INSERT;
    op.pos = pos;
    op.ch = ch;
    op.client_id = client_id;
    return op;
}

Operation op_delete(int pos, int client_id) {
    Operation op;
    op.type = OP_DELETE;
    op.pos = pos;
    op.ch = '\0';
    op.client_id = client_id;
    return op;
}

Operation op_noop(void) {
    Operation op;
    op.type = OP_NOOP;
    op.pos = 0;
    op.ch = '\0';
    op.client_id = 0;
    return op;
}

/* Застосування операції до рядкового буфера */
void doc_apply(char *doc, const Operation *op) {
    int len = (int)strlen(doc);
    if (op->type == OP_NOOP) {
        return;
    }
    if (op->type == OP_INSERT) {
        if (op->pos < 0 || op->pos > len || len + 1 >= MAX_DOC_LEN) return;
        memmove(doc + op->pos + 1, doc + op->pos, len - op->pos + 1);
        doc[op->pos] = op->ch;
    } else if (op->type == OP_DELETE) {
        if (op->pos < 0 || op->pos >= len) return;
        memmove(doc + op->pos, doc + op->pos + 1, len - op->pos);
    }
}

/* Попарна трансформація: Inclusion Transformation T(op1, op2) */
void transform_pair(const Operation *op1, const Operation *op2,
                    Operation *out1, Operation *out2) {
    *out1 = *op1;
    *out2 = *op2;

    if (op1->type == OP_NOOP || op2->type == OP_NOOP) {
        return;
    }

    if (op1->type == OP_INSERT && op2->type == OP_INSERT) {
        if (op1->pos < op2->pos || (op1->pos == op2->pos && op1->client_id < op2->client_id)) {
            out2->pos += 1;
        } else {
            out1->pos += 1;
        }
    } else if (op1->type == OP_INSERT && op2->type == OP_DELETE) {
        if (op1->pos <= op2->pos) {
            out2->pos += 1;
        } else {
            out1->pos -= 1;
        }
    } else if (op1->type == OP_DELETE && op2->type == OP_INSERT) {
        if (op1->pos < op2->pos) {
            out2->pos -= 1;
        } else {
            out1->pos += 1;
        }
    } else if (op1->type == OP_DELETE && op2->type == OP_DELETE) {
        if (op1->pos < op2->pos) {
            out2->pos -= 1;
        } else if (op1->pos > op2->pos) {
            out1->pos -= 1;
        } else {
            /* Обидва клієнти видалили один і той самий символ */
            *out1 = op_noop();
            *out2 = op_noop();
        }
    }
}

/* Трансформація одного op відносно іншого: T(op1, op2) */
Operation transform_single(const Operation *op1, const Operation *op2) {
    Operation o1, o2;
    transform_pair(op1, op2, &o1, &o2);
    return o1;
}

/* ── СЕРВЕР JUPITER ────────────────────────────────────────────────────────── */
typedef struct {
    char doc[MAX_DOC_LEN];
    Operation history[MAX_LOG_LEN];
    int revision;
} Server;

void server_init(Server *srv, const char *initial_text) {
    strncpy(srv->doc, initial_text, MAX_DOC_LEN - 1);
    srv->doc[MAX_DOC_LEN - 1] = '\0';
    srv->revision = 0;
}

/* Сервер приймає операцію від клієнта з його базовою ревізією */
Operation server_receive_op(Server *srv, Operation client_op, int client_rev) {
    Operation current_op = client_op;

    /* Трансформація проти всіх операцій, що лягли на сервері після client_rev */
    for (int r = client_rev; r < srv->revision; ++r) {
        current_op = transform_single(&current_op, &srv->history[r]);
    }

    /* Застосування до стану сервера */
    doc_apply(srv->doc, &current_op);

    /* Запис у лог ревізій */
    srv->history[srv->revision] = current_op;
    srv->revision++;

    return current_op;
}

/* ── КЛІЄНТ JUPITER ────────────────────────────────────────────────────────── */
typedef enum {
    STATE_SYNCHRONIZED,
    STATE_AWAITING_CONFIRM,
    STATE_AWAITING_CONFIRM_WITH_BUFFER
} ClientState;

typedef struct {
    int client_id;
    char doc[MAX_DOC_LEN];
    int server_revision;
    ClientState state;
    Operation in_flight;
    Operation buffer;
} Client;

void client_init(Client *cli, int client_id, const char *initial_text) {
    cli->client_id = client_id;
    strncpy(cli->doc, initial_text, MAX_DOC_LEN - 1);
    cli->doc[MAX_DOC_LEN - 1] = '\0';
    cli->server_revision = 0;
    cli->state = STATE_SYNCHRONIZED;
    cli->in_flight = op_noop();
    cli->buffer = op_noop();
}

/* Користувач натиснув клавішу (локальна дія) */
bool client_apply_local(Client *cli, Operation op, Operation *to_send) {
    doc_apply(cli->doc, &op);

    if (cli->state == STATE_SYNCHRONIZED) {
        cli->in_flight = op;
        cli->state = STATE_AWAITING_CONFIRM;
        *to_send = op;
        return true; /* Треба надіслати to_send на сервер */
    } else if (cli->state == STATE_AWAITING_CONFIRM) {
        cli->buffer = op;
        cli->state = STATE_AWAITING_CONFIRM_WITH_BUFFER;
        return false; /* Операція пішла в буфер */
    } else {
        /* Оновлення буфера (у навчальній моделі зберігаємо останню дію) */
        cli->buffer = op;
        return false;
    }
}

/* Клієнт отримав підтвердження своєї операції (ACK) від сервера */
bool client_receive_ack(Client *cli, Operation *to_send) {
    cli->server_revision++;

    if (cli->state == STATE_AWAITING_CONFIRM) {
        cli->state = STATE_SYNCHRONIZED;
        cli->in_flight = op_noop();
        return false;
    } else if (cli->state == STATE_AWAITING_CONFIRM_WITH_BUFFER) {
        cli->in_flight = cli->buffer;
        cli->buffer = op_noop();
        cli->state = STATE_AWAITING_CONFIRM;
        *to_send = cli->in_flight;
        return true; /* Відправляємо буферизовану правку */
    }
    return false;
}

/* Клієнт отримав правку іншого користувача від сервера */
void client_receive_remote_op(Client *cli, Operation srv_op) {
    cli->server_revision++;

    if (cli->state == STATE_SYNCHRONIZED) {
        doc_apply(cli->doc, &srv_op);
    } else if (cli->state == STATE_AWAITING_CONFIRM) {
        Operation srv_prime, in_flight_prime;
        transform_pair(&srv_op, &cli->in_flight, &srv_prime, &in_flight_prime);

        doc_apply(cli->doc, &srv_prime);
        cli->in_flight = in_flight_prime;
    } else if (cli->state == STATE_AWAITING_CONFIRM_WITH_BUFFER) {
        Operation srv_prime, in_flight_prime;
        transform_pair(&srv_op, &cli->in_flight, &srv_prime, &in_flight_prime);
        cli->in_flight = in_flight_prime;

        Operation srv_double_prime, buffer_prime;
        transform_pair(&srv_prime, &cli->buffer, &srv_double_prime, &buffer_prime);
        cli->buffer = buffer_prime;

        doc_apply(cli->doc, &srv_double_prime);
    }
}

/* Тестовий сценарій */
int main(void) {
    Server srv;
    Client cli_a, cli_b;

    server_init(&srv, "CAT");
    client_init(&cli_a, 1, "CAT");
    client_init(&cli_b, 2, "CAT");

    printf("Початковий стан документа: «%s»\n", srv.doc);

    /* 1. Клієнт A локально видаляє 'A' (позиція 1) */
    Operation send_a;
    client_apply_local(&cli_a, op_delete(1, 1), &send_a);
    int rev_a = cli_a.server_revision;

    /* 2. Клієнт B одночасно вставляє 'H' (позиція 0) */
    Operation send_b;
    client_apply_local(&cli_b, op_insert(0, 'H', 2), &send_b);
    int rev_b = cli_b.server_revision;

    printf("Після локальних правок: A = «%s», B = «%s»\n", cli_a.doc, cli_b.doc);

    /* 3. Сервер отримує операцію від A першим */
    Operation srv_a = server_receive_op(&srv, send_a, rev_a);
    printf("Сервер прийняв правку A -> ревізія %d, текст: «%s»\n", srv.revision, srv.doc);

    /* 4. Сервер отримує операцію від B з лагом (rev 0 при поточному rev 1) */
    Operation srv_b = server_receive_op(&srv, send_b, rev_b);
    printf("Сервер прийняв правку B -> ревізія %d, текст: «%s»\n", srv.revision, srv.doc);

    /* 5. Клієнт A отримує ACK для власної правки та трансляцію правки B */
    Operation next_op;
    client_receive_ack(&cli_a, &next_op);
    client_receive_remote_op(&cli_a, srv_b);

    /* 6. Клієнт B отримує трансляцію правки A (до свого ACK) і потім ACK */
    client_receive_remote_op(&cli_b, srv_a);
    client_receive_ack(&cli_b, &next_op);

    printf("\nФінальний результат синхронізації:\n");
    printf("  Сервер:   «%s»\n", srv.doc);
    printf("  Клієнт A: «%s»\n", cli_a.doc);
    printf("  Клієнт B: «%s»\n", cli_b.doc);

    assert(strcmp(srv.doc, "HCT") == 0);
    assert(strcmp(cli_a.doc, "HCT") == 0);
    assert(strcmp(cli_b.doc, "HCT") == 0);

    printf("\nУспіх: усі репліки збіглися до ідентичного тексту «HCT»!\n");
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <optional>
#include <cassert>

enum class OpType {
    Insert,
    Delete,
    NoOp
};

struct Operation {
    OpType type{OpType::NoOp};
    int pos{0};
    char ch{'\0'};
    int client_id{0};

    static Operation make_insert(int pos, char ch, int client_id) {
        return Operation{OpType::Insert, pos, ch, client_id};
    }

    static Operation make_delete(int pos, int client_id) {
        return Operation{OpType::Delete, pos, '\0', client_id};
    }

    static Operation make_noop() {
        return Operation{OpType::NoOp, 0, '\0', 0};
    }
};

/* Застосування операції до рядка */
void doc_apply(std::string &doc, const Operation &op) {
    if (op.type == OpType::NoOp) {
        return;
    }
    if (op.type == OpType::Insert) {
        if (op.pos >= 0 && static_cast<size_t>(op.pos) <= doc.size()) {
            doc.insert(doc.begin() + op.pos, op.ch);
        }
    } else if (op.type == OpType::Delete) {
        if (op.pos >= 0 && static_cast<size_t>(op.pos) < doc.size()) {
            doc.erase(doc.begin() + op.pos);
        }
    }
}

/* Попарна трансформація: Inclusion Transformation T(op1, op2) */
std::pair<Operation, Operation> transform_pair(const Operation &op1, const Operation &op2) {
    Operation out1 = op1;
    Operation out2 = op2;

    if (op1.type == OpType::NoOp || op2.type == OpType::NoOp) {
        return {out1, out2};
    }

    if (op1.type == OpType::Insert && op2.type == OpType::Insert) {
        if (op1.pos < op2.pos || (op1.pos == op2.pos && op1.client_id < op2.client_id)) {
            out2.pos += 1;
        } else {
            out1.pos += 1;
        }
    } else if (op1.type == OpType::Insert && op2.type == OpType::Delete) {
        if (op1.pos <= op2.pos) {
            out2.pos += 1;
        } else {
            out1.pos -= 1;
        }
    } else if (op1.type == OpType::Delete && op2.type == OpType::Insert) {
        if (op1.pos < op2.pos) {
            out2.pos -= 1;
        } else {
            out1.pos += 1;
        }
    } else if (op1.type == OpType::Delete && op2.type == OpType::Delete) {
        if (op1.pos < op2.pos) {
            out2.pos -= 1;
        } else if (op1.pos > op2.pos) {
            out1.pos -= 1;
        } else {
            out1 = Operation::make_noop();
            out2 = Operation::make_noop();
        }
    }

    return {out1, out2};
}

Operation transform_single(const Operation &op1, const Operation &op2) {
    return transform_pair(op1, op2).first;
}

/* ── СЕРВЕР JUPITER ────────────────────────────────────────────────────────── */
class JupiterServer {
public:
    explicit JupiterServer(std::string initial_text)
        : doc_(std::move(initial_text)), revision_(0) {}

    Operation receive_op(Operation client_op, int client_rev) {
        Operation current_op = client_op;

        /* Трансформація проти всіх правок від client_rev до поточної ревізії */
        for (size_t r = client_rev; r < history_.size(); ++r) {
            current_op = transform_single(current_op, history_[r]);
        }

        doc_apply(doc_, current_op);
        history_.push_back(current_op);
        revision_++;

        return current_op;
    }

    [[nodiscard]] const std::string& doc() const noexcept { return doc_; }
    [[nodiscard]] int revision() const noexcept { return revision_; }

private:
    std::string doc_;
    std::vector<Operation> history_;
    int revision_;
};

/* ── КЛІЄНТ JUPITER ────────────────────────────────────────────────────────── */
enum class ClientState {
    Synchronized,
    AwaitingConfirm,
    AwaitingConfirmWithBuffer
};

class JupiterClient {
public:
    JupiterClient(int id, std::string initial_text)
        : id_(id), doc_(std::move(initial_text)), server_revision_(0),
          state_(ClientState::Synchronized) {}

    std::optional<Operation> apply_local(Operation op) {
        doc_apply(doc_, op);

        if (state_ == ClientState::Synchronized) {
            in_flight_ = op;
            state_ = ClientState::AwaitingConfirm;
            return op;
        }
        if (state_ == ClientState::AwaitingConfirm) {
            buffer_ = op;
            state_ = ClientState::AwaitingConfirmWithBuffer;
            return std::nullopt;
        }
        buffer_ = op;
        return std::nullopt;
    }

    std::optional<Operation> receive_ack() {
        server_revision_++;

        if (state_ == ClientState::AwaitingConfirm) {
            state_ = ClientState::Synchronized;
            in_flight_ = Operation::make_noop();
            return std::nullopt;
        }
        if (state_ == ClientState::AwaitingConfirmWithBuffer) {
            in_flight_ = buffer_;
            buffer_ = Operation::make_noop();
            state_ = ClientState::AwaitingConfirm;
            return in_flight_;
        }
        return std::nullopt;
    }

    void receive_remote_op(Operation srv_op) {
        server_revision_++;

        if (state_ == ClientState::Synchronized) {
            doc_apply(doc_, srv_op);
        } else if (state_ == ClientState::AwaitingConfirm) {
            auto [srv_prime, in_flight_prime] = transform_pair(srv_op, in_flight_);
            doc_apply(doc_, srv_prime);
            in_flight_ = in_flight_prime;
        } else if (state_ == ClientState::AwaitingConfirmWithBuffer) {
            auto [srv_prime, in_flight_prime] = transform_pair(srv_op, in_flight_);
            in_flight_ = in_flight_prime;

            auto [srv_double_prime, buffer_prime] = transform_pair(srv_prime, buffer_);
            buffer_ = buffer_prime;

            doc_apply(doc_, srv_double_prime);
        }
    }

    [[nodiscard]] const std::string& doc() const noexcept { return doc_; }
    [[nodiscard]] int server_revision() const noexcept { return server_revision_; }

private:
    int id_;
    std::string doc_;
    int server_revision_;
    ClientState state_;
    Operation in_flight_{Operation::make_noop()};
    Operation buffer_{Operation::make_noop()};
};

int main() {
    JupiterServer server("CAT");
    JupiterClient client_a(1, "CAT");
    JupiterClient client_b(2, "CAT");

    std::cout << "Початковий стан: «" << server.doc() << "»\n";

    /* 1. Клієнт A видаляє символ 'A' (індекс 1) */
    auto to_send_a = client_a.apply_local(Operation::make_delete(1, 1));
    int rev_a = client_a.server_revision();

    /* 2. Клієнт B паралельно вставляє 'H' на початок (індекс 0) */
    auto to_send_b = client_b.apply_local(Operation::make_insert(0, 'H', 2));
    int rev_b = client_b.server_revision();

    std::cout << "Локальні зміни: A = «" << client_a.doc()
              << "», B = «" << client_b.doc() << "»\n";

    /* 3. Сервер обробляє запит A */
    assert(to_send_a.has_value());
    Operation srv_a = server.receive_op(*to_send_a, rev_a);
    std::cout << "Сервер після A -> ревізія " << server.revision()
              << ", текст: «" << server.doc() << "»\n";

    /* 4. Сервер обробляє запізнілий запит B */
    assert(to_send_b.has_value());
    Operation srv_b = server.receive_op(*to_send_b, rev_b);
    std::cout << "Сервер після B -> ревізія " << server.revision()
              << ", текст: «" << server.doc() << "»\n";

    /* 5. Клієнт A отримує ACK та нову подію від B */
    client_a.receive_ack();
    client_a.receive_remote_op(srv_b);

    /* 6. Клієнт B отримує подію від A та власний ACK */
    client_b.receive_remote_op(srv_a);
    client_b.receive_ack();

    std::cout << "\nФінальний результат синхронізації:\n"
              << "  Сервер:   «" << server.doc() << "»\n"
              << "  Клієнт A: «" << client_a.doc() << "»\n"
              << "  Клієнт B: «" << client_b.doc() << "»\n";

    assert(server.doc() == "HCT");
    assert(client_a.doc() == "HCT");
    assert(client_b.doc() == "HCT");

    std::cout << "\nУспіх: усі репліки збіглися до «HCT»!\n";
    return 0;
}
```
:::

## Інженерні нюанси та аналіз складності

1. **Покроковий розбір виконання тестового сценарію:**
   - Початковий рядок на сервері та клієнтах — `CAT`.
   - Клієнт A локально генерує `Del(1)`. Текст на A стає `CT`. Оскільки клієнт A був у стані `SYNCHRONIZED`, операція `Del(1)` записується в `in_flight`, відправляється на сервер із міткою `rev = 0`, а клієнт переходить у стан `AWAITING_CONFIRM`.
   - Клієнт B одночасно генерує `Ins(0, 'H')`. Текст на B стає `HCAT`. Операція `Ins(0, 'H')` записується в `in_flight`, відправляється на сервер із міткою `rev = 0`, а клієнт переходить у стан `AWAITING_CONFIRM`.
   - Сервер першим вичитує сокет від клієнта A. Оскільки базова ревізія клієнта `rev = 0` збігається з поточною ревізією сервера `0`, трансформація не потрібна. Сервер застосовує `Del(1)` до свого тексту, отримує `CT`, записує дію в лог як ревізію 1 і надсилає ACK клієнту A та broadcast клієнту B.
   - Сервер вичитує сокет від клієнта B. Клієнт B заявив базову ревізію `0`, але сервер уже перебуває на ревізії 1. Сервер виконує трансформацію: `T(Ins(0, 'H'), Del(1)) = Ins(0, 'H')`. Трансформована операція застосовується до тексту сервера, утворюючи `HCT`, і записується в лог як ревізія 2.
   - Клієнт A отримує ACK для власної правки (переходить у `SYNCHRONIZED`, ревізія 1), а потім отримує серверну правку ревізії 2 (`Ins(0, 'H')`). Оскільки клієнт у стані `SYNCHRONIZED`, він застосовує її безпосередньо і отримує `HCT`.
   - Клієнт B отримує трансляцію правки A (`Del(1)` на ревізії 1), перебуваючи в стані `AWAITING_CONFIRM`. Клієнт трансформує пару: `(Del(1), Ins(0, 'H'))` перетворюється на `(Del(2), Ins(0, 'H'))`. Клієнт застосовує `Del(2)` до свого тексту `HCAT` і отримує `HCT`, а свою `in_flight` оновлює до `Ins(0, 'H')`. Потім B отримує ACK від сервера і переходить у стан `SYNCHRONIZED`.
   - Текст на сервері та обох клієнтах збігається до `HCT`. Твердження `assert` успішно пройдено.

2. **Часова складність операцій:**
   - Локальне застосування операції до звичайного рядка вимагає зсуву пам'яті `memmove` або перерозподілу вектора із середньою складністю `O(N)`, де `N` — довжина документа. У виробничих системах для великих документів замість плаского масиву використовують структуру **Rope** (дерево рядків) або **Piece Table**, де вставка й видалення виконуються за час `O(log N)`.
   - Обробка серверної трансляції вимагає проходження крізь журнал ревізій із часовою складністю `O(K)`, де `K = server_rev - client_rev` — відставання клієнта. Оскільки в нормальному режимі затримка між вузлами невелика, `K` рідко перевищує кілька одиниць, що робить перерахунок практично миттєвим.

3. **Збирання сміття в журналі ревізій:**
   - Журнал ревізій на сервері не може зростати безкінечно. Сервер відстежує вектор ревізій усіх активних з'єднань і періодично очищає операції, ревізія яких менша за мінімальну активну ревізію `min_client_rev`. Усі нові клієнти, що підключаються після паузи, отримують повний знімок стану (snapshot), а не ланцюжок старих операцій.

4. **Мережевий протокол та відновлення з'єднання:**
   - У реальних веб-застосунках взаємодія клієнта й сервера відбувається через постійне з'єднання WebSocket. Якщо зв'язок обривається (наприклад, ноутбук перейшов у сплячий режим), клієнт накопичує локальні правки в `buffer`.
   - Після відновлення зв'язку клієнт відправляє серверу пакет перевірки `SyncRequest(last_seen_rev)`. Якщо сервер ще зберігає історію від `last_seen_rev`, він відправляє клієнту потік пропущених дельт. Якщо ж журнал уже очищено, клієнт завантажує свіжий snapshot, трансформує свій накопичений `buffer` проти змін, що відбулися за час відсутності, і повторно відправляє свої правки на сервер.
