// Одне спостереження від давача: який орієнтир, де він бачиться.
typedef struct {
    int   id;          // ідентифікатор орієнтира (-1 = ще не впізнаний)
    float r, phi;      // виміряні дальність і пеленг
} Obs;

// Знайти орієнтир за зовнішнім id у нашій карті (проста лінійна пошуковка).
static int find_lm(const Slam *s, int id) {
    for (int i=0;i<s->n_lm;i++) if (s->lm_id[i]==id) return i;
    return -1;
}

// ОДИН ПОВНИЙ КАДР EKF-SLAM: рух -> по кожному спостереженню (роздути|виправити).
void slam_step(Slam *s, float dr, float dth, MotionNoise mn,
               const Obs *obs, int n_obs, SensorNoise sn) {
    // 1) ПЕРЕДБАЧЕННЯ: просунути позу, роздути невпевненість.
    slam_predict(s, dr, dth, mn);

    // 2) КОРЕКЦІЯ/КАРТУВАННЯ: по кожному видимому орієнтиру.
    for (int k=0; k<n_obs; ++k) {
        int i = find_lm(s, obs[k].id);
        if (i < 0)
            slam_add_landmark(s, obs[k].id, obs[k].r, obs[k].phi, sn);   // новий
        else
            slam_update(s, i, obs[k].r, obs[k].phi, sn);                  // відомий
    }
}
