// TenantUnaryServerInterceptor перехоплює gRPC метадані й збагачує контекст
func TenantUnaryServerInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		md, ok := metadata.FromIncomingContext(ctx)
		if !ok {
			return nil, status.Errorf(codes.Unauthenticated, "missing gRPC metadata")
		}

		tenantIDs := md.Get("x-tenant-id")
		if len(tenantIDs) == 0 || tenantIDs[0] == "" {
			return nil, status.Errorf(codes.Unauthenticated, "missing x-tenant-id in metadata")
		}

		// Збагачуємо контекст Go і передаємо далі по ланцюжку обробників
		newCtx := WithTenant(ctx, tenantIDs[0])
		return handler(newCtx, req)
	}
}
