import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from content_templates import CONTENT_TEMPLATES
import time
import json
import sqlite3
from datetime import datetime
from cachetools import TTLCache
import pandas as pd

# 加载环境变量
load_dotenv()

# 设置页面配置
st.set_page_config(
    page_title="AI 内容生成器",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# AI 内容生成器\n 一个强大的AI驱动的内容生成工具"
    }
)

# 自定义CSS样式
st.markdown("""
    <style>
    /* 深色模式样式 */
    [data-testid="stAppViewContainer"] {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    
    [data-testid="stSidebar"] {
        background-color: #262626;
        color: #FFFFFF;
    }
    
    .stTextArea textarea {
        background-color: #2D2D2D;
        color: #FFFFFF;
        border-color: #404040;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #ff3333;
    }
    
    .output-container {
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #404040;
    }
    
    .stMarkdown {
        color: #FFFFFF;
    }
    
    /* 标题和文本颜色 */
    h1, h2, h3, p {
        color: #FFFFFF !important;
    }
    
    /* 选择框样式 */
    .stSelectbox > div > div {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    
    /* 复选框样式 */
    .stCheckbox > label {
        color: #FFFFFF !important;
    }
    
    /* 滑块样式 */
    .stSlider > div > div {
        background-color: #2D2D2D;
    }
    
    /* 分割线样式 */
    hr {
        border-color: #404040;
    }
    
    /* 信息框样式 */
    .stAlert {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('content_history.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS history
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         timestamp TEXT,
         content_type TEXT,
         input_text TEXT,
         output_text TEXT,
         model TEXT)
    ''')
    conn.commit()
    conn.close()

# 内容缓存
content_cache = TTLCache(maxsize=100, ttl=3600)  # 1小时缓存

# 内容生成函数
def generate_content(content_type, input_text, model, client):
    try:
        # 检查缓存
        cache_key = f"{content_type}_{input_text}_{model}"
        if cache_key in content_cache:
            return content_cache[cache_key]

        template = CONTENT_TEMPLATES[content_type]
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": template["system_prompt"]},
                {"role": "user", "content": template["user_prompt"].format(input_text=input_text)}
            ],
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        
        # 保存到缓存
        content_cache[cache_key] = content
        
        # 保存到历史记录
        save_to_history(content_type, input_text, content, model)
        
        return content
    except Exception as e:
        error_msg = str(e)
        if "rate limit" in error_msg.lower():
            st.error("⚠️ API速率限制已达到，请等待约1小时后再试。")
        else:
            st.error(f"生成内容时发生错误: {error_msg}")
        return None

# 保存到历史记录
def save_to_history(content_type, input_text, output_text, model):
    conn = sqlite3.connect('content_history.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO history (timestamp, content_type, input_text, output_text, model)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), content_type, input_text, output_text, model))
    conn.commit()
    conn.close()

# 获取历史记录
def get_history():
    conn = sqlite3.connect('content_history.db')
    df = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp DESC", conn)
    conn.close()
    return df

# 分析内容
def analyze_content(content):
    stats = {
        "字数": len(content),
        "段落数": len(content.split('\n\n')),
        "句子数": len([s for s in content.split('。') if s.strip()]),
        "表情符号数": len([c for c in content if c in '😀😃😄😁😅😂🤣'])
    }
    return stats

def main():
    # 初始化数据库
    init_db()
    
    # 主标题
    st.title("✨ AI 内容生成器")
    st.markdown("""
    <div style='background-color: #2D2D2D; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        🎯 这是一个强大的AI内容生成工具，可以帮助你生成各种类型的创意内容。<br>
        📝 从美食菜谱到旅游攻略，从读书笔记到小红书文案，让AI助你创作！
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("### ⚙️ 配置选项")
        
        # 内容类型选择
        content_type = st.selectbox(
            "选择内容类型",
            options=list(CONTENT_TEMPLATES.keys()),
            format_func=lambda x: f"📌 {x}"
        )
        
        # 模型选择
        model = st.selectbox(
            "选择模型",
            options=["claude-3.5-haiku", "gpt-4o", "gpt-4o-mini"],
            format_func=lambda x: f"🤖 {x}"
        )
        
        # 批量生成设置
        batch_mode = st.checkbox("批量生成模式")
        if batch_mode:
            max_items = st.slider("最大生成数量", 1, 10, 3)
    
    # 主界面
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 输入区域")
        input_text = st.text_area(
            "在这里输入你的创作主题或关键词",
            height=200,
            placeholder="例如：\n- 美食菜谱：红烧排骨\n- 旅游攻略：东京自由行\n- 读书笔记：《活着》\n- 小红书文案：咖啡店体验"
        )
        
        if st.button("🚀 开始生成", use_container_width=True):
            if not input_text:
                st.warning("请先输入内容！")
            else:
                inputs = [line.strip() for line in input_text.split('\n') if line.strip()] if batch_mode else [input_text]
                
                if batch_mode and len(inputs) > max_items:
                    inputs = inputs[:max_items]
                    st.warning(f"已限制生成数量为 {max_items} 个")
                
                progress_bar = st.progress(0)
                client = OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    base_url=os.getenv("OPENAI_API_BASE")
                )
                
                for i, text in enumerate(inputs):
                    content = generate_content(content_type, text, model, client)
                    if content:
                        with col2:
                            st.markdown(f"### 🎉 生成结果 {i+1}/{len(inputs)}")
                            st.markdown('<div class="output-container">', unsafe_allow_html=True)
                            st.markdown(content)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # 显示内容分析
                            stats = analyze_content(content)
                            st.markdown("### 📊 内容分析")
                            cols = st.columns(4)
                            for idx, (key, value) in enumerate(stats.items()):
                                with cols[idx]:
                                    st.metric(key, value)
                            
                            # 下载按钮
                            timestamp = time.strftime("%Y%m%d-%H%M%S")
                            filename = f"{content_type}_{timestamp}.md"
                            st.download_button(
                                label="📥 下载Markdown文件",
                                data=content,
                                file_name=filename,
                                mime="text/markdown"
                            )
                    
                    progress_bar.progress((i + 1) / len(inputs))
                st.success("✨ 内容生成完成！")

if __name__ == "__main__":
    main()
