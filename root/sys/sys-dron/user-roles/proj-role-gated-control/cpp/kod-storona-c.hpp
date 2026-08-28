// CustomPlugin.h
class CustomPlugin : public QGCCorePlugin
{
    Q_OBJECT

public:
    explicit CustomPlugin(QObject *parent = nullptr);

    QGCOptions *options() final { return _options; }

    /// Сервісна дія. Порожній рядок — надіслано; непорожній — причина відмови.
    Q_INVOKABLE QString resetParametersToFactory();

private slots:
    void _advancedChanged(bool advanced);

private:
    CustomOptions *_options = nullptr;
};
