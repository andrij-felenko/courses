// CustomPlugin.cc
CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
    , _options(new CustomOptions(this, this))
{
    // Ворота 2 стартують ЗАЧИНЕНИМИ. Базовий клас ініціалізує це поле в true.
    _showAdvancedUI = false;
    (void) connect(this, &QGCCorePlugin::showAdvancedUIChanged,
                   this, &CustomPlugin::_advancedChanged);
}

QString CustomPlugin::resetParametersToFactory()
{
    // Ті самі ворота ще раз — там, де їх не обійде ні помилка в QML, ні чужий виклик.
    if (!_options->showServiceActions()) {
        return tr("Ця збірка не має сервісних дій.");
    }
    if (!showAdvancedUI()) {
        return tr("Потрібен поглиблений режим.");
    }

    Vehicle *vehicle = MultiVehicleManager::instance()->activeVehicle();
    if (!vehicle) {
        return tr("Апарат не під'єднаний.");
    }
    if (vehicle->armed()) {
        return tr("Апарат зброєний — спершу роззбройте його.");
    }

    vehicle->sendCommand(vehicle->defaultComponentId(),
                         MAV_CMD_PREFLIGHT_STORAGE,
                         true,   // showError: відмову від борту застосунок покаже сам
                         2);     // PREFLIGHT_STORAGE_PARAMETER_ACTION: PARAM_RESET_FACTORY_DEFAULT
    return QString();
}

void CustomPlugin::_advancedChanged(bool advanced)
{
    // Базовий QGCOptions власних сигналів не випромінює — це обов'язок похідного класу.
    emit _options->showFirmwareUpgradeChanged(advanced);
}
