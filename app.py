import streamlit as st
import pandas as pd
import os

DATA_FILE = "data_v2.csv"
GOAL_FILE = "goals.csv"
REJEOK_FILE = "rejeok.csv"
ATTENDANCE_FILE = "attendance_data.csv" # 출석 데이터 파일 추가

# 계층 구조 정의
HIERARCHY = {
    "자문회": {"1지역": ["충성1부", "희락부", "믿음부", "승리부"], "2지역": ["창조부", "은혜1부", "은혜2부", "새가족부"]},
    "장년회": {"1지역": ["이김부", "기백부", "하나부", "완성부", "전승부"], "2지역": ["열매부", "진심부", "충성부", "일심부", "열정부"], "3지역": ["전진부", "합력부", "승리부", "소성부", "새신자부"], "기타지역": ["기타,총무"]},
    "부녀회": {"천군지역": ["천군1부", "천군2부", "천군3부"], "필승지역": ["필승1부", "필승2부", "필승3부"], "순종지역": ["순종1부", "순종2부", "순종3부"], "전심지역": ["전심1부", "전심2부", "전심3부"], "소성지역": ["소성1부", "소성2부", "소성3부"], "최강지역": ["최강1부", "최강2부"], "새신자지역": ["새신자부"], "기타지역": ["기타,총무"]},
    "청년회": {"강철지역": ["강철1부", "강철2부", "강철3부", "강철4부"], "선봉지역": ["선봉1부", "선봉2부", "선봉3부", "선봉4부"], "진격지역": ["진격1부", "진격2부", "진격3부"], "새신자지역": ["새신자1부", "새신자2부"], "진심지역": ["진심2부", "진심3부"], "기타지역": ["기타,총무"]},
    "대학부": {"대학지역": ["연합대", "조선대1부", "조선대2부", "조선대3부", "조선대4부", "조선대5부"]}
}
GROUP_ORDER = ["선택 안 함"] + list(HIERARCHY.keys())

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['날짜', '회', '지역', '부서', '상담', '복음방', '확답'])

def load_goals():
    if os.path.exists(GOAL_FILE):
        df = pd.read_csv(GOAL_FILE)
        return df.dropna(subset=['월'])
    return pd.DataFrame(columns=['월', '회', '지역', '부서', '목표확답'])

def load_rejeok():
    if os.path.exists(REJEOK_FILE): return pd.read_csv(REJEOK_FILE)
    return pd.DataFrame(columns=['회', '지역', '부서', '재적'])

def load_attendance():
    if os.path.exists(ATTENDANCE_FILE): return pd.read_csv(ATTENDANCE_FILE)
    return pd.DataFrame(columns=['날짜', '지역', '센터', '수강인원'])

CENTER_HIERARCHY = {
    "본부지역": ["일곡"],
    "광산지역": ["쌍암"],
    "북구지역": ["매곡", "신안"]
}

st.set_page_config(layout="wide")
st.title("📊 본부지역 전도현황")
menu = st.tabs(["데이터 입력", "재적 설정", "목표 설정", "출석 입력", "출석 결과"])

with menu[0]:
    st.subheader("📝일일보고")
    group = st.selectbox("회", GROUP_ORDER, key="in_group")
    if group != "선택 안 함":
        region = st.selectbox("지역", ["선택 안 함"] + list(HIERARCHY[group].keys()), key="in_region")
        department = st.selectbox("부서", ["선택 안 함"] + (HIERARCHY[group][region] if region != "선택 안 함" else []), key="in_dept")
    else:
        region, department = "선택 안 함", "선택 안 함"
        st.selectbox("지역", [region], key="in_region_dummy", disabled=True)
        st.selectbox("부서", [department], key="in_dept_dummy", disabled=True)
    date = st.date_input("날짜")
    c1, c2, c3 = st.columns(3)
    with c1: sangdam = st.number_input("상담", min_value=0)
    with c2: bokeum = st.number_input("복음방", min_value=0)
    with c3: hwkdap = st.number_input("확답", min_value=0)
    if st.button("데이터 저장"):
        if "선택 안 함" in [group, region, department]: st.error("모두 선택해 주세요!")
        else:
            df = load_data()
            new_row = {'날짜': str(date), '회': group, '지역': region, '부서': department, '상담': sangdam, '복음방': bokeum, '확답': hwkdap}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("저장 완료!")

with menu[1]:
    st.subheader("👥 부서별 재적 설정")
    r_group = st.selectbox("회", GROUP_ORDER, key="r_group")
    if r_group != "선택 안 함":
        r_region = st.selectbox("지역", ["선택 안 함"] + list(HIERARCHY[r_group].keys()), key="r_region")
        r_department = st.selectbox("부서", ["선택 안 함"] + (HIERARCHY[r_group][r_region] if r_region != "선택 안 함" else []), key="r_dept")
    else:
        r_region, r_department = "선택 안 함", "선택 안 함"
        st.selectbox("지역", [r_region], key="r_region_dummy", disabled=True)
        st.selectbox("부서", [r_department], key="r_dept_dummy", disabled=True)
    target_rejeok = st.number_input("재적 인원", min_value=0)
    if st.button("재적 저장"):
        if "선택 안 함" in [r_group, r_region, r_department]: st.error("모두 선택해 주세요!")
        else:
            rejeok_df = load_rejeok()
            mask = (rejeok_df['회'] == r_group) & (rejeok_df['지역'] == r_region) & (rejeok_df['부서'] == r_department)
            if mask.any(): rejeok_df.loc[mask, '재적'] = target_rejeok
            else: rejeok_df = pd.concat([rejeok_df, pd.DataFrame([{'회': r_group, '지역': r_region, '부서': r_department, '재적': target_rejeok}])], ignore_index=True)
            rejeok_df.to_csv(REJEOK_FILE, index=False)
            st.success("재적 설정 완료!")
            st.write("---")
    st.subheader("📋 회별 재적 현황")
    rejeok_df = load_rejeok()
    
    if not rejeok_df.empty:
        for group_name in HIERARCHY.keys():
            group_rejeok = rejeok_df[rejeok_df['회'] == group_name]
            if not group_rejeok.empty:
                st.markdown(f"#### {group_name}")
                # 1. 기존 데이터 출력
                st.table(group_rejeok[['부서', '재적']].reset_index(drop=True))
                
                # 2. 회별 총합 계산 및 출력
                total_rejeok = group_rejeok['재적'].sum()
                st.write(f"**{group_name} 총 재적 인원: {total_rejeok}명**")

