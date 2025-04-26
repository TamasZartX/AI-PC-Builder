import streamlit as st
import json
import io
import time
from ai_api import generate_response
import uuid  # Добавляем импорт модуля для генерации UUID

# Инициализация session_state
if "chats" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state.chats = {
        initial_id: {
            "name": "Новый чат",
            "messages": []
        }
    }
    st.session_state.current_chat = initial_id

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "current_edit_chat" not in st.session_state:
    st.session_state.current_edit_chat = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# Стилизация кнопок (остается без изменений)
st.markdown("""
    <style>
        .small-button {
            padding: 0.1rem 0.5rem !important;
            font-size: 0.8rem !important;
            height: 28px !important;
        }
        .loader {
            border: 3px solid #f3f3f3;
            border-radius: 50%;
            border-top: 3px solid #555;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
""", unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    st.header("История чатов")

    # Создание нового чата
    if st.button("➕ Новый чат"):
        new_id = str(uuid.uuid4())
        new_name = f"Чат {len(st.session_state.chats)}"
        st.session_state.chats[new_id] = {
            "name": new_name,
            "messages": []
        }
        st.session_state.current_chat = new_id
        st.rerun()

    # Список чатов
    for chat_id, chat_data in list(st.session_state.chats.items()):
        cols = st.columns([4, 1, 1, 1])
        chat_name = chat_data["name"]

        # Режим редактирования
        if st.session_state.edit_mode and st.session_state.current_edit_chat == chat_id:
            new_name = st.text_input("Новое название", value=chat_name, key=f"edit_{chat_id}")

            # Кнопки в одной строке
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Сохранить",
                            key=f"save_{chat_id}",
                            help="Сохранить изменения",
                            type="primary",
                            use_container_width=True):
                    if new_name and new_name != chat_name:
                        st.session_state.chats[chat_id]["name"] = new_name
                        st.session_state.edit_mode = False
                        st.rerun()
            with col2:
                if st.button("Отмена",
                             key=f"cancel_{chat_id}",
                             help="Отменить редактирование",
                             use_container_width=True):
                    st.session_state.edit_mode = False
                    st.rerun()
        else:
            with cols[0]:
                if st.button(chat_name,
                            key=f"btn_{chat_id}",
                            use_container_width=True,
                            help=f"Переключиться в чат {chat_name}"):
                    st.session_state.current_chat = chat_id

            with cols[1]:
                if st.button("✎",
                            key=f"edit_btn_{chat_id}",
                            help="Редактировать название"):
                    st.session_state.edit_mode = True
                    st.session_state.current_edit_chat = chat_id
                    st.rerun()

            with cols[2]:
                json_data = json.dumps(chat_data["messages"], ensure_ascii=False)
                st.download_button(
                    label="⤴",
                    data=json_data,
                    file_name=f"{chat_name}.json",
                    mime="application/json",
                    key=f"exp_{chat_id}",
                    help="Экспортировать чат"
                )

            with cols[3]:
                if st.button("🗑",
                            key=f"del_{chat_id}",
                            help="Удалить чат"):
                    del st.session_state.chats[chat_id]
                    if not st.session_state.chats:
                        new_id = str(uuid.uuid4())
                        st.session_state.chats[new_id] = {
                            "name": "Новый чат",
                            "messages": []
                        }
                    if st.session_state.current_chat == chat_id:
                        st.session_state.current_chat = next(iter(st.session_state.chats.keys()))
                    st.rerun()

# Основной интерфейс
current_chat_data = st.session_state.chats[st.session_state.current_chat]
st.title(f"💬 {current_chat_data['name']}")

# Отображение сообщений
for msg in current_chat_data["messages"]:
    align = "flex-end" if msg["role"] == "user" else "flex-start"
    bg_color = "#e8f5e9" if msg["role"] == "user" else "#f5f5f5"

    st.markdown(f"""
        <div style='display: flex; justify-content: {align}; margin: 5px 0;'>
            <div style='
                background: {bg_color};
                padding: 15px;
                border-radius: 15px;
                max-width: 90%;
                overflow-x: auto;
                font-family: Arial, sans-serif;
                color: #333;
            '>
                <style>
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                        font-size: 14px;
                    }}
                    th {{
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
                {msg["text"]}
            </div>
        </div>
    """, unsafe_allow_html=True)

# Индикатор загрузки
if st.session_state.processing:
    st.markdown("""
        <div style='display: flex; justify-content: center; margin: 20px 0;'>
            <div class="loader"></div>
        </div>
    """, unsafe_allow_html=True)

# Ввод сообщения
if prompt := st.chat_input("Введите сообщение..."):
    if not st.session_state.processing:
        st.session_state.processing = True
        current_chat_data["messages"].append({"role": "user", "text": prompt})
        current_chat_data["messages"].append({
            "role": "assistant",
            "text": "⏳ Обработка запроса..."
        })
        st.rerun()

# Обработка ответа
if (len(current_chat_data["messages"]) > 0 and
    current_chat_data["messages"][-1]["text"] == "⏳ Обработка запроса..."):
    
    reason = generate_response(current_chat_data["messages"][-2]["text"], st.session_state.current_chat)

    current_chat_data["messages"][-1] = {
        "role": "assistant",
        "text": reason
    }
    st.session_state.processing = False
    st.rerun()