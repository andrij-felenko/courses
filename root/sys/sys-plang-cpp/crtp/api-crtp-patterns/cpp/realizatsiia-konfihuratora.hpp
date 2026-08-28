template <typename Derived>
class NetworkBuilder {
public:
    Derived& set_host(std::string host) & {
        Derived& self = *static_cast<Derived*>(this);
        self.host_ = std::move(host);
        return self;
    }

    Derived&& set_host(std::string host) && {
        Derived& self = *static_cast<Derived*>(this);
        self.host_ = std::move(host);
        return std::move(self);
    }

    Derived& set_port(uint16_t port) & {
        Derived& self = *static_cast<Derived*>(this);
        self.port_ = port;
        return self;
    }
};

class SecureNetworkBuilder : public NetworkBuilder<SecureNetworkBuilder> {
    friend class NetworkBuilder<SecureNetworkBuilder>;
    std::string host_;
    uint16_t port_{80};
    std::string tls_certificate_;

public:
    SecureNetworkBuilder& set_certificate(std::string cert) & {
        tls_certificate_ = std::move(cert);
        return *this;
    }
};
