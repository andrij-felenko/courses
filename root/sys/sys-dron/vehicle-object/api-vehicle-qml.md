# 📋 Інтерфейс Vehicle: властивості, групи фактів, викличні методи, сигнали

Тут зібрано повний перелік того, що клас `Vehicle` віддає назовні — кожну властивість із типом, правом запису й сигналом-сповіщенням, усі вкладені групи фактів разом із повідомленням, з якого вони наповнюються, усі методи керування із сигнатурами та сигнали, на які підписуються. Довідка потрібна, щоб знайти вже готове значення замість того, щоб додавати своє, і щоб наперед знати, чи прив'язка взагалі оновиться.

Звірено з гілкою `master` репозиторію `mavlink/qgroundcontrol` 1 серпня 2026 року; чинна стабільна лінія на той час — 5.0.x. Файли: `src/Vehicle/Vehicle.h`, `src/Vehicle/Vehicle.cc`, `src/Vehicle/VehicleTypes.h`, `src/Vehicle/MavCommandQueue.{h,cc}`, `src/Vehicle/FactGroups/*`, `src/FactSystem/Fact.h`, `src/FactSystem/FactGroup.h`.

---

## Як дістатися до об'єкта

```cpp
class Vehicle : public VehicleFactGroup, public VehicleTypes
{
    Q_OBJECT
    QML_ELEMENT
    QML_UNCREATABLE("")
```

`QML_UNCREATABLE` означає, що створити апарат із QML не можна взагалі — тільки взяти вже наявний. Усі точки входу дає `MultiVehicleManager`, доступний у QML як `QGroundControl.multiVehicleManager`:

| Вхід | Тип | Сповіщення | Що дає |
|---|---|---|---|
| `activeVehicle` | `Vehicle*` | `activeVehicleChanged` | апарат, чиї показники зараз на екрані; **буває `null`** |
| `activeVehicleAvailable` | `bool` | `activeVehicleAvailableChanged` | чи є взагалі активний апарат |
| `parameterReadyVehicleAvailable` | `bool` | `parameterReadyVehicleAvailableChanged` | активний апарат є **і** його параметри вже завантажено |
| `vehicles` | `QmlObjectListModel*` | `CONSTANT` | усі відомі апарати |
| `selectedVehicles` | `QmlObjectListModel*` | `CONSTANT` | підмножина, позначена користувачем |
| `offlineEditingVehicle` | `Vehicle*` | `CONSTANT` | несправжній апарат для редагування плану без зв'язку |
| `getVehicleById(int)` | `Q_INVOKABLE Vehicle*` | — | пошук за sysid |

`activeVehicle` записуваний і з QML (`WRITE setActiveVehicle`), а сам список апаратів змінюється сигналами `vehicleAdded(Vehicle*)` / `vehicleRemoved(Vehicle*)`. Що робить менеджер із кількома апаратами водночас — у [темі про кілька апаратів](topic:sys-dron/multi-vehicle).

Перша перевірка в будь-якій прив'язці — саме `null`, бо застосунок стартує без жодного апарата:

```qml
property var _vehicle: QGroundControl.multiVehicleManager.activeVehicle
text: _vehicle ? _vehicle.flightMode : qsTr("Не під'єднано")
```

---

## Властивості: тотожність, прошивка, тип

| Q_PROPERTY | Тип | Запис | Сповіщення | Звідки |
|---|---|---|---|---|
| `id` | `int` | ні | `CONSTANT` | sysid, заданий у конструкторі; незмінний до смерті об'єкта |
| `vehicleUID` | `quint64` | ні | `vehicleUIDChanged` | унікальний ідентифікатор апарата з `AUTOPILOT_VERSION` |
| `vehicleUIDStr` | `QString` | ні | `vehicleUIDChanged` | ті самі вісім байтів, розписані шістнадцятково побайтово |
| `firmwareMajorVersion` | `int` | ні | `firmwareVersionChanged` | `AUTOPILOT_VERSION`; поки не прийшло — `versionNotSetValue`, тобто `-1` |
| `firmwareMinorVersion` | `int` | ні | `firmwareVersionChanged` | те саме |
| `firmwarePatchVersion` | `int` | ні | `firmwareVersionChanged` | те саме |
| `firmwareVersionType` | `int` | ні | `firmwareVersionChanged` | `FIRMWARE_VERSION_TYPE_*` |
| `firmwareVersionTypeString` | `QString` | ні | `firmwareVersionChanged` | той самий тип словами |
| `firmwareCustomMajorVersion` та ще дві | `int` | ні | `firmwareCustomVersionChanged` | версія вендорської прошивки, окрема від штатної |
| `gitHash` | `QString` | ні | `gitHashChanged` | хеш збірки автопілота |
| `firmwareTypeString` | `QString` | ні | `firmwareTypeChanged` | `MAV_AUTOPILOT` словами |
| `px4Firmware`, `apmFirmware`, `genericFirmware` | `bool` | ні | `firmwareTypeChanged` (`genericFirmware` — `CONSTANT`) | клас прошивки з heartbeat |
| `soloFirmware` | `bool` | **так** | `soloFirmwareChanged` | окремо позначений апарат 3DR Solo |
| `vehicleTypeString` | `QString` | ні | `vehicleTypeChanged` | `MAV_TYPE` словами |
| `airship`, `fixedWing`, `multiRotor`, `vtol`, `rover`, `sub` | `bool` | ні | `vehicleTypeChanged` | розкладка `MAV_TYPE` на зручні прапорці |
| `isOfflineEditingVehicle` | `bool` | ні | `CONSTANT` | `true` для несправжнього апарата з редактора плану |
| `motorCount`, `coaxialMotors`, `xConfigMotors` | `int`/`bool` | ні | `CONSTANT` | від плагіна прошивки |
| `vehicleImageOpaque`, `vehicleImageOutline` | `QString` | ні | `CONSTANT` | шляхи до картинок апарата |

