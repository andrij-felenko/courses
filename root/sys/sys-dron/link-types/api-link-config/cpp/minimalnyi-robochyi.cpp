class MyConfiguration : public LinkConfiguration
{
    Q_OBJECT
    Q_PROPERTY(QString endpoint READ endpoint WRITE setEndpoint NOTIFY endpointChanged)
public:
    explicit MyConfiguration(const QString &name, QObject *parent = nullptr)
        : LinkConfiguration(name, parent) {}

    // тимчасово чуже значення — доки не заведено власне (див. нижче про LinkType)
    LinkType type() const override { return LinkConfiguration::TypeUdp; }
    QString settingsURL()   const override { return QStringLiteral("MySettings.qml"); }
    QString settingsTitle() const override { return tr("My Link Settings"); }

    void loadSettings(QSettings &s, const QString &root) override {
        s.beginGroup(root);
        setEndpoint(s.value("endpoint", _endpoint).toString());
        s.endGroup();
    }
    void saveSettings(QSettings &s, const QString &root) const override {
        s.beginGroup(root);
        s.setValue("endpoint", _endpoint);
        s.endGroup();
    }
    void copyFrom(const LinkConfiguration *source) override {
        LinkConfiguration::copyFrom(source);                    // спершу базовий!
        const auto *src = qobject_cast<const MyConfiguration *>(source);
        if (src) { setEndpoint(src->endpoint()); }
    }
    QString endpoint() const { return _endpoint; }
    void setEndpoint(const QString &e) { if (e != _endpoint) { _endpoint = e; emit endpointChanged(); } }
signals:
    void endpointChanged();
private:
    QString _endpoint;
};

class MyLink : public LinkInterface
{
    Q_OBJECT
public:
    explicit MyLink(SharedLinkConfigurationPtr &config, QObject *parent = nullptr)
        : LinkInterface(config, parent)
        , _myConfig(qobject_cast<const MyConfiguration *>(config.get())) {}

    bool isConnected()       const override { return _open; }
    bool isSecureConnection() const override { return false; }

public slots:
    void disconnect() override {
        if (!_open) { return; }                                 // терпить повторний виклик
        _open = false;
        if (!_disconnectedEmitted.exchange(true)) { emit disconnected(); }
    }

private slots:
    void _writeBytes(const QByteArray &bytes) override {
        if (!_open) { emit communicationError(tr("Помилка запису"), tr("Канал роз'єднано")); return; }
        const qint64 written = _device.write(bytes);
        if (written > 0) { emit bytesSent(this, bytes.first(written)); }
    }
    void _onReadyRead() { emit bytesReceived(this, _device.readAll()); }

private:
    bool _connect() override {
        if (!_device.open(_myConfig->endpoint())) {
            emit communicationError(tr("Не вдалося під'єднатися"), _device.errorString());
            return false;
        }
        _open = true;
        _disconnectedEmitted = false;
        emit connected();                                       // менеджер уже підписаний
        return true;
    }

    const MyConfiguration *_myConfig = nullptr;
    MyDevice _device;
    bool _open = false;
    std::atomic<bool> _disconnectedEmitted{false};
};
