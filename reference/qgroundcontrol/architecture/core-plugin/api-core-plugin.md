# 🔌 Контракт ядрового розширення: сигнатури, типові значення, змінні збірки

Тут зібрано повний перелік того, що QGroundControl віддає назовні через `QGCCorePlugin`: кожен віртуальний метод із типом повернення й аргументами, типова відповідь базового класу, місце в коді, звідки метод смикають, усі властивості `QGCOptions` і `QGCFlyViewOptions` з типовими значеннями, іменовані константи та змінні збірки, якими власна тека під'єднується до проєкту. Довідник потрібен, щоб перевизначати саме той метод, який справді викликається, і наперед знати, коли він виконається.

Звірено з гілкою `master` репозиторію `mavlink/qgroundcontrol` 1 серпня 2026 року. Чинна стабільна лінія на той день — 5.0.x: перший стабільний випуск 5.0.6 вийшов 11 липня 2025, останній стабільний — 5.0.8 від 9 жовтня 2025; 5.1 на ту дату існує кандидатом у випуск (v5.1.0-RC1, 30 липня 2026). Файли: `src/API/QGCCorePlugin.h`, `src/API/QGCCorePlugin.cc`, `src/API/QGCOptions.h`.

---

## Примірник і життєвий цикл

```cpp
explicit QGCCorePlugin(QObject *parent = nullptr);
virtual ~QGCCorePlugin();

static QGCCorePlugin *instance();      // НЕ віртуальний: розвилка всередині, на препроцесорі

virtual void init()    { }
virtual void cleanup() { }
```

| Метод | Типова поведінка | Хто викликає й коли |
|---|---|---|
| `instance()` | без `QGC_CUSTOM_BUILD` — `Q_APPLICATION_STATIC(QGCCorePlugin, …)`; з ним — `CUSTOMCLASS::instance()` | будь-який код застосунку, будь-коли; перший виклик і створює об'єкт |
| `init()` | нічого | `QGCApplication::_initQmlRootWindow()` — перед створенням QML-рушія |
| `cleanup()` | нічого | `QGCApplication::shutdown()` |

Порядок, який видно в `QGCApplication`: у `_initVideo()` стоїть окремий голий виклик `QGCCorePlugin::instance();` із коментарем, що розширення має існувати раніше за `VideoManager`. Тобто конструктор виконується **до** підняття підсистем, і покладатися в ньому нема на що: усе, що потребує готового застосунку, кладеться в `init()`.

```cpp
// QGCApplication.cc — фактичний порядок
_initVideo():            QGCCorePlugin::instance();                       // лише щоб об'єкт з'явився
_initQmlRootWindow():    QGCCorePlugin::instance()->init();
                         _qmlAppEngine = …->createQmlApplicationEngine(this);
                         …->createRootWindow(_qmlAppEngine);
shutdown():              QGCCorePlugin::instance()->cleanup();
```

---

## Налаштування й метадані

```cpp
virtual QGCOptions *options();
virtual int  defaultSettings() { return 0; }
virtual bool overrideSettingsGroupVisibility(const QString &name) { return true; }
virtual void adjustSettingMetaData(const QString &settingsGroup,
                                   FactMetaData &metaData,
                                   bool         &userVisible);
```

| Метод | Типова відповідь | Хто викликає й коли |
|---|---|---|
| `options()` | `_defaultOptions` — примірник базового `QGCOptions` | QML через властивість `QGroundControl.corePlugin.options`; C++-код підсистем напряму |
| `defaultSettings()` | `0` | QML, властивість `defaultSettings` (позначена `CONSTANT` — читається один раз) |
| `overrideSettingsGroupVisibility(name)` | `true` | конструктор `SettingsGroup::SettingsGroup(...)` — рівно один раз на групу налаштувань, у момент її створення |
| `adjustSettingMetaData(group, meta, userVisible)` | правки за платформою: ховає 3D-огляд на Android, підправляє типові значення палітри й телеметрії | наприкінці статичної `SettingsManager::adjustSettingMetaData(...)`, яку кличе конструктор `SettingsFact` — один раз на кожен факт налаштувань |

Ключове про `adjustSettingMetaData`: `metaData` приходить **не-константним посиланням**, тож типове значення, межі й видимість міняються на місці, ще до того, як з метаданих зробиться готовий факт. `userVisible` теж посилання — записане в нього `false` ховає одне налаштування, тоді як `overrideSettingsGroupVisibility` ховає цілу групу. Що таке факт і його метадані — у [фактовій системі](topic:qgroundcontrol/fact-system); де ці значення осідають між запусками — у [налаштуваннях](topic:qgroundcontrol/settings-persistence).

