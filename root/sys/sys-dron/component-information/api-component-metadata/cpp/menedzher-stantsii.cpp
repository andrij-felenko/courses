ComponentInformationManager* mgr = vehicle->compInfoManager();

// смужка поступу
connect(mgr, &ComponentInformationManager::progressUpdate,
        this, [](float p) { /* 0.0 … 1.0 */ });

CompInfoParam* param = mgr->compInfoParam(MAV_COMP_ID_AUTOPILOT1);
if (param->available()) {                     // адреса опису відома
    FactMetaData* md = param->factMetaDataForName("MPC_XY_P",
                                                  FactMetaData::valueTypeFloat);
    // md->rawUnits(), md->shortDescription(), md->rawMin(), md->rawMax()
}

// що апарат узагалі обіцяв описати
CompInfoGeneral* general = mgr->compInfoGeneral(MAV_COMP_ID_AUTOPILOT1);
if (general && general->isMetaDataTypeSupported(COMP_METADATA_TYPE_ACTUATORS)) {
    // сторінку налаштування двигунів показувати можна
}
