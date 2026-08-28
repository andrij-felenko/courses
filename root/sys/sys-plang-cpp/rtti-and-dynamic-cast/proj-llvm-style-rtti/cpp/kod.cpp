class Shape {
public:
    enum Kind : unsigned char {
        SK_Rect,          // 0
        SK_RoundedRect,   // 1
        SK_Triangle,      // 2
        SK_Ellipse,       // 3
        SK_Circle,        // 4
        SK_TextLabel,     // 5

        // межі піддерев — псевдоніми, власних значень не займають
        SK_FirstPolygon = SK_Rect,    SK_LastPolygon = SK_Triangle,
        SK_FirstRect    = SK_Rect,    SK_LastRect    = SK_RoundedRect,
        SK_FirstEllipse = SK_Ellipse, SK_LastEllipse = SK_Circle,
    };

    Kind kind() const { return kind_; }
    virtual ~Shape() = default;

protected:
    explicit Shape(Kind k) : kind_(k) {}

private:
    const Kind kind_;
};
