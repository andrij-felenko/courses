bool skipFirstItem = _planType == MAV_MISSION_TYPE_MISSION &&
                     !_vehicle->firmwarePlugin()->sendHomePositionToVehicle();
// …
    if (skipFirstItem) {
        // Home is in sequence 0, remainder of items start at sequence 1
        item->setSequenceNumber(item->sequenceNumber() - 1);
        if (item->command() == MAV_CMD_DO_JUMP) {
            item->setParam1((int)item->param1() - 1);
        }
    }
