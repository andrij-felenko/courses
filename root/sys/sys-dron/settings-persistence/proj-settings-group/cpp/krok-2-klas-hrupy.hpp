#pragma once

#include <QtQmlIntegration/QtQmlIntegration>
#include "SettingsGroup.h"

class PayloadSettings : public SettingsGroup
{
    Q_OBJECT
    QML_ELEMENT
    QML_UNCREATABLE("")

public:
    PayloadSettings(QObject *parent = nullptr);

    DEFINE_SETTING_NAME_GROUP()

    DEFINE_SETTINGFACT(triggerInterval)
    DEFINE_SETTINGFACT(payloadProfile)
    DEFINE_SETTINGFACT(autoStart)
    DEFINE_SETTINGFACT(dumpDirectory)
};
