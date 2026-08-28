#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <expected>
#include <nftables/libnftables.h>

namespace netfilter {

// Кастомний делетор RAII для безпечного управління контекстом nft_ctx
struct NftCtxDeleter {
    void operator()(struct nft_ctx* ctx) const noexcept {
        if (ctx) {
            nft_ctx_free(ctx);
        }
    }
};

using NftContextPtr = std::unique_ptr<struct nft_ctx, NftCtxDeleter>;

class NftablesManager {
public:
    static std::expected<NftablesManager, std::string> create() {
        struct nft_ctx* raw_ctx = nft_ctx_new(NFT_CTX_DEFAULT);
        if (!raw_ctx) {
            return std::unexpected("Не вдалося створити контекст libnftables");
        }
        
        NftablesManager manager(NftContextPtr(raw_ctx));
        nft_ctx_buffer_output(manager.ctx_.get());
        return manager;
    }

    std::expected<void, std::string> execute(std::string_view commands) {
        // nft_run_cmd_from_buffer очікує null-terminated string
        std::string cmd_str(commands);
        int rc = nft_run_cmd_from_buffer(ctx_.get(), cmd_str.c_str());
        if (rc != 0) {
            return std::unexpected("Помилка виконання команди nftables, код: " + std::to_string(rc));
        }
        return {};
    }

    [[nodiscard]] std::string get_output_buffer() const {
        const char* buf = nft_ctx_get_output_buffer(ctx_.get());
        return buf ? std::string(buf) : std::string();
    }

private:
    explicit NftablesManager(NftContextPtr ctx) : ctx_(std::move(ctx)) {}
    NftContextPtr ctx_;
};

} // namespace netfilter

int main() {
    auto manager_res = netfilter::NftablesManager::create();
    if (!manager_res) {
        std::cerr << "Помилка ініціалізації: " << manager_res.error() << '\n';
        return EXIT_FAILURE;
    }

    auto& manager = manager_res.value();

    constexpr std::string_view rules =
        "flush ruleset\n"
        "add table inet filter_cpp_demo\n"
        "add chain inet filter_cpp_demo input_cpp { type filter hook input priority 0; policy drop; }\n"
        "add rule inet filter_cpp_demo input_cpp ct state invalid drop\n"
        "add rule inet filter_cpp_demo input_cpp ct state established,related accept\n"
        "add rule inet filter_cpp_demo input_cpp iifname \"lo\" accept\n"
        "add rule inet filter_cpp_demo input_cpp tcp dport { 80, 443 } accept\n";

    std::cout << "=== Застосування правил через C++ RAII wrapper ===\n";
    if (auto res = manager.execute(rules); !res) {
        std::cerr << "Не вдалося завантажити правила: " << res.error() << '\n';
        return EXIT_FAILURE;
    }
    std::cout << "Правила успішно завантажено в ядро.\n\n";

    if (auto res = manager.execute("list ruleset\n"); res) {
        std::cout << "=== Поточний Ruleset (C++) ===\n" << manager.get_output_buffer();
    }

    return EXIT_SUCCESS;
}
