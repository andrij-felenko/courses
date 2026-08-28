typedef struct df_graph df_graph_t;

df_status_t df_graph_create(
    df_graph_t** out_graph,
    uint32_t     max_nodes
);

df_status_t df_graph_set_node(
    df_graph_t*           graph,
    df_node_id_t          node_id,
    const df_node_desc_t* desc
);

df_status_t df_graph_destroy(df_graph_t* graph);
