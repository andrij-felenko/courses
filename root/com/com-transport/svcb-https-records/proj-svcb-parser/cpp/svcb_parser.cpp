// svcb_parser.cpp — Ідіоматичний парсер RDATA записів SVCB/HTTPS (RFC 9460) на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <expected>
#include <cstdint>
#include <cstring>
#include <array>

#if defined(_WIN32)
#include <winsock2.h>
#include <ws2tcpip.h>
#else
#include <arpa/inet.h>
#endif

enum class SvcParamKey : uint16_t {
    Mandatory      = 0,
    Alpn           = 1,
    NoDefaultAlpn  = 2,
    Port           = 3,
    Ipv4Hint       = 4,
    Ech            = 5,
    Ipv6Hint       = 6,
    DohPath        = 7
};

enum class ParseError {
    Truncated,
    InvalidName,
    CompressionNotAllowed,
    AliasHasParams,
    KeysNotSorted,
    DuplicateKey,
    InvalidParamLength,
    MandatoryViolation
};

struct SvcRecord {
    uint16_t priority{0};
    bool is_alias_mode{false};
    std::string target_name;
    
    uint16_t port{443};
    bool no_default_alpn{false};
    std::vector<std::string> alpns;
    std::vector<in_addr> ipv4_hints;
    std::vector<in6_addr> ipv6_hints;
    std::vector<uint8_t> ech_config;
    std::vector<uint16_t> mandatory_keys;
};

class SvcParser {
public:
    static std::expected<SvcRecord, ParseError> parse(std::span<const uint8_t> rdata) {
        if (rdata.size() < 3) {
            return std::unexpected(ParseError::Truncated);
        }
        
        SvcRecord rec;
        size_t offset = 0;
        
        // 1. Читання SvcPriority (uint16 big-endian)
        rec.priority = static_cast<uint16_t>((rdata[0] << 8) | rdata[1]);
        offset += 2;
        rec.is_alias_mode = (rec.priority == 0);
        
        // 2. Читання TargetName
        auto name_res = parse_name(rdata, offset);
        if (!name_res) return std::unexpected(name_res.error());
        
        rec.target_name = std::move(*name_res);
        
        if (rec.is_alias_mode) {
            if (rec.target_name == ".") {
                return std::unexpected(ParseError::InvalidName);
            }
            if (offset < rdata.size()) {
                return std::unexpected(ParseError::AliasHasParams);
            }
            return rec;
        }
        
        // 3. Читання SvcParams
        int32_t last_key = -1;
        while (offset < rdata.size()) {
            if (offset + 4 > rdata.size()) {
                return std::unexpected(ParseError::Truncated);
            }
            
            uint16_t raw_key = static_cast<uint16_t>((rdata[offset] << 8) | rdata[offset + 1]);
            uint16_t val_len = static_cast<uint16_t>((rdata[offset + 2] << 8) | rdata[offset + 3]);
            offset += 4;
            
            if (offset + val_len > rdata.size()) {
                return std::unexpected(ParseError::Truncated);
            }
            
            if (static_cast<int32_t>(raw_key) <= last_key) {
                return std::unexpected(raw_key == static_cast<uint16_t>(last_key) 
                    ? ParseError::DuplicateKey : ParseError::KeysNotSorted);
            }
            last_key = static_cast<int32_t>(raw_key);
            
            auto val_span = rdata.subspan(offset, val_len);
            auto err = parse_param(static_cast<SvcParamKey>(raw_key), val_span, rec);
            if (err != ParseError::Truncated && err != ParseError::InvalidName) {
                if (err != static_cast<ParseError>(0)) {
                    return std::unexpected(err);
                }
            }
            
            offset += val_len;
        }
        
        return rec;
    }

private:
    static std::expected<std::string, ParseError> parse_name(std::span<const uint8_t> buf, size_t &offset) {
        std::string result;
        size_t pos = offset;
        
        while (pos < buf.size()) {
            uint8_t len = buf[pos++];
            if ((len & 0xC0) != 0) {
                return std::unexpected(ParseError::CompressionNotAllowed);
            }
            if (len == 0) {
                offset = pos;
                return result.empty() ? "." : result;
            }
            if (pos + len > buf.size()) {
                return std::unexpected(ParseError::Truncated);
            }
            if (!result.empty()) result += '.';
            result.append(reinterpret_cast<const char*>(&buf[pos]), len);
            pos += len;
        }
        return std::unexpected(ParseError::Truncated);
    }
    
    static ParseError parse_param(SvcParamKey key, std::span<const uint8_t> val, SvcRecord &rec) {
        switch (key) {
            case SvcParamKey::Mandatory: {
                if (val.size() % 2 != 0) return ParseError::InvalidParamLength;
                for (size_t i = 0; i < val.size(); i += 2) {
                    rec.mandatory_keys.push_back(static_cast<uint16_t>((val[i] << 8) | val[i+1]));
                }
                break;
            }
            case SvcParamKey::Alpn: {
                size_t v_off = 0;
                while (v_off < val.size()) {
                    uint8_t slen = val[v_off++];
                    if (v_off + slen > val.size()) return ParseError::InvalidParamLength;
                    rec.alpns.emplace_back(reinterpret_cast<const char*>(&val[v_off]), slen);
                    v_off += slen;
                }
                break;
            }
            case SvcParamKey::NoDefaultAlpn:
                if (!val.empty()) return ParseError::InvalidParamLength;
                rec.no_default_alpn = true;
                break;
                
            case SvcParamKey::Port:
                if (val.size() != 2) return ParseError::InvalidParamLength;
                rec.port = static_cast<uint16_t>((val[0] << 8) | val[1]);
                break;
                
            case SvcParamKey::Ipv4Hint: {
                if (val.size() % 4 != 0) return ParseError::InvalidParamLength;
                for (size_t i = 0; i < val.size(); i += 4) {
                    in_addr addr;
                    std::memcpy(&addr.s_addr, &val[i], 4);
                    rec.ipv4_hints.push_back(addr);
                }
                break;
            }
            case SvcParamKey::Ipv6Hint: {
                if (val.size() % 16 != 0) return ParseError::InvalidParamLength;
                for (size_t i = 0; i < val.size(); i += 16) {
                    in6_addr addr;
                    std::memcpy(&addr.s6_addr, &val[i], 16);
                    rec.ipv6_hints.push_back(addr);
                }
                break;
            }
            case SvcParamKey::Ech:
                rec.ech_config.assign(val.begin(), val.end());
                break;
                
            default:
                break;
        }
        return static_cast<ParseError>(0);
    }
};
