import streamlit as st
import database_manager as db
import nlp_engine as nlp
import os

# Page Config
st.set_page_config(page_title="Lumina Library Chatbot", page_icon="📚", layout="centered")

# Custom CSS for "Lumina" aesthetics (Light Theme)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Background and typography */
    .stApp {
        background-color: #F8F9FA !important;
        font-family: 'Inter', sans-serif;
    }
    .title-text {
        text-align: center;
        color: #1A3C34;
        font-weight: 800;
        font-size: 2.8rem;
        margin-bottom: 0px;
        letter-spacing: -0.5px;
    }
    .subtitle-text {
        text-align: center;
        color: #8C9996;
        font-size: 1.1rem;
        margin-bottom: 40px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    
    /* Sidebar Styling */
    div[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAEAEA;
        padding-top: 2rem;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #148F77;
        color: white;
        border-radius: 8px;
        transition: all 0.2s ease;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #117864;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #EAEAEA;
    }
    
    /* Hide default elements for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Streamlit Chat Messages */
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #148F77 !important;
        color: #FFFFFF !important;
        border-radius: 16px 4px 16px 16px !important;
        padding: 16px !important;
        margin-left: 20% !important;
    }
    .stChatMessage[data-testid="chat-message-user"] p {
        color: #FFFFFF !important;
    }
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #FFFFFF !important;
        color: #2D3748 !important;
        border-radius: 4px 16px 16px 16px !important;
        border: 1px solid #F0F0F0 !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03) !important;
        padding: 16px !important;
        margin-right: 20% !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-text'>Lumina Library Chatbot 📚</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-text'>Your Intelligent Digital Assistant</div>", unsafe_allow_html=True)

# Initialize DB on first run if not exists
@st.cache_resource
def initialize_system():
    db.init_db()
    if os.path.exists("library_data.csv"):
        db.load_single_csv_to_db("library_data.csv")
    return True

initialize_system()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Lumina, your library assistant. How can I help you today?"}
    ]
if "username" not in st.session_state:
    st.session_state.username = None
if "teaching_question" not in st.session_state:
    st.session_state.teaching_question = None

# Sidebar for Login / Registration & Settings
with st.sidebar:
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'><img src='https://cdn-icons-png.flaticon.com/512/3389/3389081.png' width='80'></div>", unsafe_allow_html=True)
    
    if st.session_state.username is None:
        st.header("🔐 User Login")
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            log_user = st.text_input("Username", key="log_user")
            log_pass = st.text_input("Password", type="password", key="log_pass")
            if st.button("Login", use_container_width=True):
                if db.authenticate_user(log_user, log_pass):
                    st.session_state.username = log_user
                    st.success(f"Welcome back, {log_user}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            reg_user = st.text_input("New Username", key="reg_user")
            reg_pass = st.text_input("New Password", type="password", key="reg_pass")
            if st.button("Register", use_container_width=True):
                if reg_user and reg_pass:
                    if db.create_user(reg_user, reg_pass):
                        st.success("Registration successful! Please log in.")
                    else:
                        st.error("Username already exists.")
                else:
                    st.warning("Please enter username and password.")
                    
        st.markdown("---")
        st.info("💡 You are currently in Guest Mode. Chat history won't be saved.")
    else:
        st.header(f"👤 Welcome, {st.session_state.username}")
        if st.button("Logout", use_container_width=True):
            st.session_state.username = None
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I am Lumina, your library assistant. How can I help you today?"}
            ]
            st.rerun()
        
        st.markdown("---")
        st.success("✅ Logged in. Chat history is being saved securely.")
        
    st.markdown("---")
    st.header("⚙️ Database Settings")
    data_file = st.file_uploader("Upload Library Data CSV", type=["csv"])
    if st.button("Initialize & Load", use_container_width=True):
        db.init_db()
        data_path = None
        if data_file:
            data_path = "temp_library_data.csv"
            with open(data_path, "wb") as f:
                f.write(data_file.getbuffer())
        db.load_single_csv_to_db(data_path)
        st.success("Database successfully initialized and loaded!")
        if data_path and os.path.exists(data_path):
            os.remove(data_path)

# Load chat history if logged in
if st.session_state.username:
    history = db.get_chat_history(st.session_state.username)
    if history:
        st.session_state.messages = history
    elif len(st.session_state.messages) == 1:
        # Save the initial greeting to DB
        db.save_chat_message(st.session_state.username, "assistant", st.session_state.messages[0]["content"])
        
# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Helper function to add and save messages
def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})
    if st.session_state.username:
        db.save_chat_message(st.session_state.username, role, content)

# Process user input
if prompt := st.chat_input("Ask me about books, availability, or chat with me..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    add_message("user", prompt)

    response_content = ""
    
    # 1. Are we in "Teaching Mode"?
    if st.session_state.teaching_question:
        question = st.session_state.teaching_question
        answer = prompt
        db.add_to_knowledge_base(question, answer)
        response_content = f"✅ Thank you! I have successfully learned that when someone asks '{question}', I should answer '{answer}'."
        st.session_state.teaching_question = None
    
    else:
        # 2. Check trained knowledge base first
        kb_items = db.get_all_knowledge()
        kb_match = nlp.get_best_knowledge_match(prompt, kb_items)
        
        if kb_match:
            response_content = kb_match
        else:
            # 3. Process with NLP engine for library tasks
            intent, entity = nlp.extract_intent_and_entities(prompt)
            
            if intent == "search_title":
                results = db.search_books_by_title(entity)
                if results:
                    response_content = f"Here is what I found for '{entity}':\n"
                    for r in results:
                        response_content += f"- **{r[0]}** by {r[1]} ({r[2]})\n"
                else:
                    response_content = f"Sorry, I couldn't find any books with '{entity}' in the title."
                    
            elif intent == "search_author":
                results = db.search_books_by_author(entity)
                if results:
                    response_content = f"Here are books by '{entity}':\n"
                    for r in results:
                        response_content += f"- **{r[0]}** ({r[2]})\n"
                else:
                    response_content = f"Sorry, I couldn't find any books by '{entity}'."
                    
            elif intent == "recommend":
                results = db.get_recommendations_by_genre(entity)
                if results:
                    response_content = f"Here are some great '{entity}' recommendations:\n"
                    for r in results:
                        response_content += f"- **{r[0]}** by {r[1]}\n"
                else:
                    response_content = f"Sorry, I couldn't find recommendations for '{entity}' right now."
                    
            elif intent == "borrow_status":
                results = db.get_borrowing_status(entity)
                if results:
                    response_content = f"Here is the borrowing status for User {entity}:\n"
                    for r in results:
                        response_content += f"- **{r[0]}** (Due: {r[2]})\n"
                else:
                    response_content = f"No active borrowing records found for User {entity}."
            
            else:
                response_content = f"I'm not sure how to answer that yet! Can you teach me? Please type the correct answer for '{prompt}' below:"
                st.session_state.teaching_question = prompt

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response_content)
    add_message("assistant", response_content)
