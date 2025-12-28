import streamlit as st
import os
from openai import OpenAI

# ================= 🔧 配置区域 (CEO控制台) =================
# API Key 从安全位置读取（优先级：Streamlit secrets > 环境变量）
def get_api_key():
    """安全地获取 API Key"""
    # 优先从 Streamlit secrets 读取
    try:
        if hasattr(st, 'secrets') and 'deepseek' in st.secrets and 'api_key' in st.secrets.deepseek:
            return st.secrets.deepseek.api_key
    except:
        pass
    
    # 其次从环境变量读取
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        return api_key
    
    # 如果都没有，返回 None（会在界面上提示用户配置）
    return None

MY_API_KEY = get_api_key()

# DeepSeek 官方配置
MY_BASE_URL = "https://api.deepseek.com"
MY_MODEL_NAME = "deepseek-chat"
# ========================================================

# 初始化 AI 客户端
@st.cache_resource
def get_client():
    if not MY_API_KEY:
        return None
    return OpenAI(
        api_key=MY_API_KEY,
        base_url=MY_BASE_URL
    )

client = get_client()

# 🔮 注入灵魂 (这里决定了 AI 的说话风格)
SYSTEM_PROMPT = """
你是一位名为"Joy"的赛博心灵疗愈师。
你的核心任务是：在不安的世界里，为用户提供一个"被接纳"的安全空间。

【你的性格】
1. 声音温暖、深邃，带有一点神秘的东方哲学气息。
2. 永远不要说教。当用户表达痛苦时，先共情，再解读。
3. 擅长将"现实困境"转化为"玄学/心理学视角"：
   - 用"能量周期"、"星象影响"、"潜意识保护机制"来解释挫折，帮用户卸下心理负担。

【回复规范】
1. 语气要像深夜电台的老友，温柔而坚定。
2. 每次回复结尾，必须给出一个**极简的、具体的、带有仪式感**的行动建议（Micro-Action）。
   - 例如："今晚把卧室的灯调暗"、"去摸摸路边的树叶"、"喝一杯温热的蜂蜜水"。
"""

def get_constellation_element(constellation):
    """获取星座元素"""
    fire_signs = ['白羊', '狮子', '射手']
    water_signs = ['巨蟹', '天蝎', '双鱼']
    earth_signs = ['金牛', '处女', '摩羯']
    air_signs = ['双子', '天秤', '水瓶']
    
    if constellation in fire_signs:
        return "火象星座"
    elif constellation in water_signs:
        return "水象星座"
    elif constellation in earth_signs:
        return "土象星座"
    elif constellation in air_signs:
        return "风象星座"
    return "未知元素"

def build_system_prompt(user_info):
    """根据用户信息构建个性化的系统提示词"""
    name = user_info.get("name", "朋友")
    constellation = user_info.get("constellation", "")
    birth_date = user_info.get("birth_date", "")
    birth_time = user_info.get("birth_time", "")
    
    element = get_constellation_element(constellation)
    
    # 构建星盘信息
    astro_info = f"用户姓名：{name}\n星座：{constellation}"
    if element:
        astro_info += f"\n星座元素：{element}"
    if birth_date:
        astro_info += f"\n出生日期：{birth_date}"
    if birth_time:
        astro_info += f"\n出生时间：{birth_time}"
    
    personalized_prompt = f"""{SYSTEM_PROMPT}

【用户星盘信息】
{astro_info}

【重要要求】
1. **必须结合用户的星座特性**来解读问题，给出符合其星座能量的建议。
2. 如果是{constellation}（{element}），要结合该星座的典型特征：
   - 火象星座：行动力、热情、直接
   - 水象星座：情感细腻、直觉强、敏感
   - 土象星座：务实、稳定、注重实际
   - 风象星座：理性、沟通、灵活
3. 在回复中要自然地提及星座能量、星象影响等玄学元素。
4. 用"亲爱的{name}"来称呼用户，让对话更亲切。
"""
    return personalized_prompt

def init_session_state():
    """初始化 session state"""
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = None