Пастка тут одна, зате постійна: `firmwareMajorVersion` до відповіді на `AUTOPILOT_VERSION` дорівнює `-1`, а не нулю. Перевірка «версія хоча б четверта» виду `firmwareMajorVersion >= 4` на щойно народженому апараті чесно дає `false`, і саме тому в класі є `versionCompare`:

```cpp
Q_INVOKABLE int versionCompare(const QString &compare) const;   // "4.2.3"
Q_INVOKABLE int versionCompare(int major, int minor, int patch) const;
```

---

## Властивості: положення й рух

| Q_PROPERTY | Тип | Запис | Сповіщення | Примітка |
|---|---|---|---|---|
| `coordinate` | `QGeoCoordinate` | ні | `coordinateChanged` | з `GLOBAL_POSITION_INT`; **не проріджується** таймером групи |
| `latitude`, `longitude` | `float` | ні | `coordinateChanged` | ті самі дані, розібрані на числа — сигнал спільний із `coordinate` |
| `homePosition` | `QGeoCoordinate` | ні | `homePositionChanged` | точка дому з борту |
| `armedPosition` | `QGeoCoordinate` | ні | `armedPositionChanged` | де апарат стояв у мить зброєння |
| `trajectoryPoints` | `TrajectoryPoints*` | ні | `CONSTANT` | накопичений слід для карти |
| `cameraTriggerPoints` | `QmlObjectListModel*` | ні | `CONSTANT` | позначки спрацювання затвора |
| `orbitActive` | `bool` | ні | `orbitActiveChanged` | чи виконується орбіта |
| `orbitMapCircle` | `QGCMapCircle*` | ні | `CONSTANT` | сам круг для карти |
| `isROIEnabled` | `bool` | ні | `isROIEnabledChanged` | чи заданий об'єкт зацікавлення |

---

## Властивості: стан польоту й зброєння

| Q_PROPERTY | Тип | Запис | Сповіщення | Примітка |
|---|---|---|---|---|
| `armed` | `bool` | **так**, `setArmedShowError` | `armedChanged(bool)` | запис із QML завжди показує помилку при відмові |
| `autoDisarm` | `bool` | ні | `autoDisarmChanged` | чи роззброїться сам після посадки |
| `flying` | `bool` | ні | `flyingChanged(bool)` | з `EXTENDED_SYS_STATE`, поле `landed_state` |
| `landing` | `bool` | ні | `landingChanged(bool)` | звідти ж, стан `MAV_LANDED_STATE_LANDING` |
| `flightMode` | `QString` | **так**, `setFlightMode` | `flightModeChanged(const QString&)` | назву дає плагін прошивки, не сам `Vehicle` |
| `flightModes` | `QStringList` | ні | `flightModesChanged` | перелік допустимих назв для цього апарата |
| `flightModeSetAvailable` | `bool` | ні | `CONSTANT` | чи можна взагалі перемикати режим |
| `guidedMode` | `bool` | **так**, `setGuidedMode` | `guidedModeChanged(bool)` | читання й запис цілком делеговані плагінові прошивки |
| `inFwdFlight` | `bool` | ні | `inFwdFlightChanged` | конвертоплан у літаковому режимі |
| `vtolInFwdFlight` | `bool` | **так** | `vtolInFwdFlightChanged` | те саме, але з правом перемкнути |
| `prearmError` | `QString` | **так** | `prearmErrorChanged` | текст причини, чому зброїтися не можна |
| `readyToFly`, `readyToFlyAvailable` | `bool` | ні | `readyToFlyChanged`, `readyToFlyAvailableChanged` | зведена готовність; друга властивість каже, чи апарат узагалі вміє її доповідати |
| `allSensorsHealthy` | `bool` | ні | `allSensorsHealthyChanged` | з `SYS_STATUS` |
| `requiresGpsFix` | `bool` | ні | `requiresGpsFixChanged` | чи потрібен захват для поточного режиму |
| `sensorsPresentBits`, `sensorsEnabledBits`, `sensorsHealthBits`, `sensorsUnhealthyBits` | `int` | ні | окремий сигнал на кожну | сирі бітові поля `SYS_STATUS` |
| `checkListState` | `CheckList` | **так** | `checkListStateChanged` | `CheckListNotSetup = 0`, `CheckListPassed`, `CheckListFailed` |
| `hobbsMeter` | `QString` | ні | `hobbsMeterChanged` | наліт у вигляді готового рядка |

Іменовані режими подані окремими незмінними рядками, щоб QML не зашивав у себе назв: `missionFlightMode`, `pauseFlightMode`, `rtlFlightMode`, `smartRTLFlightMode`, `landFlightMode`, `takeControlFlightMode`, `followFlightMode`, `motorDetectionFlightMode`, `stabilizedFlightMode`, `gotoFlightMode` — усі `QString` і всі `CONSTANT`. Порівнювати треба саме з ними, а не з літералом «RTL»: у ArduPilot і PX4 рядки різні.

---

## Властивості: зв'язок, лічильники, поступ

