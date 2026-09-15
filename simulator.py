import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from collections import Counter

# 页面全局配置
st.set_page_config(page_title="MMO 数值验证系统", layout="wide")
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

st.title("MMO战斗与概率验证模拟器")
st.markdown("基于蒙特卡洛方法，在**左侧输入参数**，**右侧实时生成图表**。模拟次数越多，结果越逼近真实数学期望。")

# --- 左侧控制面板 ---
with st.sidebar:
    st.header("⚙️ 参数设置")
    attack = st.number_input("攻击力", value=1200, step=50)
    defense = st.number_input("防御力", value=200, step=10)
    crit_rate = st.slider("暴击率 (%)", 0, 100, 25) / 100.0
    crit_dmg = st.slider("暴击伤害 (%)", 100, 300, 180) / 100.0
    hp = st.number_input("击杀目标血量", value=8000, step=100)

    st.divider()

    success_rate = st.slider("强化成功率 (%)", 1, 100, 30) / 100.0
    n_sim = st.selectbox("模拟次数", [10000, 50000, 100000, 200000], index=2)

    run_btn = st.button("▶ 开始执行模拟", type="primary", use_container_width=True)

# --- 右侧图表区 ---
if run_btn:
    with st.spinner('正在执行蒙特卡洛模拟，请稍候...'):
        # 1. 战斗模拟
        total_damages = []  # 总伤害（含溢出）
        overkill_damages = []  # 溢出伤害
        turns_list = []  # 击杀所需回合数

        for _ in range(n_sim):
            cur_hp = hp
            total_dmg = 0
            overkill = 0
            turns = 0
            while cur_hp > 0:
                turns += 1
                base_dmg = max(1, attack - defense) * np.random.uniform(0.9, 1.1)
                if np.random.random() < crit_rate:
                    base_dmg *= crit_dmg

                # 核心逻辑：区分有效伤害和溢出伤害
                if base_dmg > cur_hp:
                    overkill += (base_dmg - cur_hp)
                    total_dmg += base_dmg
                    cur_hp = 0
                else:
                    total_dmg += base_dmg
                    cur_hp -= base_dmg

            total_damages.append(total_dmg)
            overkill_damages.append(overkill)
            turns_list.append(turns)

        total_damages = np.array(total_damages)
        overkill_damages = np.array(overkill_damages)
        turns_list = np.array(turns_list)

        # 2. 强化模拟
        levels = []
        for _ in range(n_sim):
            lvl = 0
            while lvl < 15:
                if np.random.random() < success_rate:
                    lvl += 1
                else:
                    if lvl > 0: lvl -= 1
                    break
            levels.append(lvl)

        # --- 核心指标展示区 ---
        st.markdown("### 📊 模拟结果核心指标")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("平均击杀回合数", f"{np.mean(turns_list):.2f}", help="玩家实际砍了多少刀")
        with col2:
            st.metric("平均溢出伤害", f"{np.mean(overkill_damages):.2f}", delta_color="inverse", help="浪费的伤害")
        with col3:
            st.metric("平均总伤害", f"{np.mean(total_damages):.2f}")
        with col4:
            st.metric("平均强化最终等级", f"{np.mean(levels):.2f}")

        st.divider()

        # 3. 图表展示
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # 左图：总伤害分布（包含溢出）
        ax1.hist(total_damages, bins=50, color='skyblue', edgecolor='black', alpha=0.7, label='总伤害(含溢出)')
        ax1.axvline(np.mean(total_damages), color='red', linestyle='dashed', linewidth=2,
                    label=f'均值: {np.mean(total_damages):.0f}')
        ax1.axvline(hp, color='green', linestyle='dotted', linewidth=2, label=f'怪物血量: {hp}')  # 标出怪物血量线
        ax1.set_title('击杀所需总伤害分布 (含溢出)')
        ax1.set_xlabel('总伤害')
        ax1.set_ylabel('频数')
        ax1.legend()

        # 右图：强化分布
        level_counts = Counter(levels)
        sorted_levels = sorted(level_counts.keys())
        counts = [level_counts[l] for l in sorted_levels]
        ax2.bar(sorted_levels, counts, color='salmon', edgecolor='black', alpha=0.7)
        ax2.set_title(f'装备强化最终等级分布 ({success_rate * 100:.0f}%成功率)')
        ax2.set_xlabel('最终强化等级')
        ax2.set_ylabel('频数')

        plt.tight_layout()
        st.pyplot(fig)

else:
    st.info("👈 请在左侧调整参数，然后点击「开始执行模拟」按钮。")