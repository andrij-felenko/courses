class Buffer {
public:
    explicit Buffer(std::string tag) : payload_(std::move(tag)) {}
    const Loud& payload() const&  { return payload_; }             // об'єкт має ім'я
    Loud        payload() &&      { return std::move(payload_); }  // об'єкт тимчасовий
private:
    Loud payload_;
};

static Buffer makeBuffer(std::string tag) { return Buffer(std::move(tag)); }

static void part_ref_qualifier() {
    head("4. Ref-кваліфікатор методу");

    Buffer      named("буфер-із-іменем");
    const Loud& live = named.payload();
    std::cout << "    у живого буфера позичили #" << live.id() << '\n';

    Loud taken = makeBuffer("буфер-тимчасовий").payload();
    std::cout << "    у тимчасового ЗАБРАЛИ #" << taken.id() << '\n';
}
