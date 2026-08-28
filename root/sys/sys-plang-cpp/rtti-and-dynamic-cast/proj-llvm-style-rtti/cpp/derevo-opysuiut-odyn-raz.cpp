// shapes.def — єдине місце, де записано форму ієрархії
#ifndef SHAPE
#  define SHAPE(Name, Parent)
#endif
#ifndef SHAPE_RANGE
#  define SHAPE_RANGE(Base, First, Last)
#endif

SHAPE(Rect,        Polygon)
SHAPE(RoundedRect, Rect)
SHAPE_RANGE(Rect,    Rect,    RoundedRect)
SHAPE(Triangle,    Polygon)
SHAPE_RANGE(Polygon, Rect,    Triangle)
SHAPE(Ellipse,     Shape)
SHAPE(Circle,      Ellipse)
SHAPE_RANGE(Ellipse, Ellipse, Circle)
SHAPE(TextLabel,   Shape)

#undef SHAPE
#undef SHAPE_RANGE
