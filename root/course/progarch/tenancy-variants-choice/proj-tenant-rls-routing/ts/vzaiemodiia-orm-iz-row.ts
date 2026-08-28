// Prisma Client Extension для автоматичного RLS контексту
export const prismaWithTenant = (tenantId: string) => {
  return prisma.$extends({
    query: {
      $allModels: {
        async $allOperations({ args, query }) {
          return prisma.$transaction(async (tx) => {
            await tx.$executeRaw`SELECT set_config('app.current_tenant', ${tenantId}, true)`;
            return query(args);
          });
        },
      },
    },
  });
};