| Q_PROPERTY | Тип | Сповіщення | Що рахує |
|---|---|---|---|
| `messagesReceived`, `messagesSent`, `messagesLost` | `uint` | `messagesReceivedChanged` та інші | лічильники самого `Vehicle`, скидаються `resetCounters()` |
| `mavlinkSentCount`, `mavlinkReceivedCount`, `mavlinkLossCount` | `quint64` | `mavlinkStatusChanged` | лічильники розбирача, спільний сигнал на всі чотири |
| `mavlinkLossPercent` | `float` | `mavlinkStatusChanged` | частка втрат у відсотках |
| `loadProgress` | `double` | `loadProgressChanged(float)` | поступ початкового з'єднання, 0…1 |
| `initialConnectComplete` | `bool` | `initialConnectComplete` | **сигнал і властивість звуться однаково**; читає метод `isInitialConnectComplete()` |
| `initialPlanRequestComplete` | `bool` | `initialPlanRequestCompleteChanged` | місію, геозону й точки збору забрано |
| `toolIndicators` | `QVariantList` | `toolIndicatorsChanged` | набір індикаторів панелі для цього апарата |
| `messageCount`, `formattedMessages` | `int`, `QString` | `messageCountChanged`, `formattedMessagesChanged` | накопичені `STATUSTEXT` |
| `messageTypeNone`, `messageTypeNormal`, `messageTypeWarning`, `messageTypeError` | `bool` | `messageTypeChanged` | найважчий рівень серед непрочитаних |

Розбіжність типів у парі `loadProgress` — не помилка читання: властивість оголошено `double`, а сигнал несе `float`. Прив'язці це байдуже, а от підписці з C++ на `&Vehicle::loadProgressChanged` доведеться приймати саме `float`.

---

## Властивості: підсистеми

Усі, крім двох останніх, позначені `CONSTANT` — QML прочитає їх один раз і більше ніколи не перепитає. Це нормально: самі об'єкти живуть стільки ж, скільки апарат.

| Q_PROPERTY | Тип | Сповіщення | Що це |
|---|---|---|---|
| `parameterManager` | `ParameterManager*` | `CONSTANT` | увесь доступ до параметрів борту — [окрема тема](topic:sys-dron/parameter-manager) |
| `vehicleLinkManager` | `VehicleLinkManager*` | `CONSTANT` | канали, якими апарат доступний, і стеження за тишею |
| `supports` | `VehicleSupports*` | `CONSTANT` | що апарат уміє: `guidedMode`, `pauseVehicle`, `orbitMode`, `roiMode`, `smartRTL`, `terrainFrame`, `changeHeading`, `guidedTakeoffWithAltitude`, `guidedTakeoffWithoutAltitude` та інші прапорці |
| `autopilotPlugin` | `AutoPilotPlugin*` | `CONSTANT` | сторінки налаштувань апарата |
| `gimbalController` | `GimbalController*` | `CONSTANT` | підвіс |
| `objectAvoidance` | `VehicleObjectAvoidance*` | `CONSTANT` | уникання перешкод |
| `autotune` | `Autotune*` | `CONSTANT` | автоналаштування регуляторів |
| `remoteIDManager` | `RemoteIDManager*` | `CONSTANT` | віддалена ідентифікація |
| `signingController` | `VehicleSigningController*` | `CONSTANT` | підпис MAVLink 2 |
| `actuators` | `Actuators*` | `CONSTANT` | розкладка приводів |
| `batteries`, `escs` | `QmlObjectListModel*` | `CONSTANT` | **списки**, а не групи фактів: акумуляторів і регуляторів обертів буває кілька |
| `sysStatusSensorInfo` | `QObject*` | `CONSTANT` | розшифровані біти `SYS_STATUS` |
| `healthAndArmingCheckReport` | `HealthAndArmingCheckReport*` | `CONSTANT` | звіт передпольотних перевірок PX4 |
| `staticCameraList` | `QVariantList` | `CONSTANT` | описи камер, зашиті у збірку |
| `cameraManager` | `QGCCameraManager*` | `cameraManagerChanged` | ⚠ **не** `CONSTANT`: з'являється не одразу |
| `mavlinkLogManager` | `MAVLinkLogManager*` | `mavlinkLogManagerChanged` | ⚠ те саме |

Дві останні варті окремої уваги саме тому, що ламають загальне правило. Прив'язка виду `vehicle.cameraManager.cameras` без урахування сигналу мовчки застигне на `null`, якщо апарат доповів про камеру пізніше за створення екрана.

---

## Групи фактів

`Vehicle` успадкований від `VehicleFactGroup`, тобто **сам є групою фактів**, і додатково тримає вісімнадцять вкладених груп. У кожної є ім'я в QML (властивість) і незалежне від нього ім'я в реєстрі (для `getFactGroup`).

