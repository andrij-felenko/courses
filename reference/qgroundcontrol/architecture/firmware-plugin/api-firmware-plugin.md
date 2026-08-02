# 🧩 Контракт FirmwarePlugin: сигнатури, типові значення, реєстрація

Тут зібрано все, що треба знати, аби написати або перевизначити плагін прошивки QGroundControl: кожен віртуальний метод із типом повернення, аргументами й **відповіддю базового класу**, три типи, на яких контракт тримається (`FirmwareCapabilities`, `FirmwareFlightMode`, `FirmwarePluginInstanceData`), а також контракт реєстрації — фабрика, реєстр і таблиця, за якою `MAV_AUTOPILOT` і `MAV_TYPE` згортаються в пару класів. Довідник потрібен, щоб перевизначати саме той метод, який справді викликається, і наперед бачити, що станція робитиме, якщо його не перевизначити.

Звірено з гілкою `master` репозиторію `mavlink/qgroundcontrol` 2 серпня 2026 року. Файли: `src/FirmwarePlugin/FirmwarePlugin.h`, `FirmwarePlugin.cc`, `FirmwarePluginFactory.h`, `FirmwarePluginFactory.cc`, `FirmwarePluginManager.h`, `FirmwarePluginManager.cc`, `src/MAVLink/QGCMAVLink.h`, `QGCMAVLink.cc`, `QGCMAVLinkTypes.h`. Числові значення `MAV_TYPE` й `MAV_AUTOPILOT` звірено з `message_definitions/v1.0/minimal.xml` репозиторію `mavlink/mavlink`.

---

## Три типи, на яких тримається весь контракт

### enum FirmwareCapabilities

Відповідь на питання «що цей апарат уміє» — одна бітова маска, а не десяток окремих методів:

```cpp
/// Set of optional capabilites which firmware may support
enum FirmwareCapabilities {
    SetFlightModeCapability =   1 << 0,   ///< метод setFlightMode підтримано
    PauseVehicleCapability =    1 << 1,   ///< апарат уміє зупинитися на місці
    GuidedModeCapability =      1 << 2,   ///< апарат приймає команди керованого режиму
    OrbitModeCapability =       1 << 3,   ///< апарат уміє облітати точку по колу
    TakeoffVehicleCapability =  1 << 4,   ///< апарат уміє злітати
    ROIModeCapability =         1 << 5,   ///< точка інтересу — і в польоті, і в плані
    ChangeHeadingCapability =   1 << 6,   ///< апарат уміє змінити курс на місці
    GuidedTakeoffCapability =   1 << 7,   ///< зліт саме з керованого режиму
};
```

| Біт | Значення | Що вмикає в інтерфейсі |
|---|---|---|
| `SetFlightModeCapability` | `0x01` | випадний список польотних режимів |
| `PauseVehicleCapability` | `0x02` | кнопка паузи на панелі керованих дій |
| `OrbitModeCapability` | `0x08` | коло навколо точки на карті |
| `TakeoffVehicleCapability` | `0x10` | кнопка зльоту |
| `GuidedTakeoffCapability` | `0x80` | зліт із поточного керованого режиму, без окремого переходу |

Питання завжди складене — «уміє й керований режим, і зліт», — тож маску складають побітовим `|`, а плагін відповідає одним `bool`:

```cpp
virtual bool isCapable(const Vehicle* /*vehicle*/, FirmwareCapabilities /*capabilities*/) const
{ return false; }
```

