struct ChannelSource {
    virtual ChannelSource* clone() const = 0;
    virtual ~ChannelSource() = default;
};

struct ChannelSink {
    virtual ChannelSink* clone() const = 0;
    virtual ~ChannelSink() = default;
};

struct DuplexChannel : public ChannelSource, public ChannelSink {
    // Одне перевизначення повертає точний тип DuplexChannel*
    DuplexChannel* clone() const override {
        return new DuplexChannel(*this);
    }
};
