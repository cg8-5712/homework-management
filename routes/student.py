from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils import *
from werkzeug.utils import secure_filename
import os
from datetime import datetime

student = Blueprint('student', __name__)


@student.route('/index')
def index():
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'student':
        return redirect(url_for('auth.login'))

    homework_data = load_homework_data()
    content = load_homework_content()

    student_homework = {
        homework_number: [
            submission for submission in submissions
            if submission.get('student_id') == user['id']
        ]
        for homework_number, submissions in homework_data.items()
    }

    is_correct = False
    for submissions in homework_data.values():
        for submission in submissions:
            if (submission.get('student_id') == user['id'] and
                    submission.get('teacher_reply')):
                is_correct = True
                break

    return render_template('index.html',
                           user=user,
                           homework_data=student_homework,
                           content=content,
                           is_correct=is_correct)


@student.route('/submit/<homework_number>', methods=['GET', 'POST'])
def submit_homework(homework_number):
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'student':
        return redirect(url_for('student.index'))

    homework_data = load_homework_data()
    content = load_homework_content().get(homework_number, "未找到作业内容")

    if request.method == 'POST':
        files = request.files.getlist('files')
        comment = request.form.get('comment')
        filenames = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = f"{user['name']}{secure_filename(file.filename)}"
                upload_dir = os.path.join('static/uploads', homework_number)
                # 确保上传目录存在
                os.makedirs(upload_dir, exist_ok=True)
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                filenames.append(filename)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if homework_number not in homework_data:
            homework_data[homework_number] = []

        existing_submission = next(
            (entry for entry in homework_data[homework_number]
             if entry['student_id'] == user['id']),
            None
        )

        if existing_submission:
            existing_submission.update({
                'file': filenames,
                'comment': comment,
                'timestamp': timestamp
            })
        else:
            homework_data[homework_number].append({
                'student': user['name'],
                'student_id': user['id'],
                'file': filenames,
                'comment': comment,
                'timestamp': timestamp
            })

        save_homework_data(homework_data)
        flash('作业提交成功！', 'success')
        return redirect(url_for('student.index'))

    return render_template('submit_homework.html',
                           homework_number=homework_number,
                           content=content)


@student.route('/view/<homework_number>', methods=['GET', 'POST'])
def view_homework(homework_number):
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    user = session['user']
    if user['role'] != 'student':
        return redirect(url_for('student.index'))

    homework_data = load_homework_data()
    content = load_homework_content().get(homework_number, "未找到作业内容")

    homework_submission = next(
        (submission for submission in homework_data.get(homework_number, [])
         if submission['student'] == user['name']),
        None
    )

    if not homework_submission:
        flash('未找到该作业的提交记录！', 'warning')
        return redirect(url_for('student.index'))

    if request.method == 'POST':
        new_comment = request.form['new_comment']
        if new_comment:
            if 'student_comments' not in homework_submission:
                homework_submission['student_comments'] = []
            homework_submission['student_comments'].append({
                'comment': new_comment,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_homework_data(homework_data)
            flash('评论提交成功！', 'success')
            return redirect(url_for('student.view_homework',
                                    homework_number=homework_number))

    homework_submission['file'] = [
        os.path.join(f'static/uploads/{homework_number}',
                     os.path.basename(filename))
        for filename in homework_submission['file']
    ]

    return render_template('view_homework.html',
                           homework_submission=homework_submission,
                           content=content,
                           homework_number=homework_number)