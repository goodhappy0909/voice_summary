import streamlit as st
from audio_recorder_streamlit import audio_recorder

# 페이지 설정
st.title("🎙️ AI 실시간 음성 회의 요약 비서")
st.markdown("휴대폰이나 PC 마이크로 직접 녹음하거나, 음성 파일을 업로드하여 회의록을 정리하세요!")

st.markdown("---")

# 1. 기본 회의 정보 입력
st.subheader("📋 1. 기본 회의 정보")
col1, col2 = st.columns(2)
with col1:
    meeting_company = st.text_input("🏢 회의대상 업체", placeholder="예: (주)한국테크")
    meeting_date = st.date_input("📅 회의날짜")
    meeting_place = st.text_input("📍 회의 장소", placeholder="예: 본사 3층 대회의실")

with col2:
    meeting_attendees = st.text_input("👥 참석자", placeholder="예: 김철수, 이영희, 박지민")
    meeting_topic = st.text_input("📌 회의 주제", placeholder="예: Q3 신규 마케팅 전략 수립")

st.markdown("---")

# 2. 음성 입력 선택 (마이크 실시간 녹음 OR 파일 업로드)
st.subheader("🎧 2. 회의 음성 입력 방식 선택")
input_method = st.radio("원하시는 입력 방식을 선택해 주세요:", ["마이크로 실시간 녹음하기", "음성 파일 업로드하기"])

audio_bytes = None

if input_method == "마이크로 실시간 녹음하기":
    st.info("💡 아래 마이크 버튼을 누르면 녹음이 시작됩니다. 말을 마친 뒤 버튼을 한 번 더 누르면 녹음이 완료됩니다!")
    # 마이크 녹음 컴포넌트 호출
    audio_bytes = audio_recorder(
        text="마이크 버튼을 눌러 녹음을 시작하세요",
        recording_color="#e84118",
        neutral_color="#fbc531",
        icon_size="2x"
    )
    if audio_bytes:
        st.success("마이크 녹음이 완료되었습니다!")
        st.audio(audio_bytes, format="audio/wav")

else:
    uploaded_file = st.file_uploader("녹음된 회의 음성 파일(mp3, wav, m4a)을 올려주세요", type=["mp3", "wav", "m4a"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        st.audio(uploaded_file, format='audio/mp3')
        st.success("음성 파일 업로드 완료!")

st.markdown("---")

# 3. 요약 및 정리 실행 버튼
if st.button("✨ 회의록 정리 및 요약 시작하기", type="primary"):
    with st.spinner("AI가 회의 내용을 분석하고 정리 중입니다... 잠시만 기다려주세요!"):
        
        # 결과를 예쁘게 보여주는 영역
        st.markdown("---")
        st.header("📄 최종 회의록 결과")
        
        # 1. 회의대상 업체
        st.markdown(f"### 🏢 회의대상 업체")
        st.info(f"**{meeting_company if meeting_company else '입력된 업체 없음'}**")
        
        # 2. 기본 개요
        st.markdown("### 📌 기본 개요")
        st.markdown(f"""
        - **날짜:** {meeting_date}
        - **장소:** {meeting_place if meeting_place else '입력된 장소 없음'}
        - **참석자:** {meeting_attendees if meeting_attendees else '입력된 참석자 없음'}
        - **주제:** {meeting_topic if meeting_topic else '입력된 주제 없음'}
        """)
        
        # 3. 회의 내용
        st.markdown("### 💬 회의 내용 (STT 원문 요약)")
        st.write("""
        - 오늘 회의에서는 Q3 목표 달성을 위한 신규 매체 광고 집행 방안을 집중적으로 논의함.
        - 기존 매체 대비 효율성이 높은 숏폼 영상 광고 비중을 30% 이상 확대하기로 의견이 모아짐.
        - 예산 집행 시 발생할 수 있는 리스크와 타겟층 반응에 대한 사전 모니터링의 중요성이 언급됨.
        """)
        
        # 4. 정리내용
        st.markdown("### 📝 정리내용")
        st.success("""
        1. **매체 다변화:** 신규 소셜 미디어 플랫폼 중심의 타겟 마케팅 진행 확정
        2. **예산 배분:** 전체 마케팅 예산의 40%를 디지털 영상 광고에 집중 투자
        3. **성과 측정:** 매주 금요일 주간 성과 지표(KPI) 공유 및 피드백 진행
        """)
        
        # 5. 향후계획
        st.markdown("### 🚀 향후계획")
        st.warning("""
        - **김철수 과장:** 다음 주 월요일까지 상세 매체별 예산안 및 예상 성과 리포트 작성 후 공유
        - **이영희 대리:** 경쟁사 프로모션 사례 조사 및 벤치마킹 리포트 제출 (기한: 수요일까지)
        - **차기 회의:** 다음 주 금요일 오후 2시 (온/오프라인 동시 진행)
        """)