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
from ai_analytics import AIAnalytics

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

# 初始化AI分析模块
ai_analytics = AIAnalytics()

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

@app.route('/api/ai/forecast/<dataset_id>', methods=['POST'])
def ai_forecast(dataset_id):
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
        
        # 获取请求参数
        data = request.json
        date_column = data.get('date_column')
        target_column = data.get('target_column')
        periods = int(data.get('periods', 30))
        
        # 执行时间序列预测
        result = ai_analytics.time_series_forecast(df, date_column, target_column, periods)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'预测失败: {str(e)}'}), 500

@app.route('/api/ai/anomaly/<dataset_id>', methods=['POST'])
def ai_anomaly_detection(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 获取请求参数
        data = request.json
        columns = data.get('columns', [])
        
        # 执行异常检测
        result = ai_analytics.anomaly_detection(df, columns)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'异常检测失败: {str(e)}'}), 500

@app.route('/api/ai/correlation/<dataset_id>', methods=['POST'])
def ai_correlation(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 获取请求参数
        data = request.json
        target_column = data.get('target_column')
        
        # 执行相关性分析
        result = ai_analytics.correlation_analysis(df, target_column)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'相关性分析失败: {str(e)}'}), 500

@app.route('/api/ai/pattern/<dataset_id>', methods=['POST'])
def ai_pattern(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 获取请求参数
        data = request.json
        columns = data.get('columns', [])
        n_clusters = int(data.get('n_clusters', 3))
        
        # 执行模式挖掘
        result = ai_analytics.pattern_mining(df, columns, n_clusters)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'模式挖掘失败: {str(e)}'}), 500

@app.route('/api/ai/importance/<dataset_id>', methods=['POST'])
def ai_importance(dataset_id):
    if dataset_id not in datasets:
        return jsonify({'error': '数据集不存在'}), 404
    
    dataset = datasets[dataset_id]
    file_path = os.path.normpath(dataset['path'])
    if not os.path.exists(file_path):
        return jsonify({'error': f'无法找到数据文件: {file_path}'}), 404
    
    try:
        if dataset['type'] == 'csv':
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 获取请求参数
        data = request.json
        target_column = data.get('target_column')
        feature_columns = data.get('feature_columns', [])
        
        # 执行特征重要性分析
        result = ai_analytics.feature_importance(df, target_column, feature_columns)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'特征重要性分析失败: {str(e)}'}), 500

