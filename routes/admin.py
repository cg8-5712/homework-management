from flask import Blueprint, render_template, session, redirect, url_for, request
from utils import log_access, get_real_ip
import requests
admin = Blueprint('admin', __name__)

@admin.route('/')
def index():
    log_access(request.path, request.method, get_real_ip())
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    with open('app.log', 'r') as f:
        logs = f.read()

    return render_template('admin_dashboard.html', logs=logs)