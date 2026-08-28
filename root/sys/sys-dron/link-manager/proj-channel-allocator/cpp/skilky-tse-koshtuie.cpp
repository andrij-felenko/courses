#include <bit>

uint8_t LinkManager::allocateMavlinkChannel()
{
    const uint32_t freeBits = ~_mavlinkChannelsUsedBitMask;   // одиниця = вільно
    const int i = std::countr_zero(freeBits);                 // молодший вільний номер

    if (i >= MAVLINK_COMM_NUM_BUFFERS) {
        return invalidMavlinkChannel();                       // сюди ж падає і «все зайнято»
    }
    // ... прибрати стан каналу i, виставити біт, повернути i
}
