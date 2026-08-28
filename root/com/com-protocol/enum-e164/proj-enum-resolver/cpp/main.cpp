#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <algorithm>
#include <regex>
#include <cstdint>
#include <netinet/in.h>
#include <arpa/nameser.h>
#include <resolv.h>

struct EnumNaptrEntry {
    uint16_t order{0};
    uint16_t preference{0};
    std::string flags;
    std::string services;
    std::string regexp;
    std::string replacement;
};

class ModernEnumResolver {
public:
    // Головний метод: трансляція номера у SIP URI
    static std::optional<std::string> resolvePhoneNumber(std::string_view rawInput) {
        auto canonicalNumber = canonicalizeE164(rawInput);
        if (!canonicalNumber) return std::nullopt;

        auto domainFqdn = buildEnumFqdn(*canonicalNumber);
        if (!domainFqdn) return std::nullopt;

        auto records = performDnsNaptrQuery(*domainFqdn);
        if (records.empty()) return std::nullopt;

        // Сортуємо правила за алгоритмом DDDS: Order -> Preference
        std::sort(records.begin(), records.end(), [](const EnumNaptrEntry& a, const EnumNaptrEntry& b) {
            if (a.order != b.order) return a.order < b.order;
            return a.preference < b.preference;
        });

        // Застосовуємо регулярний вираз першого відповідного правила
        for (const auto& entry : records) {
            if (isSupportedSipService(entry.services) && isTerminalUriRule(entry.flags)) {
                auto resolvedUri = applySedTransformation(entry.regexp, *canonicalNumber);
                if (resolvedUri) return resolvedUri;
            }
        }

        return std::nullopt;
    }

private:
    static std::optional<std::string> canonicalizeE164(std::string_view input) {
        if (input.empty() || input.front() != '+') return std::nullopt;

        std::string digits;
        digits.reserve(16);
        for (size_t i = 1; i < input.size(); ++i) {
            char c = input[i];
            if (std::isdigit(static_cast<unsigned char>(c))) {
                if (digits.size() >= 15) return std::nullopt;
                digits.push_back(c);
            } else if (c != ' ' && c != '-' && c != '(' && c != ')') {
                return std::nullopt;
            }
        }
        if (digits.size() < 3) return std::nullopt;
        return "+" + digits;
    }

    static std::optional<std::string> buildEnumFqdn(std::string_view canonicalNumber) {
        if (canonicalNumber.size() < 4 || canonicalNumber.front() != '+') return std::nullopt;
        std::string fqdn;
        fqdn.reserve(canonicalNumber.size() * 2 + 16);

        // Інверсія цифр із розділенням крапками
        for (auto it = canonicalNumber.rbegin(); it != canonicalNumber.rend() - 1; ++it) {
            fqdn.push_back(*it);
            fqdn.push_back('.');
        }
        fqdn += "e164.arpa";
        return fqdn;
    }

    static bool isSupportedSipService(std::string_view services) {
        return services.find("E2U+sip") != std::string_view::npos ||
               services.find("E2U+voice:sip") != std::string_view::npos;
    }

    static bool isTerminalUriRule(std::string_view flags) {
        return flags.find('u') != std::string_view::npos ||
               flags.find('U') != std::string_view::npos;
    }

    static std::vector<EnumNaptrEntry> performDnsNaptrQuery(const std::string& fqdn) {
        std::vector<EnumNaptrEntry> results;
        std::vector<uint8_t> buffer(4096);

        int bytesReceived = res_query(fqdn.c_str(), C_IN, T_NAPTR, buffer.data(), static_cast<int>(buffer.size()));
        if (bytesReceived < static_cast<int>(sizeof(HEADER))) return results;

        ns_msg handle;
        if (ns_initparse(buffer.data(), bytesReceived, &handle) < 0) return results;

        int answerCount = ns_msg_count(handle, ns_s_an);
        for (int i = 0; i < answerCount; ++i) {
            ns_rr resourceRecord;
            if (ns_parserr(&handle, ns_s_an, i, &resourceRecord) < 0) continue;
            if (ns_rr_type(resourceRecord) != T_NAPTR) continue;

            const uint8_t* rdataPtr = ns_rr_rdata(resourceRecord);
            const uint8_t* rdataEnd = rdataPtr + ns_rr_rdlen(resourceRecord);
            if (rdataEnd - rdataPtr < 7) continue;

            EnumNaptrEntry entry;
            entry.order = ns_get16(rdataPtr); rdataPtr += 2;
            entry.preference = ns_get16(rdataPtr); rdataPtr += 2;

            auto readPascalString = [](const uint8_t*& ptr, const uint8_t* limit) -> std::string {
                if (ptr >= limit) return {};
                uint8_t strLen = *ptr++;
                if (ptr + strLen > limit) return {};
                std::string s(reinterpret_cast<const char*>(ptr), strLen);
                ptr += strLen;
                return s;
            };

            entry.flags = readPascalString(rdataPtr, rdataEnd);
            entry.services = readPascalString(rdataPtr, rdataEnd);
            entry.regexp = readPascalString(rdataPtr, rdataEnd);

            char decompressedHost[256];
            if (ns_name_uncompress(buffer.data(), buffer.data() + bytesReceived, rdataPtr, decompressedHost, sizeof(decompressedHost)) >= 0) {
                entry.replacement = decompressedHost;
            }

            results.push_back(std::move(entry));
        }

        return results;
    }

    static std::optional<std::string> applySedTransformation(std::string_view sedExpr, std::string_view canonicalPhone) {
        if (sedExpr.size() < 3) return std::nullopt;
        char delim = sedExpr.front();

        auto p1 = sedExpr.find(delim, 1);
        if (p1 == std::string_view::npos) return std::nullopt;
        auto p2 = sedExpr.find(delim, p1 + 1);
        if (p2 == std::string_view::npos) return std::nullopt;

        std::string pattern(sedExpr.substr(1, p1 - 1));
        std::string replacement(sedExpr.substr(p1 + 1, p2 - p1 - 1));
        std::string flags(sedExpr.substr(p2 + 1));

        std::regex_constants::syntax_option_type regexOptions = std::regex_constants::ECMAScript;
        if (flags.find('i') != std::string::npos || flags.find('I') != std::string::npos) {
            regexOptions |= std::regex_constants::icase;
        }

        try {
            std::regex re(pattern, regexOptions);
            std::smatch matchResults;
            std::string phoneString(canonicalPhone);
            if (!std::regex_search(phoneString, matchResults, re)) return std::nullopt;

            std::string outputUri;
            outputUri.reserve(128);
            for (size_t i = 0; i < replacement.size(); ++i) {
                if (replacement[i] == '\\' && i + 1 < replacement.size() && std::isdigit(static_cast<unsigned char>(replacement[i + 1]))) {
                    size_t groupIndex = replacement[i + 1] - '0';
                    if (groupIndex < matchResults.size()) {
                        outputUri += matchResults[groupIndex].str();
                    }
                    ++i;
                } else {
                    outputUri.push_back(replacement[i]);
                }
            }
            return outputUri;
        } catch (const std::regex_error&) {
            return std::nullopt;
        }
    }
};
