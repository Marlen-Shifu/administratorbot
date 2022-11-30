import datetime

from flask import Flask, url_for

from flask import render_template

from db.operations import get_all_workers, get_periodic_tasks, get_onetime_tasks, get_periodic_task_users_of_user, \
    get_user, get_periodic_tasks_of_user, create_periodic_task_answer, get_periodic_task, get_periodic_task_answers

from utils.mailing.mail import mail

import qrcode

app = Flask(__name__, static_folder='static')


@app.route("/")
def home():

    workers = [worker.username for worker in get_all_workers()]

    return render_template("index.html", workers = workers)


@app.route("/username/<username>")
def check(username):

    now = datetime.datetime.now() + datetime.timedelta(hours=6)

    user = get_user(None, username=username)

    p_tasks = get_periodic_tasks_of_user(2)

    today_p_tasks = []


    for task in p_tasks:
        if task.current_state is None:
            if str(now.today().date().weekday() + 1) in task.get_days_list():
                today_p_tasks.append(task)
        else:
            if task.current_state.split(':')[0] == 'work':
                today_p_tasks.append(task)

    hour = now.hour

    if len(str(hour)) == 1:
        hour = "0" + str(hour)

    elif len(str(hour)) == 2:
        hour = str(hour)

    minute = now.minute

    if minute >= 30:
        minute = 30
    else:
        minute = 0

    if len(str(minute)) == 1:
        minute = str(minute) + "0"

    elif len(str(minute)) == 2:
        minute = str(minute)

    now_str = f"{hour}:{minute}"

    tasks_available_for_answer = []

    for task in today_p_tasks:

        times = task.get_times_list()

        for time in times:
            if time == now_str:

                def user_is_answered(user, answers_list):
                    for task_answer in answers_list:
                        if user.id == task_answer.user_id:
                            if task_answer.time.date() == now.date() and task_answer.time.hour == hour and task_answer.time.minute == minute:
                                return True

                    return False

                already_answered = user_is_answered(user, get_periodic_task_answers(task.id))


                if not already_answered:
                    #
                    # img = qrcode.make(f'http://94.247.128.225/login/{username}/{task.id}')
                    # img.save(f"static/{username}_qr.png")

                    tasks_available_for_answer.append(task)

                    break

                    # return f"You can answer for time: {now_str}\nTask: {task.title}\n<a href=\"{url_for('static', filename = f'{username}_qr.png')}\">Login</a>"
                #
                # else:
                #
                #     return f"You have already answered for this task for this time"

    return render_template('tasks_list.html', tasks_list = tasks_available_for_answer)



    # return f"You can NOT answer(((\nTasks:{p_tasks}\nTodays:{today_p_tasks}\nTime:{now_str}"


@app.route("/task/<username>/<task_id>")
def task(username, task_id):

    img = qrcode.make(f'http://94.247.128.225/login/{username}/{task_id}')
    img.save(f"static/{username}_qr.png")


@app.route("/login/<username>/<task_id>")
def login(username, task_id):

    task = get_periodic_task(task_id)

    answer = "yes"

    user = get_user(username=username, id = None)

    value = "Пусто"

    create_periodic_task_answer(task_id, user.id, answer, "text", value)

    return f"<h1>Hi {username}! You answered for task \"{task.title}\".</h1>"



if __name__ == '__main__':
    app.run("0.0.0.0", 5000)

