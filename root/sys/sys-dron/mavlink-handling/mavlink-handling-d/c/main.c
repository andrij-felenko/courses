if (c == MAVLINK_STX)
{
    status->parse_state = MAVLINK_PARSE_STATE_GOT_STX;
    rxmsg->magic = c;
    status->flags &= ~MAVLINK_STATUS_FLAG_IN_MAVLINK1;
} else if (c == MAVLINK_STX_MAVLINK1)
{
    status->parse_state = MAVLINK_PARSE_STATE_GOT_STX;
    rxmsg->magic = c;
    status->flags |= MAVLINK_STATUS_FLAG_IN_MAVLINK1;
}
