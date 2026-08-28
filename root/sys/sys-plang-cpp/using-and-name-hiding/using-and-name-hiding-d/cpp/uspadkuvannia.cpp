struct BaseWidget {
    BaseWidget(std::string name, int width, int height);
    BaseWidget(int width, int height);
    explicit BaseWidget(int id);
};

// До C++11: рутинне перенаправлення
struct DerivedWidgetOld : public BaseWidget {
    DerivedWidgetOld(std::string name, int w, int h) : BaseWidget(std::move(name), w, h) {}
    DerivedWidgetOld(int w, int h) : BaseWidget(w, h) {}
    explicit DerivedWidgetOld(int id) : BaseWidget(id) {}
};
