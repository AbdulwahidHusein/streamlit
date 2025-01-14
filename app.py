import streamlit as st
import openai
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Configure OpenAI and page
st.set_page_config(layout="wide", page_title="SE vs CS Roast Battle", page_icon="🔥")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Custom CSS for chat interface
st.markdown("""
<style>
.chat-container {
    max-width: 900px;
    margin: auto;
    padding: 2rem;
    background-color: #1a1a1a;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.chat-message {
    padding: 1.2rem;
    border-radius: 20px;
    margin-bottom: 1.5rem;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    animation: fadeIn 0.5s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.cs-message {
    background: linear-gradient(135deg, #614385 0%, #516395 100%);
    margin-right: 25%;
    color: white;
    border-bottom-left-radius: 5px;
    transform-origin: left;
}
.se-message {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    margin-left: 25%;
    color: white;
    border-bottom-right-radius: 5px;
    transform-origin: right;
}
.message-header {
    font-size: 0.9rem;
    margin-bottom: 0.7rem;
    color: rgba(255,255,255,0.9);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.message-content {
    font-size: 1.1rem;
    line-height: 1.5;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}
.stButton button {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border-radius: 30px;
    padding: 0.7rem 2.5rem;
    font-weight: 600;
    border: none;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stButton button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}
.main-title {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 800;
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    letter-spacing: 2px;
}
.typing-indicator {
    padding: 0.8rem 1.5rem;
    background: rgba(255,255,255,0.1);
    border-radius: 25px;
    color: #fff;
    font-size: 0.9rem;
    margin: 0.8rem 0;
    display: inline-block;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0% { opacity: 0.5; }
    50% { opacity: 1; }
    100% { opacity: 0.5; }
}
.stop-button button {
    background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%) !important;
}
.start-button button {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
}
.stApp {
    background: linear-gradient(135deg, #141E30 0%, #243B55 100%);
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'debate_history' not in st.session_state:
    st.session_state.debate_history = []
if 'debate_running' not in st.session_state:
    st.session_state.debate_running = False
if 'is_typing' not in st.session_state:
    st.session_state.is_typing = None

MAX_TOTAL_MESSAGES = 40
MAX_CONTEXT_LENGTH = 6
TYPING_DELAY = 6  # Seconds between messages

SE_PROMPT = """You are 'The SW Guy' - a savage software engineer who loves roasting CS theorists. Your style is:
- Brutally funny but clever
- Uses lots of industry/practical jokes
- Makes fun of theoretical knowledge vs real-world experience
- References famous tech companies and real products
- Always includes at least one 🔥 emoji for burns
- Keeps responses short and punchy (2-3 lines max)
- Uses modern tech slang and memes

Example tone: "While you're still debugging your bubble sort homework, I just shipped 3 apps to production. But hey, 
at least you can write that algorithm on a whiteboard! 🔥"

Remember: Be savage but funny, not mean. Make it feel like a rap battle between friends."""

CS_PROMPT = """You are 'The CSE Guy' - a theoretical computer science genius who roasts 'code monkeys'. Your style is:
- Intellectually savage but witty
- Uses complex CS concepts as burns
- Makes fun of 'simple' coding vs 'real' computer science
- References famous algorithms and theoretical breakthroughs
- Always includes at least one 🧮 emoji
- Keeps responses short and sharp (2-3 lines max)
- Uses nerdy references and academic humor

Example tone: "Aww, look who's proud of their CRUD app! Call me when you've solved P=NP. 
Until then, keep copy-pasting from Stack Overflow! 🧮"

Remember: Be intellectually savage but funny, not arrogant. Make it feel like a rap battle between friends."""

def get_ai_response(prompt, debate_history, system_prompt):
    """Get response from GPT-4 based on the conversation history"""
    recent_history = debate_history[-MAX_CONTEXT_LENGTH:] if len(debate_history) > MAX_CONTEXT_LENGTH else debate_history
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in recent_history:
        messages.append({"role": "assistant", "content": msg})
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1.0,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def display_message(message, is_se=True):
    """Display a chat message with proper styling"""
    class_name = "se-message" if is_se else "cs-message"
    role = "The SW Guy 🛠️" if is_se else "The CSE Guy 🧮"
    
    st.markdown(f"""
    <div class="chat-message {class_name}">
        <div class="message-header">{role}</div>
        <div class="message-content">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def display_typing(is_se=True):
    """Display typing indicator"""
    role = "The SW Guy" if is_se else "The CSE Guy"
    st.markdown(f"""
    <div class="typing-indicator">
        {role} is cooking up a roast... 🔥
    </div>
    """, unsafe_allow_html=True)

# Streamlit UI
st.markdown('<h1 class="main-title">🔥 SW vs CS: Ultimate Roast Battle!</h1>', unsafe_allow_html=True)

# Control buttons in columns
col1, col2 = st.columns(2)

with col1:
    start_button = st.empty()
    if start_button.button("Start New Battle 🔥", key="start_button"):
        st.session_state.debate_history = []
        st.session_state.debate_running = True

with col2:
    stop_button = st.empty()
    if stop_button.button("End Battle 🚫", key="stop_button"):
        st.session_state.debate_running = False

# Create a container for the debate
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Auto-continue the debate if it's running
    if st.session_state.debate_running:
        if len(st.session_state.debate_history) >= MAX_TOTAL_MESSAGES:
            st.session_state.debate_running = False
            st.warning("Battle reached maximum length! Start a new one to continue the roast! 🔥")
        else:
            # Display all previous messages
            for i, msg in enumerate(st.session_state.debate_history):
                display_message(msg, is_se=(i % 2 == 0))
            
            if not st.session_state.debate_history:
                # Show SE typing indicator
                st.session_state.is_typing = "SE"
                display_typing(True)
                time.sleep(TYPING_DELAY)
                
                # Initial response from SE
                se_response = get_ai_response(
                    "Start the roast battle! Give your best shot at roasting CS students!",
                    st.session_state.debate_history,
                    SE_PROMPT
                )
                st.session_state.debate_history.append(se_response)
                st.session_state.is_typing = None
                display_message(se_response, True)
                time.sleep(2)
                
                # Show CS typing indicator
                st.session_state.is_typing = "CS"
                display_typing(False)
                time.sleep(TYPING_DELAY)
                
                # CS response
                cs_response = get_ai_response(
                    f"The SW guy just roasted you with: '{se_response}' Now destroy them with your theoretical knowledge!",
                    st.session_state.debate_history,
                    CS_PROMPT
                )
                st.session_state.debate_history.append(cs_response)
                st.session_state.is_typing = None
                display_message(cs_response, False)
            else:
                last_msg = st.session_state.debate_history[-1]
                
                # Show SE typing indicator
                st.session_state.is_typing = "SE"
                display_typing(True)
                time.sleep(TYPING_DELAY)
                
                # SE response
                se_response = get_ai_response(
                    f"The CSE guy just roasted you with: '{last_msg}' Now destroy them with your practical experience!",
                    st.session_state.debate_history,
                    SE_PROMPT
                )
                st.session_state.debate_history.append(se_response)
                st.session_state.is_typing = None
                display_message(se_response, True)
                time.sleep(2)
                
                # Show CS typing indicator
                st.session_state.is_typing = "CS"
                display_typing(False)
                time.sleep(TYPING_DELAY)
                
                # CS response
                cs_response = get_ai_response(
                    f"The SW guy just roasted you with: '{se_response}' Now obliterate them with your CS knowledge!",
                    st.session_state.debate_history,
                    CS_PROMPT
                )
                st.session_state.debate_history.append(cs_response)
                st.session_state.is_typing = None
                display_message(cs_response, False)
            
            time.sleep(2)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True) 