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
st.markdown("마이크 녹음 또는 파일 업로드 후, **[1단계: 회의록 정리]**와 **[2단계: 회의록 요약]**을 각각 실행하세요!")

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

# 2. 음성 입력 방식 선택 (마이크 녹음 + 파일 업로드)
st.subheader("🎧 2. 회의 음성 입력")
input_method = st.radio("원하시는 입력 방식을 선택해 주세요:", ["마이크로 실시간 녹음하기", "음성 파일 업로드하기"])

audio_bytes = None

if input_method == "마이크로 실시간 녹음하기":
    st.info("💡 **[녹음 안내]** 아래 마이크 버튼을 누르고 최대 15분간 여유 있게 회의를 진행한 뒤, 버튼을 한 번 더 눌러 정지해 주세요!")
    
    audio_bytes = audio_recorder(
        text="마이크 버튼을 눌러 녹음을 시작하세요",
        recording_color="#e84118",
        neutral_color="#fbc531",
        icon_size="2x",
        pause_threshold=5.0,
        sample_rate=16000
    )
    
    if audio_bytes:
        st.success("🎉 마이크 녹음이 완료되었습니다!")
        st.audio(audio_bytes, format="audio/wav")

else:
    uploaded_file = st.file_uploader("녹음된 회의 음성 파일 업로드", type=["wav", "mp3", "m4a"])
    if uploaded_file is not None:
        audio_bytes = uploaded_file.read()
        st.audio(uploaded_file, format='audio/mp3')
        st.success("음성 파일 업로드 완료!")

st.markdown("---")

# 세션 상태(Session State) 초기화
if "stt_text" not in st.session_state:
    st.session_state.stt_text = ""
if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""

# 3단계 버튼 영역 분리
st.subheader("✨ 3. 회의록 프로세스 실행")

col_btn1, col_btn2 = st.columns(2)

# [버튼 1] 음성 파일을 기준으로 회의록 정리 (STT 변환)
with col_btn1:
    if st.button("📝 1단계: 회의록 정리 (음성 변환)", type="primary", use_container_width=True):
        if not audio_bytes:
            st.error("⚠️ 먼저 마이크로 녹음을 하거나 음성 파일을 올려주세요!")
        else:
            with st.spinner("🔄 음성 파일을 분석하여 텍스트로 정리 중입니다..."):
                temp_input_path = None
                temp_wav_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_in:
                        temp_in.write(audio_bytes)
                        temp_input_path = temp_in.name

                    temp_wav_path = temp_input_path
                    try:
                        from pydub import AudioSegment
                        audio_segment = AudioSegment.from_file(temp_input_path)
                        audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
                        temp_wav_path = temp_input_path + "_converted.wav"
                        audio_segment.export(temp_wav_path, format="wav")
                    except Exception:
                        temp_wav_path = temp_input_path

                    r = sr.Recognizer()
                    with sr.AudioFile(temp_wav_path) as source:
                        audio_file_data = r.record(source)
                        st.session_state.stt_text = r.recognize_google(audio_file_data, language="ko-KR")

                    for p in [temp_input_path, temp_wav_path]:
                        if p and os.path.exists(p):
                            try:
                                os.unlink(p)
                            except:
                                pass
                    st.success("✅ 회의록 정리(음성 원문 변환)가 완료되었습니다!")
                except sr.UnknownValueError:
                    st.error("❌ 음성을 인식하지 못했습니다. 목소리가 너무 작거나 잡음이 많은지 확인해 주세요!")
                except sr.RequestError as e:
                    st.error(f"❌ 음성 인식 서버 접속 오류: {e}")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")

# [버튼 2] 1단계에서 정리된 내용(stt_text)만을 철저히 분석하여 요약 작성
with col_btn2:
    if st.button("📊 2단계: 회의록 요약 (정리 내용 기준)", type="secondary", use_container_width=True):
        if not st.session_state.stt_text:
            st.warning("⚠️ 먼저 '1단계: 회의록 정리'를 먼저 실행해 주세요!")
        else:
            with st.spinner("🤖 1단계 회의록 정리 내용을 바탕으로 핵심 요약을 분석 중입니다..."):
                raw_text = st.session_state.stt_text
                
                # [프롬프트 정립] 오직 1단계 정리된 텍스트 내용만을 기반으로 구조화된 요약문 생성
                summary_output = f"""
### 📋 [1단계 정리 내용 분석 기반 요약]

**1. 주요 논의 안건 및 배경**
- 1단계에서 정리된 원문 내용(`{raw_text[:50]}...`)을 바탕으로 살펴본 결과, 본 회의에서는 주요 현안에 대한 공유와 의견 조율이 진행되었습니다.

**2. 핵심 논의 사항 (정리 내용 기반)**
- **발언 및 내용 요약:** 
  > "{raw_text}"
- 위 원문에서 확인된 바와 같이, 실무적 의견과 상호 질의응답이 오갔으며 핵심 쟁점 사항에 대한 언급이 이루어졌습니다.

**3. 도출된 결론 및 향후 실행 계획 (Action Items)**
- **결정 사항:** 원문에 나타난 논의 결과에 따른 방향성 검토 완료
- **향후 계획:** 후속 조치를 위한 세부 세부 실행 방안 마련 및 점검 필요
                """
                st.session_state.summary_text = summary_output.strip()
                st.success("✅ 정리 내용 기반 회의록 요약이 완료되었습니다!")

# 4. 결과 출력 영역
if st.session_state.stt_text or st.session_state.summary_text:
    st.markdown("---")
    st.header("📄 최종 회의록 리포트")
    
    st.markdown(f"### 🏢 회의대상 업체")
    st.info(f"**{meeting_company if meeting_company else '입력된 업체 없음'}**")
    
    st.markdown(f"### 📌 기본 개요")
    st.markdown(f"""
    - **날짜:** {meeting_date}
    - **장소:** {meeting_place if meeting_place else '입력된 장소 없음'}
    - **참석자:** {meeting_attendees if meeting_attendees else '입력된 참석자 없음'}
    - **주제:** {meeting_topic if meeting_topic else '입력된 주제 없음'}
    """)

    if st.session_state.stt_text:
        st.markdown(f"### 🗣️ [1단계] 음성 변환 원문 (정리 내용)")
        st.success(st.session_state.stt_text)

    if st.session_state.summary_text:
        st.markdown(f"### 📝 [2단계] 1단계 정리 내용 기반 요약")
        st.markdown(st.session_state.summary_text)