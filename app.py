import streamlit as st
import pandas as pd
import altair as alt
import os

DATA_FILE = "data_v2.csv"
GOAL_FILE = "goals.csv"
GROUP_ORDER = ["자문회", "장년회", "부녀회", "청년회", "대학부"]

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['날짜', '회', '재적', '상담', '복음방', '확답'])

def load_goals():
    if os.path.exists(GOAL_FILE):
        df = pd.read_csv(GOAL_FILE)
        if '월' in df.columns: return df
    return pd.DataFrame(columns=['월', '회', '목표'])

st.set_page_config(layout="wide")
st.title("📊 확답 현황 관리 시스템")
menu = st.tabs(["데이터 입력", "데이터 조회", "목표 설정"])

# 1. 목표 설정 탭
with menu[2]:
    st.subheader("⚙️ 월별 목표 설정")
    target_month = st.text_input("목표를 설정할 월 (예: 2026-07)")
    goals = load_goals()
    with st.form("goal_form"):
        current_goals = goals[goals['월'] == target_month] if not goals.empty and '월' in goals.columns else pd.DataFrame()
        new_goals = []
        for group in GROUP_ORDER:
            val = current_goals[current_goals['회'] == group]['목표'].values[0] if not current_goals.empty and group in current_goals['회'].values else 0
            new_goals.append(st.number_input(f"{group} 목표", value=int(val)))
        if st.form_submit_button("목표 저장"):
            goals = goals[goals['월'] != target_month] if not goals.empty and '월' in goals.columns else pd.DataFrame(columns=['월', '회', '목표'])
            new_df = pd.DataFrame({'월': [target_month]*len(GROUP_ORDER), '회': GROUP_ORDER, '목표': new_goals})
            pd.concat([goals, new_df]).to_csv(GOAL_FILE, index=False)
            st.success("목표가 저장되었습니다!")

# 2. 데이터 입력 탭
with menu[0]:
    st.subheader("📝 데이터 입력/수정")
    with st.form("input_form"):
        date = st.date_input("날짜")
        group = st.selectbox("회", GROUP_ORDER)
        c1, c2, c3, c4 = st.columns(4)
        with c1: rejeok = st.number_input("재적", min_value=0)
        with c2: sangdam = st.number_input("상담", min_value=0)
        with c3: bokeum = st.number_input("복음방", min_value=0)
        with c4: hwkdap = st.number_input("확답", min_value=0)
        if st.form_submit_button("데이터 저장"):
            df = load_data()
            mask = (df['날짜'] == str(date)) & (df['회'] == group)
            if mask.any(): df.loc[mask, ['재적', '상담', '복음방', '확답']] = [rejeok, sangdam, bokeum, hwkdap]
            else: df = pd.concat([df, pd.DataFrame({'날짜': [str(date)], '회': [group], '재적': [rejeok], '상담': [sangdam], '복음방': [bokeum], '확답': [hwkdap]})], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("반영되었습니다!")

# 3. 데이터 조회 탭
with menu[1]:
    st.subheader("📈 데이터 현황 조회")
    df = load_data()
    if not df.empty:
        df['날짜_dt'] = pd.to_datetime(df['날짜'])
        df['월'] = df['날짜_dt'].dt.strftime('%Y-%m')
        
        # 일별 선택
        selected_date = st.date_input("조회할 일자 선택")
        df_f = df[df['날짜'] == str(selected_date)].copy()
        
        if not df_f.empty:
            df_f = df_f.merge(load_goals(), left_on=['월', '회'], right_on=['월', '회'], how='left').fillna(0)
            df_f['목표대비 확답률(%)'] = (df_f['확답'] / df_f['목표'] * 100).fillna(0).round(2)
            df_f['재적대비 확답률(%)'] = (df_f['확답'] / df_f['재적'] * 100).fillna(0).round(2)
            
            # 표 표시 (월 컬럼 제외)
            st.dataframe(df_f[['날짜', '회', '목표', '재적', '상담', '복음방', '확답', '목표대비 확답률(%)', '재적대비 확답률(%)']], use_container_width=True)
            
            # 그래프 표시
            st.write("### 부서별 확답 현황")
            chart = alt.Chart(df_f).mark_bar().encode(
                x=alt.X('회', sort=GROUP_ORDER, axis=alt.Axis(labelAngle=0)),
                # Y축 제목에 줄바꿈 추가 및 간격(titlePadding) 설정
                y=alt.Y('목표대비 확답률(%)', 
                        scale=alt.Scale(domain=[0, 100]), 
                        axis=alt.Axis(title=['목표대비', '확답률(%)'], 
                                      titleAngle=0, 
                                      titlePadding=30)), # 숫자와 글자 간격 확보
                color='회'
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("선택한 일자에 데이터가 없습니다.")
