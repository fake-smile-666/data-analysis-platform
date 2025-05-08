from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import pandas as pd
import numpy as np
import json
import plotly
import plotly.express as px
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 创建上传文件夹
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 模拟用户数据库
users = {
    'admin': {
        'password': generate_password_hash('admin'),
        'name': '管理员'
    }
}

# 模拟数据存储
datasets = {}

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        
        if username in users:
            flash('用户名已存在！', 'danger')
        else:
            users[username] = {
                'password': generate_password_hash(password),
                'name': name
            }
            flash('注册成功，请登录！', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有文件被上传！', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件！', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            dataset_id = str(uuid.uuid4())
            # 使用os.path.join确保路径格式正确
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{dataset_id}_{filename}")
            
            # 确保上传目录存在
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            try:
                file.save(file_path)
                
                # 检查文件是否成功保存
                if not os.path.exists(file_path):
                    flash('文件保存失败，请重试！', 'danger')
                    return redirect(request.url)
                
                try:
                    # 尝试读取为CSV
                    df = pd.read_csv(file_path)
                    datasets[dataset_id] = {
                        'name': filename,
                        'path': file_path,
                        'type': 'csv',
                        'columns': df.columns.tolist(),
                        'shape': df.shape
                    }
                    flash('文件上传成功！', 'success')
                    return redirect(url_for('datasets_page'))
                except:
                    try:
                        # 尝试读取为Excel
                        df = pd.read_excel(file_path)
                        datasets[dataset_id] = {
                            'name': filename,
                            'path': file_path,
                            'type': 'excel',
                            'columns': df.columns.tolist(),
                            'shape': df.shape
                        }
                        flash('文件上传成功！', 'success')
                        return redirect(url_for('datasets_page'))
                    except Exception as e:
                        # 如果读取失败，删除文件并显示错误
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        flash(f'无法解析文件: {str(e)}，请确保上传CSV或Excel文件！', 'danger')
            except Exception as e:
                flash(f'文件上传失败: {str(e)}', 'danger')
    
    return render_template('upload.html', username=session['username'])

@app.route('/datasets')
def datasets_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('datasets.html', datasets=datasets, username=session['username'])

@app.route('/analyze/<dataset_id>')
def analyze(dataset_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if dataset_id not in datasets:
        flash('数据集不存在！', 'danger')
        return redirect(url_for('datasets_page'))
    
    dataset = datasets[dataset_id]
    # 使用os.path模块确保路径正确，并检查文件是否存在
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        flash(f'无法找到数据文件: {file_path}', 'danger')
        return redirect(url_for('datasets_page'))
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        flash(f'读取文件时出错: {str(e)}', 'danger')
        return redirect(url_for('datasets_page'))
    
    return render_template('analyze.html', dataset=dataset, columns=dataset['columns'], username=session['username'], dataset_id=dataset_id)

@app.route('/api/data/<dataset_id>')
def get_data(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    # 使用os.path模块确保路径正确，并检查文件是否存在
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        data = {
            'columns': df.columns.tolist(),
            'data': df.head(100).to_dict('records')
        }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': f'读取文件时出错: {str(e)}'}), 500

@app.route('/api/plot/<dataset_id>', methods=['POST'])
def create_plot(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    # 使用os.path模块确保路径正确，并检查文件是否存在
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        plot_type = request.json.get('plot_type')
        x_column = request.json.get('x_column')
        y_column = request.json.get('y_column')
        
        if plot_type == 'bar':
            fig = px.bar(df, x=x_column, y=y_column)
        elif plot_type == 'line':
            fig = px.line(df, x=x_column, y=y_column)
        elif plot_type == 'scatter':
            fig = px.scatter(df, x=x_column, y=y_column)
        elif plot_type == 'pie':
            fig = px.pie(df, names=x_column, values=y_column)
        else:
            return jsonify({'error': '不支持的图表类型'}), 400
        
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify({'graph': graphJSON})
    except Exception as e:
        return jsonify({'error': f'生成图表时出错: {str(e)}'}), 500

@app.route('/api/stats/<dataset_id>')
def get_stats(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    # 使用os.path模块确保路径正确，并检查文件是否存在
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max())
            }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': f'计算统计信息时出错: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 