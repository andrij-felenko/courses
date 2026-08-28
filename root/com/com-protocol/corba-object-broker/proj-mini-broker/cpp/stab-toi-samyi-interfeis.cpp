enum Completion { COMPLETED_NO, COMPLETED_YES, COMPLETED_MAYBE };
struct SystemException { std::string id; Completion completed; };

class AccountStub : public Account {
    int fd_;
    std::vector<uint8_t> key_;
    uint32_t next_id_ = 1;

    void begin(Out& o, const char* op) {
        put_header(o, MSG_REQUEST);
        o.u32(next_id_++);
        o.u32(static_cast<uint32_t>(key_.size()));
        o.raw(key_.data(), key_.size());
        o.str(op);
    }

    In call(Out& o, std::vector<uint8_t>& reply) {
        finish(o);
        size_t sent = 0;
        if (!write_all(fd_, o.bytes().data(), o.bytes().size(), &sent))
            throw SystemException{"COMM_FAILURE",
                                  sent == 0 ? COMPLETED_NO : COMPLETED_MAYBE};
        if (!recv_message(fd_, reply))
            throw SystemException{"COMM_FAILURE", COMPLETED_MAYBE};   // ось вона

        bool swap = ((reply[6] & 1) != 0) != host_is_little();
        In in(reply.data(), reply.size(), swap);
        in.skip(12);
        in.u32();                                   // номер запиту
        uint32_t status = in.u32();

        if (status == REPLY_USER_EX) {
            std::string id = in.str();
            if (id == "IDL:bank/InsufficientFunds:1.0")
                throw InsufficientFunds{in.i32()};
            throw SystemException{"UNKNOWN", COMPLETED_YES};
        }
        if (status == REPLY_SYS_EX)
            throw SystemException{in.str(), COMPLETED_MAYBE};
        return in;
    }
public:
    AccountStub(int fd, std::vector<uint8_t> key) : fd_(fd), key_(std::move(key)) {}

    int32_t balance() override {
        Out o; begin(o, "balance");
        std::vector<uint8_t> r;
        In in = call(o, r);
        return in.i32();
    }
    void withdraw(int32_t amount) override {
        Out o; begin(o, "withdraw"); o.i32(amount);
        std::vector<uint8_t> r;
        call(o, r);
    }
};
