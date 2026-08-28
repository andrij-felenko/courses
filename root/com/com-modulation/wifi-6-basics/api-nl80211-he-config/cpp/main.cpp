#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <stdexcept>
#include <system_error>
#include <cstdint>
#include <net/if.h>

#include <netlink/netlink.h>
#include <netlink/genl/genl.h>
#include <netlink/genl/ctrl.h>
#include <linux/nl80211.h>

// RAII обгортка для Netlink сокета
class NlSocket {
public:
    NlSocket() : sock_(nl_socket_alloc(), nl_socket_free) {
        if (!sock_) {
            throw std::bad_alloc();
        }
        if (genl_connect(sock_.get()) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося з'єднатися з genl");
        }
    }

    struct nl_sock* get() const noexcept { return sock_.get(); }

private:
    std::unique_ptr<struct nl_sock, void(*)(struct nl_sock*)> sock_;
};

// RAII обгортка для повідомлення Netlink
class NlMessage {
public:
    NlMessage() : msg_(nlmsg_alloc(), nlmsg_free) {
        if (!msg_) {
            throw std::bad_alloc();
        }
    }

    struct nl_msg* get() const noexcept { return msg_.get(); }

private:
    std::unique_ptr<struct nl_msg, void(*)(struct nl_msg*)> msg_;
};

struct Wifi6Status {
    bool has_he_support{false};
    int bss_color{-1};
    uint32_t frequency_mhz{0};
};

class Wifi6NlClient {
public:
    Wifi6NlClient() : family_id_(genl_ctrl_resolve(sock_.get(), "nl80211")) {
        if (family_id_ < 0) {
            throw std::runtime_error("Модуль nl80211 не знайдено у ядрі");
        }
    }

    Wifi6Status query_interface(std::string_view ifname) {
        Wifi6Status status{};
        NlMessage msg;

        genlmsg_put(msg.get(), NL_AUTO_PID, NL_AUTO_SEQ, family_id_, 0, 0,
                   NL80211_CMD_GET_INTERFACE, 0);

        const unsigned int ifindex = if_nametoindex(ifname.data());
        if (ifindex == 0) {
            throw std::system_error(errno, std::generic_category(), "Невірний інтерфейс");
        }

        nla_put_u32(msg.get(), NL80211_ATTR_IFINDEX, ifindex);

        nl_socket_modify_cb(sock_.get(), NL_CB_VALID, NL_CB_CUSTOM,
            [](struct nl_msg* msg_ptr, void* arg) -> int {
                auto* st = static_cast<Wifi6Status*>(arg);
                struct nlmsghdr* nlh = nlmsg_hdr(msg_ptr);
                struct genlmsghdr* gnlh = static_cast<struct genlmsghdr*>(nlmsg_data(nlh));
                struct nlattr* tb[NL80211_ATTR_MAX + 1];

                nla_parse(tb, NL80211_ATTR_MAX, genlmsg_attrdata(gnlh, 0),
                          genlmsg_attrlen(gnlh, 0), nullptr);

                if (tb[NL80211_ATTR_BSS_COLOR]) {
                    st->bss_color = nla_get_u8(tb[NL80211_ATTR_BSS_COLOR]);
                }
                if (tb[NL80211_ATTR_HE_CAPABILITY]) {
                    st->has_he_support = true;
                }
                if (tb[NL80211_ATTR_WIPHY_FREQ]) {
                    st->frequency_mhz = nla_get_u32(tb[NL80211_ATTR_WIPHY_FREQ]);
                }
                return NL_SKIP;
            }, &status);

        if (nl_send_auto(sock_.get(), msg.get()) < 0) {
            throw std::runtime_error("Помилка відправки Netlink запиту");
        }

        nl_recvmsgs_default(sock_.get());
        return status;
    }

private:
    NlSocket sock_;
    int family_id_;
};

int main() {
    try {
        Wifi6NlClient client;
        auto status = client.query_interface("wlan0");

        std::cout << "--- Статус 802.11ax (mac80211) ---
";
        std::cout << "Підтримка HE: " << (status.has_he_support ? "ТАК" : "НІ") << "
";
        if (status.frequency_mhz > 0) {
            std::cout << "Частота каналу: " << status.frequency_mhz << " МГц
";
        }
        if (status.bss_color >= 0) {
            std::cout << "BSS Color: " << status.bss_color << "
";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "
";
        return 1;
    }
    return 0;
}
