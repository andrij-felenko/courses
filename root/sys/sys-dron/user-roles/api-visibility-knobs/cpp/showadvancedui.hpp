Q_PROPERTY(bool showAdvancedUI READ showAdvancedUI WRITE _setShowAdvancedUI NOTIFY showAdvancedUIChanged)

public:
    bool showAdvancedUI() const { return _showAdvancedUI; }

signals:
    void showAdvancedUIChanged(bool showAdvancedUI);

protected:
    bool _showAdvancedUI = true;

private:
    void _setShowAdvancedUI(bool show);
