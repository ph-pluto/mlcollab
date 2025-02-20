from mlcollab import login_manager
from mlcollab.users.models import Users


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