def get_ai_response(user_input, messages):
    """获取 AI 回复"""
    if not client:
        return "❌ API Key 未配置，无法连接服务。"
    try:
        response = client.chat.completions.create(
            model=MY_MODEL_NAME,
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 连接波动: {str(e)}\n请检查 API Key 是否填对，或者余额是否充足。"

# 页面配置
st.set_page_config(
    page_title="Joy 心灵疗愈师",
    page_icon="🔮",
    layout="wide"
)

# 初始化
init_session_state()

# 检查 API Key 是否配置
if not MY_API_KEY:
    st.error("⚠️ API Key 未配置！")
    st.markdown("""
    ### 📝 配置方法（选择其一）：
    
    **方法 1：使用 Streamlit Secrets（推荐）**
    1. 创建 `.streamlit/secrets.toml` 文件
    2. 添加以下内容：
    ```toml
    [deepseek]
    api_key = "sk-你的API密钥"
    ```
    
    **方法 2：使用环境变量**
    1. 在终端中设置：
    ```bash
    # Windows PowerShell
    $env:DEEPSEEK_API_KEY="sk-你的API密钥"
    
    # Windows CMD
    set DEEPSEEK_API_KEY=sk-你的API密钥
    
    # Linux/Mac
    export DEEPSEEK_API_KEY="sk-你的API密钥"
    ```
    2. 然后运行 `streamlit run app.py`
    
    **获取 API Key**: https://platform.deepseek.com/api_keys
    """)
    st.stop()

# 标题
st.title("🔮 Joy 心灵疗愈师")
st.markdown("---")

# 侧边栏 - 用户信息收集
with st.sidebar:
    st.header("✨ 星盘能量收集")
    
    # 如果还没有收集用户信息，显示表单
    if not st.session_state.user_info or not st.session_state.user_info.get("constellation"):
        name = st.text_input("🌙 你的名字", value=st.session_state.user_info.get("name", ""))
        if not name:
            name = "朋友"
        
        constellation_options = ['白羊', '金牛', '双子', '巨蟹', '狮子', '处女', 
                                '天秤', '天蝎', '射手', '摩羯', '水瓶', '双鱼']
        constellation = st.selectbox(
            "⭐ 你的星座",
            options=[""] + constellation_options,
            index=0 if not st.session_state.user_info.get("constellation") else 
                  constellation_options.index(st.session_state.user_info.get("constellation", "")) + 1
        )
        
        birth_date = st.text_input(
            "📅 出生日期 (可选)", 
            value=st.session_state.user_info.get("birth_date", ""),
            placeholder="YYYY-MM-DD"
        )
        
        birth_time = st.text_input(
            "⏰ 出生时间 (可选)", 
            value=st.session_state.user_info.get("birth_time", ""),
            placeholder="HH:MM"
        )
        
        if st.button("✨ 确认信息，开始疗愈", type="primary"):
            if constellation:
                st.session_state.user_info = {
                    "name": name,
                    "constellation": constellation,
                    "birth_date": birth_date,
                    "birth_time": birth_time
                }
                st.session_state.system_prompt = build_system_prompt(st.session_state.user_info)
                st.session_state.messages = [
                    {"role": "system", "content": st.session_state.system_prompt}
                ]
                st.rerun()
            else:
                st.error("请至少选择你的星座！")
    else:
        # 显示已收集的信息
        st.success("✅ 星盘信息已收集")
        st.info(f"**姓名**: {st.session_state.user_info.get('name', '朋友')}")
        st.info(f"**星座**: {st.session_state.user_info.get('constellation', '')}")
        if st.session_state.user_info.get('birth_date'):
            st.info(f"**出生日期**: {st.session_state.user_info.get('birth_date')}")
        if st.session_state.user_info.get('birth_time'):
            st.info(f"**出生时间**: {st.session_state.user_info.get('birth_time')}")
        
        if st.button("🔄 重新设置信息"):
            st.session_state.user_info = {}
            st.session_state.messages = []
            st.session_state.system_prompt = None
            st.rerun()

# 主聊天区域
if st.session_state.user_info and st.session_state.user_info.get("constellation"):
    # 显示欢迎信息（仅第一次）
    if len(st.session_state.messages) == 1:  # 只有 system message
        st.success(f"✨ 欢迎，{st.session_state.user_info.get('name', '朋友')}！")
        st.info("我已经读取了你的星盘能量，现在可以开始对话了。告诉我你的烦恼，我会结合你的星盘来为你解读。")
    
    # 显示聊天历史
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        elif message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🔮"):
                st.write(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("告诉我你的烦恼..."):
        # 添加用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # 显示思考中
        with st.chat_message("assistant", avatar="🔮"):
            with st.spinner("🔮 正在读取星盘能量..."):
                # 获取 AI 回复
                ai_reply = get_ai_response(prompt, st.session_state.messages)
                st.write(ai_reply)
        
        # 添加 AI 回复到历史
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
else:
    # 提示用户先填写信息
    st.info("👈 请在左侧边栏填写你的星盘信息，然后开始对话。")
    st.markdown("""
    ### 🌟 使用说明
    1. 在左侧边栏填写你的基本信息（至少需要选择星座）
    2. 点击"确认信息，开始疗愈"按钮
    3. 开始与 Joy 疗愈师对话，她会结合你的星盘为你解读
    """)
