import os
from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()

# Works both locally (.env) and on Streamlit Cloud (Secrets)
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is missing. Please add it in Streamlit Secrets or your .env file.")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"   # Current working free model

# ============================================================
# KNOWLEDGE BASE
# ============================================================
KNOWLEDGE = """
Ausome Learning Minds is a specialised homeschooling and tutoring centre in Brackenhurst, Alberton, South Africa.
Address: 17 Toinette Street, Ext 2, Brackenhurst, Alberton, 1448
Registered with Impaq as a curriculum services provider.

We specialise in children with diverse learning needs including autism, ADHD, dyslexia, developmental delays, speech and language difficulties, and other special educational needs.

CONTACT
Phone: 064 909 7710 / 064 510 9728
Email: info@ausomelearningminds.co.za
Working hours: Monday–Friday 07:45–14:00 (aftercare until 18:00). Closed weekends.

FEES (2027)
- Registration (once-off, non-refundable, includes two assessments): R1 000
- Centre / school fees: R5 000 per month
- Aftercare: R1 200 per month

PROGRAMMES & HOURS
- Grade RR to Grade 7 following CAPS and DCAPS curriculum
- Main school hours: Mon–Thu 08:00–13:30, Fri 08:00–13:00
- Aftercare: Mon–Fri 14:00–18:00
- Individual remedial therapy
- Nature-based learning approach
- Robotics for kids
- Extra lessons in Maths and Afrikaans
- Extra-mural activities (coding, robotics, swimming, soccer, volleyball, basketball) – available at additional cost
- Occupational and speech therapy support integrated into the programme
- Parent support, progress updates, meetings and workshops

APPROACH
- Small class / group sizes for individual attention
- Play-based, sensory-friendly and personalised teaching
- Strong focus on safety, confidence-building and holistic development
- Staff trained to support ADHD, autism, dyslexia and other learning needs

ENROLMENT
- Enrolment for 2027 is open
- Application forms available on the website (ausomelearningminds.co.za)
- Tours of the centre are strongly encouraged
- You can register by calling, emailing, or visiting the centre

KEY FAQ ANSWERS
- Who can enrol? Children with diverse learning needs (autism, ADHD, developmental delays, speech difficulties, etc.).
- Do you involve parents? Yes – regular progress updates, parent-teacher meetings and workshops.
- Safety? Top priority. Staff trained in child protection and first aid. Classrooms and play areas are secure.
- Class sizes? Kept deliberately small so every child receives focused support.
"""

SYSTEM_PROMPT = f"""
You are the friendly and helpful FAQ assistant for Ausome Learning Minds, a specialised learning centre in Alberton for children with special educational needs.

RULES:
1. Answer ONLY using the knowledge provided below. Do not invent any information.
2. Be warm, clear, concise and parent-friendly. Use South African English and the Rand (R).
3. If the question is outside the knowledge or you are unsure, reply exactly:
   "I'm not sure about that specific detail. Please contact us on 064 909 7710 / 064 510 9728 or email info@ausomelearningminds.co.za and our team will gladly help you."
4. Always offer the contact numbers when it feels natural.
5. Never give medical, diagnostic or therapeutic advice beyond what is stated in the knowledge.

KNOWLEDGE:
{KNOWLEDGE}
"""

# ============================================================
# STREAMLIT UI
# ============================================================
st.set_page_config(
    page_title="Ausome Learning Minds FAQ",
    page_icon="🧠",
    layout="centered"
)
st.markdown("""
<style>
    /* Change the main font for the whole app */
    html, body, [class*="css"] {
        font-family: 'Quicksand Book Oblique', sans-serif;
    }

    /* Optional: Make the title bigger / different */
    h1 {
        font-family: 'Georgia', serif;
        font-weight: 700;
    }

    /* Optional: Style the chat messages */
    .stChatMessage {
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)
st.title("🧠 Ausome Learning Minds")
st.caption("FAQ Assistant – Ask anything about our programmes, fees, enrolment or approach")

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! 👋 I'm the Ausome Learning Minds assistant. How can I help you today? You can ask about fees, programmes, enrolment, aftercare, or anything else."}
    ]

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for the LLM
    llm_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in st.session_state.messages:
        llm_messages.append({"role": m["role"], "content": m["content"]})

    # Call the LLM
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=llm_messages,
                    temperature=0.3,          # low temperature = more consistent answers
                    max_tokens=600
                )
                reply = response.choices[0].message.content
            except Exception as e:
                reply = f"Sorry, something went wrong connecting to the AI service.\n\nError: {str(e)}"

        st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})