void CustomPlugin::adjustSettingMetaData(const QString &settingsGroup,
                                         FactMetaData &metaData, bool &userVisible)
{
    QGCCorePlugin::adjustSettingMetaData(settingsGroup, metaData, userVisible);  // не з'їдай базові правки

    if (settingsGroup == AppSettings::settingsGroup) {
        if (metaData.name() == AppSettings::offlineEditingFirmwareClassName) {
            metaData.setRawDefaultValue(QGCMAVLink::FirmwareClassPX4);
            userVisible = false;   // клас прошивки в цій збірці один і назавжди
            return;
        }
    }
}
