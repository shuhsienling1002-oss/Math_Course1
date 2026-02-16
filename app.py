import streamlit as st
import time
import math
import random

# ==========================================
# 1. 遊戲設定與 CSS (Game Config)
# ==========================================
st.set_page_config(page_title="Fraction Hunter", page_icon="🏹", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #2b2d42; /* 深色背景 */
        color: white;
    }
    .target-box {
        background-color: #8d99ae;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 2px dashed #ef233c;
        margin-bottom: 20px;
    }
    .card-container {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .game-card {
        background: linear-gradient(135deg, #edf2f4 0%, #8d99ae 100%);
        color: #2b2d42;
        padding: 20px;
        border-radius: 15px;
        width: 100px;
        text-align: center;
        font-weight: bold;
        font-size: 24px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        cursor: pointer;
        border: 2px solid white;
    }
    .game-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.5);
    }
    .current-pos {
        font-size: 40px;
        text-align: center;
        color: #ef233c;
        text-shadow: 0 0 10px #ef233c;
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

# 初始化遊戲狀態
if 'level' not in st.session_state: st.session_state.level = 1
if 'target' not in st.session_state: st.session_state.target = FractionCard(3, 4) # 第一關目標
if 'current' not in st.session_state: st.session_state.current = FractionCard(0, 4) # 玩家位置
if 'hand' not in st.session_state: 
    # 第一關手牌
    st.session_state.hand = [FractionCard(1, 2), FractionCard(1, 4), FractionCard(-1, 4)]
if 'message' not in st.session_state: st.session_state.message = "🎮 第一關：獵取目標！"
if 'game_over' not in st.session_state: st.session_state.game_over = False

def next_level():
    st.session_state.level += 1
    # 簡單的關卡生成邏輯
    den = random.choice([4, 6, 8, 12])
    target_num = random.randint(1, den-1)
    st.session_state.target = FractionCard(target_num, den)
    st.session_state.current = FractionCard(0, den)
    
    # 生成 3 張隨機手牌
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
    
    # 1. 檢查分母 (通分機制)
    if card.den != current.den:
        common_den = lcm(card.den, current.den)
        # 自動通分 (魔法果汁機)
        st.session_state.message = f"⚡ 啟動魔法融合！ {card.den} 和 {current.den} 變成了 {common_den}"
        
        # 更新玩家分母
        factor_c = common_den // current.den
        current.num *= factor_c
        current.den = common_den
        
        # 更新手牌分母 (全部手牌都要變，這樣比較簡單)
        for c in st.session_state.hand:
            f = common_den // c.den
            c.num *= f
            c.den = common_den
            
        time.sleep(0.5) # 假裝運算一下
        st.rerun()
        return

    # 2. 出牌 (計算)
    # 移除手牌
    st.session_state.hand.pop(idx)
    # 更新位置
    st.session_state.current.num += card.num
    
    # 3. 檢查勝利
    check_win()

def check_win():
    curr = st.session_state.current
    tgt = st.session_state.target
    
    # 統一分母比較
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

# A. 遊戲狀態條
st.info(st.session_state.message)

# B. 戰場 (Progress Bar)
# 計算進度 0% ~ 100% (假設範圍是 -1 到 2)
curr_val = st.session_state.current.value
tgt_val = st.session_state.target.value

# 繪製一個簡單的 HTML 進度條戰場
st.markdown(f"""
<div style="position: relative; width: 100%; height: 60px; background-color: #333; border-radius: 30px; margin: 30px 0;">
    <div style="position: absolute; left: {min(max((tgt_val + 0.5) / 2 * 100, 0), 100)}%; top: -35px; transform: translateX(-50%);">
        <div style="font-size: 30px;">🚩</div>
        <div style="color: #ef233c; font-weight: bold;">{st.session_state.target}</div>
    </div>
    
    <div style="position: absolute; left: {min(max((curr_val + 0.5) / 2 * 100, 0), 100)}%; top: 10px; transition: left 0.5s ease; transform: translateX(-50%);">
        <div style="font-size: 40px;">🚀</div>
    </div>
</div>
<div style="text-align: center; color: #8d99ae;">你的位置: {st.session_state.current}</div>
""", unsafe_allow_html=True)

st.markdown("---")

# C. 手牌區 (Card Battle)
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
            # 判斷是否需要通分特效
            is_diff = card.den != st.session_state.current.den
            btn_label = f"{card.num}\n--\n{card.den}"
            if is_diff:
                btn_label += "\n(⚡融合)"
                help_text = "分母不同！點擊啟動自動通分魔法"
                btn_type = "secondary"
            else:
                help_text = "出牌移動"
                btn_type = "primary"

            if st.button(btn_label, key=f"card_{card.id}", help=help_text, use_container_width=True):
                play_card(i)
                st.rerun()

# D. 簡單教學
with st.expander("📖 遊戲說明"):
    st.write("""
    1. 你的目標是控制火箭 🚀 停在旗幟 🚩 的位置。
    2. 點擊手牌 🃏 來移動。
    3. 如果卡片分母跟你不一樣（例如 1/2 和 1/4），點擊卡片會自動觸發 **「魔法融合」** (通分)，把它們變成一樣的分母！
    4. 用最少的步數抓到目標！
    """)
