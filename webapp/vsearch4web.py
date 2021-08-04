from werkzeug.utils import HTMLBuilder
from cheker import check_logged_in
from flask import copy_current_request_context
from flask import Flask, render_template, request, session
from vsearch import search_for_letters as sfl
from DBcm import DataBaseError, UseDataBase, ConnectionError, CredentialsError, SQLError, DataBaseError
from threading import Thread

#25.07.21 создать индивидуальный viewlog для каждого пользователя


app = Flask(__name__)

app.config["dbconfig"] = {"host": "",
                          "user": "",
                          "password": "",
                          "database": "", }


def insert_users_login(account: dict) -> "name":
    account = session["logged_in"]
    account = account[0]
    user = account[0]
    return user


def null_strings(login: any, password :any) -> bool:
    if bool(login) == True:
        return True
        if bool(password) == True:
            return True
        else:
            return False
    else:
        return False


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
            _SQL = """SELECT * FROM accounts WHERE login = '{0}'
                   AND password = '{1}'""".format(login, password)
            cursor.execute(_SQL)
            user = cursor.fetchall()
            
            if user != None:
                session["logged_in"] = user
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
    try:
        if null_strings(login, password) == True:
            user = users_for_DB(login, password)
            return render_template("info.html",
                                the_info = user)

        else:
            user = "Введите логин и пароль"
            return render_template("user.html",
                                   the_user = user)
    except DataBaseError as err:
        print("База данных выключена")
    except Exception as err:
        print("Непредвиденное исключение: ", str(err))
    return render_template("info.html",
                           the_info="Ошибка авторизации",
                           the_words="В данный момент нельзя авторизоваться",)


@app.route("/logout")
@check_logged_in
def logout():
    session.pop("logged_in")
    user = "Вы вышли из аккаунта"
    return render_template("user.html",
                           the_user = user)


@app.route("/search4", methods=["POST"])
def do_search() -> "html":
    """fdasfasdf"""

    @copy_current_request_context
    def log_request(reg: "flask_request", res: str) -> None:
        """Возвращает подробный отчёт о запросе и результате базе данных
         в таблицу Log в режиме многопоточности"""

        user = insert_users_login(session["logged_in"])

        try:

            with UseDataBase(app.config["dbconfig"]) as cursor:
                _SQL  = """insert into log
                                (phrase, letters, ip, browser_string, results, users_result)
                                values
                                (%s, %s, %s, %s, %s, %s)"""
                cursor.execute(_SQL, (reg.form["phrase"],
                                    reg.form["letters"],
                                    reg.remote_addr,
                                    reg.user_agent.browser,
                                    res,
                                    user))
        except ConnectionError as err:
            print("База данных выключена: ", str(err))
        except DataBaseError as err:
            print("Ошибка базы данных: ", str(err))
        except CredentialsError as err:
            print("Пароль или логин неверный", str(err))
        except SQLError as err:
            print("Неверная SQL комманда", str(err), "|", user)
        except Exception as err:
            print("Непредвиденное исключение: ", str(err))

    phrase = request.form["phrase"]
    letters = request.form["letters"]
    title = "Here are your results: "
    results = str(sfl(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print("Возникла ошибка: ", str(err))
    return render_template("results.html",
                           the_phrase=phrase,
                           the_letters=letters,
                           the_title=title,
                           the_results=results)


@app.route("/")
@app.route("/entry")
def entry_page() -> str:
    """fasdfasdfsadf"""
    try:
        with UseDataBase(app.config["dbconfig"]) as cursor:
            _SQL = """SELECT COUNT(id) FROM log"""
            cursor.execute(_SQL)
            contents = cursor.fetchone()
        return render_template("entry.html",
                               the_title="Search for vowels",
                               the_words = contents[0])
    except ConnectionError as err:
        print("База данных выключена: ", str(err))
    except DataBaseError as err:
        print("Ошибка базы данных: ", str(err))
    except CredentialsError as err:
        print("Пароль или логин неверный", str(err))
    except SQLError as err:
        print("Неверная SQL комманда", str(err))
    except Exception as err:
        print("Непредвиденное исключение: ", str(err))
    return render_template("entry.html",
                           the_title="Search for vowels",
                           the_words="""В данный момент количество всех результатов
                                        поисков пользователей недоступно""")


@app.route("/viewlog")
@check_logged_in
def view_the_log() -> "HTMLBuilder":
    """fdasfasdfasdfasd"""
    try:
        with UseDataBase(app.config["dbconfig"]) as cursor:
            _SQL = """SELECT phrase, letters, ip, browser_string,
            results FROM log WHERE users_result = '{}'""".format(insert_users_login(session["logged_in"]))
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        titles = ("phrase", "letters", "Remote_addr", "User_agent", "Results")
        return render_template("viewlog.html",
                               the_title="Your view Log",
                               the_row_titles=titles,
                               the_data=contents,)
    except ConnectionError as err:
        print("База данных выключена: ", str(err))
    except CredentialsError as err:
        print("Неверный пароль или логин базы данных")
    except SQLError as err:
        print("Неверная SQL комманда: ", str(err))
    except Exception as err:
        print("Неизвестная дичь: ", str(err))
    return render_template("info.html",
                           the_title="View Log",
                           the_words="В данный момент таблица запросов недоступна")


app.secret_key = ""

if __name__ == "__main__":
    app.run(debug=True)