---

## Вигляд: рушій, вікно, палітра, сторінки

```cpp
virtual QQmlApplicationEngine *createQmlApplicationEngine(QObject *parent);
virtual void createRootWindow(QQmlApplicationEngine *qmlEngine);
virtual const QVariantList &analyzePages();
virtual const QVariantList &toolBarIndicators();
virtual const QmlObjectListModel *customMapItems();
virtual void paletteOverride(const QString &colorName,
                             QGCPalette::PaletteColorInfo_t &colorInfo);
virtual void factValueGridCreateDefaultSettings(FactValueGrid *factValueGrid);
virtual QString showAdvancedUIMessage() const;
```

| Метод | Типова відповідь | Хто викликає й коли |
|---|---|---|
| `createQmlApplicationEngine(parent)` | новий `QQmlApplicationEngine`, додано шлях імпорту `qrc:/qml`, зареєстровано менеджер джойстика як контекстну властивість | `QGCApplication::_initQmlRootWindow()` — один раз |
| `createRootWindow(engine)` | вантажить `qrc:/qml/QGroundControl/MainWindow.qml` | `QGCApplication::_initQmlRootWindow()`, одразу після рушія |
| `analyzePages()` | список із шести `QmlComponentInfo*`: перегляд логів (лише на настільних), бортові логи, геоприв'язка знімків, консоль MAVLink, оглядач MAVLink, вібрація | QML `AnalyzeView.qml` як `model` для `Repeater` |
| `toolBarIndicators()` | один елемент — `QUrl` на `qrc:/qml/QGroundControl/Toolbar/RTKGPSIndicator.qml` | QML панелі інструментів |
| `customMapItems()` | порожній `QmlObjectListModel` | QML-компонент `CustomMapItems`, що стоїть на карті польотного вигляду |
| `paletteOverride(name, info)` | нічого | `QGCPalette::_buildMap()` — **на кожен колір окремо**, з макросів `DECLARE_QGC_COLOR`, `DECLARE_QGC_NONTHEMED_COLOR`, `DECLARE_QGC_SINGLE_COLOR` |
| `factValueGridCreateDefaultSettings(grid)` | базові налаштування сітки значень | `FactValueGrid::_resetFromSettings()` — коли збережених налаштувань немає або їхня версія непідтримувана |
| `showAdvancedUIMessage()` | англомовне попередження про вхід у розширений режим і ризик для гарантії | QML `MainWindow.qml`: `text: QGroundControl.corePlugin.showAdvancedUIMessage` |

Форма аргументів двох найтонших місць:

```cpp
// QGCPalette.h — що саме прилітає в paletteOverride
typedef QColor PaletteColorInfo_t[cMaxTheme][cMaxColorGroup];
//                                 Light|Dark   Disabled|Enabled

// QGCPalette.cc, макрос DECLARE_QGC_COLOR, спрощено до суті:
PaletteColorInfo_t colorInfo = { { QColor(lightDisabled), QColor(lightEnabled) },
                                 { QColor(darkDisabled),  QColor(darkEnabled)  } };
QGCCorePlugin::instance()->paletteOverride(#name, colorInfo);   // тут можна переписати будь-яку клітинку
_colorInfoMap[Light][ColorGroupEnabled][#name] = colorInfo[Light][ColorGroupEnabled];
// …далі всі чотири клітинки лягають у мапу палітри
```

Отже, `paletteOverride` дістає масив 2×2 **до** того, як він осів у палітрі, і міняє потрібні клітинки на місці; ім'я кольору — це рядок із першого аргументу макросу (`window`, `text`, `buttonHighlight`, `colorRed`, `brandingBlue` тощо).

Елемент `analyzePages()` мусить дати QML чотири поля — `title`, `url`, `icon`, `requiresVehicle`; саме це й пакує `QmlComponentInfo`:

```cpp
QVariant::fromValue(new QmlComponentInfo(
    tr("Onboard Logs"),
    QUrl::fromUserInput(QStringLiteral("qrc:/qml/QGroundControl/AnalyzeView/OnboardLogs/OnboardLogPage.qml")),
    QUrl::fromUserInput(QStringLiteral("qrc:/qmlimages/OnboardLogIcon.svg")),
    nullptr, true /* requiresVehicle */))
```

---

## Фабрики підсистем

