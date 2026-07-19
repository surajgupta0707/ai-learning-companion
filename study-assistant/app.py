import os
import time
import streamlit as st
import PyPDF2
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# 1. Load API Key Securely
load_dotenv(find_dotenv(), override=True)
my_key = os.getenv("GOOGLE_API_KEY")

# 2. Configure the Website Layout
st.set_page_config(page_title="AI Study Assistant", page_icon="📚", layout="centered")
st.title("📚 My AI Study Assistant")

if not my_key:
    st.error("❌ Cannot find the API Key. Please check your .env file.")
    st.stop()

# 3. Initialize the AI Brain
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.2,
    api_key=my_key
)

# 4. PROFESSIONAL UPLOAD & VECTOR DATABASE SECTION 
with st.expander("⚙️ Document Settings & Uploads", expanded=False):
    st.markdown("Upload your massive textbooks here. The AI will chunk and index them for rapid searching.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_files = st.file_uploader("Attach PDFs", type="pdf", accept_multiple_files=True, label_visibility="collapsed")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True) 
        if st.button("🗑️ Clear Chat & Memory", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.vector_store = None 
            st.session_state.indexed_files = [] # Clears the file tracker too!
            st.rerun()

# Process PDFs and Build the Vector Database with Smart Memory
if uploaded_files:
    # A. Create a list of the file names currently in the uploader
    current_file_names = [file.name for file in uploaded_files]
    
    # B. Check if these files are different from what is already in memory
    if "indexed_files" not in st.session_state or st.session_state.indexed_files != current_file_names:
        
        pdf_text = ""
        for file in uploaded_files:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted + "\n"
        
        if pdf_text:
            with st.spinner("New files detected! Updating the Vector Database..."):
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                text_chunks = text_splitter.split_text(pdf_text)
                
                embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=my_key)
                
                vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
                
                # Save the new database AND remember the new file names
                st.session_state.vector_store = vector_store
                st.session_state.indexed_files = current_file_names
                
            st.success(f"✅ {len(uploaded_files)} document(s) successfully indexed! Ready to search.")
        else:
            st.error("⚠️ We couldn't find any readable text in this PDF! It might be a scanned image or presentation slides.")

# 5. Create a "Memory Bank" for the chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 6. Draw all previous messages on the screen
for msg in st.session_state.chat_history:
    if not isinstance(msg, SystemMessage):
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

# 7. The Chat Input box with RAG (Retrieval-Augmented Generation)
user_input = st.chat_input("Ask a study question...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append(HumanMessage(content=user_input))

    with st.chat_message("assistant"):
        messages_to_send = []
        
        status_box = st.empty()
        status_box.info("🔍 Searching database for relevant context...")
        
        # SEARCH THE DATABASE FIRST
        if "vector_store" in st.session_state and st.session_state.vector_store is not None:
            # Find the top 3 most relevant paragraphs to the user's specific question
            relevant_chunks = st.session_state.vector_store.similarity_search(user_input, k=3)
            
            # Combine those paragraphs into a single context string
            context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
            
            secret_instruction = f"You are a highly precise study tutor. Answer the user's question based strictly on this specific document context:\n\n{context}"
            messages_to_send.append(SystemMessage(content=secret_instruction))
        
        messages_to_send.extend(st.session_state.chat_history)
        
        def stream_cleaner():
            first_letter_typed = False
            for chunk in llm.stream(messages_to_send):
                if not first_letter_typed:
                    status_box.empty()
                    first_letter_typed = True
                    
                if chunk.content:
                    if isinstance(chunk.content, list):
                        text_chunk = chunk.content[0].get('text', '')
                    else:
                        text_chunk = chunk.content
                    
                    for char in text_chunk:
                        yield char
                        time.sleep(0.005)
        
        full_answer = st.write_stream(stream_cleaner())
    
    st.session_state.chat_history.append(AIMessage(content=full_answer))