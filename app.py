import streamlit as st
import time
import random
import os

# --- 1. 核心功能 (嚴格遵照您的架構) ---
def safe_rerun():
    """自動判斷並執行重整"""
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except:
            st.stop()

def play_local_audio(filename):
    """
    播放指定路徑的音檔
    路徑固定為: Teacher_Course22/audio/檔名
    """
    # 這裡直接指定路徑，不使用自動搜尋
    file_path = f"Teacher_Course22/audio/{filename}"
    
    # 嘗試開啟並播放
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/mp4')
        else:
            st.error(f"找不到檔案: {file_path}")
    except Exception as e:
        st.error(f"播放錯誤: {e}")

# --- 0. 系統配置 ---
st.set_page_config(page_title="Kaolahan", page_icon="🍲", layout="centered")

# --- CSS 美化 (沿用您上傳的樣式架構，僅調整配色為暖色系) ---
st.markdown("""
    <style>
    body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .source-tag { font-size: 12px; color: #aaa; text-align: right; font-style: italic; }
    
    /* 單字卡 */
    .word-card {
        background: linear-gradient(135deg, #FFF3E0 0%, #ffffff 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 4px solid #FF7043;
    }
    .emoji-icon { font-size: 48px; margin-bottom: 10px; }
    .amis-text { font-size: 22px; font-weight: bold; color: #E64A19; }
    .chinese-text { font-size: 16px; color: #795548; }
    
    /* 句子框 */
    .sentence-box {
        background-color: #FFF8E1;
        border-left: 5px solid #FFA000;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
    }

    /* 按鈕 */
    .stButton>button {
        width: 100%; border-radius: 12px; font-size: 20px; font-weight: 600;
        background-color: #FFCCBC; color: #BF360C; border: 2px solid #FF7043; padding: 12px;
    }
    .stButton>button:hover { background-color: #FFAB91; border-color: #E64A19; }
    .stProgress > div > div > div > div { background-color: #FF7043; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 資料庫 (檔名已對應您上傳的檔案) ---
vocab_data = [
    {"amis": "Kaolahan", "chi": "所喜歡的", "icon": "❤️", "source": "核心單字", "audio": "kaolahan.m4a"},
    {"amis": "Facidol", "chi": "麵包樹果", "icon": "🍈", "source": "食材", "audio": "facidol.m4a"},
    {"amis": "Haca", "chi": "也 / 亦", "icon": "➕", "source": "連接詞", "audio": "haca.m4a"},
    {"amis": "Maemin", "chi": "全部 / 所有的", "icon": "💯", "source": "數量", "audio": "maemin.m4a"},
    {"amis": "Sikaen", "chi": "菜餚 / 配菜", "icon": "🍱", "source": "食物", "audio": "sikaen.m4a"},
    # 注意：dateng.m4a 和 kohaw.m4a 您未上傳，若無檔案按播放會顯示錯誤
    {"amis": "Dateng", "chi": "菜 / 野菜", "icon": "🥬", "source": "食物", "audio": "dateng.m4a"},
    {"amis": "Kohaw", "chi": "湯", "icon": "🍲", "source": "食物", "audio": "kohaw.m4a"},
    {"amis": "Mato’asay", "chi": "老人 / 長輩", "icon": "👵", "source": "人物", "audio": "matoasay.m4a"},
]

sentences = [
    {"amis": "O maan ko kaolahan iso a sikaen?", "chi": "你喜歡什麼樣的菜呢？", "icon": "❓", "source": "問句", "audio": "sentence_01.m4a"},
    {"amis": "O foting ko kaolahan ako a dateng.", "chi": "魚是我最喜歡的菜。", "icon": "🐟", "source": "回答", "audio": "sentence_02.m4a"},
    {"amis": "Kaolahan no wama konini a kohaw.", "chi": "這碗是爸爸最喜歡的湯。", "icon": "👨", "source": "描述", "audio": "sentence_03.m4a"},
    {"amis": "Tadakaolahan no mato’asay kona dateng.", "chi": "這些是老人家最喜歡的菜。", "icon": "👵", "source": "描述", "audio": "sentence_04.m4a"},
    {"amis": "Kaolahan ako a maemin konini a sikaen.", "chi": "這些都是我最喜歡的菜餚。", "icon": "😋", "source": "感嘆", "audio": "sentence_05.m4a"},
    {"amis": "O facidol i, o tadakaolahan haca no ’Amis.", "chi": "麵包樹果也是阿美族人最愛。", "icon": "🍈", "source": "文化", "audio": "sentence_06.m4a"},
]

# --- 3. 隨機題庫 ---
raw_quiz_pool = [
    {
        "q": "「麵包樹果」的阿美語怎麼說？",
        "audio": "facidol.m4a",
        "options": ["Facidol", "Foting", "Dateng"],
        "ans": "Facidol",
        "hint": "阿美族人最愛的食材之一"
    },
    {
        "q": "O maan ko kaolahan iso a sikaen?",
        "audio": "sentence_01.m4a",
        "options": ["你喜歡什麼樣的菜呢？", "這是誰煮的菜？", "你要去哪裡買菜？"],
        "ans": "你喜歡什麼樣的菜呢？",
        "hint": "Maan 是「什麼」，Kaolahan 是「喜歡的」"
    },
    {
        "q": "Kaolahan no wama konini a kohaw.",
        "audio": "sentence_03.m4a",
        "options": ["這碗是爸爸最喜歡的湯", "這碗是媽媽煮的湯", "我不喜歡喝湯"],
        "ans": "這碗是爸爸最喜歡的湯",
        "hint": "Wama 是爸爸，Kohaw 是湯"
    },
    {
        "q": "單字測驗：Maemin",
        "audio": "maemin.m4a",
        "options": ["全部", "一點點", "沒有"],
        "ans": "全部",
        "hint": "Kaolahan ako a maemin (這些「全部」都是我喜歡的)"
    },
    {
        "q": "單字測驗：Mato’asay",
        "audio": "matoasay.m4a",
        "options": ["老人/長輩", "小孩", "年輕人"],
        "ans": "老人/長輩",
        "hint": "Tadakaolahan no mato’asay (老人家最喜歡的)"
    },
    {
        "q": "O foting ko kaolahan ako a dateng.",
        "audio": "sentence_02.m4a",
        "options": ["魚是我最喜歡的菜", "我喜歡吃麵包樹果", "這道菜很鹹"],
        "ans": "魚是我最喜歡的菜",
        "hint": "Foting 是魚"
    },
    {
        "q": "「湯」的阿美語是？",
        "audio": "kohaw.m4a",
        "options": ["Kohaw", "Dateng", "Sapaiyo"],
        "ans": "Kohaw",
        "hint": "喝熱熱的 Kohaw"
    }
]

# --- 4. 狀態初始化 (洗牌邏輯) ---
if 'init' not in st.session_state:
    st.session_state.score = 0
    st.session_state.current_q_idx = 0
    st.session_state.quiz_id = str(random.randint(1000, 9999))
    
    # 抽題與洗牌
    selected_questions = random.sample(raw_quiz_pool, 4)
    final_questions = []
    for q in selected_questions:
        q_copy = q.copy()
        shuffled_opts = random.sample(q['options'], len(q['options']))
        q_copy['shuffled_options'] = shuffled_opts
        final_questions.append(q_copy)
        
    st.session_state.quiz_questions = final_questions
    st.session_state.init = True

# --- 5. 主介面 ---
st.markdown("<h1 style='text-align: center; color: #BF360C;'>Kaolahan 所喜歡的</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8D6E63;'>講師：高春美 | 教材提供者：高春美</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📖 詞彙與句型", "🎲 隨機挑戰"])

# === Tab 1: 學習模式 ===
with tab1:
    st.subheader("📝 核心單字")
    col1, col2 = st.columns(2)
    for i, word in enumerate(vocab_data):
        with (col1 if i % 2 == 0 else col2):
            st.markdown(f"""
            <div class="word-card">
                <div class="emoji-icon">{word['icon']}</div>
                <div class="amis-text">{word['amis']}</div>
                <div class="chinese-text">{word['chi']}</div>
                <div class="source-tag">{word['source']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 播放", key=f"btn_vocab_{i}"):
                play_local_audio(word['audio'])

    st.markdown("---")
    st.subheader("🗣️ 實用句型")
    for i, sent in enumerate(sentences):
        st.markdown(f"""
        <div class="sentence-box">
            <div style="font-size: 20px; color: #E65100; font-weight: bold;">{sent['icon']} {sent['amis']}</div>
            <div style="font-size: 16px; color: #5D4037; margin-top: 5px;">{sent['chi']}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"▶️ 朗讀句子", key=f"btn_sent_{i}"):
            play_local_audio(sent['audio'])

# === Tab 2: 測驗模式 ===
with tab2:
    st.subheader("🧠 隨機測驗 (共4題)")
    
    current_idx = st.session_state.current_q_idx
    questions = st.session_state.quiz_questions
    
    if current_idx < len(questions):
        q_data = questions[current_idx]
        progress = (current_idx / len(questions))
        st.progress(progress)
        
        st.markdown(f"### Q{current_idx + 1}: {q_data['q']}")
        
        # 播放題目語音
        if q_data.get('audio'):
            if st.button("🔊 聽題目發音", key=f"quiz_audio_{current_idx}"):
                play_local_audio(q_data['audio'])
        
        option_cols = st.columns(len(q_data['shuffled_options']))
        
        if f"answered_{current_idx}" not in st.session_state:
            for idx, opt in enumerate(q_data['shuffled_options']):
                if st.button(opt, key=f"opt_{current_idx}_{idx}"):
                    if opt == q_data['ans']:
                        st.session_state.score += 25
                        st.success(f"🎉 正確！ {q_data['ans']}")
                    else:
                        st.error(f"❌ 答錯了，正確答案是：{q_data['ans']}")
                        st.info(f"💡 提示：{q_data['hint']}")
                    
                    st.session_state[f"answered_{current_idx}"] = True
                    time.sleep(1.5)
                    st.session_state.current_q_idx += 1
                    safe_rerun()
        else:
            st.info("載入下一題中...")
            
    else:
        st.progress(1.0)
        st.balloons()
        final_score = st.session_state.score
        
        st.markdown(f"""
        <div style="text-align: center; padding: 30px; background-color: #FFF3E0; border-radius: 20px;">
            <h2 style="color: #E64A19;">測驗完成！</h2>
            <h1 style="font-size: 60px; color: #BF360C;">{final_score} 分</h1>
            <p>Kaolahan iso konini a app? (你喜歡這個App嗎？)</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 再玩一次"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            safe_rerun()
