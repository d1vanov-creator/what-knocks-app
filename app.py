import streamlit as st
import openai
import base64

# 1. Настройка внешнего вида страницы
st.set_page_config(
    page_title="Что стучит? — ИИ-Диагност",
    page_icon="🚗",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .main-title {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #E53935;
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    .input-label { font-size: 18px; font-weight: 500; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. Элементы интерфейса
st.markdown('<div class="main-title">«Что стучит?»</div>', unsafe_allow_html=True)
st.markdown('<div class="input-label">Опишите проблему и модель авто</div>', unsafe_allow_html=True)

user_text = st.text_area(
    label="Ввод проблемы", 
    placeholder="Например: БМВ Х5 Е70, при повороте руля направо появляется глухой стук...",
    label_visibility="collapsed" 
)

uploaded_photo = st.file_uploader("Добавить фото (приборная панель, деталь)", type=["jpg", "jpeg", "png"])
if uploaded_photo:
    st.image(uploaded_photo, caption="Загруженное фото", width=300)

uploaded_audio = st.audio_input("Записать аудио стука")

# 3. Логика запуска анализа
if st.button("Запустить ИИ-Диагностику 🔧", type="primary"):
    if not user_text and not uploaded_photo and not uploaded_audio:
        st.warning("Пожалуйста, введите текст или добавьте файлы.")
    else:
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("Пожалуйста, добавьте ваш API-ключ в настройки Streamlit Cloud (Secrets).")
        else:
            with st.spinner("ИИ-Механик анализирует данные..."):
                try:
                    # Инициализируем клиент по стандартному обновленному протоколу ProxyAPI
                    client = openai.OpenAI(
                        api_key=st.secrets["OPENAI_API_KEY"],
                        base_url="https://proxyapi.ru"
                    )
                    
                    system_prompt = (
                        "Ты — опытный автомеханик. Твоя задача — сделать первичную диагностику. "
                        "Отвечай строго по пунктам: 1. Вероятная причина. 2. Критичность. 3. План действий. "
                        "В конце напомни, что точный диагноз ставится только в сервисе."
                    )
                    
                    # Формируем безопасный запрос для gpt-4o-mini
                    user_prompt = f"Модель машины и описание проблемы: {user_text}\n"
                    if uploaded_photo:
                        user_prompt += "[К запросу приложено фото повреждения/панели] "
                    if uploaded_audio:
                        user_prompt += "[К запросу приложена аудиозапись шума/стука] "

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        max_tokens=500
                    )
                    
                    # Прямое безопасное чтение текста ответа
                    ai_text = response.choices[0].message.content
                    st.success("Анализ завершен!")
                    st.markdown(ai_text)
                    
                except Exception as e:
                    st.error(f"Ошибка при обработке запроса: {e}")
