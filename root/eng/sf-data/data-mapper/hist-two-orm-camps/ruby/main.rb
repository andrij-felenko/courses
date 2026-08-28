class Post
  include DataMapper::Resource

  property :id,         Serial
  property :title,      String
  property :body,       Text
  property :created_at, DateTime
end

@post = Post.new(:title => "My first DataMapper post")
@post.save