Типова відповідь `false` — не забудькуватість, а свідомий вибір: незнайомий автопілот дістає станцію лише для показу телеметрії, а всі керовані кнопки лишаються неактивними. Це та сама поведінка [порожнього об'єкта](book:programming/null-object) — заміна, що чесно нічого не робить замість того, щоб падати.

### struct FirmwareFlightMode

Один рядок таблиці режимів. Два конструктори — старий, лише з `custom_mode`, і повний, зі стандартним номером і прапорцями класу апарата:

```cpp
struct FirmwareFlightMode
{
    FirmwareFlightMode(const QString &mName, uint32_t cMode,
                       bool cbs = false, bool adv = false);

    FirmwareFlightMode(const QString &mName, uint8_t sMode, uint32_t cMode,
                       bool cbs = false, bool adv = false,
                       bool fWing = false, bool mRotor = true);

    QString  mode_name    = "Unknown";
    uint8_t  standard_mode = 0;
    uint32_t custom_mode  = UINT32_MAX;
    bool     canBeSet     = false;
    bool     advanced     = false;
    bool     fixedWing    = false;
    bool     multiRotor   = true;
};
```

| Поле | Типово | Що означає |
|---|---|---|
| `mode_name` | `"Unknown"` | напис, яким режим бачить решта застосунку; **ключ** для `setFlightMode()` |
| `standard_mode` | `0` | номер зі стандартного протоколу режимів; `0` = стандартного відповідника немає |
| `custom_mode` | `UINT32_MAX` | непрозоре число прошивки з поля `custom_mode` HEARTBEAT |
| `canBeSet` | `false` | режим можна **вибрати**; без цього він лише показується |
| `advanced` | `false` | режим ховається, поки не ввімкнено розширений інтерфейс |
| `fixedWing` | `false` | режим пропонується літаку |
| `multiRotor` | `true` | режим пропонується мультикоптеру |

Дві пастки цих типових значень. Перша: `canBeSet` типово `false`, тож режим, доданий без цього прапорця, з'явиться в рядку стану, але не в списку вибору. Друга: `multiRotor` типово `true`, а `fixedWing` — `false`, отже режим, доданий «як є», літакам не дістанеться взагалі.

### Псевдоніми типів

```cpp
typedef QList<FirmwareFlightMode>  FlightModeList;
typedef QMap<uint32_t, QString>    FlightModeCustomModeMap;

typedef QMap<QString, QString>                            remapParamNameMap_t;
typedef QMap<int, remapParamNameMap_t>                    remapParamNameMinorVersionRemapMap_t;
typedef QMap<int, remapParamNameMinorVersionRemapMap_t>   remapParamNameMajorVersionMap_t;
```

Три вкладені мапи читаються зсередини назовні: старе ім'я → нове ім'я, далі мінорна версія → цей словник, далі мажорна версія → усе попереднє.

---

## Клас прошивки й клас апарата: таблиця згортання

Типи класів оголошено не переліком, а цілим:

```cpp
// src/MAVLink/QGCMAVLinkTypes.h
struct QGCMAVLinkTypes {
    typedef int FirmwareClass_t;
    typedef int VehicleClass_t;
    static constexpr VehicleClass_t VehicleClassGeneric = 0;   // = MAV_TYPE_GENERIC
    static constexpr uint8_t maxRcChannels = 18;
};

// src/MAVLink/QGCMAVLink.h
class QGCMAVLink : public QObject, public QGCMAVLinkTypes { … };
```

Звідси дві речі, які плутають. По-перше, `QGCMAVLink::VehicleClass_t` і `QGCMAVLinkTypes::VehicleClass_t` — **той самий тип**: `QGCMAVLink` успадковує `QGCMAVLinkTypes` відкрито, тож у коді трапляються обидві кваліфікації, і це не дві різні сутності. По-друге, `int` замість `enum` тут навмисний: власна збірка може завести свій клас прошивки з новим числом, не правлячи апстримовий перелік.

Самі константи — це **представники** класу, тобто конкретні значення MAVLink, узяті за позначку всієї групи:

```cpp
static constexpr const FirmwareClass_t FirmwareClassPX4       = MAV_AUTOPILOT_PX4;            // 12
static constexpr const FirmwareClass_t FirmwareClassArduPilot = MAV_AUTOPILOT_ARDUPILOTMEGA;  // 3
static constexpr const FirmwareClass_t FirmwareClassGeneric   = MAV_AUTOPILOT_GENERIC;        // 0

static constexpr const VehicleClass_t VehicleClassFixedWing  = MAV_TYPE_FIXED_WING;                 // 1
static constexpr const VehicleClass_t VehicleClassMultiRotor = MAV_TYPE_QUADROTOR;                  // 2
static constexpr const VehicleClass_t VehicleClassAirship    = MAV_TYPE_AIRSHIP;                    // 7
static constexpr const VehicleClass_t VehicleClassRoverBoat  = MAV_TYPE_GROUND_ROVER;               // 10
static constexpr const VehicleClass_t VehicleClassSub        = MAV_TYPE_SUBMARINE;                  // 12
static constexpr const VehicleClass_t VehicleClassVTOL       = MAV_TYPE_VTOL_TAILSITTER_QUADROTOR;  // 20
static constexpr const VehicleClass_t VehicleClassSpacecraft = MAV_TYPE_SPACECRAFT_ORBITER;         // 45
```

Обидва поля, з яких усе починається, приїжджають у [HEARTBEAT](book:communications/mavlink-heartbeat) — періодичному повідомленні, яким апарат оголошує тип автопілота й тип планера. Згортання роблять дві статичні функції:

```cpp
static FirmwareClass_t firmwareClass(MAV_AUTOPILOT autopilot);
static VehicleClass_t  vehicleClass(MAV_TYPE mavType);
```

**Клас прошивки** — три гілки, решта в загальний:

| `MAV_AUTOPILOT` | Клас |
|---|---|
| `MAV_AUTOPILOT_PX4` | `FirmwareClassPX4` |
| `MAV_AUTOPILOT_ARDUPILOTMEGA` | `FirmwareClassArduPilot` |
| будь-яке інше з двох десятків значень | `FirmwareClassGeneric` |

**Клас апарата** — повна таблиця згортання `vehicleClass()`:

| `MAV_TYPE` (значення) | Клас |
|---|---|
| `FIXED_WING` (1) | `VehicleClassFixedWing` |
| `QUADROTOR` (2), `COAXIAL` (3), `HELICOPTER` (4), `HEXAROTOR` (13), `OCTOROTOR` (14), `TRICOPTER` (15) | `VehicleClassMultiRotor` |
| `AIRSHIP` (7) | `VehicleClassAirship` |
| `GROUND_ROVER` (10), `SURFACE_BOAT` (11) | `VehicleClassRoverBoat` |
| `SUBMARINE` (12) | `VehicleClassSub` |
| `VTOL_TAILSITTER_DUOROTOR` (19), `VTOL_TAILSITTER_QUADROTOR` (20), `VTOL_TILTROTOR` (21), `VTOL_FIXEDROTOR` (22), `VTOL_TAILSITTER` (23), `VTOL_TILTWING` (24), `VTOL_RESERVED5` (25) | `VehicleClassVTOL` |
| `SPACECRAFT_ORBITER` (45) | `VehicleClassSpacecraft` |
| усе інше (антенний трекер, гімбал, камера, ADSB, парашут…) | `VehicleClassGeneric` |

Перелік супутніх предикатів — усі вони лише звіряють результат `vehicleClass()`:

```cpp
static bool isMultiRotor (MAV_TYPE mavType);
static bool isFixedWing  (MAV_TYPE mavType);
static bool isVTOL       (MAV_TYPE mavType);
static bool isRoverBoat  (MAV_TYPE mavType);   // ⚠ не isRover
static bool isSub        (MAV_TYPE mavType);
static bool isAirship    (MAV_TYPE mavType);
static bool isPX4FirmwareClass       (MAV_AUTOPILOT autopilot);
static bool isArduPilotFirmwareClass (MAV_AUTOPILOT autopilot);
static bool isGenericFirmwareClass   (MAV_AUTOPILOT autopilot);
static QList<FirmwareClass_t> allFirmwareClasses();
static QList<VehicleClass_t>  allVehicleClasses(void);
static QString firmwareClassToString(FirmwareClass_t firmwareClass);
static QString vehicleClassToUserVisibleString(VehicleClass_t vehicleClass);
```

Тут захована пастка, помітна лише під час роботи: `allVehicleClasses()` повертає **шість** класів — `FixedWing`, `RoverBoat`, `Sub`, `MultiRotor`, `VTOL`, `Generic`. Дирижабля й орбітального апарата в цьому списку немає, хоча `vehicleClass()` їх розрізняє. Тож фабрика, яка покладається на типову реалізацію `supportedVehicleClasses()`, дирижабль не обслуговуватиме — його треба дописувати руками.

---

## Режими польоту

| Сигнатура | Типова відповідь |
|---|---|
| `virtual QStringList flightModes(Vehicle*) const` | `QStringList()` — порожній список |
| `virtual QString flightMode(uint8_t base_mode, uint32_t custom_mode) const` | `"PreFlight"` при `base_mode == 0`; інакше пошук у `_modeEnumToString`, а без збігу — складання назви зі стандартних прапорців `base_mode` |
| `virtual bool setFlightMode(const QString&, uint8_t *base_mode, uint32_t *custom_mode) const` | попередження в журнал і `false` |
| `virtual bool MAV_CMD_DO_SET_MODE_is_supported() const` | `false` |
| `virtual bool isGuidedMode(const Vehicle*) const` | `false` |
| `virtual void setGuidedMode(Vehicle*, bool guidedMode) const` | повідомлення «Guided mode not supported by Vehicle» |
| `virtual void updateAvailableFlightModes(FlightModeList&)` | `_updateFlightModeList(flightModeList)` |

Окремо — **ролі**: сім методів, кожен відповідає на питання «як у цій прошивці зветься режим для такої-от потреби». Усі типово віддають порожній рядок:

```cpp
virtual QString pauseFlightMode()           const { return QString(); }
virtual QString missionFlightMode()         const { return QString(); }
virtual QString rtlFlightMode()             const { return QString(); }
virtual QString smartRTLFlightMode()        const { return QString(); }
virtual QString landFlightMode()            const { return QString(); }
virtual QString takeOffFlightMode()         const { return QString(); }
virtual QString motorDetectionFlightMode()  const { return QString(); }
virtual QString stabilizedFlightMode()      const { return QString(); }
virtual QString takeControlFlightMode()     const { return QString(); }
virtual QString gotoFlightMode()            const { return QString(); }
virtual QString followFlightMode()          const { return QString(); }
virtual bool    supportsSmartRTL()          const { return false;     }
```

Порожній рядок означає «такої ролі в цій прошивці немає», і застосунок мовчки не пропонує відповідну дію. Помилки не буде — буде відсутня кнопка.

Службові члени, якими нащадок наповнює таблицю:

```cpp
protected:
    void _setModeEnumToModeStringMapping(FlightModeCustomModeMap enumToString)
        { _modeEnumToString = enumToString; }
    virtual uint32_t _convertToCustomFlightModeEnum(uint32_t val) const { return val; }
    void _updateFlightModeList(FlightModeList &flightModeList);
    void _addNewFlightMode(FirmwareFlightMode &flightMode);

    FlightModeList          _flightModeList;
    FlightModeCustomModeMap _modeEnumToString;
```

`_addNewFlightMode()` звіряє новий елемент зі списком **за `custom_mode`**, а не за ім'ям: повторне число мовчки відкидається із записом у журнал зневадження. Отже, два режими з різними іменами й однаковим числом у таблицю не потраплять обидва.

---

## Керовані дії

Усе, що виражається реченням «попросити апарат зробити X». Базовий клас на кожну з цих дій показує користувачеві повідомлення «Guided mode not supported by Vehicle» — типова поведінка не порожня й не аварійна, вона **пояснює відмову**.

```cpp
virtual void pauseVehicle(Vehicle *vehicle) const;
virtual void startTakeoff(Vehicle *vehicle) const;
virtual void startMission(Vehicle *vehicle) const;
virtual void guidedModeRTL(Vehicle *vehicle, bool smartRTL) const;
virtual void guidedModeLand(Vehicle *vehicle) const;
virtual void guidedModeTakeoff(Vehicle *vehicle, double takeoffAltRel) const;
virtual void guidedModeChangeHeading(Vehicle *vehicle, const QGeoCoordinate &headingCoord) const;
virtual void guidedModeChangeAltitude(Vehicle *vehicle, double altitudeChange, bool pauseVehicle);
virtual void guidedModeChangeGroundSpeedMetersSecond(Vehicle *vehicle, double groundspeed) const;
virtual void guidedModeChangeEquivalentAirspeedMetersSecond(Vehicle *vehicle, double airspeed_equiv) const;
virtual bool guidedModeGotoLocation(Vehicle *vehicle, const QGeoCoordinate &gotoCoord,
                                    double forwardFlightLoiterRadius = 0.0) const;
```

Дві сигнатури тут вибиваються з ряду, і обидва відхилення змістовні. `guidedModeGotoLocation()` єдина повертає `bool` — координата може бути неприйнятною (наприклад, поза геозоною), і про це треба сказати одразу, до надсилання. `guidedModeChangeAltitude()` єдина **не `const`**: зміна висоти веде за собою перехід у режим утримання, тобто плагін тут чіпає стан.

Аргумент `forwardFlightLoiterRadius` осмислений лише для літака: мультикоптер зависає над точкою, а літак мусить крутитися навколо неї колом заданого радіуса.

Обмеження, які станція показує повзунками:

| Сигнатура | Типова відповідь |
|---|---|
| `virtual double minimumTakeoffAltitudeMeters(Vehicle*) const` | `3.048` — рівно 10 футів |
| `virtual double maximumHorizontalSpeedMultirotorMetersSecond(Vehicle*) const` | `NAN` |
| `virtual double maximumEquivalentAirspeed(Vehicle*) const` | `NAN` |
| `virtual double minimumEquivalentAirspeed(Vehicle*) const` | `NAN` |
| `virtual bool mulirotorSpeedLimitsAvailable(Vehicle*) const` | `false` (⚠ друкарська помилка в імені — саме `muli`) |
| `virtual bool fixedWingAirSpeedLimitsAvailable(Vehicle*) const` | `false` |

`NAN` тут — домовлений маркер «межі невідомі», а не «нуль»; звіряти його треба через `qIsNaN()`, бо порівняння `== NAN` завжди хибне.

---

## Гачки на потоці MAVLink

```cpp
virtual bool adjustIncomingMavlinkMessage(Vehicle* /*vehicle*/, mavlink_message_t* /*message*/)
{ return true; }

virtual void adjustOutgoingMavlinkMessageThreadSafe(Vehicle* /*vehicle*/, LinkInterface* /*outgoingLink*/,
                                                    mavlink_message_t* /*message*/)
{ }
```

| Гачок | Повертає | Потік виконання | Що можна |
|---|---|---|---|
| `adjustIncomingMavlinkMessage` | `bool` — `false` **ковтає** повідомлення | потік інтерфейсу | правити повідомлення на місці, перезбирати його, відкидати |
| `adjustOutgoingMavlinkMessageThreadSafe` | нічого | **потік каналу** | правити повідомлення перед відправленням |

Суфікс `ThreadSafe` в імені — не оздоба, а попередження: другий гачок виконується не там, де живе інтерфейс, тож усе, до чого він торкається, мусить бути захищене. Розподіл потоків описано в [моделі потоків](book:qgroundcontrol/threading-model). Найвідоміше застосування пари — [параметри MAVLink](book:communications/mavlink-parameters) від ArduPilot, який пакує будь-яке значення в поле дійсного числа всупереч специфікації: вхідний гачок перезбирає `PARAM_VALUE` за стандартом, вихідний псує `PARAM_SET` назад.

---

## Ініціалізація, версія, метадані

```cpp
virtual void initializeVehicle(Vehicle* /*vehicle*/) {}
virtual bool sendHomePositionToVehicle() const { return false; }
virtual void adjustMetaData(MAV_TYPE /*vehicleType*/, FactMetaData* /*metaData*/) {}
virtual AutoPilotPlugin *autopilotPlugin(Vehicle *vehicle) const;   // → new GenericAutoPilotPlugin
virtual QMap<QString, FactGroup*> *factGroups() { return nullptr; }
virtual QString offlineEditingParamFile(Vehicle*) const { return QString(); }
```

`initializeVehicle()` виконується **рівно один раз**, коли створюється об'єкт [апарата](book:qgroundcontrol/vehicle-object). Саме сюди кладуть запит [частот потоків](book:communications/stream-rates) для прошивок, які самі нічого не надсилають, поки їх не попросять.

Метадані параметрів і звірка версії:

```cpp
ParameterMetaData *loadParameterMetaData(const Vehicle *vehicle);   // НЕ віртуальний — готовий збирач
void cacheParameterMetaDataFile(const QString &metaDataFile);

protected:
    virtual ParameterMetaData *_createParameterMetaData() { return nullptr; }
    virtual QString _internalParameterMetaDataFile(const Vehicle*) const { return QString(); }
    QString         _cachedParameterMetaDataFile(const Vehicle *vehicle) const;
    virtual QString _getLatestVersionFileUrl(Vehicle*) const { return QString(); }
    virtual QString _versionRegex() const { return QString(); }
    virtual void    _versionFileDownloadFinished(const QString &remoteFile, const QString &localFile,
                                                 const Vehicle *vehicle) const;
    virtual MAV_AUTOPILOT _autopilotType() const { return MAV_AUTOPILOT_GENERIC; }
```

Перевизначати треба два постачальники — `_createParameterMetaData()` і `_internalParameterMetaDataFile()`, — а не сам `loadParameterMetaData()`: він уже вміє вибрати між завантаженим кешем і вбудованим файлом. Що з цими описами робить далі станція — у [менеджері параметрів](book:qgroundcontrol/parameter-manager) і [фактовій системі](book:qgroundcontrol/fact-system).

Порівняння версій — звичайні методи, не віртуальні, з домовленим тризначним результатом:

```cpp
int versionCompare(const Vehicle *vehicle, const QString &compare) const;
int versionCompare(const Vehicle *vehicle, int major, int minor, int patch) const;
```

| Результат | Означає |
|---|---|
| `1` | версія на борту **новіша** за подану |
| `0` | версії збігаються точно |
| `-1` | версія на борту **старіша** за подану |

Порівняння лексикографічне за трійкою «мажорна · мінорна · латка», тож `4.10.0` правильно вважається новішою за `4.9.9`.

---

## Дрейф імен параметрів

```cpp
virtual const remapParamNameMajorVersionMap_t &paramNameRemapMajorVersionMap() const;  // базово — порожня статична мапа
virtual int remapParamNameHigestMinorVersionNumber(int /*majorVersionNumber*/) const
{ return VehicleTypes::versionNotSetValue; }
```

Форма мапи на прикладі перейменування, зробленого в ArduCopter 4.0:

```cpp
remapParamNameMajorVersionMap_t map;
map[4][0]["TUNE_MIN"] = "TUNE_LOW";     // мажорна 4 → мінорна 0 → старе ім'я → нове
map[4][0]["TUNE_MAX"] = "TUNE_HIGH";
// …
int remapParamNameHigestMinorVersionNumber(int majorVersionNumber) const override
{ return (majorVersionNumber == 4) ? 7 : VehicleTypes::versionNotSetValue; }
```

Другий метод не декоративний: станція прокручує ланцюжок перейменувань від версії файлу до версії борту, і межу цього прокручування задає саме найбільший відомий мінорний номер. Помилка в ньому не дає збою — вона мовчки лишає частину імен неперекладеними, тож збережений торік файл параметрів застосується частково. Ім'я методу містить друкарську помилку (`Higest` замість `Highest`) і в апстримі не виправлене.

---

## Місії, вигляд і дрібні можливості

```cpp
virtual QList<MAV_CMD> supportedMissionCommands(QGCMAVLinkTypes::VehicleClass_t) const
{ return QList<MAV_CMD>(); }
virtual QString missionCommandOverrides(QGCMAVLinkTypes::VehicleClass_t vehicleClass) const;
```

Порожній список від `supportedMissionCommands()` означає «обмежень немає» — тобто дозволено все дерево команд, а не «нічого не дозволено». `missionCommandOverrides()` віддає шлях до JSON-накладки на клас апарата; базова реалізація вже має гілку на кожен із шести класів.

Решта контракту — компактно, з типовими відповідями:

| Сигнатура | Типово |
|---|---|
| `virtual int defaultJoystickTXMode() const` | `2` |
| `virtual bool supportsThrottleModeCenterZero() const` | `true` |
| `virtual bool supportsNegativeThrust(Vehicle*) const` | `false` |
| `virtual bool supportsRadio() const` | `true` |
| `virtual bool supportsJSButton() const` | `false` |
| `virtual bool supportsMotorInterference() const` | `true` |
| `virtual bool multiRotorCoaxialMotors(Vehicle*) const` | `false` |
| `virtual bool multiRotorXConfig(Vehicle*) const` | `false` |
| `virtual bool hasGripper(const Vehicle*) const` | `false` |
| `virtual QString vehicleImageOpaque(const Vehicle*) const` | `"/qmlimages/vehicleArrowOpaque.svg"` |
| `virtual QString vehicleImageOutline(const Vehicle*) const` | `"/qmlimages/vehicleArrowOutline.svg"` |
| `virtual QVariant expandedToolbarIndicatorSource(const Vehicle*, const QString&) const` | `QVariant()` |
| `virtual uint32_t highLatencyCustomModeTo32Bits(uint16_t hlCustomMode) const` | `hlCustomMode` — просте розширення |
| `virtual QString getHobbsMeter(Vehicle*) const` | `"Not Supported"` |
| `virtual QString autoDisarmParameter(Vehicle*) const` | `QString()` |
| `virtual QMap<QString, FactGroup*> *factGroups()` | `nullptr` |

Оголошені без вбудованого тіла (реалізація в `FirmwarePlugin.cc`): `hasGimbal()`, `batteryConsumptionData()`, `sendGCSMotionReport()`, `createCameraManager()`, `createCameraControl()`, `createAutotune()`, `checkIfIsLatestStable()`, `toolIndicators()`. Клас має один сигнал — `toolIndicatorsChanged()`.

`getHobbsMeter()` повертає **рядок `"Not Supported"`**, а не порожній рядок: цей текст ітиме просто на екран, тож перевіряти його на порожнечу марно.

---

## FirmwarePluginInstanceData: персональний стан борту

Плагін спільний для всіх апаратів свого класу й тому не має полів під конкретний борт. Те, що треба запам'ятати саме про цей апарат, живе в окремому об'єкті:

```cpp
class FirmwarePluginInstanceData : public QObject
{
    Q_OBJECT
public:
    using QObject::QObject;

    enum class CommandSupportedResult : uint8_t {
        SUPPORTED   = 23,
        UNSUPPORTED = 24,
        UNKNOWN     = 25,
    };

    /// true, якщо будь-яка версія прошивки колись підтримувала cmd —
    /// щоб не витрачати зайвий обмін із автопілотом на розвідку
    virtual CommandSupportedResult anyVersionSupportsCommand(MAV_CMD /*cmd*/) const
        { return CommandSupportedResult::UNKNOWN; }

    void setCommandSupported(MAV_CMD cmd, CommandSupportedResult status)
        { MAV_CMD_supported[cmd] = status; }
    CommandSupportedResult getCommandSupported(MAV_CMD cmd) const;

private:
    QMap<MAV_CMD, CommandSupportedResult> MAV_CMD_supported;
};
```

Логіка читання — двошарова, і порядок шарів важить:

```cpp
CommandSupportedResult FirmwarePluginInstanceData::getCommandSupported(MAV_CMD cmd) const
{
    if (anyVersionSupportsCommand(cmd) == CommandSupportedResult::UNSUPPORTED) {
        return CommandSupportedResult::UNSUPPORTED;
    }
    return MAV_CMD_supported.value(cmd, CommandSupportedResult::UNKNOWN);
}
```

Статичне знання «жодна версія цієї прошивки такого не вміла» перекриває будь-що накопичене й економить [команду](book:communications/mavlink-commands) з очікуванням підтвердження. Якщо ж такого знання немає, відповідь беруть із мапи, наповненої з отриманих `COMMAND_ACK`, а типовий `UNKNOWN` означає «ще не питали».

Дивні числа `23`, `24`, `25` — не бітові прапорці й не номери MAVLink: це навмисно неприродні значення, щоб нульова або незаповнена пам'ять не читалася як осмислена відповідь.

Прив'язка до апарата, з коментарем апстриму:

```cpp
// Vehicle.h
FirmwarePlugin *firmwarePlugin() { return _firmwarePlugin; }
class FirmwarePluginInstanceData *firmwarePluginInstanceData() { return _firmwarePluginInstanceData; }
/// This object will be parented to the Vehicle and destroyed when the vehicle goes away.
void setFirmwarePluginInstanceData(FirmwarePluginInstanceData *firmwarePluginInstanceData);
```

Створює об'єкт сам плагін, і робить це **ліниво**, звіряючи наявний — саме тому повторний виклик нічого не затирає:

```cpp
// APMFirmwarePlugin::initializeStreamRates(), спрощено
auto instanceData = qobject_cast<APMFirmwarePluginInstanceData*>(vehicle->firmwarePluginInstanceData());
if (!instanceData) {
    instanceData = new APMFirmwarePluginInstanceData(vehicle);
    instanceData->lastBatteryStatusTime = instanceData->lastHomePositionTime = QTime::currentTime();
    vehicle->setFirmwarePluginInstanceData(instanceData);
}
```

Приведення через `qobject_cast` тут обов'язкове: сховище оголошене базовим типом, а поля лежать у нащадку.

---

## Контракт реєстрації

```cpp
class FirmwarePluginFactory : public QObject
{
    Q_OBJECT
public:
    explicit FirmwarePluginFactory(QObject *parent = nullptr);   // ← сам себе реєструє
    virtual ~FirmwarePluginFactory();

    virtual FirmwarePlugin *firmwarePluginForAutopilot(MAV_AUTOPILOT autopilotType,
                                                       MAV_TYPE vehicleType) = 0;
    virtual QList<QGCMAVLink::FirmwareClass_t> supportedFirmwareClasses() const = 0;
    virtual QList<QGCMAVLink::VehicleClass_t>  supportedVehicleClasses() const
        { return QGCMAVLink::allVehicleClasses(); }
};

class FirmwarePluginFactoryRegister : public QObject
{
    Q_OBJECT
public:
    static FirmwarePluginFactoryRegister *instance();            // Q_GLOBAL_STATIC усередині
    void registerPluginFactory(FirmwarePluginFactory *pluginFactory)
        { _factoryList.append(pluginFactory); }
    QList<FirmwarePluginFactory*> pluginFactories() const { return _factoryList; }
private:
    QList<FirmwarePluginFactory*> _factoryList;
};
```

| Член | Обов'язковість | Примітка |
|---|---|---|
| `firmwarePluginForAutopilot()` | чисто віртуальний | `nullptr` — законна відповідь «це не моє» |
| `supportedFirmwareClasses()` | чисто віртуальний | за цим списком менеджер шукає фабрику |
| `supportedVehicleClasses()` | типово всі шість | заповнює екран вибору апарата для офлайн-редагування |
| конструктор `FirmwarePluginFactory` | — | тіло: `FirmwarePluginFactoryRegister::instance()->registerPluginFactory(this);` |

Хто кого шукає:

```cpp
// FirmwarePluginManager
static FirmwarePluginManager *instance();
QList<QGCMAVLink::FirmwareClass_t> supportedFirmwareClasses();
QList<QGCMAVLink::VehicleClass_t>  supportedVehicleClasses(QGCMAVLink::FirmwareClass_t firmwareClass);
FirmwarePlugin *firmwarePluginForAutopilot(MAV_AUTOPILOT firmwareType, MAV_TYPE vehicleType);
private:
    FirmwarePluginFactory *_findPluginFactory(QGCMAVLink::FirmwareClass_t firmwareClass);
    FirmwarePlugin        *_genericFirmwarePlugin = nullptr;
```

Запасний варіант — не окремий клас, а **сам базовий**: коли жодна фабрика не відгукнулася, менеджер створює `new FirmwarePlugin(this)` й кешує його в `_genericFirmwarePlugin`. Тобто типові значення з таблиць вище — це не абстракція, а буквально поведінка станції з незнайомим автопілотом.

### Мінімальна робоча реєстрація

Найкоротший код, після якого станція справді почне звертатися до власного плагіна:

```cpp
// MyFirmwarePluginFactory.h
class MyFirmwarePluginFactory : public FirmwarePluginFactory
{
    Q_OBJECT
public:
    explicit MyFirmwarePluginFactory(QObject *parent = nullptr)
        : FirmwarePluginFactory(parent) {}        // реєстрація — у базовому конструкторі

    QList<QGCMAVLink::FirmwareClass_t> supportedFirmwareClasses() const override
        { return { QGCMAVLink::FirmwareClassPX4 }; }

    QList<QGCMAVLink::VehicleClass_t> supportedVehicleClasses() const override
        { return { QGCMAVLink::VehicleClassMultiRotor }; }

    FirmwarePlugin *firmwarePluginForAutopilot(MAV_AUTOPILOT autopilotType,
                                               MAV_TYPE vehicleType) override
    {
        if (autopilotType != MAV_AUTOPILOT_PX4) { return nullptr; }
        if (QGCMAVLink::vehicleClass(vehicleType) != QGCMAVLink::VehicleClassMultiRotor) {
            return nullptr;
        }
        if (!_pluginInstance) { _pluginInstance = new MyFirmwarePlugin(this); }
        return _pluginInstance;                   // ОДИН примірник на всі апарати класу
    }
private:
    MyFirmwarePlugin *_pluginInstance = nullptr;
};
```

```cpp
// MyFirmwarePluginFactory.cc — об'єкт файлової області, створюється до main()
MyFirmwarePluginFactory MyFirmwarePluginFactory_instance(nullptr);
```

Апстрим пише цей рядок так, що ім'я об'єкта збігається з іменем класу — `PX4FirmwarePluginFactory PX4FirmwarePluginFactory;` і `APMFirmwarePluginFactory APMFirmwarePluginFactory(nullptr);`. Мовою це дозволено, але після такого рядка ім'я в цій одиниці трансляції означає вже об'єкт, а не тип, і наступна спроба написати `PX4FirmwarePluginFactory *p;` у тому ж файлі не збереться. У власному коді безпечніше давати об'єктові окреме ім'я.

Головна вимога до конструктора фабрики — **порожнеча**. Він виконується до `main()`, а порядок створення таких об'єктів у різних одиницях трансляції стандарт не визначає ([static initialization order fiasco](book:programming/cpp-static-init-order)). Звернення звідти до налаштувань, журналу чи будь-якого іншого сінглтона дає падіння, що відтворюється через раз і залежить від порядку компонування.

> 🔧 **Навіщо це.** Перевіряти реєстрацію найзручніше не зневаджувачем, а `FirmwarePluginManager::instance()->supportedFirmwareClasses()`: якщо власного класу в списку немає, проблема не в логіці добору, а в тому, що об'єкт фабрики не потрапив у бінарник. Найчастіша причина — компонувальник викинув одиницю трансляції, з якої ніхто нічого не викликає. Файл із фабрикою має бути в переліку джерел цілі, а не в статичній бібліотеці, з якої береться лише те, на що є посилання.

---

## Пастки контракту, помітні лише під час роботи

| Що зроблено | Що зламається | Чому мовчки |
|---|---|---|
| `isCapable()` не перевизначено | усі кнопки керованих дій неактивні | типова відповідь базового класу — `false` |
| режим доданий без `canBeSet = true` | режим видно в рядку стану, але його немає у списку вибору | обидва питання відповідає одна таблиця |
| режим доданий без `fixedWing = true` | на літаку режиму немає, на мультикоптері є | `multiRotor` типово `true`, `fixedWing` — `false` |
| два режими з однаковим `custom_mode` | у списку лишиться лише перший | `_addNewFlightMode()` звіряє числа, а не імена |
| роль (`rtlFlightMode()` тощо) не перевизначено | відповідна дія просто не пропонується | порожній рядок — законна відповідь «ролі немає» |
| `adjustIncomingMavlinkMessage()` повернув `false` не для того повідомлення | телеметрія або параметри тихо не оновлюються | штатні обробники просто не покликані |
| робота зі спільним станом у `adjustOutgoingMavlinkMessageThreadSafe()` | рідкісні падіння під навантаженням | гачок працює в потоці каналу, не в потоці інтерфейсу |
| межі швидкості звірено як `== NAN` | повзунки показують хибний діапазон | будь-яке порівняння з `NAN` хибне; треба `qIsNaN()` |
| поле дописано в базовий `FirmwarePluginInstanceData` | значення протікає між апаратами або взагалі не з'являється | сховище оголошене базовим типом; свої поля живуть у нащадку й дістаються через `qobject_cast` |
| фабрика покладається на типовий `supportedVehicleClasses()` | дирижабль і орбітальний апарат не обслуговуються | `allVehicleClasses()` віддає лише шість класів із дев'яти |
| конструктор фабрики звертається до сінглтона | падіння на старті, відтворюване через раз | об'єкт створюється до `main()`, порядок не визначений |
| файл фабрики зібрано в бібліотеку без прямих посилань | плагін ніколи не вибирається | компонувальник викидає одиницю трансляції разом із реєстрацією |

Знання, які прошивка вміє віддати про себе сама, поступово переїжджають на борт — і таблиці вище через це тоншають; найдалі цей рух зайшов у [відомостях про компонент](book:qgroundcontrol/component-information).
