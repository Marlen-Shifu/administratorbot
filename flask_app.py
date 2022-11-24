import datetime

from flask import Flask

from flask import render_template

from db.operations import get_all_workers, get_periodic_tasks, get_onetime_tasks, get_periodic_task_users_of_user, \
    get_user

from utils.mailing.mail import mail

app = Flask(__name__)


@app.route("/")
def home():

    workers = [worker.username for worker in get_all_workers()]

    return render_template("index.html", workers = workers)


@app.route("/username/<username>")
def check(username):

    now = datetime.datetime.now()

    user = get_user(None, username=username)

    p_tasks = get_periodic_task_users_of_user(user.id)

    today_p_tasks = []

    mail(user.user_id, f"{p_tasks}")

    for task in p_tasks:
        if task.current_state is None:
            if str(now.today().date().weekday() + 1) in task.get_days_list():
                today_p_tasks.append(task)
        else:
            if task.current_state.split(':')[0] == 'work':
                today_p_tasks.append(task)

    mail(user.user_id, f"{today_p_tasks}")

    hour = now.hour

    if len(str(hour)) == 1:
        minute = "0" + str(hour)

    elif len(str(hour)) == 2:
        minute = str(hour)

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

    mail(user.user_id, f"{now_str}")



    for task in today_p_tasks:

        times = task.get_times_list()

        for time in times:
            if time == now_str:
                return f"You can answer for time: {now_str}\nTask: {task.title}"

    return f"You can NOT answer((("




if __name__ == '__main__':
    app.run("0.0.0.0", 5000)

