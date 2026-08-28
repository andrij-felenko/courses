avrdude -c usbasp -p m328p -t

avrdude> read lfuse
>>> read lfuse
0x0000  62                                                |.       |

avrdude> read hfuse
>>> read hfuse
0x0000  d9                                                |.       |

avrdude> read efuse
>>> read efuse
0x0000  ff                                                |.       |

avrdude> read lock
>>> read lock
0x0000  ff                                                |.       |

avrdude> part
>>> part
AVR Part                      : ATmega328P
Chip Erase delay              : 9000 us
PAGEL                         : PD7
BS2                           : PC2
RESET Disposition             : dedicated
