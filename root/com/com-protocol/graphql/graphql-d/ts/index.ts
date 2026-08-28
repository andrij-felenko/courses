// АНТИПАТЕРН: авторизація всередині резолвера
const resolvers = {
  Post: {
    secretNotes: (post, args, context) => {
      if (!context.currentUser.isAdmin) {
        throw new Error("Доступ заборонено");
      }
      return post.secretNotes;
    }
  }
};
