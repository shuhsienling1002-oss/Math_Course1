import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple

# ==========================================
# 1. 頁面設定與 CSS (View Layer)
# ==========================================
st.set_page_config(page_title="零熵分數挑戰", page_icon="🧩", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    
    /* 遊戲區塊容器 */
    .game-container {
        background: #313244;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 2px solid #45475a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* 進度條背景 */
    .progress-track {
        background: #45475a;
        height: 24px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        margin: 20px 0;
    }
    
    /* 進度條本身 */
    .progress-fill {
        background: linear-gradient(90deg, #89b4fa, #74c7ec);
        height: 100%;
        transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    /* 目標標記 */
    .target-marker {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: #f38ba8;
        z-index: 10;
        box-shadow: 0 0 10px #f38ba8;
    }

    /* 卡片按鈕優化 */
    div.stButton > button {
        background-color: #cba6f7 !important;
        color: #181825 !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        transition: all 0.2s !important;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(203, 166, 247, 0.4);
    }
    div.stButton > button:active {
        transform: translateY(1px);
    }
    
    /* 狀態訊息 */
    .status-msg {
        font-size: 1.2rem;
        text-align: center;
        font-weight: bold;
        color: #f9e2af;
        margin-bottom: 10px;
    }
    
    /* 數學推導區塊優化 */
    .math-steps {
        background-color: #313244;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #89b4fa;
        margin-top: 15px;
        font-family: 'Courier New', monospace;
        color: #cdd6f4;
        line-height: 1.6;
    }
    .math-step-title {
        font-weight: bold;
        color: #f9e2af;
        margin-bottom: 5px;
        display: block;
        font-size: 1.1rem;
    }
    .math-list {
        margin: 5px 0 15px 20px;
        padding: 0;
    }
    /* 讓 MathJax 公式有足夠空間 */
    .katex-display {
        margin: 10px 0 !important;
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
    id: int = field(default_factory=lambda: random.randint(10000, 99999))

    @property
    def value(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    @property
    def display(self) -> str:
        return f"{self.numerator}/{self.denominator}"

    def __repr__(self):
        return self.display

# ==========================================
# 3. 核心引擎 (Game Engine) - 縮排修正版 v2.4
# ==========================================

class GameEngine:
    def __init__(self):
        required_keys = ['level', 'target', 'current', 'hand', 'msg', 'game_state', 'feedback_header', 'math_log', 'correct_hand_cache']
        if any(key not in st.session_state for key in required_keys):
            self.reset_game()
    
    @property
    def level(self): return st.session_state.get('level', 1)
    @property
    def target(self): return st.session_state.get('target', Fraction(1, 1))
    @property
    def current(self): return st.session_state.get('current', Fraction(0, 1))
    @property
    def hand(self): return st.session_state.get('hand', [])
    @property
    def message(self): return st.session_state.get('msg', "系統載入中...")
    @property
    def state(self): return st.session_state.get('game_state', 'playing')
    @property
    def feedback_header(self): return st.session_state.get('feedback_header', "")
    @property
    def math_log(self): return st.session_state.get('math_log', "")

    def reset_game(self):
        st.session_state.level = 1
        self.start_level(1)

    def start_level(self, level: int):
        st.session_state.level = level
        target, start_val, hand, correct_subset = self._generate_math_data(level)
        
        st.session_state.target = target
        st.session_state.current = start_val
        st.session_state.hand = hand
        st.session_state.correct_hand_cache = correct_subset
        
        st.session_state.game_state = 'playing'
        st.session_state.msg = f"⚔️ 第 {level} 關: 尋找平衡點！"
        st.session_state.feedback_header = "" 
        st.session_state.math_log = ""

    def _generate_math_data(self, level: int) -> Tuple[Fraction, Fraction, List[Card], List[Card]]:
        if level == 1: den_pool = [2, 4]
        elif level == 2: den_pool = [2, 3, 4, 6]
        elif level <= 5: den_pool = [2, 3, 4, 5, 8]
        else: den_pool = [3, 6, 7, 9, 12]

        target_val = Fraction(0, 1)
        correct_hand = []
        steps = random.randint(2, 3 + (level // 3))
        
        for _ in range(steps):
            d = random.choice(den_pool)
            n = random.choice([1, 1, 2])
            card = Card(n, d)
            correct_hand.append(card)
            target_val += card.value

        target = target_val
        current = Fraction(0, 1)

        distractor_count = random.randint(1, 2)
        distractors = []
        for _ in range(distractor_count):
            d = random.choice(den_pool)
            n = random.choice([1, 2])
            distractors.append(Card(n, d))
            
        final_hand = correct_hand + distractors
        random.shuffle(final_hand)
        
        return target, current, final_hand, correct_hand

    def play_card(self, card_idx: int):
        if self.state != 'playing': return
        if not st.session_state.get('hand') or card_idx >= len(st.session_state.hand): return

        card = st.session_state.hand.pop(card_idx)
        st.session_state.current += card.value
        self._check_win_condition()

    def _check_win_condition(self):
        curr = st.session_state.get('current', Fraction(0, 1))
        tgt = st.session_state.get('target', Fraction(1, 1))
        
        if curr == tgt:
            self._trigger_end_game('won')
        elif curr > tgt:
            self._trigger_end_game('lost_over')
        elif not st.session_state.get('hand', []):
            self._trigger_end_game('lost_empty')
        else:
            diff = tgt - curr
            st.session_state.msg = f"🚀 推進中... 還差 {diff}"

    def _trigger_end_game(self, status):
        st.session_state.game_state = 'won' if status == 'won' else 'lost'
        
        if status == 'won':
            st.session_state.msg = "🎉 完美平衡！"
            st.session_state.feedback_header = "✅ 驗算成功！你找到了正確的組合。"
        elif status == 'lost_over':
            st.session_state.msg = "💥 能量過載！"
            st.session_state.feedback_header = "❌ 誤差分析：總和超過了目標。"
        elif status == 'lost_empty':
            st.session_state.msg = "💀 資源耗盡！"
            st.session_state.feedback_header = "❌ 誤差分析：手牌用盡但未達目標。"

        st.session_state.math_log = self._generate_step_by_step_solution(st.session_state.correct_hand_cache)

    def _generate_step_by_step_solution(self, cards: List[Card]) -> str:
        """
        生成 HTML 格式的解題步驟
        關鍵修正：移除所有 f-string 內部的縮排，防止 Markdown 誤判為代碼區塊
        """
        if not cards: return "無解"
        
        denoms = [c.denominator for c in cards]
        lcm = denoms[0]
        for d in denoms[1:]:
            lcm = (lcm * d) // math.gcd(lcm, d)
            
        expansion_items = ""
        numerators_sum_str = []
        total_numerator = 0
        
        for c in cards:
            factor = lcm // c.denominator
            expanded_num = c.numerator * factor
            total_numerator += expanded_num
            
            if factor > 1:
                expansion_items += f"<li><b>{c.display}</b> 擴分 (×{factor}) → <b>{expanded_num}/{lcm}</b></li>"
            else:
                expansion_items += f"<li><b>{c.display}</b> (無需擴分) → <b>{expanded_num}/{lcm}</b></li>"
            
            numerators_sum_str.append(str(expanded_num))
            
        # 注意：這裡的 HTML 字串全部靠左對齊，不要縮排！
        html = f"""
<div class="math-steps">
<span class="math-step-title">Step 1: 尋找公分母</span>
<div style="margin-left: 20px;">
分母 {denoms} 的最小公倍數是 <b>{lcm}</b>。
</div>
<br>
<span class="math-step-title">Step 2: 通分變形</span>
<ul class="math-list">
{expansion_items}
</ul>
<span class="math-step-title">Step 3: 分子加總</span>
<div style="margin-left: 20px;">
$$ \\frac{{{' + '.join(numerators_sum_str)}}}{{{lcm}}} = \\frac{{{total_numerator}}}{{{lcm}}} $$
</div>
"""
        
        final_frac = Fraction(total_numerator, lcm)
        if final_frac.denominator != lcm:
            # 這裡也必須靠左對齊，不能因為在 if 裡面就縮排
            html += f"""
<br>
<span class="math-step-title">Step 4: 約分 (最終答案)</span>
<div style="margin-left: 20px;">
$$ \\frac{{{total_numerator}}}{{{lcm}}} = {final_frac.numerator}/{final_frac.denominator} $$
</div>
"""
        
        html += "</div>"
        return html

    def next_level(self):
        self.start_level(self.level + 1)

    def retry_level(self):
        self.start_level(self.level)

# ==========================================
# 4. UI 渲染層 (View Layer)
# ==========================================

engine = GameEngine()

st.title(f"🧩 零熵分數挑戰")
st.markdown(f"<div class='status-msg'>{engine.message}</div>", unsafe_allow_html=True)

# 1. 視覺化軌道
target_val = engine.target if engine.target > 0 else Fraction(1, 1)
max_val = max(target_val * Fraction(3, 2), Fraction(2, 1)) 

curr_pct = min((engine.current / max_val) * 100, 100)
tgt_pct = (engine.target / max_val) * 100

html_content = f"""
<div class="game-container">
<div style="display: flex; justify-content: space-between; font-family: monospace;">
<span>🏁 起點: 0</span>
<span>🚩 目標: {engine.target}</span>
</div>
<div class="progress-track">
<div class="target-marker" style="left: {float(tgt_pct)}%;"></div>
<div class="progress-fill" style="width: {float(curr_pct)}%;"></div>
</div>
<div style="text-align: center; font-size: 24px; font-weight: bold;">
當前總和: <span style="color: #89b4fa;">{engine.current}</span>
</div>
</div>
"""
st.markdown(html_content, unsafe_allow_html=True)

# 2. 遊戲互動區
if engine.state == 'playing':
    st.write("### 🎴 你的策略手牌")
    if engine.hand:
        cols = st.columns(len(engine.hand))
        for i, card in enumerate(engine.hand):
            with cols[i]:
                if st.button(f"{card.display}", key=f"btn_{card.id}", help=f"值約為 {float(card.value):.2f}"):
                    engine.play_card(i)
                    st.rerun()
    else:
        st.info("手牌已空，正在結算...")

else:
    # --- 遊戲結束結算區 ---
    st.markdown("---")
    
    # 1. 狀態條
    if engine.state == 'won':
        st.success(engine.feedback_header)
    else:
        st.error(engine.feedback_header)
    
    # 2. 數學推導
    st.markdown(engine.math_log, unsafe_allow_html=True)
    
    # 操作按鈕
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if engine.state == 'won':
            if st.button("🚀 進入下一層維度 (Next Level)", type="primary", use_container_width=True):
                engine.next_level()
                st.rerun()
        else:
            if st.button("🔄 重置時間線 (Retry)", type="secondary", use_container_width=True):
                engine.retry_level()
                st.rerun()

# 3. 側邊欄
with st.sidebar:
    st.markdown("### 📊 遊戲數據")
    st.write(f"當前關卡: **{engine.level}**")
    st.progress(min(engine.level / 10, 1.0))
    
    st.markdown("---")
    st.markdown("""
    **玩法說明 (Zero-Entropy):**
    1. **目標**: 讓藍色進度條剛好停在粉紅線上。
    2. **陷阱**: 手牌中混有「雜訊牌」，全部打出會爆掉！
    3. **策略**: 計算並選擇正確的組合 (納什均衡)。
    """)
