# Happy debugging suckers!!!!

from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# 配置日志记录
logging.basicConfig(level=logging.INFO)
handler = RotatingFileHandler('app.log', maxBytes=5000000, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 用户信息加载
def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# 作业数据加载
# 确保作业数据结构中包含 student_comments 和 teacher_replies
# def load_homework_data():
#     if os.path.exists('homework_data.json'):
#         with open('homework_data.json', 'r') as f:
#             homework_data = json.load(f)
#             # 初始化每条作业记录的字段
#             for homework_number, submissions in homework_data.items():
#                 for submission in submissions:
#                     if 'student_comments' not in submission:
#                         submission['student_comments'] = []  # 初始化学生评论
#                     if 'teacher_replies' not in submission:
#                         submission['teacher_replies'] = []  # 初始化教师回复
#             return homework_data
#     return {}

def load_homework_data():
    if os.path.exists('homework_data.json'):
        with open('homework_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data.pop('content')
            # print(data)
            return data
            # return json.load(f).pop('content')
    return {}

def load_homework_content():
    if os.path.exists('homework_data.json'):
        with open('homework_data.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('content', {})
    return {}

homework_data = load_homework_data()
homework_content = load_homework_content()
# print(homework_content)
# 保存作业数据
def save_homework_data(homework_data):
    with open('homework_data.json', 'w', encoding='utf-8') as f:
        homework_data['content'] = homework_content
        json.dump(homework_data, f)

# 判断文件类型是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 登录验证
def get_user_by_credentials(username, password):
    users = load_users()
    for user in users:
        if user['name'] == username and user['id'] == password:
            return user
    return None

# 记录访问日志
def log_access(route, method, ip):
    logger.info(f"访问时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, 访问方式: {method}, "
                f"访问用户: {'未登录' if 'user' not in session else session['user']['name']}, "
                f"访问路由: {route}, "
                f"访问IP: {ip}")

def get_real_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For 可能是多个 IP 地址的列表，取第一个
        real_ip = forwarded_for.split(',')[0]
    else:
        # 如果没有 X-Forwarded-For，使用 remote_addr
        real_ip = request.remote_addr
    return real_ip

@app.route('/', methods=['GET', 'POST'])
def login():
    log_access(request.path, request.method, get_real_ip())
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_credentials(username, password)

        if user:
            session['user'] = user
            return redirect(url_for('index'))  # 登录成功后跳转到首页
        else:
            flash("Invalid credentials!", "danger")
            return render_template('login.html', message="用户名或密码错误，请重试。")
    return render_template('login.html')

@app.route('/index')
def index():
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))  # 未登录则跳转到登录页面

    user = session['user']
    homework_data = load_homework_data()
    content = homework_content
    print(user['role'])
    # 学生查看自己的作业提交情况
    if user['role'] == 'student':
        student_homework = {
            homework_number: [
                submission for submission in submissions if submission.get('student_id') == user['id']
            ]
            for homework_number, submissions in homework_data.items()
        }
        # print(user['id'])
        for homework_number, submissions in homework_data.items():
            for submission in submissions:
                # print(submissions)
                if submission.get('student_id') == user['id']:
                    print(submission.get('teacher_reply'))
                    if submission.get('teacher_reply') != '':
                        is_correct = True
                    else:
                        is_correct = False
        return render_template('index.html', user=user, homework_data=student_homework, content=content, is_correct=is_correct)

    # 教师查看所有学生的作业
    elif user['role'] == 'teacher':
        return redirect(url_for('teacher_review'))

    # 课代表查看所有学生的作业
    elif user['role'] == 'classrep':
        return redirect(url_for('class_rep_manage'))

    else:
        return redirect(url_for('admin'))

# 修改作业数据的结构：确保每个作业数据包含学生的 id 或 name
@app.route('/submit_homework/<homework_number>', methods=['GET', 'POST'])
def submit_homework(homework_number):
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user['role'] != 'student':
        return redirect(url_for('index'))

    homework_data = load_homework_data()
    content = homework_content.get(homework_number, "未找到作业内容")

    if request.method == 'POST':
        files = request.files.getlist('files')
        comment = request.form.get('comment')
        filenames = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = str(user['name']) + secure_filename(file.filename)
                filepath = os.path.join(f'static/uploads/{homework_number}', filename)
                file.save(filepath)
                filenames.append(filename)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if homework_number not in homework_data:
            homework_data[homework_number] = []

        # 查找该学生是否已经提交过此作业
        existing_submission = next((entry for entry in homework_data[homework_number] if entry['student_id'] == user['id']), None)

        if existing_submission:
            existing_submission['file'] = filenames
            existing_submission['comment'] = comment
            existing_submission['timestamp'] = timestamp
        else:
            homework_data[homework_number].append({
                'student': user['name'],
                'student_id': user['id'],  # 确保保存 student_id
                'file': filenames,
                'comment': comment,
                'timestamp': timestamp
            })

        save_homework_data(homework_data)
        flash('作业提交成功！', 'success')
        return redirect(url_for('index'))
    print(content)
    return render_template('submit_homework.html', homework_number=homework_number, content=content)

@app.route('/view_homework/<homework_number>', methods=['GET', 'POST'])
def view_homework(homework_number):
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user['role'] != 'student':
        return redirect(url_for('index'))

    homework_data = load_homework_data()
    content = homework_content.get(homework_number, "未找到作业内容")

    # 查找对应作业和学生的提交记录
    homework_submission = None
    for submission in homework_data.get(homework_number, []):
        if submission['student'] == user['name']:
            homework_submission = submission
            break

    if not homework_submission:
        flash('未找到该作业的提交记录！', 'warning')
        return redirect(url_for('index'))

    # 如果是POST请求，学生可以提交新的评论
    if request.method == 'POST':
        new_comment = request.form['new_comment']
        if new_comment:
            homework_submission['student_comments'].append({
                'comment': new_comment,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_homework_data(homework_data)
            flash('评论提交成功！', 'success')
            return redirect(url_for('view_homework', homework_number=homework_number))
    print(homework_submission)
    homework_submission['file'] = [os.path.join(f'static/uploads/{homework_number}', os.path.basename(filename)) for filename in homework_submission['file']]
    return render_template('view_homework.html', homework_submission=homework_submission, content=content, homework_number=homework_number)

@app.route('/teacher_review', methods=['GET', 'POST'])
def teacher_review():
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user['role'] != 'teacher':
        return redirect(url_for('index'))

    homework_data = load_homework_data()
    users = load_users()

    # 获取作业数量（n）和学生数量（m）
    n = len(homework_data)  # 作业数量
    m = len(users)  # 学生数量

    # 获取切换视图的模式，默认为按提交时间排序
    view_mode = request.args.get('view_mode', 'time')  # 默认为按时间查看

    if view_mode == 'time':
        # 按提交时间倒序显示作业
        sorted_homework_data = {}
        for homework_number, submissions in homework_data.items():
            sorted_homework_data[homework_number] = sorted(submissions, key=lambda x: x['timestamp'], reverse=True)
        return render_template('teacher_review.html', homework_data=sorted_homework_data, users=users, view_mode=view_mode, n=n, m=m)

    elif view_mode == 'summary':
        # 按总表显示作业
        # 总表格：行是学生，列是作业，显示是否已提交
        summary_table = []
        for user in users:
            if user['role'] == 'teacher':
                continue  # 教师不显示在总表格中
            else:
                student_submission = []
                for homework_number in range(1, n+1):  # 假设作业编号从1到n
                    homework_number_str = "homework_" + str(homework_number)
                    submission_found = False
                    homework_link = ""

                    # 检查该作业是否有该学生的提交记录
                    if homework_number_str in homework_data:
                        for submission in homework_data[homework_number_str]:
                            if submission['student'] == user['name']:
                                submission_found = True
                                homework_link = url_for('teacher_review_reply', homework_number=homework_number_str, student_name=submission['student'])
                                break

                    if submission_found:
                        student_submission.append(f'<a href="{homework_link}" target="_blank">已提交</a>')
                    else:
                        student_submission.append('未提交')
                summary_table.append({'student_name': user['name'], 'submissions': student_submission})

        return render_template('teacher_review.html', summary_table=summary_table, users=users, view_mode=view_mode, n=n, m=m)

@app.route('/teacher_review_reply/<homework_number>/<student_name>', methods=['GET', 'POST'])
def teacher_review_reply(homework_number, student_name):
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user['role'] != 'teacher':
        return redirect(url_for('index'))

    homework_data = load_homework_data()
    content = homework_content.get(homework_number, "未找到作业内容")

    # 查找对应作业的提交记录
    homework = None
    if homework_number in homework_data:
        for submission in homework_data[homework_number]:
            if submission['student'] == student_name:
                homework = submission
                break

    if not homework:
        return "未找到该作业提交记录"

    if request.method == 'POST':
        reply = request.form['reply']
        homework['teacher_reply'] = reply
        save_homework_data(homework_data)  # 保存更新后的作业数据
        flash("回复成功！", "success")
        return redirect(url_for('teacher_review'))  # 回复完成后跳转到教师批阅页面
    homework['file'] = [os.path.join(f'static/uploads/{homework_number}', os.path.basename(filename)) for filename in homework['file']]
    return render_template('teacher_review_reply.html', homework=homework, homework_number=homework_number, student_name=student_name, content=content)

@app.route('/class_rep_manage', methods=['GET', 'POST'])
def class_rep_manage():
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    if user['role'] != 'classrep':
        return redirect(url_for('index'))

    homework_data = load_homework_data()  # 载入作业数据
    users = load_users()  # 载入用户数据

    # 获取作业数量（n）和学生数量（m）
    n = len(homework_data)  # 作业数量
    m = len(users)  # 学生数量

    # 获取切换视图的模式，默认为按提交时间排序
    view_mode = request.args.get('view_mode', 'time')  # 默认为按时间查看

    if view_mode == 'time':
        # 按提交时间倒序显示作业
        sorted_homework_data = {}
        for homework_number, submissions in homework_data.items():
            sorted_homework_data[homework_number] = sorted(submissions, key=lambda x: x['timestamp'], reverse=True)
        return render_template('class_rep_manage.html', homework_data=sorted_homework_data, users=users, view_mode=view_mode, n=n, m=m)

    elif view_mode == 'summary':
        # 按总表显示作业
        # 总表格：行是学生，列是作业，显示是否已提交
        summary_table = []
        for user in users:
            if user['role'] == 'teacher':
                continue  # 教师不显示在总表格中
            else:
                student_submission = []
                for homework_number in range(1, n+1):  # 假设作业编号从1到n
                    homework_number_str = "homework_" + str(homework_number)
                    submission_found = False
                    # 检查该作业是否有该学生的提交记录
                    if homework_number_str in homework_data:
                        for submission in homework_data[homework_number_str]:
                            if submission['student'] == user['name']:
                                submission_found = True
                                break

                    student_submission.append('已提交' if submission_found else '未提交')
                summary_table.append({'student_name': user['name'], 'submissions': student_submission})
        return render_template('class_rep_manage.html', summary_table=summary_table, users=users, view_mode=view_mode, n=n, m=m)
@app.route('/enter_as_student', methods=['GET'])
def enter_as_student():
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']
    print(user)
    if user['role'] != 'classrep':
        return redirect(url_for('index'))

    # 临时修改用户角色为 student
    session['user']['role'] = 'student'
    print(session['user'])
    session.modified = True
    # 确保角色变更立即生效
    return redirect(url_for('index'))

@app.route('/set_role_classrep', methods=['POST'])
def set_role_classrep():
    log_access(request.path, request.method, request.remote_addr)
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    # 修改 session 中的角色为 classrep
    session['user']['role'] = 'classrep'
    session.modified = True  # 强制 Flask 更新 session

    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    log_access(request.path, request.method, request.remote_addr)
    with open('app.log', 'r') as f:
        logs = f.read()

    return render_template('admin_dashboard.html', logs=logs)

@app.route('/logout')
def logout():
    log_access(request.path, request.method, request.remote_addr)
    session.pop('user', None)  # 删除session中的用户数据
    return redirect(url_for('login'))  # 重定向到主页

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)