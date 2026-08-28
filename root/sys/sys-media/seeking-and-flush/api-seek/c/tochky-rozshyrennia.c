static gboolean
my_src_is_seekable (GstBaseSrc *src)
{
  MySrc *self = MY_SRC (src);
  return self->fd >= 0 && self->size > 0;    /* живий потік поверне FALSE */
}

static gboolean
my_src_do_seek (GstBaseSrc *src, GstSegment *segment)
{
  MySrc *self = MY_SRC (src);

  /* сегмент уже готовий: базовий клас застосував до нього подію.
     Наше діло — переставити носій на segment->start і сказати «так». */
  if (lseek (self->fd, segment->start, SEEK_SET) < 0)
    return FALSE;

  self->read_offset = segment->start;
  return TRUE;
}
