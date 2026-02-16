import streamlit as st
import random
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
# 3. 核心引擎 (Game Engine) - 防呆機制 v2
# ==========================================

class GameEngine:
    """
    核心邏輯引擎 (High Cohesion)
    負責所有數學運算、狀態判定與關卡生成。
    完全不依賴 Streamlit UI，確保可測試性。
    """
    def __init__(self):
        # 初始化檢查：如果 session_state 缺少關鍵變數，強制重置
        required_keys = ['level', 'target', 'current', 'hand', 'msg', 'game_state']
        # 使用更嚴格的檢查，如果缺少任何一個 key 就重置
        if any(key not in st.session_state for key in required_keys):
            self.reset_game()
    
    # 所有的屬性讀取都使用 .get()，這是防止紅字錯誤的關鍵
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
        st.session_state.msg = f"⚔️ 第 {level} 關: 尋找平衡點！"

    def _generate_math_data(self, level: int) -> Tuple[Fraction, Fraction, List[Card]]:
        """
        生成關卡數據 (Procedural Generation)
        """
        # 難度設定
        if level == 1: den_pool = [2, 4]
        elif level == 2: den_pool = [2, 3, 4, 6]
        elif level <= 5: den_pool = [2, 3, 4, 5, 8]
        else: den_pool = [3, 6, 7, 9, 12]

        # 1. 建構正確路徑
        target_val = Fraction(0, 1)
        correct_hand = []
        steps = random.randint(2, 3 + (level // 3))
        
        for _ in range(steps):
            d = random.choice(den_pool)
            n = random.choice([1, 1, 2])
            card = Card(n, d)
            correct_hand.append(card)
            target_val += card.value

        # 設定起點與目標
        target = target_val
        current = Fraction(0, 1)

        # 2. 注入熵 (干擾牌)
        distractor_count = random.randint(1, 2)
        distractors = []
        for _ in range(distractor_count):
            d = random.choice(den_pool)
            n = random.choice([1, 2])
            distractors.append(Card(n, d))
            
        final_hand = correct_hand + distractors
        random.shuffle(final_hand)
        
        return target, current, final_hand

    def play_card(self, card_idx: int):
        if self.state != 'playing': return
        
        # 安全檢查
        if not st.session_state.get('hand') or card_idx >= len(st.session_state.hand):
            return

        card = st.session_state.hand.pop(card_idx)
        st.session_state.current += card.value
        
        # 觸發回饋迴路
        self._check_win_condition()

    def _check_win_condition(self):
        curr = st.session_state.get('current', Fraction(0, 1))
        tgt = st.session_state.get('target', Fraction(1, 1))
        
        if curr == tgt:
            st.session_state.game_state = 'won'
            st.session_state.msg = "🎉 完美平衡！(Perfect Equilibrium)"
        elif curr > tgt:
            st.session_state.game_state = 'lost'
            st.session_state.msg = "💥 能量過載！超過目標值了"
        elif not st.session_state.get('hand', []):
            st.session_state.game_state = 'lost'
            st.session_state.msg = "💀 資源耗盡！手牌用光了"
        else:
            diff = tgt - curr
            st.session_state.msg = f"🚀 推進中... 還差 {diff}"

    def next_level(self):
        self.start_level(self.level + 1)

    def retry_level(self):
        self.start_level(self.level)

# ==========================================
# 4. UI 渲染層 (View Layer)
# ==========================================

# 初始化引擎
engine = GameEngine()

st.title(f"🧩 零熵分數挑戰")
st.markdown(f"<div class='status-msg'>{engine.message}</div>", unsafe_allow_html=True)

# 1. 視覺化軌道 (Visual Feedback Loop)
# 計算百分比
target_val = engine.target if engine.target > 0 else Fraction(1, 1)
max_val = max(target_val * Fraction(3, 2), Fraction(2, 1)) 

curr_pct = min((engine.current / max_val) * 100, 100)
tgt_pct = (engine.target / max_val) * 100

# 修正：移除縮排以避免被誤判為程式碼區塊
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

# 2. 手牌區 (Interaction Layer)
st.write("### 🎴 你的策略手牌")

if engine.state == 'playing':
    if engine.hand:
        cols = st.columns(len(engine.hand))
        for i, card in enumerate(engine.hand):
            with cols[i]:
                if st.button(f"{card.display}", key=f"btn_{card.id}", help=f"值約為 {float(card.value):.2f}"):
                    engine.play_card(i)
                    st.rerun()
    else:
        st.info("手牌已空")
else:
    # 遊戲結束按鈕
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        if engine.state == 'won':
            if st.button("🚀 下一關", type="primary", use_container_width=True):
                engine.next_level()
                st.rerun()
        else:
            if st.button("🔄 再試一次", type="secondary", use_container_width=True):
                engine.retry_level()
                st.rerun()

# 3. 側邊欄與說明
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
