// Децимація після ФНЧ: лишаємо кожен M-тий відлік.
// ФНЧ уже прибрав усе вище за fs_dec/2 — аліасингу не буде.
#define DECIM  10            // 20 кГц / 10 = 2 кГц на виході
int   dec_cnt = 0;
float env_buf[ENV_N];        // буфер обвідної (на зниженій частоті)
int   env_idx = 0;

void on_lowpassed_sample(float lp) {
    if (++dec_cnt >= DECIM) {
        dec_cnt = 0;
        if (env_idx < ENV_N)
            env_buf[env_idx++] = lp;   // зберігаємо лише кожен 10-й
    }
}
