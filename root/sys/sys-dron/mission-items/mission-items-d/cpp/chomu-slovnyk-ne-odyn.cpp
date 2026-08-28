for (const MAV_CMD command: cmdList->commandIds()) {
    MissionCommandUIInfo *const uiInfo = cmdList->getUIInfo(command);
    if (uiInfo) {
        if (collapsedTree.contains(command)) {
            collapsedTree[command]->_overrideInfo(uiInfo);   // команда вже є — перекриваємо ключі
        } else {
            collapsedTree[command] = new MissionCommandUIInfo(*uiInfo);  // команда нова — беремо цілком
        }
    }
}
