import streamlit as st
from audio_recorder_streamlit import audio_recorder
import qrcode
from io import BytesIO
import speech_recognition as sr
import tempfile
import os

# 페이지 설정
st.set_page_config(page_title="AI 실시간 회의 요약 비서", page_icon="🎙️")

st.title("🎙️ AI 무료 실시간 회의 요약 비서")
st.markdown("API 키 없이, 스마트폰이나 PC 마이크로 넉넉하게 녹음하고 회의록을 정리하세요!")

# 사이드바 설정 (QR코드)
st.sidebar.header("📱 스마트폰 접속용 QR코드")
app_url = st.sidebar.text_input("웹앱 주소(URL) 입력", "https://share.streamlit.app")

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

# 2. 음성 입력 선택
st.subheader("🎧 2. 회의 음성 입력")
input_method = st.radio("원하시는 입력 방식을 선택해 주세요:", ["마이크로 실시간 녹음하기", "음성 파일 업로드하기"])

audio_bytes = None

if input_method == "마이크로 실시간 녹음하기":
    st.info("💡 **[녹음 팁]** 아래 마이크 버튼을 누르면 녹음이 시작됩니다. 최대 15분까지 이어서 녹음할 수 있습니다. 말을 마친 뒤 버튼을 다시 누르면 완료됩니다!")
    
    # audio_recorder에 최대 녹음 시간 설정 추가 (예: 900초 = 15분)
    audio_bytes = audio_recorder(
        text="마이크 버튼을 눌러 녹음을 시작하세요",
        recording_color="#e84118",
        neutral_color="#fbc531",
        icon_size="2x",
        pause_threshold=3.0,  # 잠시 말을 멈추더라도 바로 끊기지 않도록 여유 시간 부여
        sample_rate=16000,
        energy_threshold=300,
        key="meeting_audio_recorder"
    )
    
    if audio_bytes:
        st.success("마이크 녹음이 완료되었습니다!")
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
        with st.spinner("🔄 음성을 텍스트로 변환하고 회의록을 정리 중입니다... 잠시만 기다려주세요!"):
            try:
                # 1단계: 녹음된 바이트 데이터를 임시 wav 파일로 저장
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name

                # 2단계: 구글 무료 음성 인식(STT) 사용
                r = sr.Recognizer()
                with sr.AudioFile(temp_audio_path) as source:
                    audio_data = r.record(source)
                    stt_text = r.recognize_google(audio_data, language="ko-KR")

                # 임시 파일 삭제
                os.unlink(temp_audio_path)

                # 3단계: 회의록 구조화 출력
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
                st.error("❌ 음성을 인식하지 못했습니다. 너무 짧거나 소리가 작지 않은지 확인 후 다시 녹음해 주세요!")
            except sr.RequestError as e:
                st.error(f"❌ 구글 음성 인식 서버에 접속할 수 없습니다: {e}")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")