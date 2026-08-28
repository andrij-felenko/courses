namespace sev {

struct alignas(8) snp_guest_request_ioctl {
    uint8_t msg_version{1};
    uint64_t req_data{0};
    uint64_t resp_data{0};
    uint64_t fw_error{0};
};

struct snp_report_req {
    std::array<uint8_t, 64> user_data{};
    uint32_t vmpl{0};
    std::array<uint8_t, 28> rsvd{};
};

struct snp_report_resp {
    std::array<uint8_t, 4000> data{};
};

} // namespace sev
