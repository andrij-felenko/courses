// CustomPlugin.h — власна збірка «Sparrow»
class CustomOptions : public QGCOptions
{
    Q_OBJECT
    /// Ворота 1. CONSTANT тут чесний: значення вирішує компілятор,
    /// і за життя застосунку воно змінитися не може.
    Q_PROPERTY(bool showServiceActions READ showServiceActions CONSTANT)

public:
    explicit CustomOptions(CustomPlugin *plugin, QObject *parent = nullptr);

    bool showServiceActions() const { return kServiceBuild; }

    // Взірець із апстримного custom-example: сторінка прошивання — теж лише для експерта.
    bool showFirmwareUpgrade() const final { return _plugin->showAdvancedUI(); }

private:
    // target_compile_definitions(Sparrow PRIVATE SPARROW_SERVICE_BUILD)
#ifdef SPARROW_SERVICE_BUILD
    static constexpr bool kServiceBuild = true;
#else
    static constexpr bool kServiceBuild = false;
#endif

    QGCCorePlugin *_plugin = nullptr;
};
