from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils import *
import os

teacher = Blueprint('teacher', __name__)


@teacher.route('/review', methods=['GET', 'POST'])
def review():
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'teacher':
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
        return render_template('teacher_review.html',
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
                submission_found = False
                homework_link = ""

                if homework_number in homework_data:
                    for submission in homework_data[homework_number]:
                        if submission['student'] == user['name']:
                            submission_found = True
                            homework_link = url_for('teacher.review_reply',
                                                    homework_number=homework_number,
                                                    student_name=submission['student'])
                            break

                cell = f'<a href="{homework_link}" target="_blank">已提交</a>' \
                    if submission_found else '未提交'
                student_submission.append(cell)

            summary_table.append({
                'student_name': user['name'],
                'submissions': student_submission
            })

        return render_template('teacher_review.html',
                               summary_table=summary_table,
                               users=users,
                               view_mode=view_mode,
                               n=n, m=m)


@teacher.route('/review_reply/<homework_number>/<student_name>',
               methods=['GET', 'POST'])
def review_reply(homework_number, student_name):
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'teacher':
        return redirect(url_for('auth.login'))

    homework_data = load_homework_data()
    content = load_homework_content().get(homework_number, "未找到作业内容")

    homework = next(
        (submission for submission in homework_data.get(homework_number, [])
         if submission['student'] == student_name),
        None
    )

    if not homework:
        return "未找到该作业提交记录"

    if request.method == 'POST':
        reply = request.form['reply']
        homework['teacher_reply'] = reply
        save_homework_data(homework_data)
        flash("回复成功！", "success")
        return redirect(url_for('teacher.review'))

    homework['file'] = [
        os.path.join(f'static/uploads/{homework_number}',
                     os.path.basename(filename))
        for filename in homework['file']
    ]

    return render_template('teacher_review_reply.html',
                           homework=homework,
                           homework_number=homework_number,
                           student_name=student_name,
                           content=content)