import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.arima.model import ARIMA
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils
import json

class AIAnalytics:
    """AI辅助数据分析类，提供高级分析功能"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
    
    def time_series_forecast(self, df, date_column, target_column, periods=30):
        """
        时间序列预测
        
        参数:
            df: DataFrame，包含时间序列数据
            date_column: 日期列名
            target_column: 目标值列名
            periods: 预测未来的周期数
            
        返回:
            预测结果和可视化JSON
        """
        # 确保日期列是日期类型
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(date_column)
        
        # 设置日期为索引
        ts_data = df.set_index(date_column)[target_column]
        
        # 拟合ARIMA模型
        model = ARIMA(ts_data, order=(5,1,0))
        model_fit = model.fit()
        
        # 保存模型
        self.models[f"forecast_{target_column}"] = model_fit
        
        # 预测未来值
        forecast = model_fit.forecast(steps=periods)
        forecast_dates = pd.date_range(start=ts_data.index[-1], periods=periods+1, inclusive='right')
        forecast_df = pd.DataFrame({
            'date': forecast_dates,
            'forecast': forecast
        })
        
        # 创建可视化
        fig = go.Figure()
        
        # 添加历史数据
        fig.add_trace(go.Scatter(
            x=ts_data.index, 
            y=ts_data.values,
            mode='lines',
            name='历史数据'
        ))
        
        # 添加预测数据
        fig.add_trace(go.Scatter(
            x=forecast_df['date'],
            y=forecast_df['forecast'],
            mode='lines',
            name='预测数据',
            line=dict(dash='dash')
        ))
        
        # 设置图表布局
        fig.update_layout(
            title=f'{target_column}的时间序列预测',
            xaxis_title='日期',
            yaxis_title=target_column,
            legend_title='数据类型',
            hovermode='x unified'
        )
        
        # 转换为JSON
        forecast_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return {
            'forecast_data': forecast_df.to_dict('records'),
            'visualization': forecast_json,
            'model_summary': str(model_fit.summary())
        }
    
    def anomaly_detection(self, df, columns):
        """
        异常值检测
        
        参数:
            df: DataFrame，包含数据
            columns: 用于异常检测的列名列表
            
        返回:
            带有异常标记的DataFrame和可视化JSON
        """
        # 准备数据
        data = df[columns].copy()
        
        # 使用IsolationForest进行异常检测
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data)
        
        # 保存scaler
        self.scalers['anomaly_detection'] = scaler
        
        # 训练模型
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(scaled_data)
        
        # 保存模型
        self.models['anomaly_detection'] = model
        
        # 预测异常
        predictions = model.predict(scaled_data)
        anomaly_score = model.decision_function(scaled_data)
        
        # 添加异常标记到原始数据
        result_df = df.copy()
        result_df['异常标记'] = np.where(predictions == -1, '异常', '正常')
        result_df['异常分数'] = anomaly_score
        
        # 为每个列创建可视化
        visualizations = {}
        for column in columns:
            fig = px.scatter(
                result_df, 
                x=result_df.index, 
                y=column,
                color='异常标记',
                color_discrete_map={'正常': 'blue', '异常': 'red'},
                title=f'{column}的异常检测'
            )
            
            visualizations[column] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 将numpy类型转换为Python原生类型，解决JSON序列化问题
        anomaly_count = int((predictions == -1).sum())
        anomaly_percent = float((predictions == -1).mean() * 100)
        
        return {
            'data': result_df.to_dict('records'),
            'visualizations': visualizations,
            'anomaly_count': anomaly_count,
            'anomaly_percent': anomaly_percent
        }
    
    def correlation_analysis(self, df, target_column=None):
        """
        高级相关性分析
        
        参数:
            df: DataFrame，包含数据
            target_column: 目标列名(可选)
            
        返回:
            相关性分析结果和可视化JSON
        """
        # 只选择数值列
        numeric_df = df.select_dtypes(include=[np.number])
        
        # 计算相关系数
        corr_matrix = numeric_df.corr()
        
        # 创建热图
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title='变量相关性热图'
        )
        
        heatmap_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 如果指定了目标列，计算各变量与目标变量的相关性并排序
        target_correlations = None
        target_viz = None
        
        if target_column and target_column in numeric_df.columns:
            target_corr = corr_matrix[target_column].sort_values(ascending=False)
            target_correlations = target_corr.to_dict()
            
            # 创建条形图
            fig2 = px.bar(
                x=target_corr.index,
                y=target_corr.values,
                title=f'与{target_column}的相关性',
                labels={'x': '变量', 'y': '相关系数'}
            )
            
            target_viz = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'heatmap_visualization': heatmap_json,
            'target_correlations': target_correlations,
            'target_visualization': target_viz
        }
    
    def pattern_mining(self, df, columns, n_clusters=3):
        """
        模式挖掘
        
        参数:
            df: DataFrame，包含数据
            columns: 用于模式挖掘的列名列表
            n_clusters: 聚类数量
            
        返回:
            模式挖掘结果和可视化JSON
        """
        # 准备数据
        data = df[columns].copy()
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data)
        
        # 保存scaler
        self.scalers['pattern_mining'] = scaler
        
        # 降维 (PCA)
        pca = PCA(n_components=min(2, len(columns)))
        pca_result = pca.fit_transform(scaled_data)
        
        # 聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        
        # 保存模型
        self.models['pattern_mining_pca'] = pca
        self.models['pattern_mining_kmeans'] = kmeans
        
        # 添加聚类结果到DataFrame
        result_df = df.copy()
        result_df['聚类'] = clusters
        
        # 添加PCA结果
        for i in range(pca_result.shape[1]):
            result_df[f'PCA{i+1}'] = pca_result[:, i]
        
        # 聚类可视化
        if pca_result.shape[1] >= 2:
            fig = px.scatter(
                result_df,
                x='PCA1',
                y='PCA2',
                color='聚类',
                title='数据聚类模式分析',
                labels={'PCA1': '主成分1', 'PCA2': '主成分2'}
            )
        else:
            # 一维PCA结果
            fig = px.histogram(
                result_df,
                x='PCA1',
                color='聚类',
                title='一维聚类模式分析',
                labels={'PCA1': '主成分1'}
            )
        
        clustering_viz = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 分析每个聚类的特征
        cluster_profiles = {}
        for cluster in range(n_clusters):
            cluster_data = data[result_df['聚类'] == cluster]
            # 将numpy类型转换为Python原生类型
            profile = {col: float(val) for col, val in cluster_data.mean().to_dict().items()}
            cluster_profiles[f'聚类{cluster}'] = profile
        
        # 创建聚类特征雷达图
        radar_figs = {}
        if len(columns) > 1:
            for cluster in range(n_clusters):
                # 获取该聚类的平均值
                cluster_means = [cluster_profiles[f'聚类{cluster}'][col] for col in columns]
                
                # 创建雷达图
                fig = go.Figure()
                
                fig.add_trace(go.Scatterpolar(
                    r=cluster_means,
                    theta=columns,
                    fill='toself',
                    name=f'聚类{cluster}'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                        )
                    ),
                    title=f'聚类{cluster}特征分析'
                )
                
                radar_figs[f'聚类{cluster}'] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        # 将numpy类型转换为Python原生类型
        explained_variance = None
        if hasattr(pca, 'explained_variance_ratio_'):
            explained_variance = [float(val) for val in pca.explained_variance_ratio_]
        
        return {
            'data': result_df.to_dict('records'),
            'clustering_visualization': clustering_viz,
            'cluster_profiles': cluster_profiles,
            'radar_visualizations': radar_figs,
            'explained_variance': explained_variance
        }
    
    def feature_importance(self, df, target_column, feature_columns=None):
        """
        特征重要性分析
        
        参数:
            df: DataFrame，包含数据
            target_column: 目标列名
            feature_columns: 特征列名列表(可选)
            
        返回:
            特征重要性分析结果和可视化JSON
        """
        # 准备数据
        if feature_columns is None:
            # 使用所有数值列作为特征
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            # 如果目标列在特征列中，则移除
            if target_column in feature_columns:
                feature_columns.remove(target_column)
        
        X = df[feature_columns]
        y = df[target_column]
        
        # 检查目标变量类型
        is_classification = False
        if df[target_column].dtype.name in ['object', 'category'] or len(df[target_column].unique()) < 10:
            is_classification = True
        
        # 使用随机森林
        if is_classification:
            model = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # 训练模型
        model.fit(X, y)
        
        # 保存模型
        self.models[f'feature_importance_{target_column}'] = model
        
        # 获取特征重要性
        importance = model.feature_importances_
        
        # 创建特征重要性DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_columns,
            'importance': [float(val) for val in importance]  # 将numpy类型转换为Python float
        }).sort_values('importance', ascending=False)
        
        # 创建可视化
        fig = px.bar(
            importance_df,
            x='feature',
            y='importance',
            title=f'{target_column}的特征重要性',
            labels={'feature': '特征', 'importance': '重要性'}
        )
        
        importance_viz = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return {
            'importance_data': importance_df.to_dict('records'),
            'visualization': importance_viz,
            'model_type': 'RandomForestClassifier' if is_classification else 'RandomForestRegressor'
        }
