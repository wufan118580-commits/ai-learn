from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello from SCF!"


# 这个函数会被云函数调用
def main_handler(event, context):
    from serverless_wsgi import handle_request

    return handle_request(app, event, context)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000)