with menu[2]:
    st.subheader("🎯 부서별 목표 및 현황 조회")
    # 목표 설정 입력 폼
    target_month = st.text_input("목표 월 (예: 2026-07)")
    g_group = st.selectbox("회", GROUP_ORDER, key="g_group")
    if g_group != "선택 안 함":
        g_region = st.selectbox("지역", ["선택 안 함"] + list(HIERARCHY[g_group].keys()), key="g_region")
        g_department = st.selectbox("부서", ["선택 안 함"] + (HIERARCHY[g_group][g_region] if g_region != "선택 안 함" else []), key="g_dept")
    else:
        g_region, g_department = "선택 안 함", "선택 안 함"
        st.selectbox("지역", [g_region], key="g_region_dummy", disabled=True)
        st.selectbox("부서", [g_department], key="g_dept_dummy", disabled=True)
    target_hwkdap = st.number_input("목표 확답", min_value=0)
    
    if st.button("목표 저장"):
        if "선택 안 함" in [g_group, g_region, g_department]:
            st.error("회, 지역, 부서를 모두 선택해 주세요!")
        else:
            goals = load_goals()
            new_goal = pd.DataFrame([{'월': target_month, '회': g_group, '지역': g_region, '부서': g_department, '목표확답': int(target_hwkdap)}])
            goals = pd.concat([goals, new_goal], ignore_index=True)
            goals.to_csv(GOAL_FILE, index=False)
            st.success("목표 저장 완료!")
    
    st.write("---")
    
    # 데이터 조회 및 표 출력
    goals_df = load_goals()
    data_df = load_data()
    rejeok_df = load_rejeok()

    if not goals_df.empty:
        goals_df['월'] = goals_df['월'].astype(str)
        selected_m = st.selectbox("조회할 월 선택", ["선택 안 함", "전체 조회"] + sorted(goals_df['월'].unique(), reverse=True))
        
        if selected_m != "선택 안 함":
            filtered_goals = goals_df if selected_m == "전체 조회" else goals_df[goals_df['월'] == selected_m]
            
            # 현재 확답 계산: 일별 누적이 아닌 최신 데이터 추출
            if not data_df.empty and all(col in data_df.columns for col in ['회', '지역', '부서', '확답', '날짜']):
                data_df['날짜'] = pd.to_datetime(data_df['날짜'])
                data_df['월'] = data_df['날짜'].dt.strftime('%Y-%m')
                
                # 날짜순으로 정렬 후 가장 마지막 값(최신 데이터)을 가져옵니다[cite: 1]
                data_df = data_df.sort_values(by='날짜') 
                current = data_df.groupby(['회', '지역', '부서'])['확답'].last().reset_index().rename(columns={'확답': '현재확답'})
            else:
                current = pd.DataFrame(columns=['회', '지역', '부서', '현재확답'])
            
            # 데이터 병합[cite: 1]
            merged = pd.merge(filtered_goals, rejeok_df, on=['회', '지역', '부서'], how='left')
            merged = pd.merge(merged, current, on=['회', '지역', '부서'], how='left')
            
            # 결측치 처리 및 정수 변환[cite: 1]
            merged[['재적', '현재확답']] = merged[['재적', '현재확답']].fillna(0).astype(int)
            
            st.subheader("📋 부서 상세 목표 및 현황")
            st.table(merged[['월', '회', '지역', '부서', '재적', '목표확답', '현재확답']])
# 파일의 맨 마지막 부분

with menu[3]:
    st.subheader("📝 센터 출석 입력")
    a_date = st.date_input("날짜", key="a_date")
    # 지역 선택
    a_region = st.selectbox("지역", ["본부지역", "광산지역", "북구지역"], key="a_region")
    # 센터 선택: ALL_CENTERS 변수를 정확하게 사용
    a_center = st.selectbox("센터", ["일곡", "쌍암", "매곡", "신안"], key="a_center")
    a_count = st.number_input("수강 인원", min_value=0, step=1)
    
    if st.button("출석 정보 저장"):
        df = load_attendance()
        new_row = {'날짜': str(a_date), '지역': a_region, '센터': a_center, '수강인원': a_count}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(ATTENDANCE_FILE, index=False)
        st.success("출석 데이터 저장 완료!")

with menu[4]:
    st.subheader("📊 날짜별 지역 수강 현황")
    df = load_attendance()
    
    if not df.empty:
        # 날짜별, 지역별 수강인원 피벗 테이블
        result_df = df.pivot_table(index='날짜', columns='지역', values='수강인원', aggfunc='sum', fill_value=0)
        st.table(result_df)
    else:
        st.info("데이터가 없습니다.")
