/* Диспетчер клієнтської сесії */
sasl_result_t sasl_client_init(sasl_client_session_t *sess, const sasl_mech_t *mech,
                               const sasl_credentials_t *cred) {
    if (!sess || !mech || !cred) return SASL_ERR_SYNTAX;
    sess->mech = mech;
    sess->cred = *cred;
    sess->mech_ctx = NULL;
    sess->state = SASL_STATE_INIT;
    return SASL_OK;
}

sasl_result_t sasl_client_evaluate(sasl_client_session_t *sess, const sasl_buffer_t *server_challenge,
                                   sasl_buffer_t *client_response) {
    if (!sess || !sess->mech) return SASL_ERR_SYNTAX;

    sasl_result_t res;
    switch (sess->state) {
    case SASL_STATE_INIT:
        res = sess->mech->client_start(&sess->mech_ctx, &sess->cred, client_response);
        if (res == SASL_OK) {
            sess->state = SASL_STATE_DONE;
        } else if (res == SASL_CONTINUE) {
            sess->state = SASL_STATE_STEP;
        } else {
            sess->state = SASL_STATE_FAIL;
        }
        return res;

    case SASL_STATE_STEP:
        if (!sess->mech->client_step) {
            sess->state = SASL_STATE_FAIL;
            return SASL_ERR_SYNTAX;
        }
        res = sess->mech->client_step(sess->mech_ctx, server_challenge, client_response);
        if (res == SASL_OK) {
            sess->state = SASL_STATE_DONE;
        } else if (res == SASL_CONTINUE) {
            sess->state = SASL_STATE_STEP;
        } else {
            sess->state = SASL_STATE_FAIL;
        }
        return res;

    default:
        return SASL_ERR_SYNTAX;
    }
}
