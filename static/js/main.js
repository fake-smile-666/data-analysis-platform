/**
 * 数据分析平台 - 主JavaScript文件
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化Bootstrap提示工具
    initTooltips();
    
    // 淡入效果
    addFadeInEffect();
    
    // 自动隐藏消息提示
    setupAlertDismiss();
});

/**
 * 初始化Bootstrap提示工具
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * 为主要内容添加淡入动画效果
 */
function addFadeInEffect() {
    const mainContent = document.querySelector('.container');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
}

/**
 * 设置警告消息自动消失
 */
function setupAlertDismiss() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

/**
 * 格式化数值为带千位分隔符的字符串
 * @param {number} number - 要格式化的数值
 * @returns {string} 格式化后的字符串
 */
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * 将CSV字符串转换为数组对象
 * @param {string} csv - CSV格式的字符串
 * @returns {Array} 解析后的对象数组
 */
function csvToArray(csv) {
    const rows = csv.split("\n");
    const result = [];
    const headers = rows[0].split(",");
    
    for (let i = 1; i < rows.length; i++) {
        const obj = {};
        const currentRow = rows[i].split(",");
        
        for (let j = 0; j < headers.length; j++) {
            obj[headers[j]] = currentRow[j];
        }
        
        result.push(obj);
    }
    
    return result;
}

/**
 * 下载数据为CSV文件
 * @param {Array} data - 要导出的数据
 * @param {string} filename - 文件名
 */
function downloadCSV(data, filename) {
    // 获取表头（所有键）
    const headers = Object.keys(data[0]);
    
    // 创建CSV内容
    let csvContent = headers.join(",") + "\n";
    
    // 添加每一行数据
    data.forEach(item => {
        const row = headers.map(header => {
            // 处理包含逗号的数据，将其用引号包裹
            const cell = item[header] || "";
            return cell.toString().includes(",") ? `"${cell}"` : cell;
        });
        csvContent += row.join(",") + "\n";
    });
    
    // 创建Blob对象
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    
    // 创建下载链接
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = "hidden";
    
    // 触发下载
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * 生成随机颜色
 * @returns {string} 十六进制颜色代码
 */
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

/**
 * 显示加载中动画
 * @param {HTMLElement} container - 要显示加载动画的容器元素
 * @param {string} message - 加载提示文本
 */
function showLoading(container, message = "加载中...") {
    container.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-2">${message}</p>
        </div>
    `;
}

/**
 * 显示错误消息
 * @param {HTMLElement} container - 要显示错误消息的容器元素
 * @param {string} message - 错误提示文本
 */
function showError(container, message) {
    container.innerHTML = `
        <div class="alert alert-danger" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
        </div>
    `;
} 