class CustomFlyViewOptions : public QGCFlyViewOptions
{
    Q_OBJECT

public:
    explicit CustomFlyViewOptions(CustomOptions *options, QObject *parent = nullptr);

    bool showInstrumentPanel() const final { return false; }   // у збірці своя панель приладів
    bool showMultiVehicleList() const final { return false; }
};

// у CustomOptions:
QGCFlyViewOptions *flyViewOptions() const final { return _flyViewOptions; }
