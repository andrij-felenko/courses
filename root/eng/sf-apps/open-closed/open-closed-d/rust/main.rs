enum Shape { Circle(f64), Rect(f64, f64), Triangle(f64, f64) }

fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle(r)       => 3.14159265 * r * r,
        Shape::Rect(w, h)      => w * h,
        Shape::Triangle(b, h)  => 0.5 * b * h,
        // додав Shape::Hexagon — і КОЖЕН match без цієї гілки
        // перестає компілюватися: компілятор перелічує всі місця
    }
}
