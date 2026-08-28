interface Vec2 { x: number; y: number; }
interface Body { pos: Vec2; vel: Vec2; invMass: number; }   // invMass === 0 → стіна

const dot   = (a: Vec2, b: Vec2): number => a.x * b.x + a.y * b.y;
const add   = (a: Vec2, b: Vec2): Vec2   => ({ x: a.x + b.x, y: a.y + b.y });
const sub   = (a: Vec2, b: Vec2): Vec2   => ({ x: a.x - b.x, y: a.y - b.y });
const scale = (v: Vec2, s: number): Vec2 => ({ x: v.x * s, y: v.y * s });

// n — одинична нормаль від b до a; depth — глибина проникання.
function resolveContact(a: Body, b: Body, n: Vec2, depth: number, e: number): void {
  const invSum = a.invMass + b.invMass;
  if (invSum === 0) return;                            // дві стіни

  const vn = dot(sub(a.vel, b.vel), n);                // швидкість зближення
  if (vn > 0) return;                                  // розходяться

  const eEff = vn > -1 ? 0 : e;                        // поріг проти дрижання
  const j = -(1 + eEff) * vn / invSum;                 // скалярний поштовх
  const P = scale(n, j);
  a.vel = add(a.vel, scale(P,  a.invMass));
  b.vel = add(b.vel, scale(P, -b.invMass));

  const slop = 0.01, beta = 0.2;                       // позиційна корекція
  const corr = Math.max(depth - slop, 0) / invSum * beta;
  const C = scale(n, corr);
  a.pos = add(a.pos, scale(C,  a.invMass));
  b.pos = add(b.pos, scale(C, -b.invMass));
}
