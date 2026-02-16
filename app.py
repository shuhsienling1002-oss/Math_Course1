import streamlit as st
import time
import math
import random

# ==========================================
# 1. 遊戲設定與 CSS
# ==========================================
st.set_page_config(page_title="Fraction Hunter", page_icon="🏹", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #2b2d42;
        color: white;
    }
    div.stButton > button {
        background: linear-gradient(to bottom, #ffffff 0%, #e0e0e0 100%) !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 10px 0px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 0 #999 !important;
    }
    div.stButton > button p {
        color: #2b2d42 !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        margin: 0 !important;
    }
    div.stButton > button:hover {
        transform: translateY(2px) !important;
        box-shadow: 0 2px 0 #666 !important;
        background: #ffecd1 !important;
        border-color: #ef233c !important;
    }
    div.stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 遊戲邏輯 (修正核心數學錯誤)
# ==========================================

class FractionCard:
    def __init__(self, num, den):
        self.num = num
        self.den = den
        self.id = random.randint(1000, 9999)

    # 🚨 關鍵修正：將 value 變成動態屬性
    # 這樣每次分子分母改變時，數值才會跟著變！
    @property
    def value(self):
        return self.num / self.den

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
    # 確保目標不為 0 且小於 2 (避免太難)
    target_num = random.randint(1, int(den * 1.5))
    st.session_state.target = FractionCard(target_num, den)
    st.session_state.current = FractionCard(0, den)
    
    new_hand = []
    for _ in range(4): # 給 4 張牌比較好過關
        h_den = random.choice([2, 3, 4, 6])
        h_num = random.choice([1, 1, -1]) # 多一點正數
        new_hand.append(FractionCard(h_num, h_den))
    
    st.session_state.hand = new_hand
    st.session_state.message = f"🚀 進入第 {st.session_state.level} 關！"
    st.balloons()

def play_card(idx):
    card = st.session_state.hand[idx]
    current = st.session_state.current
    
    # 通分邏輯 (魔法融合)
    if card.den != current.den:
        common_den = lcm(card.den, current.den)
        st.session_state.message = f"⚡ 魔法融合！分母統一為 {common_den}"
        
        # 更新當前位置的分母
        factor_curr = common_den // current.den
        current.num *= factor_curr
        current.den = common_den
        
        # 更新所有手牌的分母
        for c in st.session_state.hand:
            # 只有當分母不同時才更新，避免重複乘
            if c.den != common_den:
                factor_c = common_den // c.den
                c.num *= factor_c
                c.den = common_den
            
        time.sleep(0.3)
        st.rerun()
        return

    # 正常出牌邏輯
    st.session_state.hand.pop(idx)
    st.session_state.current.num += card.num # 直接加分子
    
    # 這裡不需要手動更新 value，因為 @property 會自動算
    check_win()

def check_win():
    # 判斷勝利 (容許極小誤差，雖然整數運算應該無誤差)
    if abs(st.session_state.current.value - st.session_state.target.value) < 0.0001:
        st.session_state.message = "🎉 捕獲成功！"
        next_level()
    elif len(st.session_state.hand) == 0:
        st.session_state.message = "💀 沒牌了... (按重置)"
    else:
        st.session_state.message = "🚀 飛行中..."

def reset_game():
    st.session_state.level = 1
    st.session_state.target = FractionCard(3, 4)
    st.session_state.current = FractionCard(0, 4)
    st.session_state.hand = [FractionCard(1, 2), FractionCard(1, 4), FractionCard(-1, 4)]
    st.session_state.message = "🔄 遊戲重置"

# ==========================================
# 3. UI 渲染
# ==========================================

st.title(f"🏹 分數獵人 Level {st.session_state.level}")

st.info(st.session_state.message)

# 取得動態計算的數值
curr_val = st.session_state.current.value
tgt_val = st.session_state.target.value

# 視覺化縮放 (讓 0~2 的範圍填滿進度條)
scale = 2.0 
pos_tgt = min(max(tgt_val / scale * 100, 2), 98)
pos_curr = min(max(curr_val / scale * 100, 2), 98)

# 戰場顯示
st.markdown(f"""
<div style="position: relative; width: 100%; height: 120px; background-color: #353b48; border-radius: 15px; margin: 20px 0; border: 3px solid #7f8fa6; overflow: hidden;">
    <div style="position: absolute; width: 100%; height: 100%; background: repeating-linear-gradient(90deg, transparent, transparent 19%, #444 20%); opacity: 0.3;"></div>
    
    <div style="position: absolute; bottom: 5px; left: 10px; color: #aaa; font-size: 12px;">0</div>
    <div style="position: absolute; bottom: 5px; right: 10px; color: #aaa; font-size: 12px;">2.0</div>

    <div style="position: absolute; left: {pos_tgt}%; top: 20px; transform: translateX(-50%); text-align: center; z-index: 1;">
        <div style="font-size: 30px; line-height: 1;">🚩</div>
        <div style="background: rgba(239, 35, 60, 0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 14px; margin-top: 5px;">
            {st.session_state.target}
        </div>
    </div>
    
    <div style="position: absolute; left: {pos_curr}%; top: 60px; transition: left 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: translateX(-50%); z-index: 2; text-align: center;">
        <div style="font-size: 40px; filter: drop-shadow(0 0 10px #4cd137); transform: rotate(90deg);">🚀</div>
    </div>
</div>

<div style="text-align: center; margin-bottom: 20px;">
    <span style="color: #bbb; font-size: 18px;">當前位置: </span>
    <span style="color: #4cd137; font-weight: bold; font-size: 32px;">{st.session_state.current}</span>
</div>
""", unsafe_allow_html=True)

st.write("### 🃏 你的手牌")

if not st.session_state.hand:
    if "成功" not in st.session_state.message:
        st.error("任務失敗！")
        if st.button("🔄 重來"):
            reset_game()
            st.rerun()
else:
    cols = st.columns(len(st.session_state.hand))
    for i, card in enumerate(st.session_state.hand):
        with cols[i]:
            is_diff = card.den != st.session_state.current.den
            
            if is_diff:
                label = f"{card.num}/{card.den}\n⚡"
                help_txt = "分母不同！點擊通分"
            else:
                label = f"{card.num}/{card.den}"
                help_txt = "移動"

            if st.button(label, key=f"card_{card.id}", help=help_txt, use_container_width=True):
                play_card(i)
                st.rerun()

with st.expander("📖 玩法說明"):
    st.markdown("""
    1. **目標**：讓火箭 🚀 與旗幟 🚩 的位置數字一樣。
    2. **出牌**：點擊卡片，把分數加到你的位置上。
    3. **⚡ 閃電**：如果分母不同，必須先點擊卡片進行「通分融合」。
    4. **技巧**：小心不要飛過頭！負數卡片可以讓你往回飛。
    """)
