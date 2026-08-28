// ET++, кінець 1980-х: серце діалогу — абстрактний «директор»
class DialogDirector {
public:
    virtual ~DialogDirector();
    virtual void ShowDialog();
    virtual void WidgetChanged(Widget*) = 0;   // віджет каже: «я змінився»
protected:
    virtual void CreateWidgets() = 0;          // підклас будує свої віджети
};

// конкретний директор шрифтового діалогу
class FontDialogDirector : public DialogDirector {
public:
    void WidgetChanged(Widget*) override;      // уся логіка вікна — тут
protected:
    void CreateWidgets() override;
private:
    ListBox*    _fontList;                     // директор тримає своїх віджетів
    EntryField* _fontName;
    Button*     _ok;
};
