struct InsufficientFunds { int32_t shortfall; };

class Account {                                   // спільний контракт обох сторін
public:
    virtual ~Account() = default;
    virtual int32_t balance() = 0;
    virtual void withdraw(int32_t amount) = 0;
};

class AccountImpl : public Account {              // сервант: звичайний клас C++
    int32_t balance_;
public:
    explicit AccountImpl(int32_t start) : balance_(start) {}
    int32_t balance() override { return balance_; }
    void withdraw(int32_t amount) override {
        if (amount > balance_) throw InsufficientFunds{amount - balance_};
        balance_ -= amount;
    }
};

class AccountSkeleton {
    Account* servant_;
public:
    explicit AccountSkeleton(Account* s) : servant_(s) {}

    void invoke(const std::string& op, In& in, Out& reply) {
        if (op == "balance") {
            int32_t v = servant_->balance();
            reply.u32(REPLY_OK);
            reply.i32(v);
        } else if (op == "withdraw") {
            int32_t amount = in.i32();            // читаємо строго за контрактом
            try {
                servant_->withdraw(amount);
                reply.u32(REPLY_OK);
            } catch (const InsufficientFunds& e) {
                reply.u32(REPLY_USER_EX);
                reply.str("IDL:bank/InsufficientFunds:1.0");
                reply.i32(e.shortfall);
            }
        } else {
            reply.u32(REPLY_SYS_EX);
            reply.str("BAD_OPERATION");
        }
    }
};
