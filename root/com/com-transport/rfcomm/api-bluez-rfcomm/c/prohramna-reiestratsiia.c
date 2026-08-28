#include <bluetooth/bluetooth.h>
#include <bluetooth/sdp.h>
#include <bluetooth/sdp_lib.h>

sdp_session_t *register_spp_service(uint8_t channel, const char *service_name) {
    uuid_t root_uuid, l2cap_uuid, rfcomm_uuid, svc_uuid;
    sdp_list_t *root_list = 0, *l2cap_list = 0, *rfcomm_list = 0, *proto_list = 0, *access_proto_list = 0;
    sdp_data_t *channel_data = 0;

    sdp_record_t *record = sdp_record_alloc();

    // 1. Встановлення класу служби: Serial Port Profile (0x1101)
    sdp_uuid16_create(&svc_uuid, SERIAL_PORT_SVCLASS_ID);
    sdp_set_service_classes(record, sdp_list_append(0, &svc_uuid));

    // 2. Встановлення ідентифікатора кореневої групи (Public Browse Group: 0x1002)
    sdp_uuid16_create(&root_uuid, PUBLIC_BROWSE_GROUP);
    root_list = sdp_list_append(0, &root_uuid);
    sdp_set_browse_groups(record, root_list);

    // 3. Формування стека протоколів: L2CAP (0x0100) -> RFCOMM (0x0003, канал K)
    sdp_uuid16_create(&l2cap_uuid, L2CAP_UUID);
    l2cap_list = sdp_list_append(0, &l2cap_uuid);
    proto_list = sdp_list_append(0, l2cap_list);

    sdp_uuid16_create(&rfcomm_uuid, RFCOMM_UUID);
    channel_data = sdp_data_alloc(SDP_UINT8, &channel);
    rfcomm_list = sdp_list_append(0, &rfcomm_uuid);
    sdp_list_append(rfcomm_list, channel_data);
    sdp_list_append(proto_list, rfcomm_list);

    access_proto_list = sdp_list_append(0, proto_list);
    sdp_set_access_protos(record, access_proto_list);

    // 4. Текстова назва служби
    sdp_set_info_attr(record, service_name, "Provider", "SPP Service Description");

    // 5. Підключення до локального демона SDP та збереження запису
    sdp_session_t *session = sdp_connect(BDADDR_ANY, BDADDR_LOCAL, SDP_RETRY_IF_BUSY);
    sdp_record_register(session, record, 0);

    // Очищення виділених списків структури
    sdp_data_free(channel_data);
    sdp_list_free(l2cap_list, 0);
    sdp_list_free(rfcomm_list, 0);
    sdp_list_free(root_list, 0);
    sdp_list_free(proto_list, 0);
    sdp_list_free(access_proto_list, 0);

    return session; // Зберігати дескриптор сесії відкритим, поки служба працює
}
