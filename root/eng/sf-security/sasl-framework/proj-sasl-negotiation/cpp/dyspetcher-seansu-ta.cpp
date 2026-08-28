class SaslClientSession {
public:
    SaslClientSession(std::shared_ptr<ISaslMechanism> mech, SaslCredentials cred)
        : mech_(std::move(mech)), cred_(std::move(cred)), state_(SaslState::Init) {}

    SaslStatus process(std::span<const uint8_t> challenge, SecureByteVector& response) {
        switch (state_) {
        case SaslState::Init: {
            auto status = mech_->client_start(cred_, response);
            if (status == SaslStatus::Ok) {
                state_ = SaslState::Done;
            } else if (status == SaslStatus::Continue) {
                state_ = SaslState::Step;
            } else {
                state_ = SaslState::Fail;
            }
            return status;
        }
        case SaslState::Step: {
            auto status = mech_->client_step(challenge, response);
            if (status == SaslStatus::Ok) {
                state_ = SaslState::Done;
            } else if (status == SaslStatus::Continue) {
                state_ = SaslState::Step;
            } else {
                state_ = SaslState::Fail;
            }
            return status;
        }
        default:
            return SaslStatus::ErrorSyntax;
        }
    }

    [[nodiscard]] SaslState state() const noexcept { return state_; }

private:
    std::shared_ptr<ISaslMechanism> mech_;
    SaslCredentials cred_;
    SaslState state_;
};
