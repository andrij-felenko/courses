#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>

#define MAX_BODIES 64
#define MAX_CONTACTS 128

typedef struct {
    float x;
    float y;
} Vec2;

static inline Vec2 vec2_make(float x, float y) { return (Vec2){x, y}; }
static inline Vec2 vec2_add(Vec2 a, Vec2 b) { return (Vec2){a.x + b.x, a.y + b.y}; }
static inline Vec2 vec2_sub(Vec2 a, Vec2 b) { return (Vec2){a.x - b.x, a.y - b.y}; }
static inline Vec2 vec2_scale(Vec2 v, float s) { return (Vec2){v.x * s, v.y * s}; }
static inline float vec2_dot(Vec2 a, Vec2 b) { return a.x * b.x + a.y * b.y; }
static inline float vec2_cross(Vec2 a, Vec2 b) { return a.x * b.y - a.y * b.x; }

typedef struct {
    Vec2 pos;
    Vec2 vel;
    float ang;
    float ang_vel;
    float inv_mass; /* 0 для нерухомої опори */
    float inv_i;    /* 0 для нерухомої опори */
    float width;
    float height;
} RigidBody;

typedef struct {
    int body_a;              /* індекс першого тіла */
    int body_b;              /* індекс другого тіла (нормаль від b до a) */
    Vec2 normal;             /* одинична нормаль контакту */
    Vec2 r_a;                /* плече від центра мас A до точки дотику */
    Vec2 r_b;                /* плече від центра мас B до точки дотику */
    float penetration;       /* глибина перекриття (м) */
    float normal_mass;       /* ефективна маса 1 / (J M^-1 J^T) */
    float bias;              /* швидкісний доважок Баумгарте */
    float accumulated_imp;   /* накопичений нормальний імпульс lambda */
    uint64_t feature_id;     /* ключ ідентифікації між кадрами */
} ContactConstraint;

typedef struct {
    RigidBody bodies[MAX_BODIES];
    int num_bodies;
    ContactConstraint contacts[MAX_CONTACTS];
    int num_contacts;
    Vec2 gravity;
    float slop;              /* допустиме мертве занурення (м) */
    float baumgarte;         /* коефіцієнт повернення beta */
} PhysicsWorld;

void world_init(PhysicsWorld *world) {
    memset(world, 0, sizeof(*world));
    world->gravity = vec2_make(0.0f, -9.8f);
    world->slop = 0.005f;       /* 5 мм */
    world->baumgarte = 0.2f;    /* 20% виправлення за кадр */
}

int world_add_body(PhysicsWorld *world, Vec2 pos, float mass, float width, float height) {
    assert(world->num_bodies < MAX_BODIES);
    int idx = world->num_bodies++;
    RigidBody *b = &world->bodies[idx];
    memset(b, 0, sizeof(*b));
    b->pos = pos;
    b->width = width;
    b->height = height;

    if (mass > 0.0f) {
        b->inv_mass = 1.0f / mass;
        /* Момент інерції прямокутника I = (1/12) * m * (w^2 + h^2) */
        float i = (1.0f / 12.0f) * mass * (width * width + height * height);
        b->inv_i = (i > 0.0f) ? (1.0f / i) : 0.0f;
    } else {
        b->inv_mass = 0.0f;
        b->inv_i = 0.0f;
    }
    return idx;
}

int world_add_contact(PhysicsWorld *world, int b_a, int b_b, Vec2 n, Vec2 r_a, Vec2 r_b, 
                      float depth, uint64_t id) {
    assert(world->num_contacts < MAX_CONTACTS);
    int idx = world->num_contacts++;
    ContactConstraint *c = &world->contacts[idx];
    c->body_a = b_a;
    c->body_b = b_b;
    c->normal = n;
    c->r_a = r_a;
    c->r_b = r_b;
    c->penetration = depth;
    c->feature_id = id;
    c->accumulated_imp = 0.0f;
    return idx;
}

static inline Vec2 body_point_velocity(const RigidBody *b, Vec2 r) {
    return vec2_make(b->vel.x - b->ang_vel * r.y, b->vel.y + b->ang_vel * r.x);
}

