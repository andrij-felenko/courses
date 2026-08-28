/* sysdeps/unix/sysv/linux/clock_gettime.c, спрощено */
int
__clock_gettime (clockid_t clock_id, struct timespec *tp)
{
  struct __timespec64 tp64;
  int ret = __clock_gettime64 (clock_id, &tp64);

  if (ret == 0)
    {
      if (! in_time_t_range (tp64.tv_sec))
        {
          __set_errno (EOVERFLOW);
          return -1;
        }
      *tp = valid_timespec64_to_timespec (tp64);
    }
  return ret;
}
