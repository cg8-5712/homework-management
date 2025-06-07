from flask import Blueprint, render_template, request, redirect, url_for, session
from utils import *

class_rep = Blueprint('class_rep', __name__)

@class_rep.route('/manage', methods=['GET', 'POST'])
def manage():
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'classrep':
        return redirect(url_for('auth.login'))

    homework_data = load_homework_data()
    users = load_users()
    n = len(homework_data)
    m = len([u for u in users if u['role'] != 'teacher'])
    view_mode = request.args.get('view_mode', 'time')

    if view_mode == 'time':
        sorted_homework_data = {
            number: sorted(submissions,
                         key=lambda x: x['timestamp'],
                         reverse=True)
            for number, submissions in homework_data.items()
        }
        return render_template('class_rep_manage.html',
                             homework_data=sorted_homework_data,
                             users=users,
                             view_mode=view_mode,
                             n=n, m=m)
    else:
        summary_table = []
        for user in users:
            if user['role'] == 'teacher':
                continue
            student_submission = []
            for i in range(1, n + 1):
                homework_number = f"homework_{i}"
                submission_found = any(
                    submission['student'] == user['name']
                    for submission in homework_data.get(homework_number, [])
                )
                student_submission.append('已提交' if submission_found else '未提交')

            summary_table.append({
                'student_name': user['name'],
                'submissions': student_submission
            })

        return render_template('class_rep_manage.html',
                             summary_table=summary_table,
                             users=users,
                             view_mode=view_mode,
                             n=n, m=m)

@class_rep.route('/enter_as_student')
def enter_as_student():
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'classrep':
        return redirect(url_for('auth.login'))

    session['user']['role'] = 'student'
    session.modified = True
    return redirect(url_for('student.index'))

@class_rep.route('/set_role_classrep', methods=['POST'])
def set_role_classrep():
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    session['user']['role'] = 'classrep'
    session.modified = True
    return redirect(url_for('class_rep.manage'))