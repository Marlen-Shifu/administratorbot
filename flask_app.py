from flask import Flask

from flask import render_template

from db.operations import get_all_workers


app = Flask(__name__)

@app.route("/")
def hello_world():

    workers = [worker.username for worker in get_all_workers()]

    return render_template("index.html", workers = workers)


if __name__ == '__main__':
    app.run("0.0.0.0", 5000)

