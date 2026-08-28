class Polygon : public Shape {
public:
    static bool classof(const Shape* s) {
        return s->kind() >= SK_FirstPolygon && s->kind() <= SK_LastPolygon;
    }
    // операція, якої в Shape немає і не буде
    void smooth_corners(double r) { corner_radius_ = r; }

protected:
    using Shape::Shape;

private:
    double corner_radius_ = 0;
};

class Rect : public Polygon {          // конкретний, але сам має нащадка
public:
    Rect() : Rect(SK_Rect) {}
    static bool classof(const Shape* s) {
        return s->kind() >= SK_FirstRect && s->kind() <= SK_LastRect;
    }
protected:
    explicit Rect(Kind k) : Polygon(k) { assert(Rect::classof(this)); }
};

class RoundedRect final : public Rect {
public:
    RoundedRect() : Rect(SK_RoundedRect) {}
    static bool classof(const Shape* s) { return s->kind() == SK_RoundedRect; }
};

class Triangle final : public Polygon {
public:
    Triangle() : Polygon(SK_Triangle) {}
    static bool classof(const Shape* s) { return s->kind() == SK_Triangle; }
};

class Ellipse : public Shape {
public:
    Ellipse() : Ellipse(SK_Ellipse) {}
    static bool classof(const Shape* s) {
        return s->kind() >= SK_FirstEllipse && s->kind() <= SK_LastEllipse;
    }
protected:
    explicit Ellipse(Kind k) : Shape(k) {}
};

class Circle final : public Ellipse {
public:
    Circle() : Ellipse(SK_Circle) {}
    static bool classof(const Shape* s) { return s->kind() == SK_Circle; }
};
