from flask_sqlalchemy import SQLAlchemy
from mlcollab.users.models import Posts

db = SQLAlchemy()

# To fetch all posts
posts = Posts.query.all()

# To create a post
new_post = Posts(post_user_id=12)
db.session.add(new_post)
# Post id will be generated upon commit
db.session.commit()

# To delete post
del_post = Posts.query.filter(Posts.post_id == 321).first()
db.session.delete(del_post)
db.session.commit()