| Властивість QML | Ім'я в реєстрі | Клас | Джерело | Ключові факти |
|---|---|---|---|---|
| `vehicle` | *(не зареєстровано)* | `VehicleFactGroup` | `ATTITUDE`, `VFR_HUD`, `ALTITUDE`, `GLOBAL_POSITION_INT` та інші | `roll`, `pitch`, `heading`, `rollRate`, `pitchRate`, `yawRate`, `groundSpeed`, `airSpeed`, `climbRate`, `altitudeRelative`, `altitudeAMSL`, `altitudeAboveTerr`, `flightDistance`, `distanceToHome`, `timeToHome`, `headingToHome`, `distanceToGCS`, `missionItemIndex`, `distanceToNextWP`, `throttlePct`, `rcRSSI`, `imuTemp`, `hobbs`, `xTrackError`, `rangeFinderDist` |
| `gps` | `gps` | `VehicleGPSFactGroup` | `GPS_RAW_INT`, `GNSS_INTEGRITY`, `HIGH_LATENCY`, `HIGH_LATENCY2` | `lat`, `lon`, `mgrs`, `hdop`, `vdop`, `count`, `lock`, `courseOverGround`, `yaw`, `spoofingState`, `jammingState`, `authenticationState`, `systemQuality`, `gnssSignalQuality` |
| `gps2` | `gps2` | `VehicleGPS2FactGroup` | `GPS2_RAW`, `GNSS_INTEGRITY` | ті самі імена, другий приймач |
| `gpsAggregate` | `gpsAggregate` | `VehicleGPSAggregateFactGroup` | зведення з `gps` і `gps2` | `spoofingState`, `jammingState`, `authenticationState`, `isStale` — береться найгірше з двох |
| `wind` | `wind` | `VehicleWindFactGroup` | `WIND_COV`, `WIND`, `HIGH_LATENCY`, `HIGH_LATENCY2` | `direction`, `speed`, `verticalSpeed` |
| `vibration` | `vibration` | `VehicleVibrationFactGroup` | `VIBRATION` | `xAxis`, `yAxis`, `zAxis`, `clipCount1`, `clipCount2`, `clipCount3` |
| `temperature` | `temperature` | `VehicleTemperatureFactGroup` | `SCALED_PRESSURE`, `SCALED_PRESSURE2`, `SCALED_PRESSURE3`, `HIGH_LATENCY`, `HIGH_LATENCY2` | `temperature1`, `temperature2`, `temperature3` |
| `clock` | `clock` | `VehicleClockFactGroup` | **годинник самої станції**, не ефір | `currentTime`, `currentUTCTime`, `currentDate` |
| `setpoint` | `setpoint` | `VehicleSetpointFactGroup` | `ATTITUDE_TARGET` | `roll`, `pitch`, `yaw`, `rollRate`, `pitchRate`, `yawRate` — **завдання**, не виміряне |
| `estimatorStatus` | `estimatorStatus` | `VehicleEstimatorStatusFactGroup` | `ESTIMATOR_STATUS` | `goodAttitudeEstimate`, `goodHorizPosAbsEstimate`, `goodVertPosAGLEstimate`, `gpsGlitch`, `accelError`, `velRatio`, `magRatio`, `horizPosAccuracy`, `vertPosAccuracy` |
| `terrain` | `terrain` | `TerrainFactGroup` | `TERRAIN_REPORT` через `TerrainProtocolHandler` | `blocksPending`, `blocksLoaded` |
| **`distanceSensors`** | **`distanceSensor`** | `VehicleDistanceSensorFactGroup` | `DISTANCE_SENSOR` | `rotationNone`, `rotationYaw45`…`rotationYaw315`, `rotationPitch90`, `rotationPitch270`, `minDistance`, `maxDistance` |
| `localPosition` | `localPosition` | `VehicleLocalPositionFactGroup` | `LOCAL_POSITION_NED` | `x`, `y`, `z`, `vx`, `vy`, `vz` |
| `localPositionSetpoint` | `localPositionSetpoint` | `VehicleLocalPositionSetpointFactGroup` | `POSITION_TARGET_LOCAL_NED` | ті самі шість імен — завдання, не поточне |
| `hygrometer` | `hygrometer` | `VehicleHygrometerFactGroup` | `HYGROMETER_SENSOR` | `hygroID`, `hygroTemp`, `hygroHumi` |
| `generator` | `generator` | `VehicleGeneratorFactGroup` | `GENERATOR_STATUS` | `status`, `genSpeed`, `batteryCurrent`, `loadCurrent`, `powerGenerated`, `busVoltage`, `rectifierTemp`, `genTemp`, `runtime`, `timeMaintenance`, `flagsListGenerator` |
| `efi` | `efi` | `VehicleEFIFactGroup` | `EFI_STATUS` | `health`, `rpm`, `fuelConsumed`, `fuelFlow`, `engineLoad`, `throttlePos`, `intakePress`, `intakeTemp`, `cylinderTemp`, `exGasTemp`, `ignVoltage`, `fuelPressure` |
| *(немає)* | `rpm` | `VehicleRPMFactGroup` | `RAW_RPM`, `RPM` | `rpm1`…`rpm4`, `rpmSensor1`, `rpmSensor2` |
| `radioStatus` | `radioStatus` | `RadioStatusFactGroup` | `RADIO_STATUS` | `lrssi`, `rrssi`, `rxErrors`, `fixed`, `txBuffer`, `lNoise`, `rNoise` |

Три розбіжності в цій таблиці збивають з пантелику найчастіше, і всі три видно просто з коду.

**Перша: `distanceSensors` проти `distanceSensor`.** Властивість названо в множині, а рядок реєстру — в однині:

```cpp
Q_PROPERTY(FactGroup* distanceSensors READ distanceSensorFactGroup CONSTANT)
const QString _distanceSensorFactGroupName = QStringLiteral("distanceSensor");
```

Отже, `vehicle.distanceSensors` працює, а `vehicle.getFactGroup("distanceSensors")` віддає `nullptr` — треба `getFactGroup("distanceSensor")`.

**Друга: `rpm` є в реєстрі, але не має властивості.** Група створюється й отримує повідомлення нарівні з рештою, її ім'я є в `factGroupNames`, але рядка `Q_PROPERTY(FactGroup* rpm …)` у класі просто немає. Єдина дорога до неї з QML — виклик:

```qml
property var rpmGroup: vehicle.getFactGroup("rpm")
text: rpmGroup ? rpmGroup.getFact("rpm1").valueString : ""
```

**Третя: `vehicle` — це сам апарат.** У конструкторі член ініціалізовано вказівником на себе, а реєстрація навмисне закоментована:

```cpp
, _vehicleFactGroup             (this)
…
// _addFactGroup(_vehicleFactGroup,            _vehicleFactGroupName);
```

Наслідок практичний: `vehicle.vehicle.roll` і `vehicle.roll` — те саме число, бо `Vehicle` **успадкований** від `VehicleFactGroup` і всі його факти вже є прямими властивостями апарата. Зате `getFactGroup("vehicle")` віддасть `nullptr`, а `factGroupNames` не міститиме рядка `vehicle`. Реєстрація тут створила б групу, що містить саму себе, — і обхід груп при кожному повідомленні зациклився б.

Сам механізм факта — число плюс метадані — розібрано у [фактовій системі](topic:sys-dron/fact-system). Для довідки досить чотирьох властивостей `Fact`, якими користуються найчастіше:

