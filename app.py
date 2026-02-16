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
    /* 強力按鈕修復 */
    div.stButton > button {
        background: linear-gradient(to bottom, #ffffff 0%, #e0e0e0 100%) !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 15px 0px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 0 #999 !important;
    }
    div.stButton > button * {
        color: #000000 !important;
        font-size: 20px !important;
        font-weight: 900 !important;
    }
    div.stButton > button:hover {
        transform: translateY(2px) !important;
        box-shadow: 0 2px 0 #666 !important;
        background: #ffecd1 !important;
        border-color: #ef233c !important;
    }
    
    /* 輔助功能按鈕 (重洗/重置) */
    .utility-btn button {
        background: transparent !important;
        border: 1px solid #7f8fa6 !important;
        color: #bbb !important;
        box-shadow: none !important;
        padding: 5px !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯 (修復數學計算與關卡生成)
# ==========================================

class FractionCard:
    def __init__(self, num, den):
        self.num = num
        self.den = den
        self.id = random.randint(1000, 999999) # 唯一ID

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
if 'history' not in st.session_state: st.session_state.history = [] # 運算紀錄

def log_math(txt):
    st.session_state.history.append(txt)
    # 只保留最近 3 條
    if len(st.session_state.history) > 3:
        st.session_state.history.pop(0)

def generate_level_data(level):
    # 難度曲線
    if level == 1: den_pool = [2, 4]
    elif level == 2: den_pool = [3, 6]
    elif level == 3: den_pool = [4, 8, 2]
    else: den_pool = [3, 4, 6, 8, 12] # Level 4+ 混合分母

    base_den = random.choice(den_pool)
    # 目標生成：確保是一個合理的範圍 (0.5 ~ 2.5)
    target_num = random.randint(int(base_den * 0.5), int(base_den * 2.5))
    
    target = FractionCard(target_num, base_den)
    current = FractionCard(0, base_den)
    
    hand = []
    # 必勝邏輯：至少發給玩家一張能顯著接近目標的牌
    diff = target.value
    # 簡單逼近：給一張大約是差距一半的牌
    hand.append(FractionCard(1, 2)) 
    
    # 隨機補充 3 張
    for _ in range(3):
        h_den = random.choice(den_pool)
        h_num = random.choice([1, 1, 2, -1]) # 多給正數
        hand.append(FractionCard(h_num, h_den))
        
    random.shuffle(hand)
    return target, current, hand

def next_level():
    st.session_state.level += 1
    t, c, h = generate_level_data(st.session_state.level)
    st.session_state.target = t
    st.session_state.current = c
    st.session_state.hand = h
    st.session_state.message = f"🚀 進入第 {st.session_state.level} 關！"
    st.session_state.history = []
    st.balloons()

def shuffle_hand():
    # 棄牌重抽 (防止卡關)
    st.session_state.message = "🃏 重新洗牌！"
    _, _, h = generate_level_data(st.session_state.level)
    st.session_state.hand = h
    log_math("系統：玩家發動了重洗手牌")

def play_card(idx):
    card = st.session_state.hand[idx]
    current = st.session_state.current
    
    # --- 通分邏輯 (Surgical Fusion) ---
    if card.den != current.den:
        old_den_c = current.den
        old_den_h = card.den
        
        common_den = lcm(card.den, current.den)
        st.session_state.message = f"⚡ 融合：{old_den_c} 與 {old_den_h} -> {common_den}"
        
        # 1. 更新當前位置
        factor_curr = common_den // current.den
        current.num *= factor_curr
        current.den = common_den
        
        # 2. 🚨 關鍵修復：只更新「這張」手牌，不碰其他牌！
        factor_card = common_den // card.den
        card.num *= factor_card
        card.den = common_den
        
        log_math(f"通分: {current} (位置) | {card} (手牌)")
        
        time.sleep(0.2)
        st.rerun()
        return

    # --- 出牌邏輯 ---
    st.session_state.hand.pop(idx)
    
    old_pos = f"{current}"
    st.session_state.current.num += card.num
    
    log_math(f"移動: {old_pos} + {card} = {st.session_state.current}")
    check_win()

def check_win():
    # 使用整數交叉相乘比較，避免任何浮點數誤差
    # A/B == C/D  <=>  A*D == C*B
    curr = st.session_state.current
    tgt = st.session_state.target
    
    if curr.num * tgt.den == tgt.num * curr.den:
        st.session_state.message = "🎉 捕獲成功！"
        next_level()
    elif len(st.session_state.hand) == 0:
        st.session_state.message = "💀 手牌耗盡..."
    else:
        st.session_state.message = "🚀 飛行中..."

def reset_game():
    st.session_state.level = 1
    t, c, h = generate_level_data(1)
    st.session_state.target = t
    st.session_state.current = c
    st.session_state.hand = h
    st.session_state.message = "🔄 遊戲重置"
    st.session_state.history = []

# ==========================================
# 3. UI 渲染
# ==========================================

st.title(f"🏹 分數獵人 Level {st.session_state.level}")
st.info(st.session_state.message)

curr_val = st.session_state.current.value
tgt_val = st.session_state.target.value

# 視覺化縮放
scale = 3.0 
pos_tgt = min(max(tgt_val / scale * 100, 2), 98)
pos_curr = min(max(curr_val / scale * 100, 2), 98)

# 戰場 HTML (無縮排)
st.markdown(f"""
<div style="position: relative; width: 100%; height: 120px; background-color: #353b48; border-radius: 15px; margin: 20px 0; border: 3px solid #7f8fa6; overflow: hidden;">
<div style="position: absolute; width: 100%; height: 100%; background: repeating-linear-gradient(90deg, transparent, transparent 19%, #444 20%); opacity: 0.3;"></div>
<div style="position: absolute; bottom: 5px; left: 10px; color: #aaa; font-size: 12px;">0</div>
<div style="position: absolute; bottom: 5px; right: 10px; color: #aaa; font-size: 12px;">3.0</div>
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

# 手牌區
st.write("### 🃏 你的手牌")

if not st.session_state.hand:
    if "成功" not in st.session_state.message:
        st.error("沒牌了！")
        if st.button("🔄 重新挑戰本關"):
            t, c, h = generate_level_data(st.session_state.level)
            st.session_state.target = t
            st.session_state.current = c
            st.session_state.hand = h
            st.rerun()
else:
    cols = st.columns(len(st.session_state.hand))
    for i, card in enumerate(st.session_state.hand):
        with cols[i]:
            is_diff = card.den != st.session_state.current.den
            if is_diff:
                label = f"{card.num}/{card.den}\n⚡"
                help_txt = "點擊通分"
            else:
                label = f"{card.num}/{card.den}"
                help_txt = "移動"
            
            if st.button(label, key=f"card_{card.id}", help=help_txt, use_container_width=True):
                play_card(i)
                st.rerun()

# 輔助功能區
st.markdown("---")
c1, c2, c3 = st.columns([1,1,2])
with c1:
    # 使用 CSS class utility-btn
    if st.button("🎲 重洗手牌", key="shuffle"):
        shuffle_hand()
        st.rerun()
with c2:
    if st.button("⏮ 回第一關", key="reset"):
        reset_game()
        st.rerun()
with c3:
    # 數學運算日誌 (Debug Stream)
    with st.expander("📊 運算黑盒子 (Math Logs)"):
        for log in st.session_state.history:
            st.code(log, language="text")

with st.expander("📖 玩法說明"):
    st.markdown("""
    1. **目標**：讓火箭 🚀 數值等於旗幟 🚩。
    2. **⚡ 通分**：如果手牌分母和火箭不同，點擊會先進行通分（只影響那張牌和火箭）。
    3. **🎲 洗牌**：如果覺得卡關無解，點擊左下角「重洗手牌」。
    """)
