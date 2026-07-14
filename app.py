import streamlit as st
import pandas as pd
import os
import altair as alt # 파일 상단에 import altair 추가 필수!

DATA_FILE = "data_v2.csv"
GOAL_FILE = "goals.csv"
REJEOK_FILE = "rejeok.csv"
ATTENDANCE_FILE = "attendance_data.csv" # 출석 데이터 파일 추가
RECEPTION_FILE = "reception.csv"

# 계층 구조 정의
HIERARCHY = {
    "자문회": {"1지역": ["충성1부", "희락부", "믿음부", "승리부"], "2지역": ["창조부", "은혜1부", "은혜2부", "새가족부"]},
    "장년회": {"1지역": ["이김부", "기백부", "하나부", "완성부", "전승부"], "2지역": ["열매부", "진심부", "충성부", "일심부", "열정부"], "3지역": ["전진부", "합력부", "승리부", "소성부", "새신자부"], "기타지역": ["기타,총무"]},
    "부녀회": {"천군지역": ["천군1부", "천군2부", "천군3부"], "필승지역": ["필승1부", "필승2부", "필승3부"], "순종지역": ["순종1부", "순종2부", "순종3부"], "전심지역": ["전심1부", "전심2부", "전심3부"], "소성지역": ["소성1부", "소성2부", "소성3부"], "최강지역": ["최강1부", "최강2부", "새신자부"], "기타지역": ["기타,총무"]},
    "청년회": {"강철지역": ["강철1부", "강철2부", "강철3부", "강철4부"], "선봉지역": ["선봉1부", "선봉2부", "선봉3부", "선봉4부"], "진격지역": ["진격1부", "진격2부", "진격3부"], "새신자지역": ["새신자1부", "새신자2부"], "진심지역": ["진심2부", "진심3부"], "기타지역": ["기타,총무"]},
    "대학부": {"대학지역": ["연합대", "조선대1부", "조선대2부", "조선대3부", "조선대4부", "조선대5부"]}
}
GROUP_ORDER = ["선택 안 함"] + list(HIERARCHY.keys())

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['날짜', '회', '지역', '부서', '상담', '복음방', '확답'])

def load_goals():
    if os.path.exists(GOAL_FILE):
        try:
            # 파일이 비어있지 않을 때만 읽기 시도
            if os.path.getsize(GOAL_FILE) > 0:
                return pd.read_csv(GOAL_FILE, encoding='utf-8')
            else:
                return pd.DataFrame(columns=['월', '회', '지역', '부서', '목표'])
        except Exception:
            # 파일 읽기 실패 시 빈 데이터프레임 반환
            return pd.DataFrame(columns=['월', '회', '지역', '부서', '목표'])
    return pd.DataFrame(columns=['월', '회', '지역', '부서', '목표'])

def load_rejeok():
    if os.path.exists(REJEOK_FILE): return pd.read_csv(REJEOK_FILE)
    return pd.DataFrame(columns=['회', '지역', '부서', '재적'])

def load_attendance():
    if os.path.exists(ATTENDANCE_FILE): return pd.read_csv(ATTENDANCE_FILE)
    return pd.DataFrame(columns=['날짜', '지역', '센터', '수강인원'])

def load_reception():
    if os.path.exists(RECEPTION_FILE): return pd.read_csv(RECEPTION_FILE)
    return pd.DataFrame(columns=['월', '지역', '센터', '접수인원'])

REGION_ORDER = ["본부지역", "광산지역", "북구지역"]
CENTER_HIERARCHY = {
    "본부지역": ["일곡"],
    "광산지역": ["쌍암"],
    "북구지역": ["매곡", "신안"]
}

