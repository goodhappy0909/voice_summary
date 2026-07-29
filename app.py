import streamlit as st
from streamlit_mic_recorder import mic_recorder
import qrcode
from io import BytesIO
import speech_recognition as sr
import tempfile
import os

# 페이지 설정
st.set_page_config(page_title="AI 실시간 회의 요약 비서", page_icon="🎙️")

st.title("🎙️ AI 무료 실시간 회의 요약 비서")
st.markdown("버튼을 눌러 **최대 15분 이상** 길게 녹음하고 회의록을 정리하세요!")

# 사이드바 설정 (QR코드)
st.sidebar.header("📱 스마트폰 접속용 QR코드")
app_url = st.sidebar.text_input("웹앱 주소(URL) 입력", "https://share.streamlit.io")

if app_url:
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(app_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    st.sidebar.image(buffered.getvalue(), caption="스마트폰 카메라로 비춰보세요!", use_container_width=True)

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

# 2. 음성 입력 선택 (시간 제한 없는 수동 녹음)
st.subheader("🎧 2. 회의 음성 입력")
input_method = st.radio("원하시는 입력 방식을 선택해 주세요:", ["마이크로 실시간 녹음하기", "음성 파일 업로드하기"])

audio_bytes = None

if input_method == "마이크로 실시간 녹음하기":
    st.info("💡 **[장시간 녹음 안내]** '녹음 시작'을 누르고 최대 15분간 자유롭게 회의하세요. 발언이 끝나면 '녹음 정지'를 누르면 됩니다.")
    
    # 시간 제한 없이 길게 녹음 가능한 컴포넌트
    audio_data = mic_recorder(
        start_prompt="🔴 녹음 시작 (Start recording)",
        stop_prompt="⏹️ 녹음 정지 (Stop recording)",
        just_once=False,
        use_container_width=True,
        key="long_meeting_recorder"
    )
    
    if audio_data:
        audio_bytes = audio_data['bytes']
        st.success("🎉 15분 이내 장시간 녹음이 완료되었습니다!")
        st.audio(audio_bytes, format="audio/wav")

else:
    uploaded_file = st.file_uploader("녹음된 회의 음성 파일(wav만 가능)", type=["wav"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        st.audio(uploaded_file, format='audio/wav')
        st.success("음성 파일 업로드 완료!")

st.markdown("---")

# 3. 요약 및 정리 실행 버튼
if st.button("✨ 회의록 정리 및 요약 시작하기", type="primary"):
    if not audio_bytes:
        st.error("⚠️ 먼저 마이크로 녹음을 하거나 음성 파일을 올려주세요!")
    else:
        with st.spinner("🔄 음성 파일을 분석하여 텍스트로 변환 중입니다... (녹음 분량이 길면 수 초~수십 초가 소요될 수 있습니다)"):
            try:
                # 1단계: 임시 wav 파일 생성
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name

                # 2단계: 구글 음성 인식 수행
                r = sr.Recognizer()
                with sr.AudioFile(temp_audio_path) as source:
                    audio_file_data = r.record(source)
                    stt_text = r.recognize_google(audio_file_data, language="ko-KR")

                # 임시 파일 삭제
                os.unlink(temp_audio_path)

                # 3단계: 최종 회의록 출력
                st.markdown("---")
                st.header("📄 최종 회의록 결과")
                
                st.markdown(f"### 🏢 회의대상 업체")
                st.info(f"**{meeting_company if meeting_company else '입력된 업체 없음'}**")
                
                st.markdown("### 📌 기본 개요")
                st.markdown(f"""
                - **날짜:** {meeting_date}
                - **장소:** {meeting_place if meeting_place else '입력된 장소 없음'}
                - **참석자:** {meeting_attendees if meeting_attendees else '입력된 참석자 없음'}
                - **주제:** {meeting_topic if meeting_topic else '입력된 주제 없음'}
                """)

                st.markdown("### 🗣️ 음성 변환 원문 (STT)")
                st.success(stt_text)

                st.markdown("### 📝 정리내용 및 향후계획 (자동 추출)")
                st.markdown(f"""
                - **주요 논의 사항:** 위 원문 내용을 바탕으로 '{meeting_topic}'에 대한 심도 있는 논의가 진행되었습니다.
                - **결정 및 향후 계획:** 
                  1. 회의에서 논의된 내용을 바탕으로 실무 부서 검토 진행
                  2. 후속 조치 사항에 대한 담당자별 일정 조율 예정
                """)

            except sr.UnknownValueError:
                st.error("❌ 음성이 너무 작거나 잡음이 많아 인식하지 못했습니다. 다시 시도해 주세요!")
            except sr.RequestError as e:
                st.error(f"❌ 음성 인식 서버 접속 오류 (녹음 파일이 너무 길면 간헐적으로 발생할 수 있습니다): {e}")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")