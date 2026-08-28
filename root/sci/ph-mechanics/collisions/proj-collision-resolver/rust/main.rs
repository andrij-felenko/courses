use std::ops::{Add, Sub, Mul};

#[derive(Clone, Copy)]
struct Vec2 { x: f32, y: f32 }

impl Add for Vec2 { type Output = Vec2; fn add(self, o: Vec2) -> Vec2 { Vec2 { x: self.x + o.x, y: self.y + o.y } } }
impl Sub for Vec2 { type Output = Vec2; fn sub(self, o: Vec2) -> Vec2 { Vec2 { x: self.x - o.x, y: self.y - o.y } } }
impl Mul<f32> for Vec2 { type Output = Vec2; fn mul(self, s: f32) -> Vec2 { Vec2 { x: self.x * s, y: self.y * s } } }
impl Vec2 { fn dot(self, o: Vec2) -> f32 { self.x * o.x + self.y * o.y } }

struct Body { pos: Vec2, vel: Vec2, inv_mass: f32 }   // inv_mass == 0.0 → стіна

/// n — одинична нормаль від b до a; depth — глибина проникання.
fn resolve_contact(a: &mut Body, b: &mut Body, n: Vec2, depth: f32, e: f32) {
    let inv_sum = a.inv_mass + b.inv_mass;
    if inv_sum == 0.0 { return; }                     // дві стіни

    let vn = (a.vel - b.vel).dot(n);                  // швидкість зближення
    if vn > 0.0 { return; }                           // розходяться

    let e_eff = if vn > -1.0 { 0.0 } else { e };      // поріг проти дрижання
    let j = -(1.0 + e_eff) * vn / inv_sum;            // скалярний поштовх
    let p = n * j;
    a.vel = a.vel + p * a.inv_mass;
    b.vel = b.vel - p * b.inv_mass;

    let (slop, beta) = (0.01_f32, 0.2_f32);           // позиційна корекція
    let corr = (depth - slop).max(0.0) / inv_sum * beta;
    let c = n * corr;
    a.pos = a.pos + c * a.inv_mass;
    b.pos = b.pos - c * b.inv_mass;
}