| Властивість `Fact` | Тип | Що дає |
|---|---|---|
| `value` | `QVariant` | значення в одиницях користувача (метри або фути) |
| `rawValue` | `QVariant` | значення в одиницях протоколу, завжди метричне |
| `valueString` | `QString` | готовий рядок із потрібною кількістю знаків |
| `units` | `QString` | підпис одиниць, теж у системі користувача |

`FactGroup` віддає ще чотири виклики, спільні для всіх груп:

```cpp
Q_INVOKABLE bool       factExists(const QString &name) const;
Q_INVOKABLE Fact      *getFact(const QString &name) const;
Q_INVOKABLE FactGroup *getFactGroup(const QString &name) const;
Q_INVOKABLE void       setLiveUpdates(bool liveUpdates);   // вимкнути проріджування сигналів
```

---

## Методи керування: команди загального призначення

Єдиний спосіб послати довільну команду з QML:

```cpp
Q_INVOKABLE void sendCommand(int compId, int command, bool showError,
                             double param1 = 0.0, double param2 = 0.0, double param3 = 0.0,
                             double param4 = 0.0, double param5 = 0.0, double param6 = 0.0,
                             double param7 = 0.0);
```

| Параметр | Значення |
|---|---|
| `compId` | компонент-адресат; `defaultComponentId()` — автопілот, `MAV_COMP_ID_ALL` — усі |
| `command` | число з переліку `MAV_CMD` |
| `showError` | чи показати користувачеві вікно, якщо команда провалилася |
| `param1`…`param7` | сім параметрів команди; **усі сім звужуються до `float`** усередині |

Тіло — тонка обгортка, і звуження в ньому видно просто:

```cpp
void Vehicle::sendCommand(int compId, int command, bool showError, double param1, …)
{
    sendMavCommand(compId, static_cast<MAV_CMD>(command), showError,
                   static_cast<float>(param1), …);
}
```

Тобто `double` у сигнатурі — поступка QML, у якого всі числа й так подвійної точності; у ефір іде `float`. Для широти й довготи цього замало, тому їх шлють не тут, а окремими цілочисловими командами. Що таке `COMMAND_LONG`, `COMMAND_INT` і `COMMAND_ACK` як протокол — у [командах MAVLink](topic:sys-dron/mavlink-commands).

З C++ доступний ширший набір:

```cpp
void sendMavCommand(int compId, MAV_CMD command, bool showError,
                    float param1 = 0.0f, …, float param7 = 0.0f);

void sendMavCommandDelayed(int compId, MAV_CMD command, bool showError, int milliseconds,
                           float param1 = 0.0f, …);

void sendMavCommandInt(int compId, MAV_CMD command, MAV_FRAME frame, bool showError,
                       float param1, float param2, float param3, float param4,
                       double param5, double param6, float param7);

void sendMavCommandWithHandler(const MavCmdAckHandlerInfo_t *ackHandlerInfo,
                               int compId, MAV_CMD command,
                               float param1 = 0.0f, …);

void sendMavCommandIntWithHandler(const MavCmdAckHandlerInfo_t *ackHandlerInfo,
                                  int compId, MAV_CMD command, MAV_FRAME frame,
                                  float param1 = 0.0f, …, double param5 = 0.0f, double param6 = 0.0f,
                                  float param7 = 0.0f);

void sendMavCommandWithLambdaFallback(std::function<void()> lambda, int compId, MAV_CMD command,
                                      bool showError, float param1 = 0.0f, …);
void sendMavCommandIntWithLambdaFallback(std::function<void()> lambda, int compId, MAV_CMD command,
                                         MAV_FRAME frame, bool showError, float param1 = 0.0f, …);
```

Різниця між парами `…Command` і `…CommandInt` — у п'ятому й шостому параметрі: у цілочисловій формі вони `double` і призначені для координат, які `float` спотворив би на десятки сантиметрів.

Форма `…WithLambdaFallback` спрацьовує рівно на одну відповідь — `MAV_RESULT_UNSUPPORTED`. Тоді станція запам'ятовує в даних плагіна прошивки, що ця команда апаратові невідома, і виконує подану лямбду замість неї:

```cpp
case MAV_RESULT_UNSUPPORTED:
    instanceData->setCommandSupported(MAV_CMD(ack.command),
                                      FirmwarePluginInstanceData::CommandSupportedResult::UNSUPPORTED);
    data->unsupportedLambda();
    break;
```

Так тримають запасні дороги для старих прошивок: спершу пробують сучасну команду, а на відмову тихо переходять на давню. Відповіді, відмінні від `ACCEPTED` і `UNSUPPORTED`, лямбди не запускають — вони йдуть звичайним шляхом помилки.

Відповідь на команду приходить у зворотному виклику:

```cpp
typedef enum {
    MavCmdResultCommandResultOnly,          // у commandResult повна відповідь про успіх або відмову
    MavCmdResultFailureNoResponseToCommand, // апарат не відповів узагалі
    MavCmdResultFailureDuplicateCommand,    // така сама команда вже чекає на відповідь
} MavCmdResultFailureCode_t;

typedef void (*MavCmdResultHandler)(void *resultHandlerData, int compId,
                                    const mavlink_command_ack_t &ack,
                                    MavCmdResultFailureCode_t failureCode);

typedef void (*MavCmdProgressHandler)(void *progressHandlerData, int compId,
                                      const mavlink_command_ack_t &ack);

typedef struct MavCmdAckHandlerInfo_s {
    MavCmdResultHandler   resultHandler;        // nullptr — обробника немає
    void                 *resultHandlerData;
    MavCmdProgressHandler progressHandler;      // ловить MAV_RESULT_IN_PROGRESS
    void                 *progressHandlerData;
} MavCmdAckHandlerInfo_t;
```

Черга команд повторює втрачені сама, і її числа варто знати:

