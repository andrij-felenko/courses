typedef struct df_istructure df_istructure_t;

df_status_t df_istructure_create(
    df_istructure_t** out_istruct,
    size_t            element_count
);

df_status_t df_istructure_read_async(
    df_istructure_t* istruct,
    size_t           index,
    df_token_t       consumer_token
);

df_status_t df_istructure_write(
    df_engine_t*     engine,
    df_istructure_t* istruct,
    size_t           index,
    uint64_t         value
);

df_status_t df_istructure_destroy(df_istructure_t* istruct);
