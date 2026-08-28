// C++: Безпечний обгортковий метод класу AtomicTransaction
class AtomicTransaction {
    AtomicReqPtr req_;
public:
    AtomicTransaction() : req_(create_atomic_request()) {}

    void add_property(uint32_t obj_id, uint32_t prop_id, uint64_t val) {
        if (::drmModeAtomicAddProperty(req_.get(), obj_id, prop_id, val) < 0) {
            throw std::runtime_error("Не вдалося додати властивість у атомарний запит");
        }
    }
};