| Константа | Значення | Що означає |
|---|---|---|
| час очікування підтвердження | `1200` мс | стільки `MavCommandQueue` чекає на `COMMAND_ACK` перед повтором |
| `kMaxRetryCount` | `3` | стільки разів команду шлють, якщо вона з тих, що варто повторювати |
| `kTestAckTimeoutMs` | `500` | скорочений час очікування під час автотестів |

Команда, яку повторювати не можна (наприклад, зміна лічильника чи одноразова дія), отримує `maxTries = 1`. Вичерпавши спроби, черга віддає `MavCmdResultFailureNoResponseToCommand`.

Окремо стоїть запит одного повідомлення:

```cpp
void requestMessage(RequestMessageResultHandler resultHandler, void *resultHandlerData,
                    int compId, int messageId,
                    float param1 = 0.0f, …, float param5 = 0.0f);

typedef enum {
    RequestMessageNoFailure,
    RequestMessageFailureCommandError,
    RequestMessageFailureCommandNotAcked,
    RequestMessageFailureMessageNotReceived,   // підтвердили, але повідомлення не надіслали
    RequestMessageFailureDuplicate,
} RequestMessageResultHandlerFailureCode_t;
```

Розділення двох останніх кодів — не педантизм: апарат цілком може підтвердити `MAV_CMD_REQUEST_MESSAGE` і не надіслати нічого, і це інша поломка, ніж мовчання на саму команду.

---

## Методи керування: політ

Усі викличні з QML. Порядок — від найуживаніших.

| Сигнатура | Параметри | Примітка |
|---|---|---|
| `void guidedModeTakeoff(double altitudeRelative)` | висота над точкою зльоту, метри | перевіряє `supports.guidedMode`, далі — плагін прошивки |
| `void guidedModeLand()` | — | те саме |
| `void guidedModeRTL(bool smartRTL)` | `true` — повернення слідом, а не по прямій | те саме |
| `bool guidedModeGotoLocation(const QGeoCoordinate &gotoCoord, double forwardFlightLoiterRadius = 0.0)` | точка; радіус кола очікування для літака | **повертає `bool`** — єдиний із цієї родини |
| `void guidedModeChangeAltitude(double altitudeChange, bool pauseVehicle)` | приріст висоти; чи спинити апарат | приріст, не абсолютна висота |
| `void guidedModeChangeHeading(const QGeoCoordinate &headingCoord)` | курс задається **точкою**, на яку дивитися | не градусами |
| `void guidedModeChangeGroundSpeedMetersSecond(double groundspeed)` | м/с | шляхова швидкість |
| `void guidedModeChangeEquivalentAirspeedMetersSecond(double airspeed)` | м/с | еквівалентна повітряна, не шляхова |
| `void guidedModeOrbit(const QGeoCoordinate &centerCoord, double radius, double amslAltitude)` | центр, радіус, висота над рівнем моря | висота саме AMSL |
| `void guidedModeROI(const QGeoCoordinate &centerCoord)` | точка зацікавлення | камера й ніс дивляться туди |
| `void stopGuidedModeROI()` | — | скасувати попереднє |
| `void pauseVehicle()` | — | зависання на місці |
| `void emergencyStop()` | — | негайне зняття живлення з моторів |
| `void abortLanding(double climbOutAltitude)` | висота відходу, метри | перервати захід на посадку |
| `void startTakeoff()` | — | зліт у режимі місії, не в керованому |
| `void startMission()` | — | почати виконання плану |
| `void setCurrentMissionSequence(int seq)` | номер елемента | перескочити на потрібний пункт |
| `void doSetHome(const QGeoCoordinate &coord)` | нова точка дому | |
| `void setEstimatorOrigin(const QGeoCoordinate &centerCoord)` | початок місцевих координат | для апаратів без GPS |
| `void landingGearDeploy()` / `void landingGearRetract()` | — | шасі |
| `void motorInterlock(bool enable)` | дозвіл на обертання | |
| `void motorTest(int motor, int percent, int timeoutSecs, bool showError)` | номер мотора, тяга у відсотках, обмеження часу | |
| `void sendGripperAction(GRIPPER_ACTIONS gripperOption)` | дія захвата | |
| `void triggerSimpleCamera()` | — | спуск затвора |
| `void rebootVehicle()` | — | перезавантаження автопілота |
| `void flashBootloader()` | — | перепрошивка завантажувача |
| `void sendPlan(QString planFile)` | шлях до файлу плану | вивантажити план на борт; про сам формат — у [моделі плану](topic:sys-dron/plan-model) |
| `void closeVehicle()` | — | від'єднатися й знищити об'єкт |
| `void resetCounters()` | — | обнулити лічильники повідомлень |
| `void virtualTabletJoystickValue(double roll, double pitch, double yaw, double thrust)` | −1…1 на кожну вісь | екранний джойстик |
| `void sendParamMapRC(const QString &paramName, double scale, double centerValue, int tuningID, double minValue, double maxValue)` | прив'язка параметра до ручки апаратури | |
| `void clearAllParamMapRC()` | — | зняти всі прив'язки |
| `void setPIDTuningTelemetryMode(PIDTuningTelemetryMode mode)` | режим частої телеметрії для налаштування регуляторів | |
| `double minimumTakeoffAltitudeMeters()` | — | нижня межа для `guidedModeTakeoff` |
| `double maximumHorizontalSpeedMultirotorMetersSecond()` | — | стеля швидкості мультиротора |
| `double minimumEquivalentAirspeed()` / `double maximumEquivalentAirspeed()` | — | межі еквівалентної повітряної швидкості |
| `QString vehicleClassInternalName()` | — | внутрішня назва класу апарата |
| `QVariant expandedToolbarIndicatorSource(const QString &indicatorName)` | ім'я індикатора | QML-джерело розгорнутої панелі |

