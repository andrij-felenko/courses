struct nft_expr_ops {
	void				(*eval)(const struct nft_expr *expr,
						struct nft_regs *regs,
						const struct nft_pktinfo *pkt);
	int				(*size);
	int				(*init)(const struct nft_ctx *ctx,
						const struct nft_expr *expr,
						const struct nlattr * const tb[]);
	void				(*activate)(const struct nft_ctx *ctx,
						   const struct nft_expr *expr);
	void				(*deactivate)(const struct nft_ctx *ctx,
						     const struct nft_expr *expr,
						     enum nft_trans_phase phase);
	void				(*destroy)(const struct nft_ctx *ctx,
						  const struct nft_expr *expr);
	int				(*dump)(struct sk_buff *skb,
						const struct nft_expr *expr,
						bool reset);
	int				(*validate)(const struct nft_ctx *ctx,
						   const struct nft_expr *expr,
						   const struct nft_data **data);
	const struct nft_expr_type	*type;
};