st.set_page_config(layout="wide")
st.title("📊 본부지역 전도현황")
menu = st.tabs(["데이터 입력", "재적 설정", "목표 설정", "센터 접수", "출석 입력", "출석 결과", "목표 달성 그래프"])

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
    target_hwkdap = st.number_input("목표", min_value=0)
    
    if st.button("목표 저장"):
        if "선택 안 함" in [g_group, g_region, g_department]:
            st.error("회, 지역, 부서를 모두 선택해 주세요!")
        else:
            goals = load_goals()
            # 같은 조건의 기존 데이터 삭제 (덮어쓰기)
            mask = (goals['월'] == target_month) & (goals['회'] == g_group) & (goals['지역'] == g_region) & (goals['부서'] == g_department)
            goals = goals[~mask]
            
            new_goal = pd.DataFrame([{'월': target_month, '회': g_group, '지역': g_region, '부서': g_department, '목표': int(target_hwkdap)}])
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
        selected_m = st.selectbox("조회할 월 선택", ["선택 안 함"] + sorted(goals_df['월'].unique(), reverse=True))
        
        if selected_m != "선택 안 함":
            st.subheader(f"📅 {selected_m} 부서 상세 목표 및 현황") # 월을 제목으로 출력
            
            filtered_goals = goals_df[goals_df['월'] == selected_m]
            
            # 현재 확답 계산
           # 1. 일일 데이터에서 최신 상담, 복음방, 확답 값을 가져옵니다.
            if not data_df.empty:
                data_df['날짜'] = pd.to_datetime(data_df['날짜'])
                latest_data = data_df.groupby(['회', '지역', '부서']).last().reset_index()
            else:
                latest_data = pd.DataFrame(columns=['회', '지역', '부서', '상담', '복음방', '확답'])

            # 2. 목표, 재적, 일일 데이터를 하나로 병합
            merged = pd.merge(filtered_goals, rejeok_df, on=['회', '지역', '부서'], how='left')
            merged = pd.merge(merged, latest_data[['회', '지역', '부서', '상담', '복음방', '확답']], on=['회', '지역', '부서'], how='left')
            
            # 3. 결측치 처리 (데이터가 없는 경우 0으로 채움)
            merged[['재적', '목표', '상담', '복음방', '확답']] = merged[['재적', '목표', '상담', '복음방', '확답']].fillna(0).astype(int)
            
            # 4. 달성률 계산
            merged['달성률(%)'] = merged.apply(lambda x: (x['확답'] / x['목표'] * 100) if x['목표'] > 0 else 0, axis=1).round(1)
            
            # 회(자문회, 장년회 등)별로 나누어 출력[cite: 1]
            # 169번 줄부터 176번 줄까지 아래 코드로 교체하세요
           # 회(자문회, 장년회 등)별로 나누어 출력
            # 회(자문회, 장년회 등)별로 나누어 출력
            # 수정해야 할 코드 구조의 예시입니다.
            # 1. 회별 루프 시작
            for group in GROUP_ORDER:
                if group == "선택 안 함": continue
                
                group_data = merged[merged['회'] == group]
                
                # 1. 지역 순서 정의 (기타지역을 맨 뒤로 설정)
                region_order = [r for r in HIERARCHY[group].keys() if r != "기타지역"] + ["기타지역"]
                
                # 2. 부서 순서 정의
                dept_order = []
                for reg in HIERARCHY[group].values():
                    dept_order.extend(reg)
                
                # 3. 범주형 데이터 변환 및 정렬
                group_data['지역'] = pd.Categorical(group_data['지역'], categories=region_order, ordered=True)
                group_data['부서'] = pd.Categorical(group_data['부서'], categories=dept_order, ordered=True)
                
                # 4. 정의한 순서대로 정렬
                group_data = group_data.sort_values(by=['지역', '부서'])
                
                # 2. 데이터가 있을 때만 출력 (이 안에서만 표가 나와야 합니다)
                # 192번 줄 근처의 표 출력 로직을 아래와 같이 수정하세요.
                if not group_data.empty:
                    st.markdown(f"#### 🏢 {group}")
                    
                    # 1. 출력용 데이터 구성
                    table_data = group_data[['지역', '부서', '재적', '목표', '상담', '복음방', '확답', '달성률(%)']].copy()
                    
                    # 2. 지역별 소계 계산 및 추가
                    rows = []
                    # 지역 순서대로 정렬된 상태를 유지하며 루프
                    for region, region_df in table_data.groupby('지역', sort=False):
                        # 원래 부서 데이터 추가
                        for _, row in region_df.iterrows():
                            rows.append(row)
                        
                        # 해당 지역의 소계 계산
                        subtotal = {
                            '지역': "계",
                            '부서': "-",
                            '재적': region_df['재적'].sum(),
                            '목표': region_df['목표'].sum(),
                            '상담': region_df['상담'].sum(),
                            '복음방': region_df['복음방'].sum(),
                            '확답': region_df['확답'].sum(),
                            '달성률(%)': (region_df['확답'].sum() / region_df['목표'].sum() * 100) if region_df['목표'].sum() > 0 else 0
                        }
                        rows.append(pd.Series(subtotal))
                    
                    display_data = pd.DataFrame(rows)
                    display_data['달성률(%)'] = display_data['달성률(%)'].apply(lambda x: f"{x:.1f}%")
                    
                    # 3. 지역 병합 효과 처리
                    display_data['지역'] = display_data['지역'].astype(str)
                    last_region = None
                    for i in range(len(display_data)):
                        current_region = display_data.iloc[i, 0]
                        # 소계 행이 아니고, 이전 행과 같은 지역명이라면 지역명 지우기
                        if "소계" not in current_region and current_region == last_region:
                            display_data.iloc[i, 0] = ""
                        else:
                            last_region = current_region
                    
                    # 4. 표 출력
                    st.table(display_data.reset_index(drop=True))
                    
                    # 5. [선택] 전체 합계 출력 (원하시면 유지, 아니면 삭제)
                    # (기존에 작성하셨던 'group 합계' 출력 코드가 있다면 여기 아래에 두시면 됩니다.)
                    
                    # 4. 총합 계산 및 출력 (기존과 동일)
                    total_rejeok = group_data['재적'].sum()
                    total_goal = group_data['목표'].sum()
                    total_current = group_data['확답'].sum()
                    total_rate = (total_current / total_goal * 100) if total_goal > 0 else 0
                    
                    st.write(f"**{group} 합계 - 재적: {total_rejeok}명, 목표: {total_goal}명, 현재: {total_current}명 (전체 달성률: {total_rate:.1f}%)**")
                    st.write("---")