```cpp
virtual VideoReceiver *createVideoReceiver(QObject *parent);
virtual void          *createVideoSink(QQuickItem *widget, QObject *parent);
virtual void           releaseVideoSink(void *sink);
virtual QGeoPositionInfoSource *createPositionSource(QObject *parent) { return nullptr; }
```

| Метод | Типова відповідь | Хто викликає й коли |
|---|---|---|
| `createVideoReceiver(parent)` | `VideoBackend::createReceiver()` | `VideoManager::_createVideoReceivers()` |
| `createVideoSink(widget, parent)` | `VideoBackend::createSink()` | `VideoManager::_initVideoReceiver()` — `widget` це QML-елемент, у який ітиме картинка |
| `releaseVideoSink(sink)` | `VideoBackend::releaseSink()` | `VideoManager::cleanup()` |
| `createPositionSource(parent)` | `nullptr` | `QGCPositionManager::_setupPositionSources()` |

Дві особливості, через які тут найчастіше ламаються.

**Стертий тип приймальника.** `createVideoSink` повертає `void *`, бо конкретний тип належить відеорушію, а `src/API` його не бачить. Компілятор не перевіряє нічого: що створило розширення, те воно й мусить звільнити у `releaseVideoSink`, і жодна помилка типу не спливе на збірці. Що робить із цими об'єктами сама підсистема — у [відеопідсистемі](topic:qgroundcontrol/video-manager).

**`nullptr` тут не помилка, а вибір.** Менеджер позиції перевіряє відповідь і, коли її немає, іде до системного джерела:

```cpp
_defaultSource = QGCCorePlugin::instance()->createPositionSource(this);
if (_defaultSource) {
    _usingPluginSource = true;
} else {
    _defaultSource = QGeoPositionInfoSource::createDefaultSource(this);
    if (!_defaultSource) { /* джерела координат немає взагалі */ return; }
}
```

---

## Потік MAVLink

```cpp
virtual bool mavlinkMessage(Vehicle *vehicle, LinkInterface *link,
                            const mavlink_message_t &message) { return true; }
```

| Значення | Наслідок |
|---|---|
| `true` (типово) | повідомлення йде далі звичайним шляхом |
| `false` | `Vehicle::_mavlinkMessageReceived()` виходить негайно; жоден штатний обробник цього повідомлення не побачить |

Місце виклику всередині `Vehicle::_mavlinkMessageReceived()` — **після** того, як плагін прошивки вже мав нагоду підправити повідомлення, і **перед** протоколом рельєфу та рештою підсистем:

```cpp
// Give the Core Plugin access to all mavlink traffic
if (!QGCCorePlugin::instance()->mavlinkMessage(this, link, message)) {
    return;
}
```

Аргумент `message` — константне посилання, тож перехопити тут можна, а переписати вміст ні. Що таке об'єкт апарата, крізь який тече цей потік, — в [моделі апарата](topic:qgroundcontrol/vehicle-object).

---

## План місії: JSON-гачки, елементи, майстри

```cpp
virtual void preSaveToJson         (PlanMasterController *pController, QJsonObject &json)        { }
virtual void preSaveToMissionJson  (PlanMasterController *pController, QJsonObject &missionJson) { }
virtual void postSaveToMissionJson (PlanMasterController *pController, QJsonObject &missionJson) { }
virtual void postSaveToJson        (PlanMasterController *pController, QJsonObject &json)        { }
virtual void preLoadFromJson       (PlanMasterController *pController, QJsonObject &json)        { }
virtual void postLoadFromJson      (PlanMasterController *pController, QJsonObject &json)        { }

virtual QVariantList complexMissionItemNames(Vehicle *vehicle);
virtual ComplexMissionItem *createComplexMissionItem(const QString &complexItemType,
                                                     PlanMasterController *masterController,
                                                     bool flyView,
                                                     const QString &kmlOrShpFile = QString());
virtual QList<PlanCreator *> planCreators(PlanMasterController *planMasterController);
```

Порядок гачків у `PlanMasterController` — саме такий, і він важить, бо між парою «pre» і «post» об'єкт JSON встигає наповнитися штатними ключами:

| Операція | Послідовність викликів |
|---|---|
| `saveToJson()` | `preSaveToJson` → `preSaveToMissionJson` → `postSaveToMissionJson` → `postSaveToJson` |
| `loadFromFile()` | `preLoadFromJson` → `postLoadFromJson` |

