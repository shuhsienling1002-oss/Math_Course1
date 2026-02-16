import streamlit as st
import random
import math
from fractions import Fraction
from dataclasses import dataclass, field
from typing import List, Literal

# ==========================================
# 0. 強制重置機制 (解決崩潰與舊資料衝突)
# ==========================================
SYSTEM_VERSION = "v6.0_STABLE"

if st.session_state.get("sys_ver") != SYSTEM_VERSION:
    st.session_state.clear()
    st.session_state.sys_ver = SYSTEM_VERSION

# ==========================================
# 1. 頁面設定與 CSS (修復亂碼與視覺回饋)
# ==========================================
st.set_page_config(page_title="分數運算大師", page_icon="🎓", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    
    /* 遊戲區塊 */
    .game-container {
        background: #313244;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        border: 2px solid #45475a;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* 進度條軌道 */
    .progress-track {
        background: #45475a;
        height: 24px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        margin: 20px 0;
    }
    
    /* 進度條填充 - 正常 */
    .progress-fill {
        background: linear-gradient(90deg, #89b4fa, #74c7ec);
        height: 100%;
        transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    /* 進度條填充 - 警告 (超過時) */
    .progress-fill.warning {
        background: linear-gradient(90deg, #fab387, #f38ba8); /* 橘紅漸層 */
    }
    
    /* 目標標記 */
    .target-marker {
        position: absolute; top: 0; bottom: 0; width: 4px;
        background-color: #f38ba8; z-index: 10; box-shadow: 0 0 10px #f38ba8;
    }

    /* 按鈕樣式 (強制字型，解決亂碼) */
    div.stButton > button {
        background-color: #cba6f7 !important;
        color: #181825 !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 24px !important;
        font-family: 'Arial', 'Helvetica', sans-serif !important; /* 強制通用字型 */
        font-weight: bold !important;
        height: 70px !important;
        transition: all 0.2s !important;
    }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(203, 166, 247, 0.4); }
    
    /* 狀態訊息 */
    .status-msg {
        font-size: 1.4rem; text-align: center; font-weight: bold;
        color: #f9e2af; margin-bottom: 10px; min-height: 1.5em;
    }
    
    /* 數學步驟 */
    .math-steps {
        background-color: #313244; padding: 20px; border-radius: 10px;
        border-left: 5px solid #89b4fa; margin-top: 15px;
        font-family: 'Courier New', monospace; color: #cdd6f4; line-height: 1.6;
    }
    .step-row { margin-bottom: 8px; font-size: 1.1rem; }
    .final-result { font-size: 1.3rem; color: #a6e3a1; font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 數據模型
# ==========================================

@dataclass
class Card:
    numerator: int
    denominator: int
    op: Literal['+', '-', '*', '/']
    id: int = field(default_factory=lambda: random.randint(10000, 99999))

    @property
    def value(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    @property
    def display(self) -> str:
        # 使用最安全的標準符號，不使用 Emoji，避免亂碼
        op_map = {'+': '+', '-': '-', '*': '×', '/': '÷'}
        return f"{op_map[self.op]} {self.numerator}/{self.denominator}"

# ==========================================
# 3. 核心引擎 (邏輯修復)
# ==========================================

class GameEngine:
    def __init__(self):
        defaults = {
            'level': 1, 'target': Fraction(1, 1), 'current': Fraction(0, 1),
            'start_val': Fraction(0, 1), 'hand': [], 'msg': "歡迎挑戰！",
            'game_state': 'playing', 'math_log': "", 'unit': "單元一：分數加減",
            'history': []
        }
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v

    # --- 屬性 ---
    @property
    def level(self): return st.session_state.level
    @property
    def unit(self): return st.session_state.unit
    @property
    def current(self): return st.session_state.current
    @property
    def target(self): return st.session_state.target
    @property
    def start_val(self): return st.session_state.start_val
    @property
    def state(self): return st.session_state.game_state

    # --- 邏輯 ---
    def set_unit(self, unit_name):
        if st.session_state.unit != unit_name:
            st.session_state.unit = unit_name
            st.session_state.level = 1
            self.start_level(1)

    def start_level(self, level: int):
        st.session_state.level = level
        st.session_state.history = []
        
        target, start_val, hand, title = self._generate_data(self.unit, level)
        
        st.session_state.target = target
        st.session_state.current = start_val
        st.session_state.start_val = start_val
        st.session_state.hand = hand
        st.session_state.game_state = 'playing'
        st.session_state.msg = f"{title}"
        st.session_state.math_log = ""

    def _generate_data(self, unit, level):
        hand = []
        target = Fraction(0, 1)
        start_val = Fraction(0, 1)
        title = ""
        
        # === 單元一：分數加減 ===
        if unit == "單元一：分數加減":
            start_val = Fraction(0, 1)
            den_pool = [2, 4] if level <= 2 else [2, 3, 4, 6]
            steps = 2 + (level // 2)
            allow_neg = level >= 3 
            
            current_val = start_val
            for _ in range(steps):
                d = random.choice(den_pool)
                n = random.choice([1, 1, 2])
                op = '+'
                if allow_neg and random.random() < 0.3: op = '-'
                
                card = Card(n, d, op)
                hand.append(card)
                if op == '+': current_val += card.value
                else: current_val -= card.value
            
            target = current_val
            title = f"Lv {level}: 分數加減"

        # === 單元二：分數乘除 ===
        elif unit == "單元二：分數乘除":
            start_val = Fraction(1, 1)
            steps = 2 + (level // 3)
            current_val = start_val
            for _ in range(steps):
                if random.random() < 0.5:
                    op = '*'
                    card = Card(random.choice([2, 3]), 1, op) if random.random() < 0.5 else Card(1, random.choice([2, 3]), op)
                else:
                    op = '/'
                    card = Card(random.choice([2, 4]), 1, op) if random.random() < 0.5 else Card(1, 2, op)
                
                hand.append(card)
                if op == '*': current_val *= card.value
                else: current_val /= card.value
            target = current_val
            title = f"Lv {level}: 分數乘除"

        # === 單元三：混合運算 ===
        elif unit == "單元三：分數加減乘除":
            start_val = Fraction(0, 1)
            steps = 3 + (level // 3)
            current_val = start_val
            
            # 第一張通常是加法做底
            c1 = Card(1, random.choice([2, 3]), '+')
            hand.append(c1)
            current_val += c1.value
            
            for _ in range(steps - 1):
                op = random.choice(['+', '-', '*', '/'])
                if op in ['+', '-']:
                    card = Card(1, random.choice([2, 4]), op)
                    if op == '+': current_val += card.value
                    else: current_val -= card.value
                else:
                    card = Card(random.choice([2, 3]), 1, op)
                    if op == '*': current_val *= card.value
                    else: current_val /= card.value
                hand.append(card)
            target = current_val
            title = f"Lv {level}: 混合挑戰"

        # 干擾牌
        dist_count = 1 if level < 3 else 2
        for _ in range(dist_count):
            op = random.choice(['+', '-', '*', '/']) if unit == "單元三：分數加減乘除" else ('+' if unit=="單元一：分數加減" else '*')
            hand.append(Card(1, 2, op))
            
        random.shuffle(hand)
        return target, start_val, hand, title

    def play_card(self, idx):
        if self.state != 'playing': return
        if not st.session_state.hand or idx >= len(st.session_state.hand): return
        
        card = st.session_state.hand.pop(idx)
        old_val = self.current
        
        if card.op == '+': new_val = old_val + card.value
        elif card.op == '-': new_val = old_val - card.value
        elif card.op == '*': new_val = old_val * card.value
        elif card.op == '/': 
            new_val = old_val if card.value == 0 else old_val / card.value
        
        st.session_state.current = new_val
        st.session_state.history.append({'old': old_val, 'card': card, 'new': new_val})
        
        self._check_status()

    def _check_status(self):
        curr = self.current
        tgt = self.target
        
        # 1. 勝利判定
        if curr == tgt:
            self._end_game('won')
            return

        # 2. 超過目標判定 (修復此功能！)
        if curr > tgt:
            diff = curr - tgt
            st.session_state.msg = f"⚠️ 超過了 {diff}！"
            # 注意：這裡不結束遊戲，給玩家機會修正 (如果有減法或除法)
            
            # 如果手牌沒了，且依然超過 -> 輸了
            if not st.session_state.hand:
                self._end_game('lost')
            return

        # 3. 未達目標且沒牌 -> 輸了
        if not st.session_state.hand:
            self._end_game('lost')
            return
            
        # 4. 正常進行中
        st.session_state.msg = f"🚀 計算中..."

    def _end_game(self, status):
        st.session_state.game_state = status
        if status == 'won':
            st.session_state.msg = "🎉 成功！答案正確！"
        else:
            st.session_state.msg = "❌ 挑戰失敗"
        self._generate_log()

    def _generate_log(self):
        html = "<div class='math-steps'>"
        html += f"<div class='step-row'>🏁 起始值：{self.start_val}</div>"
        for step in st.session_state.history:
            c = step['card']
            op_map = {'+': '加', '-': '減', '*': '乘', '/': '除'}
            html += f"<div class='step-row'>{step['old']} {op_map[c.op]} <b>{c.value}</b> = {step['new']}</div>"
        
        res_color = "#a6e3a1" if self.current == self.target else "#f38ba8"
        html += f"<div class='final-result' style='color:{res_color}'>🚩 最終：{self.current} (目標：{self.target})</div></div>"
        st.session_state.math_log = html

    def next_level(self): self.start_level(self.level + 1)
    def retry(self): self.start_level(self.level)

# ==========================================
# 4. 介面渲染
# ==========================================
engine = GameEngine()

# --- 側邊欄 ---
with st.sidebar:
    st.title("📚 課程選單")
    sel_unit = st.radio("選擇單元：", ["單元一：分數加減", "單元二：分數乘除", "單元三：分數加減乘除"], key="u_sel")
    if sel_unit != engine.unit:
        engine.set_unit(sel_unit)
        st.rerun()
    
    st.markdown("---")
    st.write(f"等級：Lv {engine.level}")
    st.progress(min(engine.level/10, 1.0))

# --- 主畫面 ---
st.title("🎓 分數運算大師")
st.markdown(f"<div class='status-msg'>{st.session_state.msg}</div>", unsafe_allow_html=True)

# 進度條邏輯 (修復變色功能)
tgt = engine.target
curr = engine.current
max_val = float(tgt) * 1.5 if float(tgt) > 0 else 2.0
tgt_pct = min((float(tgt) / max_val) * 100, 100)
curr_pct = min(max(0, (float(curr) / max_val) * 100), 100)

# 關鍵 CSS 判斷：若超過目標，套用 warning 樣式
bar_class = "progress-fill warning" if curr > tgt else "progress-fill"

st.markdown(f"""
<div class="game-container">
    <div style="display: flex; justify-content: space-between; font-family: monospace;">
        <span>🏁 {engine.start_val}</span>
        <span>🚩 {tgt}</span>
    </div>
    <div class="progress-track">
        <div class="target-marker" style="left: {tgt_pct}%;"></div>
        <div class="{bar_class}" style="width: {curr_pct}%;"></div>
    </div>
    <div style="text-align: center; font-size: 24px; font-weight: bold;">
        當前: <span style="color: #89b4fa;">{curr}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 遊戲區
if engine.state == 'playing':
    st.write("### 🎴 點擊卡牌運算")
    if st.session_state.hand:
        cols = st.columns(len(st.session_state.hand))
        for i, card in enumerate(st.session_state.hand):
            with cols[i]:
                # key 加上 random 確保每次渲染都是新的按鈕實例，避免狀態殘留
                if st.button(card.display, key=f"btn_{card.id}_{random.randint(0,999)}"):
                    engine.play_card(i)
                    st.rerun()
    else:
        st.warning("結算中...")
        engine._check_status() # 雙重檢查
        st.rerun()
else:
    st.markdown(st.session_state.math_log, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.session_state.game_state == 'won':
            if st.button("🚀 下一關", type="primary", use_container_width=True):
                engine.next_level()
                st.rerun()
        else:
            if st.button("🔄 重試", type="secondary", use_container_width=True):
                engine.retry()
                st.rerun()
