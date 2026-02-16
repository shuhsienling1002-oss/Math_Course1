import streamlit as st
import plotly.graph_objects as go
import time
import math

# ==========================================
# 1. 系統配置與深海 HUD 樣式 (System Config)
# ==========================================
st.set_page_config(
    page_title="Deep Dive: Zero-Entropy Math",
    page_icon="⚓",
    layout="centered"
)

# 注入深海全息介面 CSS
st.markdown("""
<style>
    /* 全局背景：深海漸層 */
    .stApp {
        background: radial-gradient(circle at center, #1B263B 0%, #0D1B2A 100%);
        color: #E0E1DD;
        font-family: 'Courier New', Courier, monospace;
    }

    /* 標題樣式 */
    h1 {
        color: #00FFFF; /* 螢光青 */
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        border-bottom: 2px solid #00FFFF;
        padding-bottom: 10px;
        text-align: center;
    }

    /* 戰術按鈕樣式 */
    div.stButton > button {
        width: 100%;
        background-color: rgba(65, 90, 119, 0.3);
        color: #4CC9F0;
        border: 1px solid #4CC9F0;
        border-radius: 6px;
        padding: 0.6rem;
        transition: all 0.2s ease;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        background-color: #4CC9F0;
        color: #0D1B2A;
        box-shadow: 0 0 15px #4CC9F0;
        border-color: transparent;
        transform: scale(1.02);
    }

    /* 資訊面板：玻璃擬態 */
    div[data-testid="stMetric"], .stAlert {
        background-color: rgba(27, 38, 59, 0.6) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(119, 141, 169, 0.3);
        border-radius: 8px;
        color: #E0E1DD !important;
    }
    
    /* 隱藏預設元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心邏輯層 (The Logic Engine)
# ==========================================

class FractionObj:
    """ 分數物件：封裝數值與顯示邏輯 """
    def __init__(self, num, den, label=""):
        self.num = num
        self.den = den
        self.value = num / den
        self.label = label
        self.id = time.time()  # 唯一標識符

    def __repr__(self):
        sign = "+" if self.num > 0 else ""
        return f"{sign}{self.num}/{self.den}"

def get_lcm(a, b):
    """ 計算最小公倍數 (共振頻率) """
    if a == 0 or b == 0: return 0
    return abs(a * b) // math.gcd(a, b)

# 初始化 Session State (狀態管理)
if 'depth' not in st.session_state:
    st.session_state.depth = 0.0
if 'attachments' not in st.session_state:
    st.session_state.attachments = [] 
if 'feedback' not in st.session_state:
    st.session_state.feedback = "系統就緒。等待潛航指令..."
if 'radar_mode' not in st.session_state:
    st.session_state.radar_mode = False
if 'pending_obj' not in st.session_state:
    st.session_state.pending_obj = None

# ==========================================
# 3. 互動函數 (The Actions)
# ==========================================

def add_attachment(num, den):
    """ 嘗試掛載物件 (加法) """
    new_obj = FractionObj(num, den)
    
    # [衝突檢測] 檢查分母是否一致 (通分雷達邏輯)
    if st.session_state.attachments:
        current_den = st.session_state.attachments[0].den
        if den != current_den:
            # 觸發雷達模式
            st.session_state.radar_mode = True
            st.session_state.pending_obj = new_obj
            st.session_state.lcm_target = get_lcm(current_den, den)
            st.session_state.feedback = f"⚠️ 接口不合 ({current_den} vs {den})！啟動通分雷達..."
            return

    # 無衝突，直接執行
    execute_attach(new_obj)

def execute_attach(obj):
    """ 執行掛載並更新深度 """
    st.session_state.attachments.append(obj)
    st.session_state.depth += obj.value
    
    if obj.value > 0:
        st.session_state.feedback = f"✅ 掛載氣球 ({obj}) -> 浮力增加 -> 上浮"
    else:
        st.session_state.feedback = f"⚓ 掛載鐵錨 ({obj}) -> 負重增加 -> 下潛"

def remove_attachment(idx):
    """ 移除掛載物 (減法) - 核心物理反饋 """
    if idx >= len(st.session_state.attachments): return
    
    obj = st.session_state.attachments.pop(idx)
    st.session_state.depth -= obj.value
    
    # [物理反饋] 負負得正的關鍵邏輯
    if obj.value < 0:
        st.session_state.feedback = f"✂️ 剪斷鐵錨 ({obj})！負重消失 -> 急速上浮！ (減去負數)"
    else:
        st.session_state.feedback = f"💥 戳破氣球 ({obj})！浮力消失 -> 下沉！ (減去正數)"

def resolve_radar():
    """ 解決異分母衝突 (通分) """
    lcm = st.session_state.lcm_target
    
    # 1. 轉換現有的所有物件
    for obj in st.session_state.attachments:
        if obj.den != lcm:
            factor = lcm // obj.den
            obj.num *= factor
            obj.den = lcm
    
    # 2. 轉換待掛載的物件
    pending = st.session_state.pending_obj
    factor = lcm // pending.den
    pending.num *= factor
    pending.den = lcm
    
    execute_attach(pending)
    
    # 重置狀態
    st.session_state.radar_mode = False
    st.session_state.pending_obj = None
    st.session_state.feedback = f"⚡ 頻率同步完成！統一分母為 {lcm}"

def reset_game():
    st.session_state.depth = 0.0
    st.session_state.attachments = []
    st.session_state.radar_mode = False
    st.session_state.feedback = "系統重置完成。海平面深度 0。"

# ==========================================
# 4. UI 渲染層 (The View)
# ==========================================

st.title("⚓ Deep Dive: Zero-Entropy Math")

# A. 狀態反饋欄 (HUD Banner)
if "⚠️" in st.session_state.feedback:
    st.warning(st.session_state.feedback)
elif "✂️" in st.session_state.feedback or "💥" in st.session_state.feedback:
    st.error(st.session_state.feedback) # 使用紅色強調物理變化
else:
    st.info(st.session_state.feedback)

# ------------------------------------------
# 模式 A: 通分雷達 (Resonance Radar)
# ------------------------------------------
if st.session_state.radar_mode:
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ⚙️ 頻率校準")
        st.write("檢測到異分母衝突。請調整齒輪以尋找共振頻率 (LCM)。")
        
        current_den = st.session_state.attachments[0].den
        target_den = st.session_state.pending_obj.den
        lcm = st.session_state.lcm_target
        
        st.metric("系統頻率", f"1 / {current_den}")
        st.metric("目標頻率", f"1 / {target_den}")

    with col2:
        # 互動滑桿
        st.write(f"### 尋找目標: {lcm}")
        slider_val = st.slider("旋轉齒輪", min_value=1, max_value=lcm + 5, value=1)
        
        if slider_val == lcm:
            st.success(f"✨ 共振鎖定！ (LCM = {lcm})")
            if st.button(">> 執行同步與掛載 <<", type="primary"):
                resolve_radar()
                st.rerun()
        elif slider_val % current_den == 0 and slider_val % target_den == 0:
             st.info("這是公倍數，但不是最小的... 再試試！")
        else:
            st.caption("拖動滑桿直到鎖定...")

# ------------------------------------------
# 模式 B: 深海戰情室 (Dashboard)
# ------------------------------------------
else:
    # 1. 深海儀表板 (Plotly Visualization)
    fig = go.Figure()

    # 海平面
    fig.add_hline(y=0, line_dash="dash", line_color="cyan", annotation_text="海平面 (0)")

    # 潛艇位置
    depth = st.session_state.depth
    fig.add_trace(go.Scatter(
        x=[0], y=[depth],
        mode='markers+text',
        marker=dict(size=50, color='#FFD700', symbol='diamond', line=dict(width=2, color='white')),
        text=['🚁<br>Sub'],
        textposition="middle right",
        textfont=dict(color="#FFD700", size=14),
        name='Submarine'
    ))

    # 視覺化氣球與鐵錨
    for i, obj in enumerate(st.session_state.attachments):
        is_balloon = obj.value > 0
        color = "#00FF00" if is_balloon else "#FF4500" # 螢光綠 vs 橘紅
        symbol = "circle" if is_balloon else "triangle-down"
        
        # 簡單堆疊顯示，避免重疊
        offset = (i + 1) * 0.8
        y_pos = depth + offset if is_balloon else depth - offset
        
        # 連接線
        fig.add_trace(go.Scatter(
            x=[0, 0], y=[depth, y_pos],
            mode='lines',
            line=dict(color='white', width=1, dash='dot'),
            hoverinfo='skip'
        ))

        # 物件本體
        fig.add_trace(go.Scatter(
            x=[0], y=[y_pos],
            mode='markers+text',
            marker=dict(size=25, color=color, line=dict(width=1, color='white')),
            text=[f"{abs(obj.num)}/{obj.den}"],
            textposition="middle left",
            textfont=dict(color="white", weight="bold"),
            hoverinfo='text',
            hovertext=f"物件 ID: {i+1} | 數值: {obj.value}"
        ))

    # 圖表佈局設定
    fig.update_layout(
        title=dict(text="深海探測儀 (Depth Gauge)", font=dict(color="#4CC9F0")),
        yaxis=dict(range=[-8, 8], title="深度", gridcolor="rgba(255,255,255,0.1)", zeroline=False),
        xaxis=dict(showgrid=False, showticklabels=False, range=[-1, 1]),
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 2. 戰術控制台 (Control Panel)
    st.markdown("### 🎮 戰術控制台")
    
    tab1, tab2 = st.tabs(["➕ 掛載裝備 (加法)", "✂️ 移除裝備 (減法)"])
    
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### 🎈 氣球 (正數)")
            if st.button("加 1/2"): add_attachment(1, 2); st.rerun()
            if st.button("加 1/3"): add_attachment(1, 3); st.rerun()
            if st.button("加 1/4"): add_attachment(1, 4); st.rerun()
        with col_b:
            st.markdown("##### ⚓ 鐵錨 (負數)")
            if st.button("加 -1/2"): add_attachment(-1, 2); st.rerun()
            if st.button("加 -1/3"): add_attachment(-1, 3); st.rerun()
            if st.button("加 -1/4"): add_attachment(-1, 4); st.rerun()

    with tab2:
        if not st.session_state.attachments:
            st.info("潛艇目前無掛載物")
        else:
            st.write("點擊按鈕以執行減法 (剪斷繩索)：")
            # 為了版面整潔，每行顯示 3 個移除按鈕
            cols = st.columns(3)
            for i, obj in enumerate(st.session_state.attachments):
                with cols[i % 3]:
                    label = f"✂️ {obj}"
                    # 根據正負給予不同樣式提示
                    help_text = "剪斷氣球 (下沉)" if obj.value > 0 else "剪斷鐵錨 (上浮)"
                    if st.button(label, key=f"del_{obj.id}", help=help_text):
                        remove_attachment(i)
                        st.rerun()

    # 重置按鈕
    st.markdown("---")
    if st.button("🔄 重置系統 (Reset System)"):
        reset_game()
        st.rerun()

    # 3. 數學黑盒子 (Debug Data)
    with st.expander("📊 數學黑盒子 (Math Data Stream)"):
        st.metric("當前深度", f"{st.session_state.depth:.4f}")
        st.write("掛載序列:", [str(x) for x in st.session_state.attachments])