Пара з іменем `…MissionJson` працює з вкладеним об'єктом місії, звичайна пара — з кореневим об'єктом усього плану. Обидва — не-константні посилання, тож власні ключі кладуться просто туди; чужа станція їх проігнорує. Що всередині цього файлу — у [моделі плану](topic:qgroundcontrol/plan-model).

| Метод | Типова відповідь | Хто викликає й коли |
|---|---|---|
| `complexMissionItemNames(vehicle)` | `Survey`, `CorridorScan`, а для мультироторів і конвертопланів іще `StructureScan` | `MissionController::complexMissionItems()` — коли інтерфейс будує меню «додати складний елемент» |
| `createComplexMissionItem(type, ctl, flyView, file)` | збирає `SurveyComplexItem`, `CorridorScanComplexItem`, `StructureScanComplexItem`, `FixedWingLandingComplexItem`, `VTOLLandingComplexItem` за рядком | `MissionController::insertComplexMissionItem()`, `insertComplexMissionItemFromKMLOrSHP()`, `_loadJsonMissionFileV2()` |
| `planCreators(ctl)` | чотири майстри: `SurveyPlanCreator`, `CorridorScanPlanCreator`, `StructureScanPlanCreator`, `BlankPlanCreator` | `PlanMasterController::_updatePlanCreatorsList()` |

Форма елемента списку назв — мапа рівно з двома ключами:

```cpp
QVariantMap entry;
entry[QStringLiteral("canonicalName")]  = QString(canonical);   // цим рядком прийде виклик фабрики
entry[QStringLiteral("translatedName")] = translated;           // це побачить користувач у меню
```

Саме `canonicalName` повертається потім у `complexItemType` фабрики, і саме він же лежить у збереженому файлі плану — тож при завантаженні `createComplexMissionItem` кличеться з тим самим рядком. Розбіжність в один символ між списком і фабрикою не помітить ні компілятор, ні збірка. Про самі елементи — в [елементах місії](topic:qgroundcontrol/mission-items).

---

## Підказки першого запуску

```cpp
virtual QList<int> firstRunPromptStdIds()    { return QList<int>({ kInitialSetupPromptId }); }
virtual QList<int> firstRunPromptCustomIds() { return QList<int>(); }
Q_INVOKABLE virtual QString firstRunPromptResource(int id) const;
Q_INVOKABLE QVariantList firstRunPromptsToShow();       // НЕ віртуальний
```

| Метод | Типова відповідь | Хто викликає |
|---|---|---|
| `firstRunPromptStdIds()` | `{ 3 }` — тобто сам лише `kInitialSetupPromptId` | `firstRunPromptsToShow()` |
| `firstRunPromptCustomIds()` | порожній список | `firstRunPromptsToShow()` |
| `firstRunPromptResource(id)` | для `kInitialSetupPromptId` — `/qml/QGroundControl/FirstRunPromptDialogs/InitialSetupPrompt.qml`; інакше порожній рядок | QML `MainWindow.qml`, через `Qt.createComponent(...)` |
| `firstRunPromptsToShow()` | обидва списки, з яких викинуто вже показані ідентифікатори | QML `MainWindow.qml` |

`firstRunPromptsToShow()` навмисно **не віртуальний** — це готова логіка, яка складає два списки й віднімає показане:

```cpp
QVariantList QGCCorePlugin::firstRunPromptsToShow()
{
    QList<int> rgIdsToShow;
    rgIdsToShow.append(firstRunPromptStdIds());
    rgIdsToShow.append(firstRunPromptCustomIds());

    const QList<int> rgAlreadyShownIds = AppSettings::firstRunPromptsIdsVariantToList(
        SettingsManager::instance()->appSettings()->firstRunPromptIdsShown()->rawValue());
    for (int idToRemove: rgAlreadyShownIds) {
        (void) rgIdsToShow.removeOne(idToRemove);
    }
    …
}
```

Перевизначати треба два постачальники списків і мапу «ідентифікатор → QML-файл», а не сам збирач. Пам'ять про показане живе в налаштуванні `firstRunPromptIdsShown`.

---

## Джойстик, камера, перевірка версії

```cpp
struct JoystickAction { QString name; bool canRepeat = false; };
virtual QList<JoystickAction> joystickActions() { return {}; }

virtual bool getOfflineCameraDefinitionFile(const QString &cameraName, QFile &file) { return false; }

virtual QString stableVersionCheckFileUrl() const;
virtual QString stableDownloadLocation() const { return QStringLiteral("qgroundcontrol.com"); }
```

