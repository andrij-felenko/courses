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
