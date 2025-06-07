from flask import session, request
import json
import os
import logging
from logging.handlers import RotatingFileHandler  # 正确的导入方式
from datetime import datetime
from werkzeug.utils import secure_filename

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# 创建日志目录
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志记录
logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

handler = RotatingFileHandler(
    filename=os.path.join(log_dir, 'app.log'),
    maxBytes=5 * 1024 * 1024,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)

def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_homework_data():
    if os.path.exists('homework_data.json'):
        with open('homework_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data.pop('content')
            return data
    return {}

def load_homework_content():
    if os.path.exists('homework_data.json'):
        with open('homework_data.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('content', {})
    return {}

def save_homework_data(homework_data):
    with open('homework_data.json', 'w', encoding='utf-8') as f:
        homework_data['content'] = homework_content
        json.dump(homework_data, f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_by_credentials(username, password):
    users = load_users()
    for user in users:
        if user['name'] == username and user['id'] == password:
            return user
    return None

def log_access(route, method, ip):
    logger.info(f"访问时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, 访问方式: {method}, "
                f"访问用户: {'未登录' if 'user' not in session else session['user']['name']}, "
                f"访问路由: {route}, "
                f"访问IP: {ip}")

def get_real_ip():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        real_ip = forwarded_for.split(',')[0]
    else:
        real_ip = request.remote_addr
    return real_ip

homework_content = load_homework_content()