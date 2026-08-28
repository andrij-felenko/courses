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
