from flask import session, render_template
from functools import wraps

def check_logged_in(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            return func(*args, **kwargs)
        user = "Вы не авторизованы!"
        return render_template("user.html",
                               the_user = user)
    return wrapper