# 파일의 맨 마지막 부분
# 165번 줄 아래에 추가
# 166번 줄부터 시작되는 with menu[3]: 부분을 아래 코드로 교체하세요
with menu[3]:
    st.subheader("📝 센터 접수 기록")
    r_month = st.text_input("날짜(월) 입력 (예: 2026-07)", key="reception_month") # 수정
    r_region = st.selectbox("지역", ["선택 안 함"] + REGION_ORDER, key="reception_region") # 수정
    r_center = st.selectbox("센터", ["선택 안 함", "일곡", "쌍암", "매곡", "신안"], key="reception_center")
    r_count = st.number_input("센터 접수 인원", min_value=0, step=1) # 이 줄을 추가하세요
    
    if st.button("접수 정보 저장"):
        if "선택 안 함" in [r_region, r_center]:
            st.error("지역과 센터를 선택해 주세요!")
        else:
            df = load_reception()
            # 같은 월, 지역, 센터가 있으면 제거 후 덮어쓰기
            mask = (df['월'] == r_month) & (df['지역'] == r_region) & (df['센터'] == r_center)
            df = df[~mask]
            new_row = {'월': r_month, '지역': r_region, '센터': r_center, '접수인원': r_count}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(RECEPTION_FILE, index=False)
            st.success("접수 데이터 저장 완료!")
    
    st.write("---")
    st.subheader("📋 월별 센터 접수 조회")
    df = load_reception()
    if not df.empty:
        options = ["선택 안 함"] + sorted(df['월'].unique(), reverse=True)
        selected_m = st.selectbox("조회할 월", options)
        if selected_m != "선택 안 함":
            filtered_df = df[df['월'] == selected_m]
            pivot_df = filtered_df.pivot_table(index='지역', columns='센터', values='접수인원', aggfunc='sum', fill_value=0)
            pivot_df = pivot_df.reindex(REGION_ORDER).fillna(0)
            st.table(pivot_df.astype(int))

