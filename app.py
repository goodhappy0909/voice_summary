import streamlit as st
from audio_recorder_streamlit import audio_recorder
import qrcode
from io import BytesIO
from openai import OpenAI

# 페이지 설정
st.title("🎙️ AI 실시간 음성 회의 요약 비서")
st.markdown("휴대폰이나 PC 마이크로 직접 녹음하거나, 음성 파일을 업로드하면 AI가 완벽한 회의록을 만들어 드립니다!")

# 사이드바 설정 (API 키 입력 및 QR코드)
st.sidebar.header("🔑 설정 및 접속")
openai_api_key = st.sidebar.text_input("OpenAI API Key 입력", type="password", placeholder="sk-...")

st.sidebar.markdown("---")
st.sidebar.markdown("📱 **스마트폰 접속용 QR코드**")
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

# 2. 음성 입력 선택
st.subheader("🎧 2. 회의 음성 입력")
input_method = st.radio("원하시는 입력 방식을 선택해 주세요:", ["마이크로 실시간 녹음하기", "음성 파일 업로드하기"])

audio_bytes = None

if input_method == "마이크로 실시간 녹음하기":
    st.info("💡 아래 마이크 버튼을 누르면 녹음이 시작됩니다. 말을 마친 뒤 버튼을 한 번 더 누르면 녹음이 완료됩니다!")
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
    if not openai_api_key:
        st.error("⚠️ 왼쪽 사이드바에 OpenAI API Key를 먼저 입력해 주세요!")
    elif not audio_bytes:
        st.error("⚠️ 먼저 마이크로 녹음을 하거나 음성 파일을 올려주세요!")
    else:
        with st.spinner("🤖 AI가 음성을 글자로 변환하고 회의록을 작성 중입니다... 잠시만 기다려주세요!"):
            try:
                # 1단계: 음성 데이터를 파일 형태로 OpenAI에 전달하기 위해 변환
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                    temp_audio.write(audio_bytes)
                    temp_audio_path = temp_audio.name

                # 2단계: OpenAI Whisper API를 이용해 음성을 텍스트(STT)로 변환
                client = OpenAI(api_key=openai_api_key)
                
                with open(temp_audio_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                
                stt_text = transcript.text  # 음성이 변환된 원문 글자

                # 3단계: OpenAI GPT를 이용해 회의록 구조에 맞춰 요약하기
                prompt = f"""
                다음은 회의 음성을 텍스트로 변환한 원문입니다. 이 내용을 바탕으로 전문적인 회의록을 작성해 주세요.
                
                [회의 원문]
                {stt_text}
                
                아래 항목에 맞춰서 마크다운 형식으로 깔끔하게 작성해 줘:
                1. 회의 내용 (STT 원문 요약)
                2. 정리내용 (핵심 결정 사항 및 내용 3가지 이상)
                3. 향후계획 (담당자와 할 일, 기한 등)
                """

                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                ai_result = response.choices[0].message.content

                # 결과 출력 영역
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
                st.text_area("변환된 텍스트", stt_text, height=100)

                st.markdown("### 📝 AI 분석 및 요약 결과")
                st.markdown(ai_result)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")