import streamlit as st
import time
import math
import random

# ==========================================
# 1. 遊戲設定與 CSS
# ==========================================
st.set_page_config(page_title="Fraction Hunter", page_icon="🏹", layout="centered")

# CSS 修復：針對 Streamlit 不同版本的 DOM 結構進行全面覆蓋
st.markdown("""
<style>
    .stApp {
        background-color: #2b2d42;
        color: white;
    }
    
    /* 按鈕容器 */
    div.stButton > button {
        background: linear-gradient(to bottom, #ffffff 0%, #f1f1f1 100%) !important;
        border: 2px solid #ffffff !important;
        border-radius: 12px !important;
        padding: 12px 0px !important;
        box-shadow: 0 4px 0 #999 !important;
        width: 100%;
    }

    /* 🚨 核彈級修復：強制所有按鈕內的文字變成黑色 */
    div.stButton > button, 
    div.stButton > button p, 
    div.stButton > button div,
    div.stButton > button span {
        color: #000000 !important; 
        font-family: sans-serif !important;
        font-weight: 800 !important;
        font-size: 22px !important;
    }

    /* 懸停效果 */
    div.stButton > button:hover {
        transform: translateY(2px) !important;
        box-shadow: 0 2px 0 #666 !important;
        background: #ffecd1 !important;
        border-color: #ef233c !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯 (倒推生成法 - 保證有解)
# ==========================================

class FractionCard:
    def __init__(self, num, den):
        self.num = num
        self.den = den
        self.id = random.randint(1000, 999999)

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
    st.session_state.hand = [FractionCard(1, 2), FractionCard(1, 4)]
if 'message' not in st.session_state: st.session_state.message = "🎮 第一關：把手牌全打出去！"

def generate_level_data(level):
    # 倒推生成法：先發牌，再算目標
    if level == 1: den_pool = [2, 4]
    elif level == 2: den_pool = [3, 6]
    elif level == 3: den_pool = [4, 8, 2]
    else: den_pool = [2, 3, 4, 6]

    hand = []
    total_num = 0
    common_base = 24 # 用於統一計算的基數
    
    card_count = random.randint(3, 5)
    
    for _ in range(card_count):
        den = random.choice(den_pool)
        num = random.choice([1, 1, 2, -1]) 
        
        # 防止總和變負
        current_val = total_num / common_base
        if current_val + (num/den) < 0:
            num = 1 
            
        hand.append(FractionCard(num, den))
        
        factor = common_base // den
        total_num += num * factor

    # 計算目標
    target_gcd = gcd(total_num, common_base)
    target = FractionCard(total_num // target_gcd, common_base // target_gcd)
    current = FractionCard(0, target.den) 
    
    random.shuffle(hand)
    return target, current, hand

def next_level():
    st.session_state.level += 1
    t, c, h = generate_level_data(st.session_state.level)
    st.session_state.target = t
    st.session_state.current = c
    st.session_state.hand = h
    st.session_state.message = f"🚀 進入第 {st.session_state.level} 關！"
    st.balloons()

def play_card(idx):
    card = st.session_state.hand[idx]
    current = st.session_state.current
    
    # 通分邏輯
    if card.den != current.den:
        common_den = lcm(card.den, current.den)
        st.session_state.message = f"⚡ 融合：{current.den} 與 {card.den} -> {common_den}"
        
        factor_curr = common_den // current.den
        current.num *= factor_curr
        current.den = common_den
        
        factor_card = common_den // card.den
        card.num *= factor_card
        card.den = common_den
        
        time.sleep(0.2)
        st.rerun()
        return

    # 出牌
    st.session_state.hand.pop(idx)
    st.session_state.current.num += card.num
    
    check_win()

def check_win():
    curr = st.session_state.current
    tgt = st.session_state.target
    
    if curr.num * tgt.den == tgt.num * curr.den:
        st.session_state.message = "🎉 任務完成！"
        next_level()
    elif len(st.session_state.hand) == 0:
        st.session_state.message = "💀 運算偏離軌道... (請重試)"
    else:
        st.session_state.message = "🚀 飛行中..."

def reset_current_level():
    t, c, h = generate_level_data(st.session_state.level)
    st.session_state.target = t
    st.session_state.current = c
    st.session_state.hand = h
    st.session_state.message = "🔄 關卡重置"

# ==========================================
# 3. UI 渲染 (字串拼接修復版)
# ==========================================

st.title(f"🏹 分數獵人 Level {st.session_state.level}")
st.info(st.session_state.message)

curr_val = st.session_state.current.value
tgt_val = st.session_state.target.value

track_scale = max(tgt_val * 1.5, 2.0)
pos_tgt = min(max(tgt_val / track_scale * 100, 2), 95)
pos_curr = min(max(curr_val / track_scale * 100, 2), 95)

# 🚨 終極修復：使用 Python 變數拼接 HTML
# 這避免了任何縮排或 Markdown 解析器的誤判
game_html = ""
game_html += f'<div style="position: relative; width: 100%; height: 120px; background-color: #353b48; border-radius: 15px; margin: 20px 0; border: 3px solid #7f8fa6; overflow: hidden;">'
game_html += f'  <div style="position: absolute; width: 100%; height: 100%; background: repeating-linear-gradient(90deg, transparent, transparent 19%, #444 20%); opacity: 0.3;"></div>'
game_html += f'  <div style="position: absolute; bottom: 5px; left: 10px; color: #aaa; font-size: 12px;">0</div>'
game_html += f'  <div style="position: absolute; bottom: 5px; right: 10px; color: #aaa; font-size: 12px;">{track_scale:.1f}</div>'
game_html += f'  <div style="position: absolute; left: {pos_tgt}%; top: 20px; transform: translateX(-50%); text-align: center; z-index: 1;">'
game_html += f'    <div style="font-size: 30px; line-height: 1;">🚩</div>'
game_html += f'    <div style="background: rgba(239, 35, 60, 0.8); color: white; padding: 2px 6px; border-radius: 4px; font-size: 14px; margin-top: 5px;">{st.session_state.target}</div>'
game_html += f'  </div>'
game_html += f'  <div style="position: absolute; left: {pos_curr}%; top: 60px; transition: left 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); transform: translateX(-50%); z-index: 2; text-align: center;">'
game_html += f'    <div style="font-size: 40px; filter: drop-shadow(0 0 10px #4cd137); transform: rotate(90deg);">🚀</div>'
game_html += f'  </div>'
game_html += f'</div>'
game_html += f'<div style="text-align: center; margin-bottom: 20px;">'
game_html += f'  <span style="color: #bbb; font-size: 18px;">當前位置: </span>'
game_html += f'  <span style="color: #4cd137; font-weight: bold; font-size: 32px;">{st.session_state.current}</span>'
game_html += f'</div>'

st.markdown(game_html, unsafe_allow_html=True)

st.write("### 🃏 你的手牌")

if not st.session_state.hand:
    if "成功" not in st.session_state.message:
        st.error("任務失敗！(手牌用完了)")
        if st.button("🔄 重置本關"):
            reset_current_level()
            st.rerun()
else:
    cols = st.columns(len(st.session_state.hand))
    for i, card in enumerate(st.session_state.hand):
        with cols[i]:
            is_diff = card.den != st.session_state.current.den
            
            # 手動添加 Emoji 確保不依賴 CSS 渲染
            if is_diff:
                label = f"{card.num}/{card.den} ⚡"
                help_txt = "分母不同！點擊通分"
            else:
                label = f"{card.num}/{card.den}"
                help_txt = "移動"
            
            if st.button(label, key=f"card_{card.id}", help=help_txt, use_container_width=True):
                play_card(i)
                st.rerun()

st.markdown("---")
if st.button("🎲 換一題 (跳過本關)"):
    reset_current_level()
    st.rerun()

with st.expander("📖 玩法說明"):
    st.markdown("""
    1. **必勝法**：保證有解！只要把手上的牌**全部**打出去，就會剛好到達終點。
    2. **⚡ 通分**：如果手牌分母和火箭不同，點擊會先進行「融合」通分。
    3. **策略**：觀察分母，先把容易通分的牌打出去。
    """)
