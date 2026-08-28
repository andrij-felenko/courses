#include <array>
#include <vector>
#include <optional>
#include <span>
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <utility>

class DoubleRatchetSession {
public:
    static constexpr size_t KeySize = 32;
    static constexpr size_t MaxSkippedKeys = 64;
    static constexpr size_t MaxForwardSteps = 256;

    using Key = std::array<uint8_t, KeySize>;

    struct Header {
        Key      dh_pub{};
        uint32_t pn{0};
        uint32_t n{0};
    };

    struct KeyPair {
        Key priv{};
        Key pub{};

        ~KeyPair() {
            volatile uint8_t *p = priv.data();
            for (size_t i = 0; i < KeySize; ++i) p[i] = 0;
        }
    };

    DoubleRatchetSession(const Key &shared_key, const std::optional<Key> &peer_dh_pub, bool is_alice)
        : rk_(shared_key) {
        for (size_t i = 0; i < KeySize; ++i) {
            dhs_.priv[i] = static_cast<uint8_t>(i + (is_alice ? 1 : 2));
            dhs_.pub[i]  = static_cast<uint8_t>(dhs_.priv[i] ^ 0xAA);
        }

        if (is_alice && peer_dh_pub.has_value()) {
            dhr_ = *peer_dh_pub;
            auto dh_secret = dh(dhs_.priv, *dhr_);
            auto [new_rk, new_cks] = kdf_rk(rk_, dh_secret);
            rk_  = new_rk;
            cks_ = new_cks;
        }
    }

    ~DoubleRatchetSession() {
        wipe(rk_);
        wipe(cks_);
        wipe(ckr_);
    }

    // Шифрування повідомлення
    std::pair<Header, Key> encrypt_step() {
        auto [next_cks, mk] = kdf_ck(cks_);
        cks_ = next_cks;

        Header hdr{
            .dh_pub = dhs_.pub,
            .pn     = pn_,
            .n      = ns_++
        };
        return {hdr, mk};
    }

    // Дешифрування повідомлення
    Key decrypt_step(const Header &hdr) {
        // 1. Пошук у таблиці пропущених ключів
        auto it = std::find_if(skipped_keys_.begin(), skipped_keys_.end(), [&](const SkippedKey &sk) {
            return sk.n == hdr.n && sk.dh_pub == hdr.dh_pub;
        });

        if (it != skipped_keys_.end()) {
            Key mk = it->mk;
            wipe(it->mk);
            skipped_keys_.erase(it);
            return mk;
        }

        // 2. Асиметричний крок при новому відкритому ключі
        if (!dhr_.has_value() || *dhr_ != hdr.dh_pub) {
            if (dhr_.has_value()) {
                skip_keys(hdr.pn);
            }

            dhr_ = hdr.dh_pub;
            auto dh_secret = dh(dhs_.priv, *dhr_);
            auto [rk1, ckr_new] = kdf_rk(rk_, dh_secret);
            rk_  = rk1;
            ckr_ = ckr_new;

            // Оновлюємо нашу локальну пару для наступних відповідей
            for (size_t i = 0; i < KeySize; ++i) {
                dhs_.priv[i] = static_cast<uint8_t>(dhs_.priv[i] + 1);
                dhs_.pub[i]  = static_cast<uint8_t>(dhs_.priv[i] ^ 0xAA);
            }

            auto dh_secret_send = dh(dhs_.priv, *dhr_);
            auto [rk2, cks_new] = kdf_rk(rk_, dh_secret_send);
            rk_  = rk2;
            cks_ = cks_new;

            pn_ = ns_;
            ns_ = 0;
            nr_ = 0;
        }

        // 3. Перемотування поточного ланцюга
        skip_keys(hdr.n);

        // 4. Отримання ключа
        auto [next_ckr, mk] = kdf_ck(ckr_);
        ckr_ = next_ckr;
        nr_++;
        return mk;
    }

private:
    struct SkippedKey {
        Key      dh_pub;
        uint32_t n;
        Key      mk;
    };

    KeyPair               dhs_{};
    std::optional<Key>    dhr_{std::nullopt};
    Key                   rk_{};
    Key                   cks_{};
    Key                   ckr_{};
    uint32_t              ns_{0};
    uint32_t              nr_{0};
    uint32_t              pn_{0};
    std::vector<SkippedKey> skipped_keys_{};

    static void wipe(Key &k) {
        volatile uint8_t *p = k.data();
        for (size_t i = 0; i < KeySize; ++i) p[i] = 0;
    }

    static Key dh(const Key &priv, const Key &pub) {
        Key out{};
        for (size_t i = 0; i < KeySize; ++i) out[i] = static_cast<uint8_t>(priv[i] ^ pub[i]);
        return out;
    }

    static std::pair<Key, Key> kdf_rk(const Key &rk, const Key &dh_out) {
        Key next_rk{}, next_ck{};
        for (size_t i = 0; i < KeySize; ++i) {
            next_rk[i] = static_cast<uint8_t>(rk[i] ^ dh_out[i] ^ 0x01);
            next_ck[i] = static_cast<uint8_t>(rk[i] ^ dh_out[i] ^ 0x02);
        }
        return {next_rk, next_ck};
    }

    static std::pair<Key, Key> kdf_ck(const Key &ck) {
        Key next_ck{}, mk{};
        for (size_t i = 0; i < KeySize; ++i) {
            mk[i]      = static_cast<uint8_t>(ck[i] ^ 0x11);
            next_ck[i] = static_cast<uint8_t>(ck[i] ^ 0x22);
        }
        return {next_ck, mk};
    }

    void skip_keys(uint32_t until) {
        if (nr_ + MaxForwardSteps < until) {
            throw std::runtime_error("Message jump exceeds MaxForwardSteps");
        }
        while (nr_ < until) {
            auto [next_ckr, mk] = kdf_ck(ckr_);
            ckr_ = next_ckr;
            if (skipped_keys_.size() >= MaxSkippedKeys) {
                throw std::runtime_error("Skipped keys table overflow");
            }
            skipped_keys_.push_back({*dhr_, nr_, mk});
            nr_++;
        }
    }
};