static inline void body_apply_impulse(RigidBody *a, RigidBody *b, const ContactConstraint *c, float dl) {
    Vec2 p = vec2_scale(c->normal, dl);
    a->vel = vec2_add(a->vel, vec2_scale(p, a->inv_mass));
    a->ang_vel += a->inv_i * vec2_cross(c->r_a, p);

    b->vel = vec2_sub(b->vel, vec2_scale(p, b->inv_mass));
    b->ang_vel -= b->inv_i * vec2_cross(c->r_b, p);
}

void world_prestep(PhysicsWorld *world, float dt) {
    for (int i = 0; i < world->num_contacts; ++i) {
        ContactConstraint *c = &world->contacts[i];
        RigidBody *a = &world->bodies[c->body_a];
        RigidBody *b = &world->bodies[c->body_b];

        float rn_a = vec2_cross(c->r_a, c->normal);
        float rn_b = vec2_cross(c->r_b, c->normal);
        float k = a->inv_mass + b->inv_mass +
                  a->inv_i * rn_a * rn_a + b->inv_i * rn_b * rn_b;

        c->normal_mass = (k > 0.0f) ? (1.0f / k) : 0.0f;

        float pen_excess = c->penetration - world->slop;
        if (pen_excess < 0.0f) pen_excess = 0.0f;
        c->bias = (world->baumgarte / dt) * pen_excess;

        /* Теплий старт збереженим імпульсом минулого кадру */
        body_apply_impulse(a, b, c, c->accumulated_imp);
    }
}

void world_solve_velocities(PhysicsWorld *world) {
    for (int i = 0; i < world->num_contacts; ++i) {
        ContactConstraint *c = &world->contacts[i];
        RigidBody *a = &world->bodies[c->body_a];
        RigidBody *b = &world->bodies[c->body_b];

        Vec2 va = body_point_velocity(a, c->r_a);
        Vec2 vb = body_point_velocity(b, c->r_b);
        Vec2 dv = vec2_sub(va, vb);

        float vn = vec2_dot(dv, c->normal);
        float dl = c->normal_mass * (c->bias - vn);

        /* Затиск накопиченого імпульсу: lambda >= 0 */
        float old_imp = c->accumulated_imp;
        float new_imp = old_imp + dl;
        if (new_imp < 0.0f) new_imp = 0.0f;
        c->accumulated_imp = new_imp;

        float delta_to_apply = new_imp - old_imp;
        body_apply_impulse(a, b, c, delta_to_apply);
    }
}

void world_step(PhysicsWorld *world, float dt, int iterations) {
    /* 1. Вільний крок зовнішніх сил */
    for (int i = 0; i < world->num_bodies; ++i) {
        RigidBody *b = &world->bodies[i];
        if (b->inv_mass > 0.0f) {
            b->vel = vec2_add(b->vel, vec2_scale(world->gravity, dt));
        }
    }

    /* 2. Підготовка ефективних мас і теплий старт */
    world_prestep(world, dt);

    /* 3. Ітерації Projected Gauss-Seidel */
    for (int iter = 0; iter < iterations; ++iter) {
        world_solve_velocities(world);
    }

    /* 4. Симплектичне оновлення положень */
    for (int i = 0; i < world->num_bodies; ++i) {
        RigidBody *b = &world->bodies[i];
        b->pos = vec2_add(b->pos, vec2_scale(b->vel, dt));
        b->ang += b->ang_vel * dt;
    }
}

float contact_normal_force(const ContactConstraint *c, float dt) {
    return c->accumulated_imp / dt;
}

/* ==================== ВЕРИФІКАЦІЙНІ ТЕСТИ ==================== */

void test_single_box_on_ground(void) {
    PhysicsWorld world;
    world_init(&world);

    int ground = world_add_body(&world, vec2_make(0.0f, 0.0f), 0.0f, 10.0f, 0.5f);
    int box = world_add_body(&world, vec2_make(0.0f, 0.5f), 6.0f, 0.4f, 0.4f);

    float dt = 1.0f / 60.0f;
    world_add_contact(&world, box, ground, vec2_make(0.0f, 1.0f),
                      vec2_make(0.0f, -0.2f), vec2_make(0.0f, 0.25f), 0.005f, 101);

    for (int frame = 0; frame < 60; ++frame) {
        world_step(&world, dt, 10);
    }

    float force = contact_normal_force(&world.contacts[0], dt);
    printf("[C99] Тест 1 (Ящик 6 кг на підлозі): N = %.2f Н (очікувано mg = 58.80 Н)\n", force);
    assert(fabsf(force - 58.80f) < 0.05f);
    assert(fabsf(world.bodies[box].vel.y) < 1e-4f);
}

