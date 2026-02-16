import streamlit as st
import random
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Tuple

# ==========================================
# 🏗️ Model Layer: 數學核心 (First Principles)
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

class GameEngine:
    """
    核心邏輯引擎 (High Cohesion)
    負責所有數學運算、狀態判定與關卡生成。
    完全不依賴 Streamlit UI，確保可測試性。
    """
    def __init__(self):
        if 'level' not in st.session_state:
            self.reset_game()
    
    @property
    def level(self): return st.session_state.level
    @property
    def target(self): return st.session_state.target
    @property
    def current(self): return st.session_state.current
    @property
    def hand(self): return st.session_state.hand
    @property
    def message(self): return st.session_state.msg
    @property
    def state(self): return st.session_state.game_state # 'playing', 'won', 'lost'

    def reset_game(self):
        st.session_state.level = 1
        self.start_level(1)

    def start_level(self, level: int):
        st.session_state.level = level
        target, start_val, hand = self._generate_math_data(level)
        st.session_state.target = target
        st.session_state.current = start_val
        st.session_state.hand = hand
        st.session_state.game_state = 'playing'
        st.session_state.msg = f"⚔️ Level {level}: 尋找平衡點！"

    def _generate_math_data(self, level: int) -> Tuple[Fraction, Fraction, List[Card]]:
        """
        生成關卡數據 (Procedural Generation)
        依據難度曲線 (Progression) 動態生成
        """
        # 難度設定 (Complexity Thresholds)
        if level == 1: den_pool = [2, 4]
        elif level == 2: den_pool = [2, 3, 4, 6]
        elif level <= 5: den_pool = [2, 3, 4, 5, 8]
        else: den_pool = [3, 6, 7, 9, 12] # 高難度

        # 1. 建構正確路徑 (The Happy Path)
        target_val = Fraction(0, 1)
        correct_hand = []
        steps = random.randint(2, 3 + (level // 3))
        
        for _ in range(steps):
            d = random.choice(den_pool)
            n = random.choice([1, 1, 2])
            card = Card(n, d)
            correct_hand.append(card)
            target_val += card.value

        # 設定起點與目標 (Target needs to be reachable)
        # 讓 Target 稍微大於 0，並讓 current 從 0 開始
        target = target_val
        current = Fraction(0, 1)

        # 2. 注入熵 (Entropy Injection) - 干擾牌
        distractor_count = random.randint(1, 2)
        distractors = []
        for _ in range(distractor_count):
            d = random.choice(den_pool)
            n = random.choice([1, 2]) # 故意放正數，讓玩家容易爆掉
            distractors.append(Card(n, d))
            
        final_hand = correct_hand + distractors
        random.shuffle(final_hand)
        
        return target, current, final_hand

    def play_card(self, card_idx: int):
        if st.session_state.game_state != 'playing': return

        card = st.session_state.hand.pop(card_idx)
        st.session_state.current += card.value
        
        # 觸發回饋迴路 (Feedback Loop)
        self._check_win_condition()

    def _check_win_condition(self):
        curr = st.session_state.current
        tgt = st.session_state.target
        
        if curr == tgt:
            st.session_state.game_state = 'won'
            st.session_state.msg = "🎉 完美平衡！(Perfect Equilibrium)"
        elif curr > tgt:
            st.session_state.game_state = 'lost'
            st.session_state.msg = "💥 能量過載！你超過了目標值 (Entropy Overload)"
        elif not st.session_state.hand:
            st.session_state.game_state = 'lost'
            st.session_state.msg = "💀 資源耗盡！沒有手牌了 (Resource Depletion)"
        else:
            # 計算剩餘距離，給予提示 (Bayesian Update hint)
            diff = tgt - curr
            st.session_state.msg = f"🚀 推進中... 還差 {diff}"

    def next_level(self):
        self.start_level(st.session_state.level + 1)

    def retry_level(self):
        self.start_level(st.session_state.level)

# ==========================================
# 🎨 View Layer: UI/UX (Streamlit)
# ==========================================

st.set_page_config(page_title="Zero-Entropy Fraction", page_icon="🧩", layout="centered")

# CSS 優化：引入 Thumb Zone 與 Visual Hierarchy
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
</style>
""", unsafe_allow_html=True)

# 初始化引擎
engine = GameEngine()

# UI 渲染
st.title(f"🧩 Zero-Entropy Fraction")
st.markdown(f"<div class='status-msg'>{engine.message}</div>", unsafe_allow_html=True)

# 1. 視覺化軌道 (Visual Feedback Loop)
# 將分數轉換為百分比 (假設最大值為 Target * 1.5 以保留溢出空間)
max_val = max(engine.target * Fraction(3, 2), Fraction(2, 1)) 
curr_pct = min((engine.current / max_val) * 100, 100)
tgt_pct = (engine.target / max_val) * 100

st.markdown(f"""
<div class="game-container">
    <div style="display: flex; justify-content: space-between; font-family: monospace;">
        <span>🏁 START: 0</span>
        <span>🚩 TARGET: {engine.target}</span>
    </div>
    
    <div class="progress-track">
        <div class="target-marker" style="left: {float(tgt_pct)}%;"></div>
        <div class="progress-fill" style="width: {float(curr_pct)}%;"></div>
    </div>
    
    <div style="text-align: center; font-size: 24px; font-weight: bold;">
        當前總和: <span style="color: #89b4fa;">{engine.current}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. 手牌區 (Interaction Layer)
# 使用 Container 分隔，避免重新渲染時跳動
st.write("### 🎴 你的策略手牌")

if engine.state == 'playing':
    cols = st.columns(len(engine.hand)) if engine.hand else [st.empty()]
    for i, card in enumerate(engine.hand):
        with cols[i]:
            # Tooltip 顯示小數值，輔助決策 (Auxiliary Info)
            if st.button(f"{card.display}", key=f"btn_{card.id}", help=f"值約為 {float(card.value):.2f}"):
                engine.play_card(i)
                st.rerun()
else:
    # 遊戲結束狀態處理
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        if engine.state == 'won':
            if st.button("🚀 下一關 (Next Level)", type="primary", use_container_width=True):
                engine.next_level()
                st.rerun()
        else:
            if st.button("🔄 再試一次 (Retry)", type="secondary", use_container_width=True):
                engine.retry_level()
                st.rerun()

# 3. 側邊欄與說明 (Meta Info)
with st.sidebar:
    st.markdown("### 📊 遊戲數據")
    st.write(f"當前關卡: **{engine.level}**")
    st.progress(min(engine.level / 10, 1.0))
    
    st.markdown("---")
    st.markdown("""
    **玩法說明 (Zero-Entropy):**
    1. **目標**: 讓藍色進度條剛好停在紅線上。
    2. **陷阱**: 手牌中混有「雜訊牌」，全部打出會爆掉！
    3. **策略**: 計算並選擇正確的組合 (納什均衡)。
    """)
