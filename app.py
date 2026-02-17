import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ==========================================
# 1. 配置與 CSS (View Layer)
# ==========================================
st.set_page_config(page_title="分數拼湊大作戰 v3.1", page_icon="🧩", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    
    .game-container {
        background: #313244;
        border-radius: 16px;
        padding: 24px;
        border: 2px solid #45475a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .fraction-visual-container {
        display: flex;
        gap: 4px;
        align-items: center;
        justify-content: center;
        margin-bottom: 8px;
    }
    
    .pie-chart {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: conic-gradient(#89b4fa var(--p), #45475a 0);
        border: 2px solid #cba6f7;
        flex-shrink: 0;
    }
    .pie-full {
        background: #89b4fa;
        border-color: #f9e2af;
        box-shadow: 0 0 5px rgba(249, 226, 175, 0.5);
    }
    .pie-negative {
        background: conic-gradient(#f38ba8 var(--p), #45475a 0);
        border-color: #f38ba8;
    }
    .pie-full-negative {
        background: #f38ba8;
        border-color: #eba0ac;
    }

    div.stButton > button {
        background-color: #cba6f7 !important;
        color: #181825 !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        padding: 8px 16px !important;
        width: 100%;
        border: 2px solid transparent !important;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #f5c2e7 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .progress-track {
        background: #45475a;
        height: 36px;
        border-radius: 18px;
        position: relative;
        overflow: hidden;
        margin: 20px 0;
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.3);
    }
    .progress-fill {
        height: 100%;
        transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 12px;
        font-size: 14px;
        font-weight: 800;
        color: #181825;
        text-shadow: 0 1px 2px rgba(255,255,255,0.3);
    }
    .fill-normal { background: linear-gradient(90deg, #89b4fa, #b4befe); }
    .fill-warning { background: linear-gradient(90deg, #f9e2af, #fab387); }
    .fill-danger { background: linear-gradient(90deg, #f38ba8, #eba0ac); }
    
    .target-line {
        position: absolute;
        top: 0; bottom: 0;
        width: 4px;
        background: #a6e3a1;
        z-index: 10;
        box-shadow: 0 0 15px #a6e3a1;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 數據模型 (Data Model)
# ==========================================

@dataclass
class Card:
    numerator: int
    denominator: int
    id: str = field(default_factory=lambda: str(random.randint(10000, 99999)))

    @property
    def value(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def get_visual_html(self) -> str:
        val = self.value
        abs_val = abs(val)
        integer_part = int(abs_val)
        fraction_part = abs_val - integer_part
        
        is_neg = val < 0
        pie_class = "pie-negative" if is_neg else "pie-chart"
        full_class = "pie-full-negative" if is_neg else "pie-full"
        
        html = '<div class="fraction-visual-container">'
        
        # 1. 渲染整數部分的滿圓
        display_integers = min(integer_part, 3) 
        for _ in range(display_integers):
            html += f'<div class="pie-chart {full_class}" style="--p: 100%;"></div>'
            
        if integer_part > 3:
            html += '<span style="font-size:20px; color:#f9e2af;">+...</span>'

        # 2. 渲染分數部分
        if fraction_part > 0:
            percent = float(fraction_part) * 100
            html += f'<div class="{pie_class}" style="--p: {percent}%;"></div>'
            
        html += '</div>'
        return html

# ==========================================
# 3. 核心引擎 (Logic Layer)
# ==========================================

class GameEngine:
    
    @staticmethod
    def init_state():
        # [修復]: 強制檢查 game_status，防止舊版 Session 殘留導致崩潰
        if 'level' not in st.session_state or 'game_status' not in st.session_state:
            st.session_state.level = 1
            GameEngine.start_level(1)

    @staticmethod
    def start_level(level: int):
        st.session_state.level = level
        target, start_val, hand, title = GameEngine._generate_math_data(level)
        
        st.session_state.target = target
        st.session_state.current = start_val
        st.session_state.hand = hand
        st.session_state.played_history = []
        st.session_state.game_status = 'playing' # 初始化關鍵狀態
        st.session_state.level_title = title
        st.session_state.msg = "請選擇卡片湊出目標數值！"
        st.session_state.msg_type = "info"

    @staticmethod
    def _generate_math_data(level: int):
        if level == 1:
            den_pool, steps, title = [2, 4], 2, "暖身：簡單同分母"
        elif level == 2:
            den_pool, steps, title = [2, 3, 4, 6], 3, "進階：通分挑戰"
        elif level == 3:
            den_pool, steps, title = [2, 4, 8], 3, "挑戰：帶分數的概念"
        elif level == 4:
            den_pool, steps, title = [2, 3, 4, 5], 4, "大師：負數逆流"
        else:
            den_pool, steps, title = [2, 3, 5, 7, 10], 5, "傳說：質數地獄"

        target = Fraction(0, 1)
        hand = []
        
        for _ in range(steps):
            d = random.choice(den_pool)
            max_n = 5 if level >= 3 else 2 
            n = random.choice([x for x in range(1, max_n+1)])
            
            if level >= 4 and random.random() < 0.4:
                n = -n
                
            card = Card(n, d)
            hand.append(card)
            target += card.value

        distractor_count = 2 if level < 3 else 3
        for _ in range(distractor_count):
            d = random.choice(den_pool)
            n = random.choice([1, 2])
            if level >= 4 and random.random() < 0.5: n = -n
            hand.append(Card(n, d))
            
        random.shuffle(hand)
        return target, Fraction(0, 1), hand, title

    @staticmethod
    def play_card_callback(card_idx: int):
        hand = st.session_state.hand
        if 0 <= card_idx < len(hand):
            card = hand.pop(card_idx)
            st.session_state.current += card.value
            st.session_state.played_history.append(card)
            GameEngine._check_win_condition()

    @staticmethod
    def undo_callback():
        if st.session_state.played_history:
            card = st.session_state.played_history.pop()
            st.session_state.current -= card.value
            st.session_state.hand.append(card)
            st.session_state.msg = "↩️ 時光倒流成功"
            st.session_state.msg_type = "info"
            st.session_state.game_status = 'playing'

    @staticmethod
    def _check_win_condition():
        curr = st.session_state.current
        tgt = st.session_state.target
        
        if curr == tgt:
            st.session_state.game_status = 'won'
            st.session_state.msg = "🎉 完美拼湊！"
            st.session_state.msg_type = "success"
        elif curr > tgt:
            has_negative = any(c.numerator < 0 for c in st.session_state.hand)
            if not has_negative:
                st.session_state.game_status = 'lost'
                st.session_state.msg = "💥 爆掉了！且沒有負數牌可以修正。"
                st.session_state.msg_type = "error"
            else:
                st.session_state.msg = "⚠️ 超過了！快找負數牌修正！"
                st.session_state.msg_type = "warning"

# ==========================================
# 4. UI 渲染層
# ==========================================

def render_progress_bar(current: Fraction, target: Fraction):
    if target == 0: target = Fraction(1,1)
    max_val = max(target * Fraction(3, 2), current * Fraction(11, 10), Fraction(2, 1))
    
    curr_pct = float(current / max_val) * 100
    tgt_pct = float(target / max_val) * 100
    
    fill_class = "fill-normal"
    if current > target: fill_class = "fill-warning"
    
    # [修復]: 安全讀取 game_status，避免 AttributeError
    status = st.session_state.get('game_status', 'playing')
    if status == 'lost': fill_class = "fill-danger"

    st.markdown(f"""
    <div class="game-container">
        <div style="display: flex; justify-content: space-between; font-family: monospace; margin-bottom:5px; font-size: 1.1em;">
            <span>🏁 起點</span>
            <span style="color: #a6e3a1; font-weight:bold;">🎯 目標: {target}</span>
        </div>
        <div class="progress-track">
            <div class="target-line" style="left: {tgt_pct}%;"></div>
            <div class="progress-fill {fill_class}" style="width: {max(0, min(curr_pct, 100))}%;">
                {current}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 主程式
# ==========================================

# 狀態初始化
GameEngine.init_state()

st.title(f"🧩 分數拼湊大作戰 v3.1")
st.caption(f"Level {st.session_state.level}: {st.session_state.level_title}")

msg_type = st.session_state.get('msg_type', 'info')
if msg_type == 'success': st.success(st.session_state.msg)
elif msg_type == 'error': st.error(st.session_state.msg)
elif msg_type == 'warning': st.warning(st.session_state.msg)
else: st.info(st.session_state.msg)

render_progress_bar(st.session_state.current, st.session_state.target)

if st.session_state.game_status == 'playing':
    st.markdown("### 🎴 你的手牌")
    
    hand = st.session_state.hand
    if not hand:
        st.warning("手牌耗盡！")
        if st.button("🔄 重試本關"):
            GameEngine.start_level(st.session_state.level)
            st.rerun()
    else:
        cols = st.columns(4)
        for i, card in enumerate(hand):
            with cols[i % 4]:
                st.markdown(card.get_visual_html(), unsafe_allow_html=True)
                n, d = card.numerator, card.denominator
                label = f"{n}/{d}"
                if abs(n) >= d:
                    whole = int(n/d)
                    rem = abs(n) % d
                    if rem == 0: label = f"{whole}"
                    else: label = f"{whole}又{rem}/{d}"

                st.button(
                    label, 
                    key=f"btn_{card.id}", 
                    on_click=GameEngine.play_card_callback, 
                    args=(i,),
                    use_container_width=True
                )

    st.markdown("---")
    c1, c2 = st.columns([1, 4])
    with c1:
        st.button("↩️ 悔棋", on_click=GameEngine.undo_callback)

else:
    st.markdown("---")
    if st.session_state.game_status == 'won':
        st.balloons()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 重玩本關", use_container_width=True):
                GameEngine.start_level(st.session_state.level)
                st.rerun()
        with c2:
            if st.button("🚀 下一關", type="primary", use_container_width=True):
                GameEngine.start_level(st.session_state.level + 1)
                st.rerun()
    else:
        if st.button("🔄 再試一次", type="primary", use_container_width=True):
            GameEngine.start_level(st.session_state.level)
            st.rerun()

with st.sidebar:
    st.markdown("### 📘 數學之眼")
    st.markdown("""
    **帶分數視覺化 (Anti-Ghost Integer):**
    * 當分數大於 1 時，我們會畫出**完整的滿圓**，代表被忽略的整數。
    * 不要只看分數部分，整數也是運算的一部分！
    """)
    st.markdown(f"**目前數值:** `{st.session_state.current}`")
    st.markdown(f"**目標數值:** `{st.session_state.target}`")