| Метод | Типова відповідь | Хто викликає й коли |
|---|---|---|
| `joystickActions()` | порожній список | `Joystick::_buildAvailableButtonsActionList()` — назви лягають у перелік дій, які користувач вішає на кнопки |
| `getOfflineCameraDefinitionFile(name, file)` | `false` | `VehicleCameraControl::_dataReady()` — коли опис камери не приїхав мережею; `true` означає «файл відкрито, беріть звідси» |
| `stableVersionCheckFileUrl()` | у власній збірці — **порожній рядок**; в апстримі — `https://s3-us-west-2.amazonaws.com/qgroundcontrol/latest/QGC.version.txt` | `QGCApplication::_checkForNewVersion()` |
| `stableDownloadLocation()` | `qgroundcontrol.com` | текст повідомлення про нову версію |

Дві деталі. По-перше, `stableVersionCheckFileUrl()` — єдиний метод, чиє **типове тіло вже розрізняє збірки** через `#ifdef QGC_CUSTOM_BUILD`: порожній рядок вимикає перевірку оновлень, щоб покупцеві чужого продукту не пропонували завантажити апстрим. По-друге, `JoystickAction::canRepeat` у власних дій зараз лише зберігає перемикач повтору в інтерфейсі — саме повторне надсилання для дій розширення не підтримане, бо диспетчер несе тільки перехід кнопки вниз.

---

## Стан, сигнали, константи

```cpp
bool showTouchAreas() const { return _showTouchAreas; }   // читання — публічне
bool showAdvancedUI() const { return _showAdvancedUI; }   // запис — приватний, лише через Q_PROPERTY із QML

signals:
    void showTouchAreasChanged(bool showTouchAreas);
    void showAdvancedUIChanged(bool showAdvancedUI);

protected:
    bool _showTouchAreas = false;
    bool _showAdvancedUI = true;      // ⚠ в апстримі розширений режим УВІМКНЕНО

static constexpr int kInitialSetupPromptId          = 3;
static constexpr int kFirstRunPromptIdsFirstCustomId = 10000;
```

| Константа | Значення | Що означає |
|---|---|---|
| `kInitialSetupPromptId` | `3` | ідентифікатор єдиної штатної підказки першого запуску; видно з QML як `initialSetupPromptId` |
| `kFirstRunPromptIdsFirstCustomId` | `10000` | нижня межа діапазону, відрізаного для підказок виробника; апстрим обіцяє не заходити вище, тож нові штатні підказки ніколи не зіткнуться номером із власними |

Типове `_showAdvancedUI = true` варте окремої уваги: апстримова збірка стартує вже в розширеному режимі, а замикає його саме виробник у своєму конструкторі — `_showAdvancedUI = false;`. Хто цього не зробить, отримає повний доступ до всіх екранів попри всі перевизначені прапорці.

Повний перелік властивостей, які клас віддає в QML:

| Q_PROPERTY | Тип | Доступ |
|---|---|---|
| `showAdvancedUI` | `bool` | читання й запис, `NOTIFY showAdvancedUIChanged` |
| `showTouchAreas` | `bool` | читання й запис, `NOTIFY showTouchAreasChanged` |
| `defaultSettings` | `int` | `CONSTANT` |
| `initialSetupPromptId` | `int` | `CONSTANT` (`MEMBER kInitialSetupPromptId`) |
| `options` | `const QGCOptions *` | `CONSTANT` |
| `customMapItems` | `const QmlObjectListModel *` | `CONSTANT` |
| `showAdvancedUIMessage` | `QString` | `CONSTANT` |
| `analyzePages` | `QVariantList` | `CONSTANT` |
| `toolBarIndicators` | `QVariantList` | `CONSTANT` |

Клас позначено `QML_UNCREATABLE("")`: створити його з QML не можна, дістатися до примірника — тільки через глобальний об'єкт `QGroundControl.corePlugin`.

---

## QGCOptions: усі властивості й типові значення

