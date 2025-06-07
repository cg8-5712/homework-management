from flask import Flask
from routes.auth import auth
from routes.student import student
from routes.teacher import teacher
from routes.class_rep import class_rep
from routes.admin import admin

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 注册蓝图
app.register_blueprint(auth)
app.register_blueprint(student, url_prefix='/student')
app.register_blueprint(teacher, url_prefix='/teacher')
app.register_blueprint(class_rep, url_prefix='/class_rep')
app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)