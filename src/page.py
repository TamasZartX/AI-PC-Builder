import streamlit as st
from ai_api import generate_response
from uuid import uuid4

# Инициализация session_state
if "chats" not in st.session_state:
    st.session_state.chats = {"Новый чат": {"msg": [], "session_id": str(uuid4())}}
    st.session_state.current_chat = "Новый чат"
    
if "sidebar_expanded" not in st.session_state:
    st.session_state.sidebar_expanded = True
    
# Настройки страницы
st.set_page_config(page_title="Компьютенатор", layout="wide")

# Стилизация
st.markdown("""
    <style>
        .css-1aumxhk {display: none} /* Убирает кнопку "Made with Streamlit"
    </style>
""", unsafe_allow_html=True)

# Боковая панель
if st.session_state.sidebar_expanded:
    with st.sidebar:
        st.title("📂 История чатов")
        #if st.button("🔽 Свернуть / Развернуть панель"):
        #    st.session_state.sidebar_expanded = False
        #    st.rerun()
        selected_chat = st.radio("Выберите чат", list(st.session_state.chats.keys()))

        col1, col2 = st.columns([2, 1])
        if col1.button("➕ Новый чат"):
            new_chat_name = f"Чат {len(st.session_state.chats)}"
            st.session_state.chats[new_chat_name] = {"msg": [], "session_id": str(uuid4())}
            st.session_state.current_chat = new_chat_name
            st.rerun()
        if col2.button("🗑 Удалить чат"):
            if selected_chat in st.session_state.chats:
                del st.session_state.chats[selected_chat]
                if not st.session_state.chats:
                    st.session_state.chats["Новый чат"] = {"msg": [], "session_id": str(uuid4())}
                st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                st.rerun()
#else:
#    if st.button("🔼 Развернуть боковую панель"):
#        st.session_state.sidebar_expanded = True
#        st.rerun()
        
st.session_state.current_chat = selected_chat if st.session_state.sidebar_expanded else st.session_state.current_chat

# Заголовок
st.title("Компьютенатор")

# Вывод истории сообщений текущего чата
st.write(f"### {st.session_state.current_chat}")
chat_history = st.session_state.chats[st.session_state.current_chat]["msg"]

for message in chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

if prompt := st.chat_input("Behold, Perry the Platopus! I'm Computenator"):
    # Добавляем сообщение пользователя в историю текущего чата
    chat_history.append({"role": "user", "text": prompt})
    
    message_placeholder = st.empty()
    with st.spinner(text="Thinking..."):
        response = generate_response(prompt, st.session_state.chats[st.session_state.current_chat]["session_id"])
        message_placeholder.markdown(response)
    chat_history.append({"role": "assistant", "text": response})
        
    # Обновляем страницу
    st.rerun()