Кожен рядок — віртуальний `const`-метод у `QGCOptions`, водночас доступний із QML під тим самим ім'ям (`QGroundControl.corePlugin.options.<ім'я>`). Стовпчик «сповіщення» показує, чи має властивість сигнал зміни: `CONSTANT` означає, що QML прочитає її один раз і більше ніколи не перепитає — динамічне перемикання таких прапорців у роботі не дасть нічого.

| Метод | Тип | Типово | Сповіщення |
|---|---|---|---|
| `allowJoystickSelection()` | `bool` | `true` | `allowJoystickSelectionChanged` |
| `checkFirmwareVersion()` | `bool` | `true` | `CONSTANT` |
| `combineSettingsAndSetup()` | `bool` | `false` | `CONSTANT` |
| `enableSaveMainWindowPosition()` | `bool` | `true` | `CONSTANT` |
| `guidedActionsRequireRCRSSI()` | `bool` | `false` | `CONSTANT` |
| `missionWaypointsOnly()` | `bool` | `false` | `missionWaypointsOnlyChanged` |
| `multiVehicleEnabled()` | `bool` | `true` | `multiVehicleEnabledChanged` |
| `sensorsHaveFixedOrientation()` | `bool` | `false` | `CONSTANT` |
| `showFirmwareUpgrade()` | `bool` | `true` | `showFirmwareUpgradeChanged` |
| `showMissionAbsoluteAltitude()` | `bool` | `true` | `showMissionAbsoluteAltitudeChanged` |
| `showMissionStatus()` | `bool` | `true` | `CONSTANT` |
| `showOfflineMapExport()` | `bool` | `true` | `showOfflineMapExportChanged` |
| `showOfflineMapImport()` | `bool` | `true` | `showOfflineMapImportChanged` |
| `showPX4LogTransferOptions()` | `bool` | `true` | `CONSTANT` |
| `showSensorCalibrationAccel()` | `bool` | `true` | `showSensorCalibrationAccelChanged` |
| `showSensorCalibrationAirspeed()` | `bool` | `true` | `showSensorCalibrationAirspeedChanged` |
| `showSensorCalibrationCompass()` | `bool` | `true` | `showSensorCalibrationCompassChanged` |
| `showSensorCalibrationGyro()` | `bool` | `true` | `showSensorCalibrationGyroChanged` |
| `showSensorCalibrationLevel()` | `bool` | `true` | `showSensorCalibrationLevelChanged` |
| `showSimpleMissionStart()` | `bool` | `false` | `showSimpleMissionStartChanged` |
| `useMobileFileDialog()` | `bool` | `true` на Android та iOS, `false` на настільних | `CONSTANT` |
| `toolbarHeightMultiplier()` | `double` | `1.0` | `CONSTANT` |
| `devicePixelDensity()` | `float` | `0.0f` | `devicePixelDensityChanged` |
| `devicePixelRatio()` | `float` | `0.0f` | `devicePixelRatioChanged` |
| `firmwareUpgradeSingleURL()` | `QString` | порожній рядок | `CONSTANT` |
| `surveyBuiltInPresetNames()` | `QStringList` | порожній список | `CONSTANT` |
| `preFlightChecklistUrl()` | `QUrl` | `qrc:/qml/QGroundControl/FlyView/PreFlightCheckList.qml` | `CONSTANT` |
| `flyViewOptions()` | `const QGCFlyViewOptions *` | `_defaultFlyViewOptions` | `CONSTANT`, у QML зветься `flyView` |

Два методи є в класі, але **не виведені в QML** — читає їх лише C++:

| Метод | Тип | Типово |
|---|---|---|
| `toolbarBackgroundLight()` | `QColor` | `QColorConstants::White` |
| `toolbarBackgroundDark()` | `QColor` | `QColorConstants::Black` |

Нуль у `devicePixelRatio()` і `devicePixelDensity()` — це не «нульовий масштаб», а домовлений маркер «нічого не нав'язую, беріть системне значення».

---

## QGCFlyViewOptions: польотний вигляд

Вкладений об'єкт, який віддає `QGCOptions::flyViewOptions()`. Особливість, через яку буває плутанина: всі методи оголошені в секції **`protected`** — перевизначити їх у нащадку можна, викликати ззовні з C++ ні; назовні вони видні тільки як властивості QML, бо moc обходить це обмеження.

| Метод | Тип | Типово | Сповіщення |
|---|---|---|---|
| `showMultiVehicleList()` | `bool` | `true` | `CONSTANT` |
| `showInstrumentPanel()` | `bool` | `true` | `CONSTANT` |
| `showMapScale()` | `bool` | `true` | `CONSTANT` |
| `guidedBarShowEmergencyStop()` | `bool` | `true` | `guidedBarShowEmergencyStopChanged` |
| `guidedBarShowOrbit()` | `bool` | `true` | `guidedBarShowOrbitChanged` |
| `guidedBarShowROI()` | `bool` | `true` | `guidedBarShowROIChanged` |

Читаються з QML так:

```qml
visible: QGroundControl.corePlugin.options.flyView.showMapScale && …
```

Конструктор бере власника: `QGCFlyViewOptions(QGCOptions *options, QObject *parent = nullptr)`.

---

## Мінімальне робоче перевизначення

Найкоротший клас, який уже щось міняє й нічого не ламає, — з `custom-example`:

```cpp
// CustomPlugin.h
class CustomFlyViewOptions : public QGCFlyViewOptions
{
    Q_OBJECT
public:
    explicit CustomFlyViewOptions(CustomOptions *options, QObject *parent = nullptr);
protected:
    bool showInstrumentPanel() const final { return false; }
    bool showMultiVehicleList() const final { return false; }
};