Три головні дії родини `guidedMode…` побудовані однаково — перевірка можливості, потім передача плагінові прошивки:

```cpp
void Vehicle::guidedModeTakeoff(double altitudeRelative)
{
    if (!_vehicleSupports->guidedMode()) {
        QGC::showAppMessage(guided_mode_not_supported_by_vehicle);
        return;
    }
    _firmwarePlugin->guidedModeTakeoff(this, altitudeRelative);
}
```

Отже, сам `Vehicle` жодної команди зльоту не формує: що саме полетить у ефір, вирішує [плагін прошивки](topic:sys-dron/firmware-plugin), і для PX4 та ArduPilot це різні речі.

---

## Зброєння й режим польоту

Ці дві дії викликають не як методи, а **записом у властивість**, і саме тут ховається різниця між QML і C++.

```cpp
bool armed() const { return _armed; }
void setArmed(bool armed, bool showError);                 // повна форма, тільки з C++
void setArmedShowError(bool armed) { setArmed(armed, true); }   // те, що кличе запис із QML
Q_INVOKABLE void forceArm();
```

Тіло обох — одна команда:

```cpp
void Vehicle::setArmed(bool armed, bool showError)
{
    // саме COMMAND_LONG:MAV_CMD_COMPONENT_ARM_DISARM — його підтримує більше польотних стеків
    sendMavCommand(_defaultComponentId, MAV_CMD_COMPONENT_ARM_DISARM, showError,
                   armed ? 1.0f : 0.0f);
}

void Vehicle::forceArm()
{
    sendMavCommand(_defaultComponentId, MAV_CMD_COMPONENT_ARM_DISARM, true,
                   1.0f,     // зброїти
                   2989);    // домовлене число «попри перевірки»
}
```

Число `2989` — не помилка й не випадковість: це домовлений у MAVLink магічний параметр, який просить автопілот обійти передпольотні перевірки. Через це `forceArm` навмисно не має форми без показу помилок.

Запис у `armed` — це **прохання**, а не встановлення. Властивість зміниться лише тоді, коли з борту прийде heartbeat зі зміненим бітом, і сигнал `armedChanged` вилетить саме звідти. Прив'язка, яка після `vehicle.armed = true` одразу читає `vehicle.armed`, побачить старе значення.

Те саме з режимом:

```cpp
void Vehicle::setFlightMode(const QString &flightMode)
{
    uint8_t base_mode; uint32_t custom_mode;
    if (setFlightModeCustom(flightMode, &base_mode, &custom_mode)) {
        …
        if (_firmwarePlugin->MAV_CMD_DO_SET_MODE_is_supported()) {
            sendMavCommand(defaultComponentId(), MAV_CMD_DO_SET_MODE, true,
                           MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, custom_mode);
        } else {
            // запасна дорога для прошивок без DO_SET_MODE — старе повідомлення SET_MODE
            mavlink_msg_set_mode_pack_chan(…, id(), newBaseMode, custom_mode);
            sendMessageOnLinkThreadSafe(sharedLink.get(), msg);
        }
    }
}
```

Рядок режиму мусить бути одним із `flightModes`; невідому назву `setFlightModeCustom` відкине, і в журнал ляже попередження — жодного винятку й жодної відповіді назовні не буде.

---

## Сигнали

| Сигнал | Аргументи | Коли |
|---|---|---|
| `armedChanged` | `bool armed` | біт зброєння в heartbeat змінився |
| `flightModeChanged` | `const QString &flightMode` | плагін прошивки витлумачив нову пару `base_mode`/`custom_mode` |
| `coordinateChanged` | `QGeoCoordinate coordinate` | нова позиція з `GLOBAL_POSITION_INT`, **без проріджування** |
| `homePositionChanged` | `const QGeoCoordinate &` | борт доповів нову точку дому |
| `armedPositionChanged` | — | зброєння сталося в новому місці |
| `flyingChanged` / `landingChanged` | `bool` | `EXTENDED_SYS_STATE` |
| `guidedModeChanged` | `bool guidedMode` | вхід у керований режим або вихід із нього |
| `mavCommandResult` | `int vehicleId, int targetComponent, int command, int ackResult, int failureCode` | будь-яка команда без власного обробника дійшла краю: відповідь, вичерпані спроби або відмова |
| `mavlinkMessageReceived` | `const mavlink_message_t &message` | **кожен** кадр, адресований цьому апаратові |
| `textMessageReceived` | `int sysid, int componentid, int severity, QString text, QString description` | `STATUSTEXT` |
| `newFormattedMessage` | `QString formattedMessage` | той самий текст, уже готовий до показу |
| `initialConnectComplete` | — | машина початкового з'єднання дійшла кінця |
| `loadProgressChanged` | `float value` | поступ того самого з'єднання |
| `mavlinkStatusChanged` | — | будь-який із чотирьох лічильників розбирача |
| `firmwareVersionChanged` / `firmwareCustomVersionChanged` / `gitHashChanged` | — / — / `QString hash` | прийшов `AUTOPILOT_VERSION` |
| `vehicleUIDChanged` | — | звідти ж |
| `capabilityBitsChanged` | `uint64_t capabilityBits` | стало відомо, що апарат уміє |
| `capabilitiesKnownChanged` | `bool capabilitiesKnown` | до цієї миті питати `supports` рано |
| `allSensorsHealthyChanged` | `bool` | `SYS_STATUS` |
| `readyToFlyChanged` / `readyToFlyAvailableChanged` | `bool` | зведена готовність |
| `rcChannelsRawChanged` / `rcChannelsClampedChanged` | `QVector<int> channelValues` | канали апаратури керування |
| `servoOutputsChanged` | `QVector<int> servoValues` | виходи на приводи |
| `mavlinkMsgIntervalsChanged` | `uint8_t compid, uint16_t msgId, int32_t rate` | змінено частоту потоку |
| `requestOperatorControlReceived` | `int sysIdRequestingControl, int allowTakeover, int requestTimeoutSecs` | інша станція просить керування |
| `roiCoordChanged` | `const QGeoCoordinate &centerCoord` | змінилася точка зацікавлення |
| `mavlinkLogData` | `Vehicle*, uint8_t, uint8_t, uint16_t, uint8_t, QByteArray, bool` | шматок бортового журналу |

