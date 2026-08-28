struct Circle { r: f64 }
struct Rect   { w: f64, h: f64 }

trait Area { fn area(&self) -> f64; }           // операція = трейт
impl Area for Circle { fn area(&self) -> f64 { std::f64::consts::PI * self.r * self.r } }
impl Area for Rect   { fn area(&self) -> f64 { self.w * self.h } }

// НОВА операція = НОВИЙ трейт + impl-и; наявного не чіпаємо:
trait Perimeter { fn perimeter(&self) -> f64; }
impl Perimeter for Circle { fn perimeter(&self) -> f64 { 2.0 * std::f64::consts::PI * self.r } }

// НОВИЙ тип = новий struct + impl наявних трейтів:
struct Triangle { b: f64, h: f64 }
impl Area for Triangle { fn area(&self) -> f64 { 0.5 * self.b * self.h } }
