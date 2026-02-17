import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ==========================================
# 1. 配置與 CSS (Mobile First)
# ==========================================
st.set_page_config(
    page_title="分數拼湊 v3.2", 
    page_icon="🧩", 
    layout="centered",
    initial_sidebar_state="collapsed" # 強制隱藏側邊欄
)

st.markdown("""
<style>
    /* 全局設定 - 手機版適配 */
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    
    /* 隱藏 Streamlit 預設漢堡選單與Footer，爭取空間 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 遊戲容器 - 減少內距以適應窄螢幕 */
    .game-container {
        background: #313244;
        border-radius: 12px;
        padding: 16px;
        border: 2px solid #45475a;
        margin-bottom: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* 視覺化容器 */
    .fraction-visual-container {
        display: flex;
        gap: 2px;
        align-items: center;
        justify-content: center;
        margin-bottom: 4px;
        flex-wrap: wrap; /* 允許換行，防止爆版 */
    }
    
    /* 圓餅圖縮小一點適應手機 */
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

    /* 按鈕優化 - 更大的觸控區 */
    div.stButton > button {
        background-color: #cba6f7 !important;
        color: #181825 !important;
        border-radius: 10px !important;
        font-size: 18px !important; /* 字體加大 */
        font-weight: bold !important;
        padding: 12px 0 !important; /* 增加高度 */
        width: 100%;
        border: 2px solid transparent !important;
        transition: transform 0.1s;
    }
    div.stButton > button:active {
        transform: scale(0.95);
    }
    
    /* 進度條 */
    .progress-track {
        background: #45475a;
        height: 30px;
        border-radius: 15px;
        position: relative;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-fill {
        height: 100%;
        transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        display: flex;
        align-items: center;
        justify-content: flex-end;
        padding-right: 8px;
        font-size: 12px;
        font-weight: 800;
        color: #181825;
    }
    .fill-normal { background: linear-gradient(90deg, #89b4fa, #b4befe); }
    .fill-warning { background: linear-gradient(90deg, #f9e2af, #fab387); }
    .fill-danger { background: linear-gradient(90deg, #f38ba8, #eba0ac); }
    
    .target-line {
        position: absolute;
        top: 0; bottom: 0;
        width: 3px;
        background: #a6e3a1;
        z-index: 10;
        box-shadow: 0 0 8px #a6e3a1;
    }
    
    /* 數值面板 */
    .stats-panel {
        display: flex; 
        justify-content: space-between; 
        font-family: monospace; 
        font-size: 1rem;
        padding: 0 4px;
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
        
        # 限制手機版最多顯示 2 個滿圓，超過用 +...
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
# 3. 核心引擎 (Logic Layer)
# ==========================================

class GameEngine:
    
    @staticmethod
    def init_state():
        # [安全檢查] 確保 game_status 存在
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
        st.session_state.msg = "點擊卡片湊數值"
        st.session_state.msg_type = "info"

    @staticmethod
    def _generate_math_data(level: int):
        if level == 1:
            den_pool, steps, title = [2, 4], 2, "暖身：簡單同分母"
        elif level == 2:
            den_pool, steps, title = [2, 3, 4, 6], 3, "進階：通分挑戰"
        elif level == 3:
            den_pool, steps, title = [2, 4, 8], 3, "挑戰：帶分數與整數"
        elif level == 4:
            den_pool, steps, title = [2, 3, 4, 5], 4, "大師：負數逆流"
        else:
            den_pool, steps, title = [2, 3, 5, 7, 10], 5, "傳說：質數地獄"

        target = Fraction(0, 1)
        hand = []
        
        for _ in range(steps):
            d = random.choice(den_pool)
            max_n = 4 if level >= 3 else 2 
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
            st.session_state.msg = "↩️ 已悔棋"
            st.session_state.msg_type = "info"
            st.session_state.game_status = 'playing'

    @staticmethod
    def _check_win_condition():
        curr = st.session_state.current
        tgt = st.session_state.target
        
        if curr == tgt:
            st.session_state.game_status = 'won'
            st.session_state.msg = "🎉 成功！"
            st.session_state.msg_type = "success"
        elif curr > tgt:
            has_negative = any(c.numerator < 0 for c in st.session_state.hand)
            if not has_negative:
                st.session_state.game_status = 'lost'
                st.session_state.msg = "💥 爆掉了！無牌可救。"
                st.session_state.msg_type = "error"
            else:
                st.session_state.msg = "⚠️ 超過了！快用負數！"
                st.session_state.msg_type = "warning"

# ==========================================
# 4. UI 渲染層 (Mobile Optimized)
# ==========================================

def render_progress_bar(current: Fraction, target: Fraction):
    if target == 0: target = Fraction(1,1)
    max_val = max(target * Fraction(3, 2), current * Fraction(11, 10), Fraction(2, 1))
    
    curr_pct = float(current / max_val) * 100
    tgt_pct = float(target / max_val) * 100
    
    fill_class = "fill-normal"
    if current > target: fill_class = "fill-warning"
    
    status = st.session_state.get('game_status', 'playing')
    if status == 'lost': fill_class = "fill-danger"

    st.markdown(f"""
    <div class="game-container">
        <div class="stats-panel">
            <span>🏁 Start</span>
            <span style="color: #a6e3a1; font-weight:bold;">🎯 {target}</span>
        </div>
        <div class="progress-track">
            <div class="target-line" style="left: {tgt_pct}%;"></div>
            <div class="progress-fill {fill_class}" style="width: {max(0, min(curr_pct, 100))}%;">
                {current}
            </div>
        </div>
        <div class="stats-panel" style="justify-content: flex-end; font-size: 0.9em; color: #b4befe;">
            <span>目前: {current}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. 主程式
# ==========================================

GameEngine.init_state()

# 簡潔的標題
st.markdown(f"### 🧩 Lv.{st.session_state.level} {st.session_state.level_title}")

# 訊息提示 (精簡版)
msg_type = st.session_state.get('msg_type', 'info')
if msg_type == 'success': st.success(st.session_state.msg)
elif msg_type == 'error': st.error(st.session_state.msg)
elif msg_type == 'warning': st.warning(st.session_state.msg)
else: st.info(st.session_state.msg)

render_progress_bar(st.session_state.current, st.session_state.target)

if st.session_state.game_status == 'playing':
    hand = st.session_state.hand
    if not hand:
        st.warning("手牌耗盡")
        if st.button("🔄 重試", use_container_width=True):
            GameEngine.start_level(st.session_state.level)
            st.rerun()
    else:
        # [手機優化]: 改為 2 欄佈局，按鈕更大，更好點
        cols = st.columns(2)
        for i, card in enumerate(hand):
            with cols[i % 2]:
                st.markdown(card.get_visual_html(), unsafe_allow_html=True)
                n, d = card.numerator, card.denominator
                
                # 簡化標籤顯示
                label = f"{n}/{d}"
                if abs(n) >= d:
                    whole = int(n/d)
                    rem = abs(n) % d
                    if rem == 0: label = f"{whole}"
                    else: label = f"{whole} {rem}/{d}"

                st.button(
                    label, 
                    key=f"btn_{card.id}", 
                    on_click=GameEngine.play_card_callback, 
                    args=(i,),
                    use_container_width=True
                )

    st.markdown("---")
    # 悔棋按鈕全寬
    st.button("↩️ 悔棋 (Undo)", on_click=GameEngine.undo_callback, use_container_width=True)

else:
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

# [手機優化]: 將側邊欄內容移到底部摺疊區
with st.expander("📘 數學之眼 (Math Tips)"):
    st.markdown("""
    * **滿圓代表整數:** 當你看到滿的圓圈，代表這張牌大於 1。
    * **紅色代表負數:** 用來倒退進度。
    * **目標:** 讓你的進度條精準停在綠線。
    """)
    st.caption(f"Target: {st.session_state.target} | Current: {st.session_state.current}")