Сигнал `mavCommandResult` `Vehicle` не породжує сам — він переспрямовує чужий:

```cpp
connect(_mavCmdQueue, &MavCommandQueue::commandResult, this, &Vehicle::mavCommandResult);
```

Тобто підписуватися треба на апарат, а не на чергу, і фільтрувати відповіді за парою `targetComponent` + `command`: у черзі водночас буває кілька різних команд, і всі вони приходять одним сигналом.

Ще одна тонкість, помітна лише в оголошенні: `mavlinkMessageReceived` летить на **кожен** кадр цього апарата. Підписка на нього з віджета, що малюється, — надійний спосіб з'їсти головну нитку: за звичайного набору потоків це кількасот викликів на секунду. Скільки роботи припадає на головну нитку й чому, розібрано в [моделі потоків](topic:sys-dron/threading-model).

---

## Мінімальний робочий виклик

Показ трьох значень і одна дія — усе, що потрібно для перевірки, чи інтерфейс живий:

```qml
import QtQuick
import QtQuick.Controls
import QGroundControl

Column {
    property var vehicle: QGroundControl.multiVehicleManager.activeVehicle

    Text { text: vehicle ? vehicle.flightMode : "—" }

    // факт сам знає свої одиниці й потрібну кількість знаків
    Text { text: vehicle ? vehicle.altitudeRelative.valueString + " " +
                           vehicle.altitudeRelative.units : "—" }

    Text { text: vehicle ? qsTr("Супутників: ") + vehicle.gps.count.valueString : "—" }

    Button {
        text: vehicle && vehicle.armed ? qsTr("Роззброїти") : qsTr("Зброїти")
        enabled: vehicle !== null
        onClicked: vehicle.armed = !vehicle.armed   // прохання; відповідь прийде heartbeat'ом
    }
}
```

З C++ — команда з власним обробником відповіді, бо саме тут найлегше помилитися з часом життя даних:

```cpp
struct RebootContext { QPointer<MyWidget> owner; };

static void rebootResultHandler(void *data, int compId,
                                const mavlink_command_ack_t &ack,
                                Vehicle::MavCmdResultFailureCode_t failureCode)
{
    auto *ctx = static_cast<RebootContext*>(data);
    if (failureCode == Vehicle::MavCmdResultCommandResultOnly && ack.result == MAV_RESULT_ACCEPTED) {
        qCDebug(MyLog) << "апарат прийняв перезавантаження";
    } else {
        qCWarning(MyLog) << "відмова:" << MavCommandQueue::failureCodeToString(failureCode);
    }
    delete ctx;                       // обробник викликається рівно один раз
}

void MyWidget::reboot(Vehicle *vehicle)
{
    auto *ctx = new RebootContext{ this };
    Vehicle::MavCmdAckHandlerInfo_t handlerInfo = {};
    handlerInfo.resultHandler     = rebootResultHandler;
    handlerInfo.resultHandlerData = ctx;

    vehicle->sendMavCommandWithHandler(&handlerInfo,
                                       vehicle->defaultComponentId(),
                                       MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
                                       1.0f);   // param1: перезавантажити автопілот
}
```

Три речі випливають просто з типів. Обробник — звичайний вказівник на функцію, а не лямбда з захватом, тож увесь контекст їде в `void*`. Структуру `MavCmdAckHandlerInfo_t` передають **вказівником на локальну змінну**, і черга копіює її вміст собі — після повернення з виклику вона більше не потрібна. І `showError` у формі з обробником немає взагалі: якщо ви взяли відповідь на себе, вікно з помилкою станція не покаже.

---

## Пастки, помітні лише під час роботи

| Що зроблено | Що зламається | Чому мовчки |
|---|---|---|
| прив'язка без перевірки `activeVehicle` на `null` | екран порожній або помилка в консолі QML | застосунок стартує без жодного апарата |
| `getFactGroup("distanceSensors")` | `nullptr` | властивість у множині, ім'я в реєстрі — в однині |
| `getFactGroup("vehicle")` | `nullptr` | група не зареєстрована, бо це сам апарат |
| очікування на властивість `rpm` | її немає | група є, `Q_PROPERTY` для неї не оголошено |
| читання `vehicle.armed` одразу після запису | старе значення | запис — це команда в ефір, а не присвоєння |
| `vehicle.cameraManager` без урахування `cameraManagerChanged` | назавжди `null` | властивість не `CONSTANT`, менеджер з'являється пізніше |
| порівняння `flightMode` з рядком «RTL» | не збігається на одній із прошивок | назви режимів дає плагін прошивки; є `rtlFlightMode` |
| `firmwareMajorVersion >= 4` до кінця початкового з'єднання | `false` на справній новій прошивці | до `AUTOPILOT_VERSION` значення `-1` |
| широта в `param5` виклику `sendCommand` | точка з'їжджає на десятки сантиметрів | усі сім параметрів звужуються до `float`; координати шлють формою `…CommandInt` |
| підписка на `mavlinkMessageReceived` з віджета | інтерфейс помітно гальмує | сигнал летить на кожен кадр, у головній нитці |
| очікування `mavCommandResult` на команду з обробником | сигнал не прийде | за наявності `resultHandler` черга кличе його **замість** сигналу |
| один обробник на дві однакові команди водночас | друга падає з `MavCmdResultFailureDuplicateCommand` | черга не приймає дубліката, поки перший чекає на відповідь |
