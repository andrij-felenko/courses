#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <bluetooth/bluetooth.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>

namespace bt {

struct SdpSessionDeleter {
    void operator()(sdp_session_t* s) const noexcept {
        if (s) sdp_close(s);
    }
};

using UniqueSdpSession = std::unique_ptr<sdp_session_t, SdpSessionDeleter>;

std::expected<UniqueSdpSession, std::error_code> register_spp_service(uint8_t channel, std::string_view name) {
    uuid_t root_uuid{}, l2cap_uuid{}, rfcomm_uuid{}, svc_uuid{};
    sdp_record_t* record = sdp_record_alloc();

    sdp_uuid16_create(&svc_uuid, SERIAL_PORT_SVCLASS_ID);
    sdp_set_service_classes(record, sdp_list_append(nullptr, &svc_uuid));

    sdp_uuid16_create(&root_uuid, PUBLIC_BROWSE_GROUP);
    sdp_list_t* root_list = sdp_list_append(nullptr, &root_uuid);
    sdp_set_browse_groups(record, root_list);

    sdp_uuid16_create(&l2cap_uuid, L2CAP_UUID);
    sdp_list_t* l2cap_list = sdp_list_append(nullptr, &l2cap_uuid);
    sdp_list_t* proto_list = sdp_list_append(nullptr, l2cap_list);

    sdp_uuid16_create(&rfcomm_uuid, RFCOMM_UUID);
    sdp_data_t* channel_data = sdp_data_alloc(SDP_UINT8, &channel);
    sdp_list_t* rfcomm_list = sdp_list_append(nullptr, &rfcomm_uuid);
    sdp_list_append(rfcomm_list, channel_data);
    sdp_list_append(proto_list, rfcomm_list);

    sdp_list_t* access_proto_list = sdp_list_append(nullptr, proto_list);
    sdp_set_access_protos(record, access_proto_list);

    std::string name_str(name);
    sdp_set_info_attr(record, name_str.c_str(), "Provider", "SPP Service Description");

    sdp_session_t* raw_session = sdp_connect(BDADDR_ANY, BDADDR_LOCAL, SDP_RETRY_IF_BUSY);
    if (!raw_session) {
        sdp_record_free(record);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    sdp_record_register(raw_session, record, 0);

    sdp_data_free(channel_data);
    sdp_list_free(l2cap_list, nullptr);
    sdp_list_free(rfcomm_list, nullptr);
    sdp_list_free(root_list, nullptr);
    sdp_list_free(proto_list, nullptr);
    sdp_list_free(access_proto_list, nullptr);

    return UniqueSdpSession(raw_session);
}

} // namespace bt