void test_box_on_30_degree_incline(void) {
    PhysicsWorld world;
    world_init(&world);

    int ground = world_add_body(&world, vec2_make(0.0f, 0.0f), 0.0f, 10.0f, 0.5f);
    int box = world_add_body(&world, vec2_make(0.0f, 1.0f), 6.0f, 0.4f, 0.4f);

    float dt = 1.0f / 60.0f;
    /* Нормаль схилу 30 градусів: (-sin 30°, cos 30°) = (-0.5, 0.866025) */
    Vec2 slope_normal = vec2_make(-0.5f, 0.8660254f);
    world_add_contact(&world, box, ground, slope_normal,
                      vec2_make(0.0f, 0.0f), vec2_make(0.0f, 0.0f), 0.005f, 202);

    world_step(&world, dt, 10);
    float force = contact_normal_force(&world.contacts[0], dt);
    float expected = 6.0f * 9.8f * 0.8660254f; /* 50.92 Н */
    printf("[C99] Тест 2 (Схил 30 градусів):      N = %.2f Н (очікувано mg*cos30 = %.2f Н)\n", 
           force, expected);
    assert(fabsf(force - expected) < 0.05f);
}

void test_three_box_stack_convergence(void) {
    PhysicsWorld world;
    world_init(&world);

    int ground = world_add_body(&world, vec2_make(0.0f, 0.0f), 0.0f, 10.0f, 0.5f);
    int b0 = world_add_body(&world, vec2_make(0.0f, 0.5f), 1.0f, 0.4f, 0.4f);
    int b1 = world_add_body(&world, vec2_make(0.0f, 1.0f), 1.0f, 0.4f, 0.4f);
    int b2 = world_add_body(&world, vec2_make(0.0f, 1.5f), 1.0f, 0.4f, 0.4f);

    float dt = 1.0f / 60.0f;
    world_add_contact(&world, b0, ground, vec2_make(0.0f, 1.0f), vec2_make(0.0f, -0.2f), vec2_make(0.0f, 0.25f), 0.005f, 301);
    world_add_contact(&world, b1, b0,     vec2_make(0.0f, 1.0f), vec2_make(0.0f, -0.2f), vec2_make(0.0f, 0.2f),  0.005f, 302);
    world_add_contact(&world, b2, b1,     vec2_make(0.0f, 1.0f), vec2_make(0.0f, -0.2f), vec2_make(0.0f, 0.2f),  0.005f, 303);

    /* Демонстрація теплий старт vs холодний */
    for (int frame = 0; frame < 10; ++frame) {
        world_step(&world, dt, 8);
    }

    float n0 = contact_normal_force(&world.contacts[0], dt);
    float n1 = contact_normal_force(&world.contacts[1], dt);
    float n2 = contact_normal_force(&world.contacts[2], dt);

    printf("[C99] Тест 3 (Стос 3х1 кг):          N0 = %.2f Н (3mg=29.40), N1 = %.2f Н (2mg=19.60), N2 = %.2f Н (mg=9.80)\n",
           n0, n1, n2);
    assert(fabsf(n0 - 29.40f) < 0.05f);
    assert(fabsf(n1 - 19.60f) < 0.05f);
    assert(fabsf(n2 - 9.80f) < 0.05f);
}

int main(void) {
    printf("================ ЗАПУСК ТЕСТІВ КОНТАКТНОГО РОЗВ'ЯЗУВАЧА (C99) ================\n");
    test_single_box_on_ground();
    test_box_on_30_degree_incline();
    test_three_box_stack_convergence();
    printf("УСІ ТЕСТИ C99 УСПІШНО ПРОЙДЕНО!\n\n");
    return 0;
}
