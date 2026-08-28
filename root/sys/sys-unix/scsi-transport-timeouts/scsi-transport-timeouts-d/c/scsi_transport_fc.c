/* Фрагмент логіки обробки тайм-ауту в drivers/scsi/scsi_transport_fc.c */
enum blk_eh_timer_return fc_eh_timedout(struct scsi_cmnd *scmd)
{
    struct fc_rport *rport = starget_to_rport(scsi_target(scmd->device));

    if (rport->port_state == FC_PORTSTATE_BLOCKED) {
        if (rport->flags & FC_RPORT_FAST_FAIL_TIMEDOUT) {
            /* fast_io_fail_tmo вже сплив: відсікаємо ескалацію scsi_eh */
            return BLK_EH_DONE;
        }
        /* Порт заблоковано, але fast_io_fail_tmo ще діє: продовжуємо таймер */
        return BLK_EH_RESET_TIMER;
    }
    return BLK_EH_DONE;
}
