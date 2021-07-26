from cheker import check_logged_in
from flask import Flask, render_template, request, session
from vsearch import search_for_letters
from DBcm import UseDataBase

#25.07.21 создать индивидуальный viewlog для каждого пользователя


app = Flask(__name__)

app.config["dbconfig"] = {}


def null_strings(login: any, password :any) -> bool:
    if bool(login) == True:
        return True
        if bool(password) == True:
            return True
        else:
            return False
    else:
        return False


def log_request(reg: "flask_request", res: str) -> None:
    "Возвращает подробный отчёт о запросе и результате базе данных в таблицу Log"

    with UseDataBase(app.config["dbconfig"]) as cursor:
        _SQL  = """insert into log
                        (phrase, letters, ip, browser_string, results)
                        values
                        (%s, %s, %s, %s, %s)"""
        cursor.execute(_SQL, (reg.form["phrase"],
                              reg.form["letters"],
                              reg.remote_addr,
                              reg.user_agent.browser,
                              res, ))


def users_for_DB(login: str, password: str) -> "Status":
    """Проводит операции с логином и паролем пользователя"""

    with UseDataBase(app.config["dbconfig"]) as cursor:

        #Проверяет наличие логина пользователя в базе данных
        _SQL = """SELECT * FROM accounts WHERE login = '{}'""".format(login)
        cursor.execute(_SQL)
        resultLog = cursor.fetchall()
        resultLog = bool(resultLog)


        #Проверяет правильность пароля к логину
        if resultLog == True:
            _SQL = """SELECT * FROM accounts WHERE login = '{0}' AND password = '{1}'""".format(login, password)
            cursor.execute(_SQL)
            user = cursor.fetchall()
            user = bool(user)
            
            if user == True:
                session["logged_in"] = True
                return "Вы авторизованы!"

            else:
                return "Неверный пароль!"

        else:
            _SQL  = """insert into accounts
                       (login, password)
                       values
                       (%s, %s)"""

            cursor.execute(_SQL, (login,
                                  password))  
            return "Вы создали аккаунт!"


@app.route("/auth")
def do_auth():
    title = "Authorization"
    return render_template("auth.html",
                           the_title=title)


@app.route("/login", methods=["POST"])
def login():
    login = request.form["login"]
    password = request.form["password"]

    if null_strings(login, password) == True:
        user = users_for_DB(login, password)
        return render_template("info.html",
                               the_info = user)

    else:
        user = "Введите логин и пароль"
        return render_template("user.html",
                               the_user = user)


@app.route("/logout")
@check_logged_in
def logout():
    session.pop("logged_in")
    user = "Вы вышли из аккаунта"
    return render_template("user.html",
                           the_user = user)


@app.route("/search4", methods=["POST"])
def do_search() -> "html":
    """asdfasdfdsaf"""
    phrase = request.form["phrase"]
    letters = request.form["letters"]
    title = "Here are your results: "
    results = str(search_for_letters(phrase, letters))
    log_request(request, results)
    return render_template("results.html",
                           the_phrase=phrase,
                           the_letters=letters,
                           the_title=title,
                           the_results=results)


@app.route("/")
@app.route("/entry")
def entry_page() -> str:
    """fasdfasdfsadf"""

    with  UseDataBase(app.config["dbconfig"]) as cursor:
        _SQL = """SELECT COUNT(1) FROM log;"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
    return render_template("entry.html",
                           the_title="Search for vowels",
                           the_words = contents)


@app.route("/viewlog")
@check_logged_in
def view_the_log() -> "html":
    """fdasfasdfasdfasd"""
    contents = list()

    with UseDataBase(app.config["dbconfig"]) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results from log"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()
    titles = ("phrase", "letters", "Remote_addr", "User_agent", "Results")
    return render_template("viewlog.html",
                           the_title="View Log",
                           the_row_titles=titles,
                           the_data=contents)


app.secret_key = ""

if __name__ == "__main__":
    app.run(debug=True)
