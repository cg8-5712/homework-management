from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils import log_access, get_real_ip, get_user_by_credentials

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    log_access(request.path, request.method, get_real_ip())
    if 'user' in session:
        user = session['user']
        if user['role'] == 'student':
            return redirect(url_for('student.index'))
        elif user['role'] == 'teacher':
            return redirect(url_for('teacher.review'))
        elif user['role'] == 'classrep':
            return redirect(url_for('class_rep.manage'))
        elif user['role'] == 'admin':
            return redirect(url_for('admin.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_credentials(username, password)

        if user:
            session['user'] = user
            if user['role'] == 'student':
                return redirect(url_for('student.index'))
            elif user['role'] == 'teacher':
                return redirect(url_for('teacher.review'))
            elif user['role'] == 'classrep':
                return redirect(url_for('class_rep.manage'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin.index'))
        else:
            flash("用户名或密码错误，请重试。", "danger")
            return render_template('login.html')

    return render_template('login.html')

@auth.route('/logout')
def logout():
    log_access(request.path, request.method, get_real_ip())
    session.pop('user', None)
    return redirect(url_for('auth.login'))