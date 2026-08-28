enum Shape {
    Circle { r: f64 },
    Rectangle { w: f64, h: f64 },
    Triangle { base: f64, height: f64 },
}

fn area(s: &Shape) -> f64 {          // ця функція — і є «AreaVisitor», лише без церемоній
    match s {
        Shape::Circle { r }            => std::f64::consts::PI * r * r,
        Shape::Rectangle { w, h }      => w * h,
        Shape::Triangle { base, height } => base * height / 2.0,
    }
}
