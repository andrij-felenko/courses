interface PermissionKey {
  userId: string;
  organizationId: string;
}

const permissionLoader = new DataLoader<PermissionKey, Permission[]>(
  async (keys) => batchFetchPermissions(keys),
  {
    cacheKeyFn: (key) => `${key.organizationId}:${key.userId}`
  }
);