class CustomOptions : public QGCOptions
{
    Q_OBJECT
public:
    explicit CustomOptions(CustomPlugin *plugin, QObject *parent = nullptr);
    // прапорець дивиться на стан, а не на константу
    bool showFirmwareUpgrade() const final { return _plugin->showAdvancedUI(); }
    const QGCFlyViewOptions *flyViewOptions() const final { return _flyViewOptions; }
private:
    CustomPlugin        *_plugin        = nullptr;
    CustomFlyViewOptions *_flyViewOptions = nullptr;
};

class CustomPlugin : public QGCCorePlugin
{
    Q_OBJECT
public:
    explicit CustomPlugin(QObject *parent = nullptr);
    static QGCCorePlugin *instance();          // обов'язково: саме це кличе CUSTOMCLASS::instance()
    QGCOptions *options() final { return _options; }
private:
    CustomOptions *_options = nullptr;
};
```

```cpp
// CustomPlugin.cc
Q_APPLICATION_STATIC(CustomPlugin, _customPluginInstance);

QGCCorePlugin *CustomPlugin::instance() { return _customPluginInstance(); }

CustomPlugin::CustomPlugin(QObject *parent)
    : QGCCorePlugin(parent)
    , _options(new CustomOptions(this, this))
{
    _showAdvancedUI = false;     // без цього рядка збірка лишиться «розширеною»
    (void) connect(this, &QGCCorePlugin::showAdvancedUIChanged,
                   this, &CustomPlugin::_advancedChanged);
}
```

Підміна QML-ресурсів вимагає лише одного перевизначення й обов'язкового прибирання за собою:

```cpp
QQmlApplicationEngine *CustomPlugin::createQmlApplicationEngine(QObject *parent)
{
    _qmlEngine = QGCCorePlugin::createQmlApplicationEngine(parent);   // спершу базовий!
    _qmlEngine->addImportPath("qrc:/qml/Custom/Widgets");
    _selector = new CustomOverrideInterceptor();
    _qmlEngine->addUrlInterceptor(_selector);
    return _qmlEngine;
}

void CustomPlugin::cleanup()
{
    if (_qmlEngine) { _qmlEngine->removeUrlInterceptor(_selector); }
    delete _selector;
}
```

Три правила видно просто з коду: базову реалізацію викликають першою й доробляють її результат; перехоплювач адрес ставлять до завантаження першого екрана; знятий у `cleanup()` перехоплювач — не формальність, бо рушій переживає розширення.

---

## Змінні збірки

Розвилка «типовий клас чи виробників» вирішується цілком у CMake, до першого рядка компіляції.

**Крок 1 — виявлення теки.** Кореневий `CMakeLists.txt`:

```cmake
if(IS_DIRECTORY "${CMAKE_SOURCE_DIR}/${QGC_CUSTOM_DIR}")
    message(STATUS "QGC: Custom build directory detected: ${QGC_CUSTOM_DIR}")
    set(QGC_CUSTOM_BUILD ON)
    list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/${QGC_CUSTOM_DIR}/cmake")
    include(CustomOverrides)
endif()
…
if(QGC_CUSTOM_BUILD)
    add_subdirectory("${QGC_CUSTOM_DIR}")
