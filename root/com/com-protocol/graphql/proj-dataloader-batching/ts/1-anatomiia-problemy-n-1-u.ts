   // Наївний резолвер поля Post.author
   const resolvers = {
     Post: {
       author: async (post, args, context) => {
         return await context.db.query(
           "SELECT id, name, avatar_url FROM users WHERE id = ?",
           [post.author_id]
         );
       }
     }
   };
