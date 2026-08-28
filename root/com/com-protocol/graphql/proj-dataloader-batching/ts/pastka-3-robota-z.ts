const resolvers = {
  Mutation: {
    updateUserName: async (_parent, { id, newName }, context) => {
      const updatedUser = await context.db.updateUser(id, { name: newName });
      
      // 1. Скидаємо старе значення з кешу
      context.loaders.userLoader.clear(id);
      
      // 2. Або записуємо оновлене значення наперед (prime)
      context.loaders.userLoader.prime(id, updatedUser);
      
      return updatedUser;
    }
  }
};
