import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from itertools import combinations

# ==========================================
# 1. 配置與 CSS
# ==========================================
st.set_page_config(
    page_title="分數拼湊 v3.5", 
    page_icon="🧩", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .dashboard-container {
        background: #313244;
        border-radius: 12px;
        padding: 16px;
        border: 2px solid #585b70;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
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

    .fraction-visual-container {
        display: flex; gap: 2px; align-items: center; justify-content: center;
        margin-bottom: 4px; flex-wrap: wrap;
    }
    .pie-chart {
        width: 28px; height: 28px; border-radius: 50%;
        background: conic-gradient(#89b4fa var(--p), #45475a 0);
        border: 2px solid #cba6f7; flex-shrink: 0;
    }
    .pie-full { background: #89b4fa; border-color: #f9e2af; }
    .pie-negative { background: conic-gradient(#f38ba8 var(--p), #45475a 0); border-color: #f38ba8; }
    .pie-full-negative { background: #f38ba8; border-color: #eba0ac; }

    div.stButton > button {
        background-color: #cba6f7 !important; color: #181825 !important;
        border-radius: 10px !important; font-size: 20px !important;
        font-weight: bold !important; padding: 12px 0 !important; width: 100%;
        border: 2px solid transparent !important;
    }
    div.stButton > button:active { transform: scale(0.96); }
    
    .progress-track {
        background: #45475a; height: 24px; border-radius: 12px;
        position: relative; overflow: hidden; margin-top: 10px;
    }
    .progress-fill { height: 100%; transition: width 0.5s ease; background: linear-gradient(90deg, #89b4fa, #b4befe); }
    .fill-warning { background: linear-gradient(90deg, #f9e2af, #fab387); }
    .fill-danger { background: linear-gradient(90deg, #f38ba8, #eba0ac); }
    .target-line { position: absolute; top: 0; bottom: 0; width: 3px; background: #a6e3a1; z-index: 10; }
    
    /* 提示與狀態樣式 */
    .status-badge {
        display: inline-block; padding: 4px 8px; border-radius: 4px;
        font-size: 0.8rem; font-weight: bold; margin-bottom: 8px;
    }
    .status-ok { background: rgba(166, 227, 161, 0.2); color: #a6e3a1; border: 1px solid #a6e3a1; }
    .status-dead { background: rgba(243, 139, 168, 0.2); color: #f38ba8; border: 1px solid #f38ba8; }
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
        
        html_content = ""
        display_integers = min(integer_part, 2) 
        for _ in range(display_integers):
            html_content += f'<div class="pie-chart {full_class}" style="--p: 100%;"></div>'
        if integer_part > 2:
            html_content += '<span style="font-size:14px; color:#f9e2af;">+..</span>'
        if fraction_part > 0:
            percent = float(fraction_part) * 100
            html_content += f'<div class="{pie_class}" style="--p: {percent}%;"></div>'

        return f'<div class="fraction-visual-container">{html_content}</div>'

# ==========================================
# 3. 核心引擎 (Smart Logic)
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
        target, start_val, hand, title = GameEngine._generate_smart_math(level)
        st.session_state.target = target
        st.session_state.current = start_val
        st.session_state.hand = hand
        st.session_state.played_history = []
        st.session_state.game_status = 'playing'
        st.session_state.level_title = title
        st.session_state.msg = "請湊出目標數值"
        st.session_state.msg_type = "info"
        st.session_state.solvable = True # 初始狀態一定可解

    @staticmethod
    def _generate_smart_math(level: int):
        # [Model 13: 複雜適應系統] - 分組相容池，避免醜陋通分
        pools = {
            1: {'dens': [2, 4], 'target': Fraction(1, 1), 'count': 3, 'neg': False},     # 二進位組
            2: {'dens': [2, 3, 6], 'target': Fraction(1, 1), 'count': 3, 'neg': False},  # 六進位組
            3: {'dens': [2, 4, 8], 'target': Fraction(2, 1), 'count': 4, 'neg': True},   # 帶分數
            4: {'dens': [2, 5, 10], 'target': Fraction(0, 1), 'count': 4, 'neg': True},  # 十進位/負數
            5: {'dens': [3, 4, 6], 'target': Fraction(1, 1), 'count': 5, 'neg': True}    # 質數混合 (移除 7 以降低難度)
        }
        cfg = pools.get(level, pools[5])
        
        # [Model 10: 奧卡姆剃刀] - 先定目標，再反推手牌，保證目標乾淨
        target_val = cfg['target']
        correct_hand = []
        
        # 隨機生成 N-1 張牌
        current_sum = Fraction(0, 1)
        for _ in range(cfg['count'] - 1):
            d = random.choice(cfg['dens'])
            n = random.choice([1, 2, 3])
            if cfg['neg'] and random.random() < 0.4: n = -n
            card = Card(n, d)
            correct_hand.append(card)
            current_sum += card.value
            
        # 計算最後一張牌 (補數)，確保總和等於 Target
        needed = target_val - current_sum
        
        # 如果最後一張牌太醜 (例如分母變成 17)，重試生成
        # 這裡我們簡化：直接把 needed 變成一張牌。
        # 為了保證 needed 是合法卡片 (分母在池中)，我們可能需要簡單的通分檢查
        # 但為了遊戲性，我們先直接允許這張「關鍵牌」出現，不管分母是否完美，至少保證數學正確。
        
        # 優化顯示：如果 needed 分母太大，嘗試約分
        # Fraction 自動約分，所以我們只需要檢查分母是否合理 (比如 < 20)
        # 如果 needed 分母太大，說明前面隨機得太爛，遞迴重試
        if needed.denominator > 20 or abs(needed.numerator) > 10:
            return GameEngine._generate_smart_math(level) # 重來
            
        last_card = Card(needed.numerator, needed.denominator)
        correct_hand.append(last_card)
        
        # 加入干擾牌
        distractors = []
        d_count = 2
        for _ in range(d_count):
            d = random.choice(cfg['dens'])
            n = random.choice([1, 2])
            if cfg['neg'] and random.random() < 0.5: n = -n
            distractors.append(Card(n, d))
            
        hand = correct_hand + distractors
        random.shuffle(hand)
        
        # 生成標題
        title_map = {
            1: "暖身：二分之一的世界",
            2: "通分：2, 3, 6 的關係",
            3: "進階：湊出整數 2",
            4: "歸零：正負抵銷",
            5: "挑戰：混合運算"
        }
        
        return target_val, Fraction(0, 1), hand, title_map.get(level, "挑戰")

    @staticmethod
    def check_solvability():
        """
        [Model 11: 回饋迴路] 死路檢測器
        檢查當前手牌是否還能組出目標
        """
        target = st.session_state.target
        current = st.session_state.current
        hand = st.session_state.hand
        
        needed = target - current
        
        # 窮舉所有子集 (手牌數很少，效能沒問題)
        vals = [c.value for c in hand]
        possible = False
        
        # 檢查 0 到全部長度的組合
        for r in range(len(vals) + 1):
            for subset in combinations(vals, r):
                if sum(subset) == needed:
                    possible = True
                    # 找到解了，可以順便存下來做提示
                    st.session_state.hint_card_val = subset[0] if subset else None
                    break
            if possible: break
            
        st.session_state.solvable = possible
        if not possible and st.session_state.game_status == 'playing':
            st.session_state.msg = "⚠️ 此路不通！請悔棋"
            st.session_state.msg_type = "error"

    @staticmethod
    def play_card_callback(card_idx: int):
        hand = st.session_state.hand
        if 0 <= card_idx < len(hand):
            card = hand.pop(card_idx)
            st.session_state.current += card.value
            st.session_state.played_history.append(card)
            
            GameEngine.check_solvability() # 每次出牌都檢查死活
            GameEngine._check_win_condition()

    @staticmethod
    def undo_callback():
        if st.session_state.played_history:
            card = st.session_state.played_history.pop()
            st.session_state.current -= card.value
            st.session_state.hand.append(card)
            st.session_state.msg = "已悔棋"
            st.session_state.msg_type = "info"
            st.session_state.game_status = 'playing'
            GameEngine.check_solvability()

    @staticmethod
    def hint_callback():
        # 簡單提示：告訴玩家手牌中哪一張是正解的一部分
        if hasattr(st.session_state, 'hint_card_val') and st.session_state.hint_card_val:
            val = st.session_state.hint_card_val
            for c in st.session_state.hand:
                if c.value == val:
                    st.session_state.msg = f"💡 提示：試試看 {c.numerator}/{c.denominator}"
                    st.session_state.msg_type = "info"
                    break
        else:
             st.session_state.msg = "💡 提示：請先悔棋，目前無解"

    @staticmethod
    def _check_win_condition():
        curr = st.session_state.current
        tgt = st.session_state.target
        if curr == tgt:
            st.session_state.game_status = 'won'
            st.session_state.msg = "成功！"
            st.session_state.msg_type = "success"

# ==========================================
# 4. UI 渲染層
# ==========================================

def render_dashboard(current: Fraction, target: Fraction):
    if target == 0: target = Fraction(1,1) # 避免除零
    max_val = max(target * Fraction(3, 2), current * Fraction(11, 10), Fraction(2, 1))
    
    # 避免 max_val 為 0
    if max_val == 0: max_val = Fraction(1,1)

    curr_pct = float(current / max_val) * 100
    tgt_pct = float(target / max_val) * 100
    
    fill_class = "progress-fill"
    if current > target: fill_class += " fill-warning"
    status = st.session_state.get('game_status', 'playing')
    if status == 'lost': fill_class += " fill-danger"

    # 狀態標籤
    solvable = st.session_state.get('solvable', True)
    status_html = ""
    if not solvable and status == 'playing':
        status_html = '<div class="status-badge status-dead">⚠️ 死局 (Dead End)</div>'
    else:
        status_html = '<div class="status-badge status-ok">✅ 路徑通暢 (Solvable)</div>'

    html = f"""
<div class="dashboard-container">
    {status_html}
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
"""
    st.markdown(html, unsafe_allow_html=True)

def render_equation_log():
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

st.markdown(f"#### 🧩 Lv.{st.session_state.level} {st.session_state.level_title}")

msg_type = st.session_state.get('msg_type', 'info')
if msg_type == 'success': st.success(st.session_state.msg)
elif msg_type == 'error': st.error(st.session_state.msg)
elif msg_type == 'warning': st.warning(st.session_state.msg)
else: st.info(st.session_state.msg)

render_dashboard(st.session_state.current, st.session_state.target)
render_equation_log()

if st.session_state.game_status == 'playing':
    hand = st.session_state.hand
    if not hand:
        # 手牌空了但沒贏
        st.error("手牌耗盡！請重試")
        if st.button("🔄 重試", use_container_width=True):
            GameEngine.start_level(st.session_state.level)
            st.rerun()
    else:
        cols = st.columns(2)
        for i, card in enumerate(hand):
            with cols[i % 2]:
                st.markdown(card.get_visual_html(), unsafe_allow_html=True)
                n, d = card.numerator, card.denominator
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
    c1, c2 = st.columns(2)
    with c1:
        st.button("↩️ 悔棋", on_click=GameEngine.undo_callback, use_container_width=True)
    with c2:
        st.button("💡 提示", on_click=GameEngine.hint_callback, use_container_width=True)

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

with st.expander("📘 規則與除錯"):
    st.markdown("""
    * **死局檢測:** 如果看到「⚠️ 死局」，表示剩下的牌怎麼湊都湊不出目標了，請按悔棋。
    * **目標鎖定:** 本版本保證目標是乾淨的數字 (如 1 或 2)，不會出現 8/105 這種怪物。
    """)
