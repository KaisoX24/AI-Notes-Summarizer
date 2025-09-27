from groq import Groq
import streamlit as st
import os
import PyPDF2
from dotenv import load_dotenv
from supabase import create_client,Client

# Loading environment variables
load_dotenv()
supabase_url=os.getenv('Supa_base_url')
supabase_key=os.getenv('Supa_base_API_KEY')
supabase: Client=create_client(supabase_url,supabase_key)

client=Groq(
    api_key=os.getenv('GROQ_API_KEY')
)


def signup(email,password):
    try:
        user=supabase.auth.sign_up({'email':email,'password':password})
        return user
    except Exception as e:
        st.error(f'Registration Failed: {e}')

def signin(email,password):
    try:
        user=supabase.auth.sign_in_with_password({'email':email,'password':password})
        return user
    except Exception as e:
        st.error(f'Sign in Failed: {e}')

def signout():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email=None
        st.rerun()
    except Exception as e:
        st.error(f'Sign out Failed: {e}')

# Function to summarize text and generate quiz questions
def summarize_text(prompt):
    try:
        response = client.chat.completions.create(
            model='openai/gpt-oss-20b',
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert educational assistant. "
                        "Your tasks are:\n"
                        "1. Summarize the provided notes in a clear and concise way.\n"
                        "2. Use easy-to-understand language suitable for students.\n"
                        "3. Present the summary in bullet points with logical flow.\n"
                        "4. Highlight key terms, formulas, or definitions clearly.\n"
                        "5. At the end, generate 3-5 multiple choice questions (MCQs) "
                        "for revision. Each MCQ should:\n"
                        "   - Have one correct answer and 3 distractors.\n"
                        "   - Be directly based on the summary.\n"
                        "   - Provide the correct answer after the options."
                    )
                },
                {
                    "role": "user",
                    "content": f"Here are the notes to process:\n\n{prompt}"
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Cant Summarize at the Moment"
    
# Streamlit UI
def main_app(user):
    st.set_page_config(page_title='Notes Summarizer and Quizer', page_icon=':books:',layout='wide')
    st.title('Notes Summarizer and Quizer :books:')
    st.write('---')

    st.sidebar.header('Upload your notes 📝')
    st.sidebar.write('---')
    uploaded_file=st.sidebar.file_uploader('Upload a PDF file containing your notes ⬇️', type=['pdf'])

    # Process the uploaded file
    if uploaded_file is not None:
        with st.spinner('Processing your notes...'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            summary = summarize_text(text)
            
        st.subheader('Summary and Quiz')
        st.markdown(summary)
        
        # Download button
        st.download_button(
            label='Download Summary and Quiz',
            data=summary,
            file_name='summary_and_quiz.txt',
            mime='application/plain'
        )
        if st.sidebar.button('Logout'):
            signout()

def auth_screen():
    st.set_page_config(layout='centered')
    st.title('WELCOME TO USER AUTHETICATION')
    option=st.selectbox('Choose action:',['Login','Sign Up'])
    email=st.text_input('Enter your email')
    passw=st.text_input('Password',type='password')
    if option=='Sign Up' and st.button('Register'):
        user=signup(email,passw)
        if user and user.user:
            st.success('Registration Successful. Please confrim the email')
            st.markdown('Confirmation Email has been sent')

    elif option=='Login' and st.button('Login'):
        user=signin(email,passw)
        if user and user.user:
            st.session_state.user_email=user.user.email
            st.success(f'Welcome back {email}')
            st.rerun()

if 'user_email' not in st.session_state:
    st.session_state.user_email=None

if st.session_state.user_email:
    main_app(st.session_state.user_email)
else:
    auth_screen()
