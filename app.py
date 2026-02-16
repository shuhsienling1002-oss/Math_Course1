import streamlit as st
import time
import math
import random

# ==========================================
# 1. 遊戲設定與 CSS (Game Config)
# ==========================================
st.set_page_config(page_title="Fraction Hunter", page_icon="🏹", layout="centered")

# 修正重點说明：
# 1. div.stButton > button p: 強制設定按鈕內文字顏色為深色 (覆蓋 Streamlit 深色模式預設的白色)
# 2. HTML 字串全部向左對齊，沒有任何縮排 (解決代碼外露問題)

st.markdown("""
<style>
    /* 全局背景設定：深藍色 */
    .stApp {
        background-color: #2b2d42;
        color: white;
    }
    
    /* --- 核彈級按鈕修復 --- */
    /* 針對按鈕容器 */
    div.stButton > button {
        background: linear-gradient(to bottom, #ffffff 0%, #e0e0e0 100%) !important; /* 強制白/灰漸層背景 */
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 10px 0px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 0 #999 !important; /* 增加立體感 */
    }

    /* 針對按鈕內的文字 (關鍵修復点) */
    div.stButton > button p {
        color: #2b2d42 !important; /* 強制深藍色文字 */
        font-size: 24px !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }
    
    /* 針對按鈕內的 Emoji 或其他元素 */
    div.stButton > button * {
        color: #2b2d42 !important;
    }

    /* 按鈕懸停效果 */
    div.stButton > button:hover {
        transform: translateY(2px) !important;
        box-shadow: 0 2px 0 #666 !important;
        background: #ffecd1 !important; /* 懸停變淡黃色 */
        border-color: #ef233c !important;
    }
    
    /* 按鈕點擊效果 */
    div.stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: none !important;
    }

    /* 隱藏 Streamlit 選單 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 遊戲邏輯 (Game Logic)
# ==========================================

class FractionCard:
    def __init__(self, num, den):
        self.num = num
        self.den = den
        self.value = num / den
        self.id = random.randint(1000, 9999)

    def __repr__(self):
        return f"{self.num}/{self.den}"

def gcd(a, b): return math.gcd(a, b)
def lcm(a, b): return abs(a * b) // gcd(a, b)

# 初始化狀態
if 'level' not in st.session_state: st.session_state.level = 1
if 'target' not in st.session_state: st.session_state.target = FractionCard(3, 4)
if 'current' not in st.session_state: st.session_state.current = FractionCard(0, 4)
if 'hand' not in st.session_state: 
    st.session_state.hand = [FractionCard(1, 2), FractionCard(1, 4), FractionCard(-1, 4)]
if 'message' not in st.session_state: st.session_state.message = "🎮 第一關：獵取目標！"

def next_level():
    st.session_state.level += 1
    den = random.choice([4, 6, 8, 12])
    target_num = random.randint(1, den-1)
    st.session_state.target = FractionCard(target_num, den)
    st.session_state.current = FractionCard(0, den)
    
    new_hand = []
    for _ in range(3):
        h_den = random.choice([2, 3, 4])
        h_num = random.choice([1, -1])
        new_hand.append(FractionCard(h_num, h_den))
    
    st.session_state.hand = new_hand
    st.session_state.message = f"🚀 進入第 {st.session_state.level} 關！"
    st.balloons()

def play_card(idx):
    card = st.session_state.hand[idx]
    current = st.session_state.current
    
    if card.den != current.den:
        common_den = lcm(card.den, current.den)
        st.session_state.message = f"⚡ 魔法融合！ {card.den} 和 {current.den} 變成了 {common_den}"
        
        factor_c = common_den // current.den
        current.num *= factor_c
        current.den = common_den
        
        for c in st.session_state.hand:
            f = common_den // c.den
            c.num *= f
            c.den = common_den
            
        time.sleep(0.5)
        st.rerun()
        return

    st.session_state.hand.pop(idx)
    st.session_state.current.num += card.num
    check_win()

def check_win():
    curr = st.session_state.current
    tgt = st.session_state.target
    
    common = lcm(curr.den, tgt.den)
    curr_val = curr.num * (common // curr.den)
    tgt_val = tgt.num * (common // tgt.den)
    
    if curr_val == tgt_val:
        st.session_state.message = "🎉 捕獲成功！"
        next_level()
    elif len(st.session_state.hand) == 0:
        st.session_state.message = "💀 沒牌了... (按重置)"

def reset_game():
    st.session_state.level = 1
    st.session_state.target = FractionCard(3, 4)
    st.session_state.current = FractionCard(0, 4)
    st.session_state.hand = [FractionCard(1, 2), FractionCard(1, 4), FractionCard(-1, 4)]
    st.session_state.message = "🔄 遊戲重置"

# ==========================================
# 3. UI 渲染 (The View)
# ==========================================

st.title(f"🏹 分數獵人 Level {st.session_state.level}")

st.info(st.session_state.message)

curr_val = st.session_state.current.value
tgt_val = st.session_state.target.value

# 計算 CSS 位置 (限制在 0% - 100%)
# 假設戰場總長度代表數值 0 到 1.5 (為了讓畫面好從寬)
scale_factor = 1.2 
pos_tgt = min(max(tgt_val / scale_factor * 100, 5), 95)
pos_curr = min(max(curr_val / scale_factor * 100, 5), 95)

# --- 修正重點：這裡的 HTML 完全沒有縮排，貼齊最左邊 ---
st.markdown(f"""
<div style="position: relative; width: 100%; height: 100px; background-color: #353b48; border-radius: 15px; margin: 40px 0; border: 3px solid #7f8fa6; box-shadow: inset 0 0 20px #000;">
<div style="position: absolute; left: {pos_tgt}%; top: 15px; transform: translateX(-50%); text-align: center; z-index: 1;">
<div style="font-size: 30px; line-height: 1;">🚩</div>
<div style="color: #ff6b6b; font-weight: bold; font-size: 18px; background: rgba(0,0,0,0.7); padding: 4px 8px; border-radius: 6px; margin-top: 5px;">{st.session_state.target}</div>
</div>
<div style="position: absolute; left: {pos_curr}%; top: 40px; transition: left 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: translateX(-50%); z-index: 2;">
<div style="font-size: 50px; filter: drop-shadow(0 0 10px #4cd137);">🚀</div>
</div>
<div style="position: absolute; bottom: 5px; left: 10px; color: #7f8fa6; font-size: 12px;">Start (0)</div>
<div style="position: absolute; bottom: 5px; right: 10px; color: #7f8fa6; font-size: 12px;">End ({scale_factor})</div>
</div>
<div style="text-align: center; font-size: 20px; margin-bottom: 20px;">
當前位置: <span style="color: #4cd137; font-weight: bold; font-size: 28px;">{st.session_state.current}</span>
</div>
""", unsafe_allow_html=True)

st.write("### 🃏 你的手牌 (點擊出牌)")

if not st.session_state.hand:
    if st.session_state.message != "🎉 捕獲成功！":
        st.error("任務失敗！")
        if st.button("🔄 重來"):
            reset_game()
            st.rerun()
else:
    # 增加手牌間距
    cols = st.columns(len(st.session_state.hand))
    for i, card in enumerate(st.session_state.hand):
        with cols[i]:
            is_diff = card.den != st.session_state.current.den
            
            # 按鈕文字內容
            if is_diff:
                label = f"{card.num}/{card.den}\n⚡"
                help_txt = "點擊進行通分"
            else:
                label = f"{card.num}/{card.den}"
                help_txt = "出牌"

            if st.button(label, key=f"card_{card.id}", help=help_txt, use_container_width=True):
                play_card(i)
                st.rerun()

with st.expander("📖 玩法說明"):
    st.markdown("""
    1. **目標**：讓火箭 🚀 飛到旗幟 🚩 的位置。
    2. **出牌**：點擊下方的白色卡片。
    3. **⚡ 閃電符號**：表示這張牌的分母跟目前位置不一樣。點擊它會自動發動 **「通分魔法」**！
    4. **負數**：分子是負數（例如 -1/4）會讓火箭往回飛。
    """)