@app.route('/ai_analysis/<dataset_id>')
def ai_analysis(dataset_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if dataset_id not in datasets:
        flash('数据集不存在！', 'danger')
        return redirect(url_for('datasets_page'))
    
    dataset = datasets[dataset_id]
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
    
    # 检测数值列和日期列
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 检测可能的日期列
    date_columns = []
    for col in df.columns:
        try:
            pd.to_datetime(df[col])
            date_columns.append(col)
        except:
            pass
    
    return render_template(
        'ai_analysis.html', 
        dataset=dataset, 
        username=session['username'], 
        dataset_id=dataset_id,
        columns=dataset['columns'],
        numeric_columns=numeric_columns,
        date_columns=date_columns
    )

@app.route('/create_ai_example_dataset')
def create_ai_example_dataset():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # 创建时间序列数据集
        if os.path.exists('ai_data_timeseries.csv'):
            timeseries_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timeseries_id}_ai_time_series_data.csv")
            # 复制文件
            import shutil
            shutil.copy('ai_data_timeseries.csv', file_path)
            
            # 读取数据并保存到datasets字典
            df = pd.read_csv(file_path)
            datasets[timeseries_id] = {
                'name': 'AI时间序列分析数据.csv',
                'path': file_path,
                'type': 'csv',
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
            flash('AI时间序列数据集创建成功！', 'success')
        
        # 创建客户数据集
        if os.path.exists('ai_data_customer.csv'):
            customer_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{customer_id}_ai_customer_data.csv")
            # 复制文件
            import shutil
            shutil.copy('ai_data_customer.csv', file_path)
            
            # 读取数据并保存到datasets字典
            df = pd.read_csv(file_path)
            datasets[customer_id] = {
                'name': 'AI客户分析数据.csv',
                'path': file_path,
                'type': 'csv',
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
            flash('AI客户分析数据集创建成功！', 'success')
        
        # 创建产品数据集
        if os.path.exists('ai_data_product.csv'):
            product_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{product_id}_ai_product_data.csv")
            # 复制文件
            import shutil
            shutil.copy('ai_data_product.csv', file_path)
            
            # 读取数据并保存到datasets字典
            df = pd.read_csv(file_path)
            datasets[product_id] = {
                'name': 'AI产品分析数据.csv',
                'path': file_path,
                'type': 'csv',
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
            flash('AI产品分析数据集创建成功！', 'success')
        
        return redirect(url_for('datasets_page'))
    except Exception as e:
        flash(f'创建示例数据集失败: {str(e)}', 'danger')
        return redirect(url_for('datasets_page'))

@app.route('/create_sales_example')
def create_sales_example():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # 检查演示销售数据文件是否存在，如果不存在则创建
        if not os.path.exists('demo_sales_data.csv'):
            # 创建示例销售数据
            sales_data = pd.DataFrame({
                '日期': pd.date_range(start='2023-01-01', periods=100, freq='D'),
                '产品ID': np.random.choice(['P001', 'P002', 'P003', 'P004', 'P005'], 100),
                '产品名称': np.random.choice(['笔记本电脑', '智能手机', '平板电脑', '耳机', '智能手表'], 100),
                '销售量': np.random.randint(1, 50, 100),
                '单价': np.random.choice([4999, 3999, 2999, 499, 1999], 100),
                '销售额': np.random.randint(10000, 100000, 100),
                '销售区域': np.random.choice(['华东', '华南', '华北', '西南', '西北'], 100),
                '销售渠道': np.random.choice(['线上', '线下', '电话', '代理商'], 100),
                '客户满意度': np.random.randint(1, 6, 100)
            })
            # 计算实际销售额
            sales_data['销售额'] = sales_data['销售量'] * sales_data['单价']
            sales_data.to_csv('demo_sales_data.csv', index=False)
        
        # 复制到用户上传目录
        sales_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{sales_id}_demo_sales_data.csv")
        import shutil
        shutil.copy('demo_sales_data.csv', file_path)
        
        # 读取数据并保存到datasets字典
        df = pd.read_csv(file_path)
        datasets[sales_id] = {
            'name': '销售数据分析示例.csv',
            'path': file_path,
            'type': 'csv',
            'columns': df.columns.tolist(),
            'shape': df.shape
        }
        flash('销售数据示例创建成功！', 'success')
        return redirect(url_for('datasets_page'))
    except Exception as e:
        flash(f'创建销售数据示例失败: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/create_survey_example')
def create_survey_example():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # 检查演示客户调查数据文件是否存在，如果不存在则创建
        if not os.path.exists('demo_customer_survey.csv'):
            # 创建示例客户调查数据
            np.random.seed(42)
            num_records = 200
            survey_data = pd.DataFrame({
                '客户ID': [f'CUS{i:04d}' for i in range(1, num_records+1)],
                '年龄': np.random.randint(18, 70, num_records),
                '性别': np.random.choice(['男', '女'], num_records),
                '会员等级': np.random.choice(['普通', '银卡', '金卡', '钻石'], num_records, p=[0.4, 0.3, 0.2, 0.1]),
                '使用频率': np.random.choice(['每天', '每周', '每月', '很少'], num_records),
                '产品质量评分': np.random.randint(1, 6, num_records),
                '服务满意度': np.random.randint(1, 6, num_records),
                '界面友好度': np.random.randint(1, 6, num_records),
                '价格满意度': np.random.randint(1, 6, num_records),
                '推荐意愿': np.random.randint(1, 11, num_records),
                '反馈日期': pd.date_range(start='2023-01-01', periods=num_records)
            })
            
            # 添加一些相关性
            survey_data['总体满意度'] = (survey_data['产品质量评分'] + survey_data['服务满意度'] + 
                                  survey_data['界面友好度'] + survey_data['价格满意度']) / 4
            survey_data['总体满意度'] = survey_data['总体满意度'].round(1)
            
            # 添加一些文本反馈
            feedback_options = [
                '非常满意，产品质量很好',
                '服务态度很好，但价格有点贵',
                '界面设计不太友好，需要改进',
                '产品质量一般，但价格合理',
                '整体体验不错，会继续使用',
                '服务有待提高，响应太慢了',
                '非常喜欢这个产品，会推荐给朋友',
                '希望能提供更多功能',
                '价格太贵了，考虑换其他产品',
                '质量不错，但使用体验一般'
            ]
            survey_data['文本反馈'] = np.random.choice(feedback_options, num_records)
            
            survey_data.to_csv('demo_customer_survey.csv', index=False)
        
        # 复制到用户上传目录
        survey_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{survey_id}_demo_customer_survey.csv")
        import shutil
        shutil.copy('demo_customer_survey.csv', file_path)
        
        # 读取数据并保存到datasets字典
        df = pd.read_csv(file_path)
        datasets[survey_id] = {
            'name': '客户调查数据分析示例.csv',
            'path': file_path,
            'type': 'csv',
            'columns': df.columns.tolist(),
            'shape': df.shape
        }
        flash('客户调查数据示例创建成功！', 'success')
        return redirect(url_for('datasets_page'))
    except Exception as e:
        flash(f'创建客户调查数据示例失败: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/create_inventory_example')
def create_inventory_example():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # 检查演示库存数据文件是否存在，如果不存在则创建
        if not os.path.exists('demo_inventory_data.csv'):
            # 创建示例库存数据
            np.random.seed(123)
            num_records = 150
            products = ['笔记本电脑', '智能手机', '平板电脑', '耳机', '智能手表', '充电器', '保护壳', '显示器', '键盘', '鼠标']
            categories = ['电子设备', '配件', '外设']
            
            # 为产品分配类别
            product_category = {
                '笔记本电脑': '电子设备', '智能手机': '电子设备', '平板电脑': '电子设备', 
                '耳机': '配件', '智能手表': '电子设备', '充电器': '配件', 
                '保护壳': '配件', '显示器': '外设', '键盘': '外设', '鼠标': '外设'
            }
            
            # 创建产品记录
            inventory_data = pd.DataFrame({
                '产品ID': [f'PROD{i:03d}' for i in range(1, len(products)+1)],
                '产品名称': products,
                '类别': [product_category[p] for p in products],
                '当前库存': np.random.randint(10, 200, len(products)),
                '最低库存': np.random.randint(5, 30, len(products)),
                '最高库存': np.random.randint(100, 300, len(products)),
                '采购周期(天)': np.random.randint(3, 15, len(products)),
                '单位成本': np.random.randint(50, 2000, len(products)),
                '销售价格': np.random.randint(100, 5000, len(products)),
                '供应商': np.random.choice(['供应商A', '供应商B', '供应商C', '供应商D'], len(products)),
                '上次更新': pd.date_range(start='2023-01-01', periods=len(products))
            })
            
            # 创建历史库存记录
            dates = pd.date_range(start='2023-01-01', periods=30)
            history_records = []
            
            for product_id, product_name in zip(inventory_data['产品ID'], inventory_data['产品名称']):
                category = product_category[product_name]
                for date in dates:
                    incoming = np.random.randint(0, 50) if np.random.random() < 0.3 else 0
                    outgoing = np.random.randint(0, 30)
                    history_records.append({
                        '产品ID': product_id,
                        '产品名称': product_name,
                        '类别': category,
                        '日期': date,
                        '入库数量': incoming,
                        '出库数量': outgoing,
                        '库存变化': incoming - outgoing
                    })
            
            history_df = pd.DataFrame(history_records)
            
            # 合并数据
            inventory_data.to_csv('demo_inventory_data.csv', index=False)
            history_df.to_csv('demo_inventory_history.csv', index=False)
            
            # 为了简化，只使用主库存数据
            inventory_data = pd.concat([inventory_data, history_df])
        
        # 复制到用户上传目录
        inventory_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{inventory_id}_demo_inventory_data.csv")
        import shutil
        shutil.copy('demo_inventory_data.csv', file_path)
        
        # 读取数据并保存到datasets字典
        df = pd.read_csv(file_path)
        datasets[inventory_id] = {
            'name': '库存数据分析示例.csv',
            'path': file_path,
            'type': 'csv',
            'columns': df.columns.tolist(),
            'shape': df.shape
        }
        flash('库存数据示例创建成功！', 'success')
        return redirect(url_for('datasets_page'))
    except Exception as e:
        flash(f'创建库存数据示例失败: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/create_timeseries_example')
def create_timeseries_example():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    try:
        # 检查是否已有AI时间序列数据
        if os.path.exists('ai_data_timeseries.csv'):
            # 使用现有的AI时间序列数据
            timeseries_id = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timeseries_id}_ai_time_series_data.csv")
            import shutil
            shutil.copy('ai_data_timeseries.csv', file_path)
            
            # 读取数据并保存到datasets字典
            df = pd.read_csv(file_path)
            datasets[timeseries_id] = {
                'name': '时间序列分析示例.csv',
                'path': file_path,
                'type': 'csv',
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
            flash('时间序列数据示例创建成功！', 'success')
            return redirect(url_for('datasets_page'))
        else:
            # 创建新的时间序列数据
            date_rng = pd.date_range(start='2022-01-01', end='2023-01-01', freq='D')
            
            # 创建基础趋势
            trend = np.linspace(100, 200, len(date_rng))
            
            # 添加季节性
            season = 30 * np.sin(np.linspace(0, 12 * np.pi, len(date_rng)))
            
            # 添加周模式
            weekly = 20 * np.sin(np.linspace(0, 52 * 2 * np.pi, len(date_rng)))
            
            # 添加噪声
            noise = np.random.normal(0, 10, len(date_rng))
            
            # 组合数据
            sales = trend + season + weekly + noise
            
            # 创建促销活动影响
            promotions = np.zeros(len(date_rng))
            # 随机选择10天作为促销日
            promo_days = np.random.choice(len(date_rng), 10, replace=False)
            promotions[promo_days] = 1
            # 促销效果
            sales += promotions * 50
            
            # 创建DataFrame
            df = pd.DataFrame({
                'date': date_rng,
                'sales': sales,
                'promotion': promotions
            })
            
            # 添加更多特征
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            
            # 保存数据
            file_path = 'ai_data_timeseries.csv'
            df.to_csv(file_path, index=False)
            
            # 复制到用户目录
            timeseries_id = str(uuid.uuid4())
            user_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timeseries_id}_time_series_data.csv")
            import shutil
            shutil.copy(file_path, user_file_path)
            
            # 保存到datasets字典
            datasets[timeseries_id] = {
                'name': '时间序列分析示例.csv',
                'path': user_file_path,
                'type': 'csv',
                'columns': df.columns.tolist(),
                'shape': df.shape
            }
            
            flash('时间序列数据示例创建成功！', 'success')
            return redirect(url_for('datasets_page'))
    except Exception as e:
        flash(f'创建时间序列数据示例失败: {str(e)}', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 