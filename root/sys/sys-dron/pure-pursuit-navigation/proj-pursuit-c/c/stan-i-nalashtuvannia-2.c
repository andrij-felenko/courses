void pursuit_init(pursuit_t *pp, const vec2 *path, int n,
                  float k_look, float L_min, float wheelbase,
                  float delta_max, float goal_tol)
{
    pp->path      = path;
    pp->n         = n;
    pp->seg       = 0;          /* починаємо з першого відрізка */
    pp->k_look    = k_look;
    pp->L_min     = L_min;
    pp->wheelbase = wheelbase;
    pp->delta_max = delta_max;
    pp->goal_tol  = goal_tol;
    pp->finished  = false;
}
