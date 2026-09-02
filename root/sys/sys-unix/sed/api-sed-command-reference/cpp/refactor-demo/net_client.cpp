// net_client.cpp — ті самі місця виклику після прогону sed/migrate_api.sed.
//
// send_urgent() лишено рівно в тому вигляді, який дає скрипт: типи полів
// структури він не чіпав, тому пара «покажчик, довжина» досі жива й лише
// загортається в span на місці виклику. send_keepalive() показує, куди це
// доводить людина, коли черга доходить і до структур даних.
#include "net_api.hpp"

#include <cstdint>
#include <expected>
#include <iostream>
#include <span>
#include <system_error>

namespace {

// Механічний крок структур не торкався: поля ті самі, що в C-версії.
struct net_frame {
    const std::uint8_t* bytes;
    std::size_t         length;
};

}  // namespace

// Результат механічної заміни: довгий рядок далі розкладає clang-format.
std::expected<std::size_t, std::error_code> send_urgent(net::net_conn& conn,
                                                        net_frame frame) {
    using net::net_send_packet;
    auto rc = net_send_packet(conn,
                              std::span<const std::uint8_t>(frame.bytes, frame.length),
                              { .flags = net::flag_urgent | net::flag_nodelay,
                                .timeout_ms = 500 });
    if (!rc) {
        std::cerr << "net_client: кадр не пішов: " << rc.error().message() << '\n';
    }
    return rc;
}

// Дороблено руками: span уже в самій структурі, окремої довжини немає.
std::expected<std::size_t, std::error_code> send_keepalive(net::net_conn& conn) {
    static constexpr std::uint8_t ping[] = { 0x00 };
    return net_send_packet(conn, std::span{ping}, { .flags = 0, .timeout_ms = 100 });
}
