// Основи MVP в Open Class: розробник успадковує кожну й перекриває методи.
// (реконструкція за схемою класів зі статті 1996 року)

class IMyModel : public IModel {                        // 1. що це за дані?
public:
    void  setData(const IData& d);
    IData getData() const;
private:
    IData myData;
};

class IMySelection : public ISelection {                // 2. як указати частину даних?
public:
    void highlightSelection();
};

class IMyModelCommand : public ICommandOn<ISelection> { // 3. як я змінюю дані?
public:
    void doCommand();
    void undoCommand();
    void redoCommand();
private:
    IData myOldData;                                    // щоб було чим вернути назад
};

class IMyView : public IView {                          // 4. як я показую дані?
public:
    void drawContents();                                // малює те, що САМЕ взяло: getData()
};

// 5. інтерактори здебільшого не пишуть: беруть готовий IMenuInteractor
//    і прив'язують пункт меню до команди — addMenuItemAndCommand()

class IMyPresenter : public IPresenter {                // 6. як це все скласти докупи?
public:
    void createView();                                  // творить модель, вибірки, команди, подання
};
