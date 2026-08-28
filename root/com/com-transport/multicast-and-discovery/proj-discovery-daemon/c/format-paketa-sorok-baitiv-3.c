static size_t build(uint8_t *out, uint8_t type, uint32_t ttl_s)
{
    size_t nl = strlen(me.name);
    if (nl > 63) nl = 63;

    memcpy(out, "DSC1", 4);
    out[4] = PROTO_VER;
    out[5] = type;
    put_u16(out + 6,  0);                 /* прапорці — резерв */
    memcpy(out + 8, me.id, 16);
    put_u32(out + 24, me.incarnation);
    put_u32(out + 28, ttl_s);             /* нуль тут і є прощання */
    put_u16(out + 32, me.port);
    put_u16(out + 34, me.caps);
    put_u16(out + 36, (uint16_t)nl);
    put_u16(out + 38, 0);                 /* лічильник «я вже знаю» — заповнює лише запит */
    memcpy(out + HDR_LEN, me.name, nl);
    return HDR_LEN + nl;
}