with menu[4]:
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

with menu[5]:
    st.subheader("📊 날짜별 지역 수강 현황")
    df = load_attendance()
    
    if not df.empty:
        # 날짜별, 지역별 수강인원 피벗 테이블
        result_df = df.pivot_table(index='날짜', columns='지역', values='수강인원', aggfunc='sum', fill_value=0)
        st.table(result_df)
    else:
        st.info("데이터가 없습니다.")

with menu[6]:
    st.subheader("📈 부서별 목표 달성률 그래프")
    
    goals_df = load_goals()
    if not goals_df.empty:
        # 조회할 월 선택
        selected_m = st.selectbox("그래프 조회할 월 선택", sorted(goals_df['월'].unique(), reverse=True), key="graph_month")
        
        # 3번 탭의 병합 로직과 동일하게 데이터를 준비합니다
        filtered_goals = goals_df[goals_df['월'] == selected_m]
        data_df = load_data()
        rejeok_df = load_rejeok()
        
        # 데이터 병합 (앞선 3번 탭 로직과 동일하게 유지)
        if not data_df.empty:
            data_df['날짜'] = pd.to_datetime(data_df['날짜'])
            latest_data = data_df.groupby(['회', '지역', '부서']).last().reset_index()
        else:
            latest_data = pd.DataFrame(columns=['회', '지역', '부서', '상담', '복음방', '확답'])
            
        merged = pd.merge(filtered_goals, rejeok_df, on=['회', '지역', '부서'], how='left')
        merged = pd.merge(merged, latest_data[['회', '지역', '부서', '상담', '복음방', '확답']], on=['회', '지역', '부서'], how='left')
        merged[['재적', '목표', '상담', '복음방', '확답']] = merged[['재적', '목표', '상담', '복음방', '확답']].fillna(0).astype(int)
        merged['달성률(%)'] = merged.apply(lambda x: (x['확답'] / x['목표'] * 100) if x['목표'] > 0 else 0, axis=1).round(1)
        
        # 각 회별로 그래프 생성
        for group in GROUP_ORDER:
            if group == "선택 안 함": continue
            
            group_data = merged[merged['회'] == group].copy()
            if not group_data.empty:
                    st.markdown(f"### 🏢 {group}")
                    
                    # 데이터 정렬 (기존과 동일)
                    dept_order = []
                    for reg in HIERARCHY[group].values(): dept_order.extend(reg)
                    group_data['부서'] = pd.Categorical(group_data['부서'], categories=dept_order, ordered=True)
                    plot_data = group_data.sort_values(by=['달성률(%)', '부서'], ascending=[False, True])
                    
                    # Altair 차트 생성 (막대 + 텍스트)
                    base = alt.Chart(plot_data).encode(
                        x=alt.X('부서', axis=alt.Axis(labelAngle=0))
                    )
                    
                    # 1. 막대 그래프 (색상 조건부 설정 추가)
                    # 1. 막대 그래프 (color 설정 부분을 아래와 같이 변경)
                    bars = base.mark_bar().encode(
                        y=alt.Y('달성률(%)', 
                                axis=alt.Axis(title='달성률(%)', titleAngle=0, titleAlign='right', 
                                              values=[i for i in range(0, 201, 10)]),
                                scale=alt.Scale(domain=[0, 200])),
                        color=alt.Color('달성률(%)', 
                                        scale=alt.Scale(domain=[0, 50, 100], 
                                                        range=['red', 'orange', 'blue']),
                                        legend=None) # 범례가 필요 없으면 None
                    )
                    
                    # 2. 막대 위 텍스트 표시
                    text = base.mark_text(dy=-5, color='white').encode(
                        y=alt.Y('달성률(%)', scale=alt.Scale(domain=[0, 200])),
                        text=alt.Text('달성률(%)', format='.1f')
                    )
                    
                    # 막대와 텍스트 합쳐서 출력
                    chart = (bars + text).properties(height=300)
                    st.altair_chart(chart, use_container_width=True)
                    st.write("---")
    else:
        st.info("목표 데이터가 없습니다.")
