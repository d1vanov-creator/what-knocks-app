import streamlit as st
import openai
import base64

# 1. Настройка внешнего вида страницы (Светлые тона, белый фон)
st.set_page_config(
    page_title="Что стучит? — ИИ-Диагност",
    page_icon="🚗",
    layout="centered"
)

# Кастомные стили: белый фон приложения и красивый красный заголовок без курсива
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    .main-title {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        color: #E53935; /* Красный цвет */
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
    }
    .input-label {
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Главный экран сверху — Красный красивый заголовок
st.markdown('<div class="main-title">«Что стучит?»</div>', unsafe_allow_html=True)

# 3. Инструкция над строкой ввода
st.markdown('<div class="input-label">Опишите проблему и модель авто</div>', unsafe_allow_html=True)

# 4. Строка ввода для пользователя (скрываем стандартную метку, так как сделали свою красивую выше)
user_text = st.text_area(
    label="Опишите проблему и модель авто", 
    placeholder="Например: БМВ Х5 Е70, при повороте руля направо появляется глухой стук в районе переднего левого колеса...",
    label_visibility="collapsed" 
)

# Кнопки для загрузки фото и аудио
uploaded_photo = st.file_uploader("Добавить фото (приборная панель, потекшая деталь и т.д.)", type=["jpg", "jpeg", "png"])
if uploaded_photo:
    st.image(uploaded_photo, caption="Загруженное фото", width=300)

uploaded_audio = st.audio_input("Записать аудио (стук, шум работы мотора)")

# Кнопка запуска анализа
if st.button("Запустить ИИ-Диагностику 🔧", type="primary"):
    if not user_text and not uploaded_photo and not uploaded_audio:
        st.warning("Пожалуйста, опишите проблему текстом, добавьте фото или запишите звук стука.")
    else:
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("Пожалуйста, добавьте ваш API-ключ в настройки Streamlit Cloud (Secrets).")
        else:
            with st.spinner("ИИ-Механик анализирует данные..."):
                try:
                    # Подключение к прокси-серверу ProxyAPI
                    client = openai.OpenAI(
                        api_key=st.secrets["OPENAI_API_KEY"],
                        base_url="https://proxyapi.ru"
                    )
                    
                    system_prompt = (
                        "Ты — опытный автомеханик с 15-летним стажем. "
                        "Твоя задача — проанализировать текст и фото, присланные пользователем, и сделать первичную диагностику. "
                        "Отвечай структурно, выделяй важное жирным шрифтом:\n"
                        "1. Вероятная причина поломки.\n"
                        "2. Насколько это критично (можно ли ехать в сервис своим ходом).\n"
                        "3. Примерный план действий для водителя.\n"
                        "Пиши простым, понятным языком. В конце обязательно напомни, что точный диагноз ставится только в автосервисе на подъемнике."
                    )
                    
                    content_list = [{"type": "text", "text": f"Запрос пользователя: {user_text}"}]
                    
                    # Если загружено фото, кодируем его для ИИ
                    if uploaded_photo:
                        bytes_data = uploaded_photo.read()
                        base64_image = base64.b64encode(bytes_data).decode('utf-8')
                        content_list.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        })
                    
                    if uploaded_audio:
                        content_list.append({
                            "type": "text", 
                            "text": "[Пользователь также прикрепил аудиозапись шума/стука. Учти это при анализе.]"
                        })
                    
                    # Запрос к нейросети
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": content_list}
                        ],
                        max_tokens=600
                    )
                    
                    st.success("Анализ завершен!")
                    st.markdown(response.choices.message.content)
                    
                except Exception as e:
                    st.error(f"Ошибка при обработке запроса: {e}")