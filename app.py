import streamlit as st
import os

st.title("🎙️ 내 손으로 만드는 음성 회의 요약기")

# 파일 업로드 상자 만들기
uploaded_file = st.file_uploader("회의 음성 파일(mp3, wav)을 올려주세요", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # 업로드된 파일을 임시로 컴퓨터에 저장
    with open("temp_audio.mp3", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.audio(uploaded_file, format='audio/mp3')
    st.success("음성 파일 업로드 및 재생 준비 완료!")
    
    # 요약 버튼 클릭 시
    if st.button("회의 내용 요약하기"):
        with st.spinner("음성을 텍스트로 변환하고 요약 중입니다... 잠시만 기다려주세요! (시간이 좀 걸릴 수 있어요)"):
            
            # [임시 시뮬레이션 단계]
            # 실제 Whisper 모델을 돌리려면 컴퓨터 사양에 따라 시간이 오래 걸릴 수 있으므로,
            # 초보자 분들이 먼저 동작을 확인할 수 있도록 가상의 변환/요약 결과를 띄워드립니다.
            
            st.markdown("---")
            st.subheader("📝 1. 음성 인식 결과 (STT)")
            st.write("안녕하세요, 오늘 회의를 시작하겠습니다. 첫 번째 안건은 Q3 마케팅 전략 수립입니다. 김 대리님이 준비해 주신 자료 먼저 공유해 주세요.")
            
            st.markdown("---")
            st.subheader("✨ 2. 핵심 요약 및 액션플랜")
            st.success("""
            - **회의 주제:** Q3 마케팅 전략 수립
            - **핵심 요약:** Q3 목표 달성을 위한 신규 매체 광고 집행 방안 및 예산 배분 논의 완료
            - **📌 액션플랜 (Action Plan):**
              1. **김 대리:** 다음 주 월요일까지 상세 매체별 예산안 작성 후 공유
              2. **박 과장:** 경쟁사 프로모션 사례 조사 및 리포트 작성
            """)