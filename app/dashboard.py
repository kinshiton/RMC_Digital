"""
Streamlit Dashboard前端
智能安防运营面板的交互式Web界面 - iOS风格
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
from ios_style import apply_ios_style, ios_card, ios_badge, ios_divider, IOS_ICONS, IOS_COLORS

# 页面配置
st.set_page_config(
    page_title="🛡️ RMC 智能安防",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用iOS风格
apply_ios_style()

# API配置
API_BASE_URL = "http://localhost:8000/api/v1"

# 移除旧CSS，使用iOS风格
st.markdown("""
<style>
    .high-risk {
        color: #388e3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def fetch_api(endpoint: str, method: str = "GET", data: dict = None):
    """调用后端API"""
    url = f"{API_BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API调用失败: {e}")
        return None


def main_dashboard():
    """主仪表板 - iOS风格"""
    # 标题
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0 1rem 0;">
        <h1 style="font-size: 3rem; margin: 0; background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {IOS_ICONS['shield']} RMC 智能安防系统
        </h1>
        <p style="color: #8E8E93; margin-top: 0.5rem; font-size: 1.1rem;">
            Intelligent Security Operations Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    ios_divider("关键绩效指标")
    
    kpi_data = fetch_api("kpi/summary")
    if kpi_data and kpi_data['status'] == 'success':
        data = kpi_data['data']
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "响应时间改善",
                data['response_time_improvement'],
                delta="↓ 良好",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "维护效率提升",
                data['maintenance_efficiency'],
                delta="↑ 优秀",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "误报率降低",
                data['false_alarm_reduction'],
                delta="↓ 显著",
                delta_color="normal"
            )
        
        with col4:
            st.metric(
                "设备可用率",
                data['device_uptime'],
                delta="稳定",
                delta_color="off"
            )
        
        with col5:
            st.metric(
                "巡检完成率",
                data['patrol_completion'],
                delta="↑ 提升",
                delta_color="normal"
            )
    
    st.markdown("---")
    
    # 两列布局
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # 报警趋势图表
        st.subheader("📈 报警趋势分析")
        
        trend_data = fetch_api("alarms/trends?days=30")
        if trend_data and trend_data['status'] == 'success':
            df = pd.DataFrame(trend_data['data'])
            
            if not df.empty:
                fig = px.line(
                    df,
                    x='date',
                    y='alarm_count',
                    title='30天报警数量趋势',
                    labels={'date': '日期', 'alarm_count': '报警数量'}
                )
                fig.update_traces(line_color='#1f77b4', line_width=3)
                st.plotly_chart(fig, use_container_width=True)
        
        # 设备健康状态
        st.subheader("🔧 设备健康状态")
        
        device_data = fetch_api("devices/health")
        if device_data and device_data['status'] == 'success':
            health = device_data['data']
            
            # 创建仪表盘图
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=health['avg_health_score'],
                title={'text': "平均健康评分"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 设备状态摘要
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.metric("总设备数", health['total_devices'])
            with col_d2:
                st.metric("严重故障", health['critical_count'], delta="需关注", delta_color="inverse")
            with col_d3:
                st.metric("需要维护", health['maintenance_needed'])
    
    with col_right:
        # 风险警报列表
        st.subheader("⚠️ 风险警报")
        
        alerts_data = fetch_api("risk/alerts?hours=24")
        if alerts_data and alerts_data['status'] == 'success':
            alerts = alerts_data['data']
            
            if alerts:
                for alert in alerts:
                    risk_class = f"{alert['risk_level']}-risk"
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="{risk_class}">{alert['risk_level'].upper()}</div>
                        <strong>{alert['description']}</strong><br>
                        <small>📍 {alert['location']} | ⏰ {alert['timestamp'][:16]}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✅ 暂无警报")
        
        # 巡检热力图
        st.subheader("🗺️ 巡检覆盖")
        
        patrol_data = fetch_api("patrol/heatmap")
        if patrol_data and patrol_data['status'] == 'success':
            heatmap = patrol_data['data']
            
            fig = go.Figure(data=go.Bar(
                x=heatmap['areas'],
                y=heatmap['coverage'],
                marker_color=['green' if c >= 80 else 'orange' if c >= 60 else 'red' 
                             for c in heatmap['coverage']]
            ))
            fig.update_layout(
                title="区域巡检覆盖率",
                xaxis_title="区域",
                yaxis_title="覆盖率 (%)",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if heatmap.get('blind_spots'):
                st.warning(f"⚠️ 盲区: {', '.join(heatmap['blind_spots'])}")


def risk_assessment_page():
    """AI风险评估页面"""
    st.title("🎯 AI风险等级判定")
    
    # 初始化 session state
    if 'assessment_result' not in st.session_state:
        st.session_state.assessment_result = None
    
    with st.form("risk_assessment_form"):
        st.subheader("报警信息输入")
        
        alarm_desc = st.text_area(
            "报警描述",
            placeholder="例如：门禁系统检测到未授权访问尝试，有人试图强行进入机房",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("地点", "机房A")
            location_type = st.selectbox(
                "区域类型",
                ["critical", "restricted", "public", "parking"]
            )
        
        with col2:
            timestamp = st.text_input(
                "时间",
                datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            device_id = st.text_input("设备ID", "DOOR_001")
        
        submitted = st.form_submit_button("🔍 评估风险")
        
        if submitted and alarm_desc:
            context = {
                "timestamp": timestamp,
                "location": location,
                "location_type": location_type,
                "device_id": device_id
            }
            
            result = fetch_api(
                "risk/assess",
                method="POST",
                data={
                    "alarm_description": alarm_desc,
                    "context": context
                }
            )
            
            if result and result['status'] == 'success':
                # 存储结果到 session state
                st.session_state.assessment_result = result
            else:
                st.error("❌ 风险评估失败，请重试")
                st.session_state.assessment_result = None
    
    # 在表单外显示结果
    if st.session_state.assessment_result:
        result = st.session_state.assessment_result
        risk = result['risk_assessment']
        template = result['investigation_template']
        
        st.success("✅ 风险评估完成")
        
        # 显示评估结果
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("风险等级", risk['risk_level'].upper())
        with col2:
            st.metric("风险评分", f"{risk['risk_score']}/10")
        with col3:
            st.metric("优先级", f"P{risk['priority']}")
        
        st.subheader("风险因素")
        for factor in risk['risk_factors']:
            st.write(f"• {factor}")
        
        st.subheader("建议措施")
        for action in template['recommended_actions'][:5]:
            st.write(f"✓ {action}")
        
        # 调查模板下载（现在在表单外部）
        st.subheader("调查模板")
        template_json = json.dumps(template, ensure_ascii=False, indent=2)
        st.download_button(
            "📥 下载调查模板 (JSON)",
            template_json,
            file_name=f"{template['case_id']}.json",
            mime="application/json"
        )


def device_management_page():
    """设备管理页面"""
    st.title("🔧 TMS设备管理")
    
    tabs = st.tabs(["设备状态", "维护计划", "备件库存"])
    
    with tabs[0]:
        st.subheader("设备健康监控")
        
        if st.button("🔄 刷新设备状态"):
            with st.spinner("正在获取设备状态..."):
                device_data = fetch_api("devices/status")
                
                if device_data and device_data.get('status') == 'success':
                    # 添加错误处理
                    if 'data' in device_data and 'device_health' in device_data.get('data', {}):
                        devices = device_data['data']['device_health']
                        df = pd.DataFrame(devices)
                    else:
                        st.warning("⚠️ 暂无设备数据，请先运行设备监控脚本")
                        df = None
                elif device_data:
                    # device_data 存在但不是 success 状态
                    st.error(f"❌ 获取设备状态失败: {device_data.get('detail', '未知错误')}")
                    df = None
                else:
                    # device_data 为 None
                    st.error("❌ 获取设备状态失败: API返回为空")
                    df = None
                
                if df is not None and not df.empty:
                    
                    # 添加颜色标记
                    def highlight_health(row):
                        if row['health_score'] >= 85:
                            return ['background-color: #c8e6c9'] * len(row)
                        elif row['health_score'] >= 70:
                            return ['background-color: #fff9c4'] * len(row)
                        elif row['health_score'] >= 50:
                            return ['background-color: #ffccbc'] * len(row)
                        else:
                            return ['background-color: #ffcdd2'] * len(row)
                    
                    st.dataframe(
                        df[['device_id', 'health_score', 'uptime_ratio', 'error_rate', 'status']],
                        use_container_width=True
                    )
    
    with tabs[1]:
        st.subheader("维护计划推荐")
        st.info("基于CrewAI代理的预测性维护建议")
        
        # 模拟维护计划
        maintenance_plan = [
            {"device_id": "DOOR_A01", "priority": "high", "action": "检查控制器连接", "date": "2025-10-30"},
            {"device_id": "CAM_B05", "priority": "medium", "action": "清洁镜头", "date": "2025-11-02"}
        ]
        
        for plan in maintenance_plan:
            priority_color = "🔴" if plan['priority'] == 'high' else "🟡"
            st.write(f"{priority_color} **{plan['device_id']}** - {plan['action']} (计划: {plan['date']})")
    
    with tabs[2]:
        st.subheader("备件库存管理")
        
        # 模拟库存数据
        inventory = pd.DataFrame({
            '备件类型': ['门禁控制器', '摄像头', '传感器', '电源适配器'],
            '当前库存': [3, 6, 8, 4],
            '安全库存': [5, 8, 10, 6],
            '状态': ['⚠️ 低库存', '✅ 正常', '✅ 正常', '⚠️ 低库存']
        })
        
        st.dataframe(inventory, use_container_width=True)


def knowledge_base_page():
    """知识库查询页面"""
    st.title("📚 安防知识库助手")
    
    st.markdown("""
    基于MCP协议的智能知识库机器人，支持自然语言查询公司安防政策、国家标准和操作流程。
    """)
    
    # 聊天界面
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 显示历史消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题，例如：门禁屏蔽流程是什么？"):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 调用知识库API（启用AI智能回答）
        result = fetch_api("knowledge/search", method="POST", data={
            "query": prompt,
            "use_ai": True  # 启用AI智能回答
        })
        
        if result and result['status'] == 'success':
            # 优先显示AI生成的智能回答
            if result.get('ai_response'):
                # AI智能回答
                response = f"🤖 **AI智能助手：**\n\n{result['ai_response']}\n\n"
                response += "---\n\n"
                
                # 添加参考文档
                if result.get('results'):
                    response += "📚 **参考文档：**\n\n"
                    for idx, item in enumerate(result['results'], 1):
                        response += f"{idx}. **{item['title']}** ({item.get('category', '其他')})\n"
                        
                        # 如果是文件，添加下载链接
                        if item.get('content_type') == 'file' and item.get('id'):
                            download_url = f"http://localhost:8000/api/v1/knowledge/download/{item['id']}"
                            file_name = item.get('file_path', '').split('/')[-1]
                            response += f"   📎 [{file_name}]({download_url})\n"
                        elif item.get('content_type') == 'url' and item.get('external_url'):
                            response += f"   🔗 [{item['external_url']}]({item['external_url']})\n"
                        
                        response += "\n"
                
                response += "\n💡 *此回答由AI基于知识库文档生成，如需详细信息请查看参考文档*"
                
            # 检查是否有结果（无AI回答时显示传统格式）
            elif result.get('results') and len(result['results']) > 0:
                # 智能分析用户意图并构建回复
                results = result['results']
                num_results = len(results)
                
                # 开始构建智能回复
                response = f"🤖 我为您找到了 **{num_results}** 条相关信息：\n\n"
                response += "---\n\n"
                
                for idx, item in enumerate(results, 1):
                    # 标题和类别
                    category_emoji = {
                        '操作流程': '📋', '政策规定': '📜', '应急预案': '🚨',
                        '设备使用': '🔧', '技术标准': '📐', '常见问题': '❓',
                        '其他': '📄'
                    }
                    emoji = category_emoji.get(item.get('category', '其他'), '📄')
                    
                    response += f"### {emoji} {idx}. {item['title']}\n\n"
                    
                    # 内容摘要
                    response += f"**📝 内容摘要：**\n{item['content']}\n\n"
                    
                    # 根据内容类型显示不同的操作
                    content_type = item.get('content_type', 'text')
                    
                    if content_type == 'file' and item.get('file_path'):
                        file_path = item['file_path']
                        file_name = file_path.split('/')[-1]
                        knowledge_id = item.get('id')
                        response += f"📎 **文件：** `{file_name}`\n\n"
                        
                        # 添加下载链接
                        if knowledge_id:
                            download_url = f"http://localhost:8000/api/v1/knowledge/download/{knowledge_id}"
                            response += f"⬇️ **[点击下载文件]({download_url})** 或在管理后台查看\n\n"
                        else:
                            response += f"💡 **提示：** 您可以在管理后台下载此文件\n\n"
                    elif content_type == 'url' and item.get('external_url'):
                        response += f"🔗 **链接：** [{item['external_url']}]({item['external_url']})\n\n"
                    elif content_type == 'powerbi':
                        if item.get('powerbi_url'):
                            response += f"📊 **Power BI：** [{item['powerbi_url']}]({item['powerbi_url']})\n\n"
                        if item.get('powerapps_url'):
                            response += f"📱 **Power Apps：** [{item['powerapps_url']}]({item['powerapps_url']})\n\n"
                    
                    # 来源和分类
                    response += f"📚 **来源：** {item.get('source', '未知')}\n"
                    response += f"🏷️ **分类：** {item.get('category', '其他')}\n\n"
                    
                    if idx < num_results:
                        response += "---\n\n"
                
                # 添加智能建议
                response += "\n💡 **智能建议：**\n"
                if any('流程' in item.get('category', '') for item in results):
                    response += "- 这些是操作流程文档，建议您仔细阅读每个步骤\n"
                if any(item.get('content_type') == 'file' for item in results):
                    response += "- 找到了文件资源，建议下载后详细查看\n"
                if any('政策' in item.get('category', '') or '规定' in item.get('category', '') for item in results):
                    response += "- 这是公司政策规定，请务必遵守相关要求\n"
                
                response += f"\n❓ **需要更多帮助？** 您可以继续提问，比如询问具体的操作步骤或细节。"
                
            else:
                # 没有找到结果
                response = f"😔 {result.get('message', '未找到相关信息')}\n\n"
                response += "这可能是因为：\n"
                response += "- 知识库中还没有相关内容\n"
                response += "- 搜索关键词不够准确\n\n"
                if result.get('suggestions'):
                    response += "💡 **您可能想了解这些内容：**\n"
                    for suggestion in result['suggestions']:
                        response += f"- {suggestion}\n"
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)
        else:
            # API调用失败
            error_msg = "❌ 知识库查询失败，请稍后重试"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)


def shielding_request_page():
    """报警屏蔽申请页面"""
    st.title("🚫 报警屏蔽申请")
    
    with st.form("shielding_form"):
        st.subheader("屏蔽申请表单")
        
        device_id = st.text_input("设备ID", placeholder="例如：DOOR_A01")
        reason = st.text_area("屏蔽原因", placeholder="请详细说明为什么需要屏蔽此设备的报警")
        duration_hours = st.slider("屏蔽时长（小时）", 1, 168, 24)
        requester = st.text_input("申请人", placeholder="您的姓名")
        
        submitted = st.form_submit_button("📤 提交申请")
        
        if submitted:
            if not all([device_id, reason, requester]):
                st.error("请填写所有必填字段")
            else:
                result = fetch_api(
                    "shielding/request",
                    method="POST",
                    data={
                        "device_id": device_id,
                        "reason": reason,
                        "duration_hours": duration_hours,
                        "requester": requester
                    }
                )
                
                if result and result['status'] == 'success':
                    st.success(f"✅ {result['message']}")
                    st.info(f"申请单号: {result['data']['application_id']}")
                    st.json(result['data'])


# ========== 侧边栏导航 - iOS风格 ==========

st.sidebar.markdown(f"""
<div style="text-align: center; padding: 1.5rem 0 1rem 0;">
    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{IOS_ICONS['shield']}</div>
    <h1 style="margin: 0; font-size: 1.5rem; color: #000000;">RMC 安防</h1>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "选择功能模块",
    [
        f"{IOS_ICONS['dashboard']} 主仪表板",
        f"{IOS_ICONS['brain']} AI风险评估",
        f"{IOS_ICONS['device']} 设备管理",
        f"{IOS_ICONS['book']} 知识库查询",
        f"{IOS_ICONS['shield']} 屏蔽申请"
    ]
)

st.sidebar.markdown("""
<div style="margin: 2rem 0 1rem 0; height: 1px; background: #E5E5EA;"></div>
<div style="padding: 0 1rem;">
    <p style="font-size: 0.875rem; font-weight: 600; color: #8E8E93; margin-bottom: 0.75rem;">
        系统状态
    </p>
</div>
""", unsafe_allow_html=True)

# 检查API健康状态
health = fetch_api("../health")
if health and health['status'] == 'healthy':
    st.sidebar.markdown(f"""
    <div style="background: rgba(52, 199, 89, 0.1); padding: 0.75rem 1rem; border-radius: 12px; 
                margin: 0 1rem; border-left: 4px solid #34C759;">
        <span style="color: #34C759; font-weight: 600;">{IOS_ICONS['check']} 系统运行正常</span>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"""
    <div style="background: rgba(255, 59, 48, 0.1); padding: 0.75rem 1rem; border-radius: 12px; 
                margin: 0 1rem; border-left: 4px solid #FF3B30;">
        <span style="color: #FF3B30; font-weight: 600;">{IOS_ICONS['warning']} 系统异常</span>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="margin: 2rem 0 1rem 0; height: 1px; background: #E5E5EA;"></div>
<div style="padding: 1rem; background: rgba(0, 122, 255, 0.05); border-radius: 12px; margin: 0 1rem;">
    <p style="font-weight: 600; color: #000000; margin-bottom: 0.5rem;">智能安防运营面板</p>
    <p style="font-size: 0.875rem; color: #8E8E93; margin: 0.25rem 0;">
        🤖 CrewAI 多代理框架<br>
        💬 Cherry Studio + MCP<br>
        🎨 iOS风格设计
    </p>
    <p style="font-size: 0.75rem; color: #C6C6C8; margin-top: 1rem; text-align: center;">
        © 2025 RMC Digital
    </p>
</div>
""", unsafe_allow_html=True)


# ========== 页面路由 ==========

if "主仪表板" in page:
    main_dashboard()
elif "AI风险评估" in page:
    risk_assessment_page()
elif "设备管理" in page:
    device_management_page()
elif "知识库查询" in page:
    knowledge_base_page()
elif "屏蔽申请" in page:
    shielding_request_page()


if __name__ == "__main__":
    pass

