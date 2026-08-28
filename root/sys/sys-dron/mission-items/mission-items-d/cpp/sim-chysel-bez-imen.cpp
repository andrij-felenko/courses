mavlink_msg_mission_item_int_pack_chan(
    MAVLinkProtocol::instance()->getSystemId(),
    MAVLinkProtocol::getComponentId(),
    sharedLink->mavlinkChannel(),
    &messageOut,
    _vehicle->id(),                 // кому: система апарата
    MAV_COMP_ID_AUTOPILOT1,         // кому: компонент-автопілот
    missionRequestSeq,              // seq — номер, який попросив борт
    item->frame(),
    item->command(),
    missionRequestSeq == 0,         // current: лише нульовий елемент
    item->autoContinue(),
    item->param1(), item->param2(), item->param3(), item->param4(),
    item->frame() == MAV_FRAME_MISSION ? item->param5() : item->param5() * 1e7,
    item->frame() == MAV_FRAME_MISSION ? item->param6() : item->param6() * 1e7,
    item->param7(),
    _planType);
