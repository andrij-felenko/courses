struct nft_expr_ops {
	void				(*eval)(const struct nft_expr *expr,
						struct nft_regs *regs,
						const struct nft_pktinfo *pkt);
	int				(*init)(const struct nft_ctx *ctx,
						const struct nft_expr *expr,
						const struct nlattr * const tb[]);
	void				(*destroy)(const struct nft_ctx *ctx,
						  const struct nft_expr *expr);
	int				(*dump)(struct sk_buff *skb,
						const struct nft_expr *expr,
						bool reset);
	const struct nft_expr_type	*type;
};
