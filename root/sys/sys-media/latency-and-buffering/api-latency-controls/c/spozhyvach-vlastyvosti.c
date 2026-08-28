if (l) {                                     /* обидва блоки — лише для живого */
  min += render_delay;                       /* затримка ПІСЛЯ споживача */
  if (max != -1)
    max += render_delay;                     /* ... іде і в підлогу, і в стелю */
}

if (l) {
  if (max == -1 || min + processing_deadline <= max)
    min += processing_deadline;              /* запас на роботу самого споживача */
  else
    GST_ELEMENT_WARNING (sink, CORE, CLOCK, (…), (…));   /* не влазить під стелю */
}
