import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple

# ==========================================
# 1. 頁面設定與 CSS (View Layer)
# ==========================================
st.set_page_config(page_title="分數拼湊大作戰", page_icon="🧩", layout="centered")

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
    /* 結果高亮 */
    .result-box {
        background: #45475a;
        padding: 10px 15px;
        border-radius: 8px;
        display: inline-block;
        font-weight: bold;
        color: #a6e3a1;
        font-size: 1.2rem;
        margin-top: 5px;
    }
    
    /* 正確手牌展示區 */
    .correct-hand-box {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .mini-card {
        background-color: #cba6f7;
        color: #181825;
        padding: 5px 15px;
        border-radius: 6px;
        font-weight: bold;
        font-family: monospace;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .mini-card.negative {
        background-color: #f38ba8; /* 紅色背景表示負數 */
        color: #181825;
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
    def is_negative(self) -> bool:
        return self.numerator < 0

    @property
    def display(self) -> str:
        # 顯示時加上正負號圖示
        icon = "🟥" if self.is_negative else "🟦"
        return f"{icon} {self.numerator}/{self.denominator}"
    
    @property
    def raw_display(self) -> str:
        # 純文字顯示 (用於數學計算區)
        return f"{self.numerator}/{self.denominator}"

    def __repr__(self):
        return self.display

# ==========================================
# 3. 核心引擎 (Game Engine) - 負數增強版 v3.1
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
        
        # 嘗試生成直到目標大於 0 (避免負目標導致進度條壞掉)
        while True:
            target, start_val, hand, correct_subset = self._generate_math_data(level)
            if target > 0:
                break
        
        st.session_state.target = target
        st.session_state.current = start_val
        st.session_state.hand = hand
        st.session_state.correct_hand_cache = correct_subset
        
        st.session_state.game_state = 'playing'
        
        if level >= 3:
            st.session_state.msg = f"⚔️ 第 {level} 關: 小心！出現負數牌了 (🟥)"
        else:
            st.session_state.msg = f"⚔️ 第 {level} 關: 目標是湊出指定分數！"
            
        st.session_state.feedback_header = "" 
        st.session_state.math_log = ""

    def _generate_math_data(self, level: int) -> Tuple[Fraction, Fraction, List[Card], List[Card]]:
        # 難度設定
        if level == 1: den_pool = [2, 4]
        elif level == 2: den_pool = [2, 3, 4, 6]
        elif level <= 5: den_pool = [2, 3, 4, 5, 8]
        else: den_pool = [3, 6, 7, 9, 12]

        target_val = Fraction(0, 1)
        correct_hand = []
        steps = random.randint(2, 3 + (level // 3))
        
        # 是否允許負數 (Level 3 開始)
        allow_negative = level >= 3
        
        # 1. 先生產正確答案
        for _ in range(steps):
            d = random.choice(den_pool)
            n = random.choice([1, 1, 2])
            
            # 30% 機率變成負數
            if allow_negative and random.random() < 0.3:
                n = -n
                
            card = Card(n, d)
            correct_hand.append(card)
            target_val += card.value

        target = target_val
        current = Fraction(0, 1)

        # 2. 混入干擾牌
        distractor_count = random.randint(1, 2)
        distractors = []
        for _ in range(distractor_count):
            d = random.choice(den_pool)
            n = random.choice([1, 2])
            
            # 干擾牌也有可能是負數
            if allow_negative and random.random() < 0.4:
                n = -n
                
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
        # 注意：有負數時，超過目標不代表輸了，因為可以減回來！
        # 只有當手牌用完且未達目標時才算輸。
        elif not st.session_state.get('hand', []):
            self._trigger_end_game('lost_empty')
        else:
            diff = tgt - curr
            st.session_state.msg = f"🚀 計算中... 距離目標還差 {diff}"

    def _trigger_end_game(self, status):
        st.session_state.game_state = 'won' if status == 'won' else 'lost'
        
        if status == 'won':
            st.session_state.msg = "🎉 挑戰成功！"
            st.session_state.feedback_header = "✅ 太棒了！正負抵銷後剛好命中！"
        elif status == 'lost_empty':
            st.session_state.msg = "💀 牌用光了！"
            st.session_state.feedback_header = "❌ 牌都出完了，但還沒湊到目標。"

        st.session_state.math_log = self._generate_step_by_step_solution(st.session_state.correct_hand_cache)

    def _generate_step_by_step_solution(self, cards: List[Card]) -> str:
        """
        生成 HTML 格式的解題步驟 (支援負數括號顯示)
        """
        if not cards: return "無解"
        
        # 生成正確手牌的 HTML 區塊 (區分顏色)
        hand_html = ""
        for c in cards:
            css_class = "mini-card negative" if c.is_negative else "mini-card"
            hand_html += f'<div class="{css_class}">{c.raw_display}</div>'
        
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
            
            # 顯示邏輯：如果是負數，加上括號
            display_num = f"({expanded_num})" if expanded_num < 0 else str(expanded_num)
            
            if factor > 1:
                expansion_items += f"<li><b>{c.raw_display}</b> 擴分 (×{factor}) → <b>{expanded_num}/{lcm}</b></li>"
            else:
                expansion_items += f"<li><b>{c.raw_display}</b> (無需擴分) → <b>{expanded_num}/{lcm}</b></li>"
            
            numerators_sum_str.append(display_num)
            
        # 構建 HTML 字串
        html = f"""
<div class="math-steps">
<span class="math-step-title">💡 正確的卡牌組合是：</span>
<div class="correct-hand-box">
{hand_html}
</div>
<hr style="border-color: #45475a; margin: 15px 0;">

<span class="math-step-title">Step 1: 找分母的最小公倍數</span>
<div style="margin-left: 20px;">
分母 {denoms} 的最小公倍數是 <b>{lcm}</b>。
</div>
<br>
<span class="math-step-title">Step 2: 通分 (把分母變一樣)</span>
<ul class="math-list">
{expansion_items}
</ul>
<span class="math-step-title">Step 3: 分子相加 (注意正負號)</span>
<div style="margin-left: 20px;">
<div class="result-box">
( {' + '.join(numerators_sum_str)} ) ÷ {lcm} = {total_numerator}/{lcm}
</div>
</div>
"""
        
        final_frac = Fraction(total_numerator, lcm)
        if final_frac.denominator != lcm:
            html += f"""
<br>
<span class="math-step-title">Step 4: 約分 (算出最後答案)</span>
<div style="margin-left: 20px;">
<div class="result-box">
{total_numerator}/{lcm} = {final_frac.numerator}/{final_frac.denominator}
</div>
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

st.title(f"🧩 分數拼湊大作戰")
st.markdown(f"<div class='status-msg'>{engine.message}</div>", unsafe_allow_html=True)

# 1. 視覺化軌道
target_val = engine.target if engine.target > 0 else Fraction(1, 1)
# 為了適應負數操作，最大值稍微拉寬一點
max_val = max(target_val * Fraction(3, 2), Fraction(2, 1)) 

# 處理負數進度條 (如果小於0，就顯示0，或者您可以設計反向進度條，這裡先簡單處理)
curr_pct = max(0, min((engine.current / max_val) * 100, 100))
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
    st.write("### 🎴 請選擇要出的牌")
    if engine.hand:
        cols = st.columns(len(engine.hand))
        for i, card in enumerate(engine.hand):
            with cols[i]:
                # 根據正負號給予不同提示
                help_text = "這是一張負數牌，會扣分！" if card.is_negative else "這是一張正數牌，會加分！"
                if st.button(f"{card.display}", key=f"btn_{card.id}", help=help_text):
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
            if st.button("🚀 挑戰下一關 (Next Level)", type="primary", use_container_width=True):
                engine.next_level()
                st.rerun()
        else:
            if st.button("🔄 再試一次 (Retry)", type="secondary", use_container_width=True):
                engine.retry_level()
                st.rerun()

# 3. 側邊欄
with st.sidebar:
    st.markdown("### 📊 遊戲數據")
    st.write(f"當前關卡: **{engine.level}**")
    st.progress(min(engine.level / 10, 1.0))
    
    st.markdown("---")
    st.markdown("""
    **玩法說明:**
    1. **目標**: 讓藍色進度條剛好停在粉紅線上。
    2. **正負數**: 
       - 🟦 藍色牌是 **加分**。
       - 🟥 紅色牌是 **扣分** (負數)。
    3. **策略**: 如果加過頭了，可以用紅牌減回來喔！
    """)
