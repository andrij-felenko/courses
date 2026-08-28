// Викликається З mission_transition при вході в новий стан.
// Кожен стан робить рівно одне: оголошує контуру свою ЦІЛЬ.
static void on_state_enter(mission_state_t s) {
    switch (s) {
    case ST_READY:    motors_disarm();                 break; // двигуни мертві
    case ST_ARMED:    motors_arm();  hold_position();  break; // тримати точку на землі
    case ST_FLYING:   set_target_alt(TAKEOFF_ALT_CM);  break; // ціль — набрати висоту
    case ST_LANDING:  set_descent_rate(LAND_SPEED_CM); break; // ціль — плавно вниз
    case ST_DISARMED: motors_disarm();                 break; // дорізати, зафіксувати
    default: break;
    }
}
