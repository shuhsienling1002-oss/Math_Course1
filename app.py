import streamlit as st
import time
import math
import random

# ==========================================
# 1. 遊戲設定與 CSS (Game Config)
# ==========================================
st.set_page_config(page_title="Fraction Hunter", page_icon="🏹", layout="centered")

# 修正重點：強制設定按鈕文字顏色與背景，避免白底白字
st.markdown("""
<style>
    /* 全局背景設定 */
    .stApp {
        background-color: #2b2d42;
        color: white;
    }
    
    /* 修正按鈕樣式：強制深色文字與淺色背景，確保可讀性 */
    div.stButton > button {
        background: linear-gradient(135deg, #edf2f4 0%, #8d99ae 100%);
        color: #2b2d42 !important; /* 強制文字為深藍色 */
        border: 2px solid white;
        border-radius: 15px;
        font-weight: bold;
        font-size: 20px;
        padding: 10px 20px;
        width: 100%;
        transition: transform 0.1s;
    }
    
    /* 按鈕懸停效果 */
    div.stButton > button:hover {
        transform: scale(1.05);
        color: #ef233c !important; /* 懸停時變紅色 */
        border-color: #ef233c;
    }

    /* 隱藏選單 */
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
        st.session_state.message = f"⚡ 啟動魔法融合！ {card.den} 和 {current.den} 變成了 {common_den}"
        
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
        st.session_state.message = "💀 手牌耗盡... 任務失敗 (按重置)"

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

# 修正重點：移除 HTML 字串內的所有縮排，防止被當成代碼區塊渲染
st.markdown(f"""
<div style="position: relative; width: 100%; height: 80px; background-color: #333; border-radius: 40px; margin: 30px 0; border: 2px solid #555;">
<div style="position: absolute; left: {min(max((tgt_val + 0.5) / 2 * 100, 0), 100)}%; top: -40px; transform: translateX(-50%); text-align: center;">
<div style="font-size: 30px;">🚩</div>
<div style="color: #ef233c; font-weight: bold; background: rgba(0,0,0,0.5); padding: 2px 5px; border-radius: 5px;">{st.session_state.target}</div>
</div>
<div style="position: absolute; left: {min(max((curr_val + 0.5) / 2 * 100, 0), 100)}%; top: 15px; transition: left 0.5s ease; transform: translateX(-50%);">
<div style="font-size: 40px;">🚀</div>
</div>
</div>
<div style="text-align: center; color: #8d99ae; font-size: 18px; margin-bottom: 20px;">你的位置: <b>{st.session_state.current}</b></div>
""", unsafe_allow_html=True)

st.markdown("---")

st.write("### 🃏 你的手牌 (點擊出牌)")

if not st.session_state.hand:
    if st.session_state.message != "🎉 捕獲成功！":
        st.error("沒牌了！請重置")
        if st.button("🔄 重來"):
            reset_game()
            st.rerun()
else:
    cols = st.columns(len(st.session_state.hand))
    for i, card in enumerate(st.session_state.hand):
        with cols[i]:
            is_diff = card.den != st.session_state.current.den
            btn_label = f"{card.num}/{card.den}"
            if is_diff:
                btn_label += " (⚡融合)"
                help_text = "分母不同！點擊啟動自動通分魔法"
            else:
                help_text = "出牌移動"

            # 這裡的 button 樣式現在會被上面的 CSS 控制
            if st.button(btn_label, key=f"card_{card.id}", help=help_text, use_container_width=True):
                play_card(i)
                st.rerun()

with st.expander("📖 遊戲說明"):
    st.write("""
    1. 你的目標是控制火箭 🚀 停在旗幟 🚩 的位置。
    2. 點擊手牌 🃏 來移動。
    3. 如果卡片分母跟你不一樣（例如 1/2 和 1/4），點擊卡片會自動觸發 **「魔法融合」** (通分)，把它們變成一樣的分母！
    4. 用最少的步數抓到目標！
    """)
