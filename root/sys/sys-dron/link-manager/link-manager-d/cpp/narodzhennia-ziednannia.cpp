bool LinkManager::createConnectedLink(SharedLinkConfigurationPtr &config)
{
    config->setSuppressAutoReconnect(false);

    SharedLinkInterfacePtr link = nullptr;
    switch (config->type()) {                       // 1. фабрика за типом опису
    case LinkConfiguration::TypeSerial: link = std::make_shared<SerialLink>(config); break;
    case LinkConfiguration::TypeUdp:    link = std::make_shared<UDPLink>(config);    break;
    case LinkConfiguration::TypeTcp:    link = std::make_shared<TCPLink>(config);    break;
    // ... Bluetooth, відтворення логу, тестовий канал
    }
    if (!link) { return false; }

    if (!link->_allocateMavlinkChannel()) {         // 2. канал — ДО з'єднання
        return false;
    }

    // 3. підписатися на сигнали, поки з'єднання ще не потекло
    connect(link.get(), &LinkInterface::bytesReceived, MAVLinkProtocol::instance(), &MAVLinkProtocol::receiveBytes);
    connect(link.get(), &LinkInterface::disconnected,  this, &LinkManager::_linkDisconnected);
    // ... bytesSent, connected, communicationError

    MAVLinkProtocol::instance()->resetMetadataForLink(link.get());

    if (!link->_connect()) {                        // 4. спроба відкрити порт чи сокет
        // повний відкат: відписатися, повернути канал, забути про з'єднання
        disconnect(link.get(), &LinkInterface::bytesReceived, MAVLinkProtocol::instance(), &MAVLinkProtocol::receiveBytes);
        disconnect(link.get(), &LinkInterface::disconnected,  this, &LinkManager::_linkDisconnected);
        // ... решта підписок
        link->_freeMavlinkChannel();
        config->setLink(nullptr);
        return false;
    }

    {                                               // 5. лише тепер — у список
        QMutexLocker locker(&_linksMutex);
        _rgLinks.append(link);
    }
    config->setLink(link);                          // 6. і зв'язати з описом
    return true;
}
