import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ==========================================
# 1. 配置與 CSS (Math-First Mobile Design)
# ==========================================
st.set_page_config(
    page_title="分數拼湊 v3.3", 
    page_icon="🧩", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 全局設定 */
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 儀表板容器 (題目區) */
    .dashboard-container {
        background: #313244;
        border-radius: 12px;
        padding: 16px;
        border: 2px solid #585b70;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* 算式顯示區 */
    .equation-box {
        background: #181825;
        color: #f9e2af;
        font-family: 'Courier New', monospace;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
        border: 1px dashed #45475a;
        font-size: 1.1rem;
    }

    /* 圓餅圖樣式 */
    .fraction-visual-container {
        display: flex;
        gap: 2px;
        align-items: center;
        justify-content: center;
        margin-bottom: 4px;
        flex-wrap: wrap;
    }
    .pie-chart {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: conic-gradient(#89b4fa var(--p), #45475a 0);
        border: 2px solid #cba6f7;
        flex-shrink: 0;
    }
    .pie-full {
        background: #89b4fa;
        border-color: #f9e2af;
        box-shadow: 0 0 3px rgba(249, 226, 175, 0.5);
    }
    .pie-negative {
        background: conic-gradient(#f38ba8 var(--p), #45475a 0);
        border-color: #f38ba8;
    }
    .pie-full-negative {
        background: #f38ba8;
        border-color: #eba0ac;
    }

    /* 按鈕優化 */
    div.stButton > button {
        background-color: #cba6f7 !important;
        color: #181825 !important;
        border-radius: 10px !important;
        font-size: 20px !important; /* 字體再加大 */
        font-weight: bold !important;
        padding: 12px 0 !important;
        width: 100%;
        border: 2px solid transparent !important;
    }
    div.stButton > button:active { transform: scale(0.96); }
    
    /* 進度條 */
    .progress-track {
        background: #45475a;
        height: 24px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        margin-top: 10px;
    }
    .progress-fill {
        height: 100%;
        transition: width 0.5s ease;
        background: linear-gradient(90deg, #89b4fa, #b4befe);
    }
    .fill-warning { background: linear-gradient(90deg, #f9e2af, #fab387); }
    .fill-danger { background: linear-gradient(90deg, #f38ba8, #eba0ac); }
    
    .target-line {
        position: absolute; top: 0; bottom: 0; width: 3px; background: #a6e3a1; z-index: 10;
        box-shadow: 0 0 8px #a6e3a1;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 數據模型
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
        display_integers = min(integer_part, 2) 
        for _ in range(display_integers):
            html += f'<div class="pie-chart {full_class}" style="--p: 100%;"></div>'
        if integer_part > 2:
            html += '<span style="font-size:14px; color:#f9e2af;">+..</span>'
        if fraction_part > 0:
            percent = float(fraction_part) * 100
            html += f'<div class="{pie_class}" style="--p: {percent}%;"></div>'
        html += '</div>'
        return html

# ==========================================
# 3. 核心引擎
# ==========================================

class GameEngine:
    @staticmethod
    def init_state():
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
        st.session_state.game_status = 'playing'
        st.session_state.level_title = title
        st.session_state.msg = "請湊出目標數值"
        st.session_state.msg_type = "info"

    @staticmethod
    def _generate_math_data(level: int):
        if level == 1: den_pool, steps, title = [2, 4], 2, "暖身"
        elif level == 2: den_pool, steps, title = [2, 3, 4, 6], 3, "通分"
        elif level == 3: den_pool, steps, title = [2, 4, 8], 3, "帶分數"
        elif level == 4: den_pool, steps, title = [2, 3, 4, 5], 4, "負數"
        else: den_pool, steps, title = [2, 3, 5, 7, 10], 5, "質數"

        target = Fraction(0, 1)
        hand = []
        for _ in range(steps):
            d = random.choice(den_pool)
            max_n = 4 if level >= 3 else 2 
            n = random.choice([x for x in range(1, max_n+1)])
            if level >= 4 and random.random() < 0.4: n = -n
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
            st.session_state.msg = "已悔棋"
            st.session_state.game_status = 'playing'

    @staticmethod
    def _check_win_condition():
        curr = st.session_state.current
        tgt = st.session_state.target
        if curr == tgt:
            st.session_state.game_status = 'won'
            st.session_state.msg = "成功！"
            st.session_state.msg_type = "success"
        elif curr > tgt:
            has_neg = any(c.numerator < 0 for c in st.session_state.hand)
            if not has_neg:
                st.session_state.game_status = 'lost'
                st.session_state.msg = "爆掉了！無牌可救"
                st.session_state.msg_type = "error"
            else:
                st.session_state.msg = "超過了！請用負數修正"
                st.session_state.msg_type = "warning"

# ==========================================
# 4. UI 渲染層 (Clear Math Dashboard)
# ==========================================

def render_dashboard(current: Fraction, target: Fraction):
    # 計算進度條百分比
    if target == 0: target = Fraction(1,1)
    max_val = max(target * Fraction(3, 2), current * Fraction(11, 10), Fraction(2, 1))
    curr_pct = float(current / max_val) * 100
    tgt_pct = float(target / max_val) * 100
    
    fill_class = "progress-fill"
    if current > target: fill_class += " fill-warning"
    if st.session_state.game_status == 'lost': fill_class += " fill-danger"

    # [修復重點]：這裡使用 LaTeX 顯示大大的數字，讓題目一目了然
    st.markdown(f"""
    <div class="dashboard-container">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <div style="text-align:center; width:45%;">
                <div style="color:#a6adc8; font-size:0.9rem;">🎯 目標 (Target)</div>
                <div style="font-size:1.8rem; font-weight:bold; color:#a6e3a1;">
                    {target}
                </div>
            </div>
            <div style="font-size:1.5rem; color:#585b70;">vs</div>
            <div style="text-align:center; width:45%;">
                <div style="color:#a6adc8; font-size:0.9rem;">⚗️ 當前 (Current)</div>
                <div style="font-size:1.8rem; font-weight:bold; color:#89b4fa;">
                    {current}
                </div>
            </div>
        </div>
        
        <div class="progress-track">
            <div class="target-line" style="left: {tgt_pct}%;"></div>
            <div class="{fill_class}" style="width: {max(0, min(curr_pct, 100))}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_equation_log():
    # [修復重點]：顯示算式，讓學生知道自己在算什麼
    history = st.session_state.played_history
    if not history:
        eq_text = "0 (起點)"
    else:
        parts = []
        for c in history:
            val_str = f"{c.numerator}/{c.denominator}"
            if c.numerator < 0: val_str = f"({val_str})"
            parts.append(val_str)
        eq_text = " + ".join(parts) + f" = {st.session_state.current}"
    
    st.markdown(f'<div class="equation-box">{eq_text}</div>', unsafe_allow_html=True)

# ==========================================
# 5. 主程式
# ==========================================

GameEngine.init_state()

# 標題區
st.markdown(f"#### 🧩 Lv.{st.session_state.level} {st.session_state.level_title}")

# 訊息提示
msg_type = st.session_state.get('msg_type', 'info')
if msg_type == 'success': st.success(st.session_state.msg)
elif msg_type == 'error': st.error(st.session_state.msg)
elif msg_type == 'warning': st.warning(st.session_state.msg)
else: st.info(st.session_state.msg)

# 1. 儀表板 (Dashboard) - 顯示題目
render_dashboard(st.session_state.current, st.session_state.target)

# 2. 算式區 (Equation) - 顯示過程
render_equation_log()

# 3. 操作區 (Hand)
if st.session_state.game_status == 'playing':
    hand = st.session_state.hand
    if not hand:
        st.warning("手牌耗盡")
        if st.button("🔄 重試", use_container_width=True):
            GameEngine.start_level(st.session_state.level)
            st.rerun()
    else:
        cols = st.columns(2)
        for i, card in enumerate(hand):
            with cols[i % 2]:
                st.markdown(card.get_visual_html(), unsafe_allow_html=True)
                n, d = card.numerator, card.denominator
                
                # 按鈕文字
                label = f"{n}/{d}"
                if abs(n) >= d:
                    whole = int(n/d)
                    rem = abs(n) % d
                    label = f"{whole}" if rem == 0 else f"{whole} {rem}/{d}"

                st.button(
                    label, 
                    key=f"btn_{card.id}", 
                    on_click=GameEngine.play_card_callback, 
                    args=(i,),
                    use_container_width=True
                )

    st.markdown("---")
    st.button("↩️ 悔棋 (Undo)", on_click=GameEngine.undo_callback, use_container_width=True)

else:
    # 結算區
    st.markdown("---")
    if st.session_state.game_status == 'won':
        st.balloons()
        if st.button("🚀 下一關", type="primary", use_container_width=True):
            GameEngine.start_level(st.session_state.level + 1)
            st.rerun()
        if st.button("🔄 重玩本關", use_container_width=True):
            GameEngine.start_level(st.session_state.level)
            st.rerun()
    else:
        if st.button("🔄 再試一次", type="primary", use_container_width=True):
            GameEngine.start_level(st.session_state.level)
            st.rerun()

# 底部摺疊說明
with st.expander("📘 規則說明"):
    st.markdown("""
    1. **看上面:** 左邊是目標，右邊是你目前的總和。
    2. **選卡片:** 點擊下方卡片，把它們加起來。
    3. **湊數字:** 想辦法讓左右兩個數字一樣！
    """)
