struct ClonableSource {
    virtual ClonableSource* clone() const = 0;
    virtual ~ClonableSource() = default;
};

struct ClonableSink {
    virtual ClonableSink* clone() const = 0;
    virtual ~ClonableSink() = default;
};

struct ClonableDuplex : public ClonableSource, public ClonableSink {
    // Одне перевизначення задовольняє обидва інтерфейси одночасно:
    ClonableDuplex* clone() const override {
        return new ClonableDuplex(*this);
    }
};
