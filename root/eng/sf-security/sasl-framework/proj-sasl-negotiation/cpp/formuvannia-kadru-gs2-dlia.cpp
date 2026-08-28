class ScramClientHelper {
public:
    static SecureByteVector build_client_first(std::string_view username,
                                               std::string_view client_nonce,
                                               bool use_channel_binding) {
        std::string gs2_hdr = use_channel_binding ? "p=tls-server-end-point,," : "n,,";
        std::string payload = gs2_hdr + "n=" + std::string(username) + ",r=" + std::string(client_nonce);

        SecureByteVector out(payload.size());
        std::memcpy(out.data(), payload.data(), payload.size());
        return out;
    }
};