endif()
```

| Змінна | Де задана | Типово | Роль |
|---|---|---|---|
| `QGC_CUSTOM_DIR` | `cmake/CustomOptions.cmake`, `CACHE STRING` | `custom` | тека власної збірки відносно кореня джерел; сама її наявність вмикає режим |
| `QGC_CUSTOM_BUILD` | ставиться в `ON` автоматично, коли тека знайдена | вимкнено | і змінна CMake, і (через `CUSTOM_DEFINITIONS`) макрос препроцесора |
| `CustomOverrides` | модуль `${QGC_CUSTOM_DIR}/cmake/CustomOverrides.cmake` | — | перевизначає бренд: `QGC_APP_NAME`, `QGC_ANDROID_PACKAGE_NAME`, шляхи до значків, прапорці на кшталт `QGC_DISABLE_APM_PLUGIN` |

**Крок 2 — п'ять змінних-каналів.** Підпроєкт виробника наповнює їх, а `src/CMakeLists.txt` без жодного знання про вміст роздає їх цілі:

| Змінна | Що з нею робить `src/CMakeLists.txt` |
|---|---|
| `CUSTOM_DEFINITIONS` | `target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE …)` |
| `CUSTOM_SOURCES` | `target_sources(${CMAKE_PROJECT_NAME} PRIVATE …)` |
| `CUSTOM_LIBRARIES` | `target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE …)` |
| `CUSTOM_INCLUDE_DIRECTORIES` | `target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE …)` |
| `CUSTOM_QT_COMPONENTS` | `find_package(Qt6 REQUIRED COMPONENTS …)` |

Усі п'ять блоків лежать усередині спільного `if(QGC_CUSTOM_BUILD)`, а кожен ще й під власним `if(<змінна>)`, тож незаповнена змінна просто нічого не додає, а в апстримовій збірці не спрацьовує жоден із них.

**Крок 3 — три визначення, які й роблять підстановку:**

```cmake
# custom-example/CMakeLists.txt
set(CUSTOM_DEFINITIONS
    QGC_CUSTOM_BUILD
    CUSTOMHEADER="CustomPlugin.h"
    CUSTOMCLASS=CustomPlugin
    CACHE INTERNAL "" FORCE
)
```

| Макрос | Тип | Куди підставляється |
|---|---|---|
| `QGC_CUSTOM_BUILD` | без значення | `#ifdef` у `QGCCorePlugin.cc` і в тілі `stableVersionCheckFileUrl()` |
| `CUSTOMHEADER` | рядок із лапками | `#include CUSTOMHEADER` у `QGCCorePlugin.cc` |
| `CUSTOMCLASS` | голе ім'я класу | `return CUSTOMCLASS::instance();` у `QGCCorePlugin::instance()` |

```cpp
// src/API/QGCCorePlugin.cc — після підстановки препроцесора
#ifdef QGC_CUSTOM_BUILD
#include CUSTOMHEADER
#endif

#ifndef QGC_CUSTOM_BUILD
Q_APPLICATION_STATIC(QGCCorePlugin, _qgcCorePluginInstance);
#endif

QGCCorePlugin *QGCCorePlugin::instance()
{
#ifndef QGC_CUSTOM_BUILD
    return _qgcCorePluginInstance();
#else
    return CUSTOMCLASS::instance();
#endif
}
```

Приписка `CACHE INTERNAL "" FORCE` тут не оздоба, а необхідність: тека виробника і тека `src` — різні каталоги збірки, і звичайна змінна з однієї в другу не долетить. Кеш робить її глобальною, `FORCE` перезаписує значення на кожному переналаштуванні, `INTERNAL` ховає її з очей у графічному налаштовувачі. Механіка кешу — в [кеші та опціях CMake](topic:build-systems/cache-and-options); загальні кроки складання — у [збірці застосунку](topic:qgroundcontrol/building-qgc), а що з цього виходить як продукт — у [власній збірці](topic:qgroundcontrol/custom-build).

---

## Пастки контракту, помітні лише під час роботи

| Що зроблено | Що зламається | Чому мовчки |
|---|---|---|
| `_showAdvancedUI` не скинуто в конструкторі | збірка стартує в розширеному режимі попри всі прапорці | типове значення базового класу — `true` |
| `mavlinkMessage()` повертає `false` для чужого типу | параметри не довантажуються, телеметрія не оновлюється | штатні обробники просто не покликані, помилок немає |
| `canonicalName` у списку й у фабриці розійшлися | пункт меню є, елемент не створюється | звірка йде рядками під час роботи |
| `releaseVideoSink()` не звільняє те, що дав `createVideoSink()` | витік на кожному перепід'єднанні відео | тип стерто до `void *` |
| властивість із `CONSTANT` міняється в роботі | QML не перемальовується | сигналу зміни для неї не існує |
| ім'я підміненого QML-ресурсу застаріло після оновлення апстриму | показується типовий екран замість власного | перехоплювач адрес звіряє рядки |
| перевизначено `createQmlApplicationEngine()` без виклику базового | немає шляху імпорту `qrc:/qml` і контекстної властивості джойстика | рушій створиться, екрани — ні |
