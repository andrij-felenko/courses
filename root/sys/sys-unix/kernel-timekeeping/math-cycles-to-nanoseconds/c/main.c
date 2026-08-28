tmp = NTP_INTERVAL_LENGTH;          /* 10⁹/HZ наносекунд */
tmp <<= clock->shift;
ntpinterval = tmp;
tmp += clock->mult / 2;
do_div(tmp, clock->mult);
interval = tmp;

tk->cycle_interval   = interval;
tk->xtime_interval   = interval * clock->mult;
tk->xtime_remainder  = ntpinterval - tk->xtime_interval;
