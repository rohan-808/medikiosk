import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import pytesseract
import google.generativeai as genai

# Try importing speech recognition (optional)
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False

# Set Tesseract path for Windows
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ============================================
# CONFIGURE GEMINI API
# ============================================
# Replace with your API key
GEMINI_API_KEY = "YOUR_API_KEY_HERE"  # ← PUT YOUR API KEY HERE

if GEMINI_API_KEY != "AQ.Ab8RN6LqdpHnhVhXza5uubagba9RBS4Ll_GoLhj2asQl5nPSAg":
    genai.configure(api_key=GEMINI_API_KEY)
    AI_AVAILABLE = True
    model = genai.GenerativeModel('gemini-pro')
else:
    AI_AVAILABLE = False

# ============================================
# AI FUNCTIONS
# ============================================
def generate_clinical_summary(patient_data, documents=None):
    """Use AI to generate professional clinical summary"""
    
    if not AI_AVAILABLE:
        return generate_manual_summary(patient_data)
    
    prompt = f"""
    You are a medical AI assistant. Generate a professional clinical history summary 
    based on the following patient data. Format it as a structured medical note.

    PATIENT DATA:
    - Chief Complaint: {patient_data.get('chief_complaint', 'Not provided')}
    - Duration: {patient_data.get('duration', 'Not provided')}
    - Severity: {patient_data.get('severity', 'Not provided')}
    - Associated Symptoms: {', '.join(patient_data.get('symptoms', []))}
    - Past Medical History: {', '.join(patient_data.get('past_history', []))}
    - Medications: {patient_data.get('medications', 'None')}
    - Allergies: {patient_data.get('allergies', 'None')}
    - Family History: {', '.join(patient_data.get('family_history', []))}

    Please provide:
    1. **Clinical Summary**: A concise paragraph summarizing the patient's condition
    2. **Key Concerns**: List 2-3 important clinical observations
    3. **Suggested Questions**: 3 questions the doctor should ask
    4. **Red Flags**: Any warning signs that need immediate attention
    5. **Differential Diagnosis**: 2-3 possible conditions to consider

    Format with clear headings and bullet points.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return generate_manual_summary(patient_data)

def generate_manual_summary(patient_data):
    """Fallback manual summary if AI not available"""
    summary = f"""
### Clinical Summary
Patient presents with {patient_data.get('chief_complaint', 'unknown complaint')} 
for duration of {patient_data.get('duration', 'unknown duration')}.

### Key Concerns
- Chief complaint: {patient_data.get('chief_complaint', 'Not specified')}
- Duration: {patient_data.get('duration', 'Not specified')}

### Red Flags
- Check for emergency signs manually
"""
    return summary

def analyze_complaint_with_ai(complaint):
    """Use AI to analyze chief complaint and suggest follow-up questions"""
    
    if not AI_AVAILABLE:
        return None
    
    prompt = f"""
    A patient reports: "{complaint}"
    
    As a medical AI, analyze this complaint and provide:
    1. **Severity Assessment**: Is this potentially serious? (Low/Medium/High/Emergency)
    2. **Key Questions**: What 3 essential questions should we ask?
    3. **Possible Systems**: Which body systems might be involved?
    
    Keep response brief and structured.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None

def detect_red_flags_with_ai(chief_complaint, symptoms, duration):
    """Use AI to detect potential red flags"""
    
    if not AI_AVAILABLE:
        return []
    
    prompt = f"""
    Patient reports:
    - Chief Complaint: {chief_complaint}
    - Symptoms: {', '.join(symptoms) if symptoms else 'None'}
    - Duration: {duration}
    
    Identify any RED FLAGS that require immediate medical attention.
    List them as bullet points. If none, say "No immediate red flags."
    
    Be specific and actionable.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Unable to analyze red flags. Please assess manually."

# ============================================
# VOICE INPUT FUNCTION
# ============================================
def record_voice(language='en-IN'):
    """Record voice and convert to text"""
    if not SPEECH_AVAILABLE:
        return None, "Speech recognition not available."
    
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            st.info("🎤 Listening... Speak now")
            r.adjust_for_ambient_noise(source, duration=1)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        
        st.info("🔄 Processing speech...")
        
        try:
            text = r.recognize_google(audio, language=language)
            return text, None
        except sr.UnknownValueError:
            return None, "Could not understand audio."
        except sr.RequestError as e:
            return None, f"Speech service error: {e}"
    
    except Exception as e:
        return None, f"Error: {e}"

# ============================================
# DOCUMENT OCR FUNCTION
# ============================================
def extract_text_from_image(image):
    """Extract text from image using OCR"""
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error: {e}"

def analyze_document_with_ai(text):
    """Use AI to analyze medical document text"""
    
    if not AI_AVAILABLE or len(text) < 10:
        return {}
    
    prompt = f"""
    Analyze this medical document text and extract:
    1. **Medications**: List all medications with dosages
    2. **Diagnoses**: Any medical conditions mentioned
    3. **Lab Values**: Any test results with values
    4. **Doctor's Name**: If mentioned
    5. **Date**: Document date if visible
    
    DOCUMENT TEXT:
    {text[:1000]}
    
    Format as structured JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        return {'analysis': response.text}
    except:
        return {}

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="MediKiosk - AI Clinical Assistant",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'voice_lang' not in st.session_state:
    st.session_state.voice_lang = "en-IN"
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = None
if 'ai_summary' not in st.session_state:
    st.session_state.ai_summary = None

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("🤖 MediKiosk AI")
    
    # AI Status
    if AI_AVAILABLE:
        st.success("✅ AI Engine: Online")
        st.write("Powered by Google Gemini")
    else:
        st.warning("⚠️ AI Engine: Offline")
        st.info("Add your Gemini API key to enable AI features")
    
    st.markdown("---")
    
    st.markdown("### Features")
    st.write("• 🎤 Voice Input")
    st.write("• 📄 Document OCR")
    st.write("• 🧠 AI Analysis")
    st.write("• 🚨 Smart Red Flags")
    st.write("• 📋 AI Summaries")
    
    st.markdown("---")
    st.markdown("### Patient Journey")
    journey_progress = st.session_state.step
    st.progress(journey_progress / 5)
    
    steps = {
        1: "📍 Step 1: Consent",
        2: "📍 Step 2: Chief Complaint",
        3: "📍 Step 3: Detailed History",
        4: "📍 Step 4: Documents",
        5: "📍 Step 5: AI Summary"
    }
    st.write(steps.get(journey_progress, "Complete"))
    
    st.markdown("---")
    st.markdown("**Version:** 0.3 AI Enhanced")

# ============================================
# MAIN TITLE
# ============================================
st.title("🏥 MediKiosk")
st.markdown("### AI-Powered Clinical History Assistant")
st.markdown("---")

# ============================================
# STEP 1: Welcome & Consent
# ============================================
if st.session_state.step == 1:
    st.markdown("## Step 1: Welcome")
    st.markdown("---")
    
    # Language selection
    st.markdown("### Select Your Language / अपनी भाषा चुनें")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🇬🇧 English", use_container_width=True, type="primary"):
            st.session_state.language = "English"
            st.session_state.patient_data['language'] = "English"
            st.session_state.voice_lang = "en-IN"
            st.success("English selected")
    
    with col2:
        if st.button("🇮🇳 हिंदी", use_container_width=True):
            st.session_state.language = "Hindi"
            st.session_state.patient_data['language'] = "Hindi"
            st.session_state.voice_lang = "hi-IN"
            st.success("हिंदी चयनित")
    
    with col3:
        if st.button("🇮🇳 தமிழ்", use_container_width=True):
            st.session_state.language = "Tamil"
            st.session_state.patient_data['language'] = "Tamil"
            st.session_state.voice_lang = "ta-IN"
            st.success("தமிழ் தேர்ந்தெடுக்கப்பட்டது")
    
    st.markdown("---")
    
    # Consent
    st.markdown("### Patient Consent")
    st.info(
        """
        I understand that:
        1. My health information will be recorded digitally
        2. AI will assist in analyzing my symptoms
        3. This information will be shared with my physician
        4. My data will be stored securely
        5. I can withdraw consent at any time
        """
    )
    
    consent_given = st.checkbox("I give my consent to proceed")
    
    if consent_given:
        if st.button("Start →", type="primary", use_container_width=True):
            st.session_state.patient_data['consent_given'] = True
            st.session_state.patient_data['consent_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.step = 2
            st.rerun()
    else:
        st.warning("⚠️ Please provide consent")

# ============================================
# STEP 2: Chief Complaint
# ============================================
elif st.session_state.step == 2:
    st.markdown("## Step 2: What is your main problem?")
    st.markdown("---")
    
    # Voice input
    st.markdown("### 🎤 Speak Your Problem")
    
    if st.button("🎤 Click to Speak", type="primary", use_container_width=True):
        text, error = record_voice(st.session_state.voice_lang)
        if error:
            st.error(error)
        elif text:
            st.session_state.patient_data['chief_complaint'] = text
            st.success(f"Recognized: {text}")
            
            # AI Analysis of complaint
            if AI_AVAILABLE:
                with st.spinner("🤖 AI analyzing your complaint..."):
                    analysis = analyze_complaint_with_ai(text)
                    if analysis:
                        st.session_state.ai_analysis = analysis
                        with st.expander("🤖 AI Analysis"):
                            st.markdown(analysis)
            
            st.session_state.step = 3
            st.rerun()
    
    st.markdown("---")
    
    # Quick selection
    st.markdown("### Quick Selection")
    
    col1, col2, col3 = st.columns(3)
    
    complaints = {
        "💔 Chest Pain": "Chest Pain",
        "🤕 Headache": "Headache",
        "🤒 Fever": "Fever",
        "😤 Breathing Issue": "Breathing Difficulty",
        "🤢 Nausea": "Nausea/Vomiting",
        "🦴 Joint Pain": "Joint Pain"
    }
    
    for i, (label, value) in enumerate(complaints.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.patient_data['chief_complaint'] = value
                
                # AI Analysis
                if AI_AVAILABLE:
                    with st.spinner("🤖 AI analyzing..."):
                        analysis = analyze_complaint_with_ai(value)
                        if analysis:
                            st.session_state.ai_analysis = analysis
                
                st.session_state.step = 3
                st.rerun()
    
    st.markdown("---")
    
    # Free text
    st.markdown("### Or Type")
    chief_complaint = st.text_area(
        "Describe your problem:",
        placeholder="Example: I have severe headache since morning with nausea...",
        height=100
    )
    
    if chief_complaint:
        if st.button("Analyze with AI →", type="primary", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = chief_complaint
            
            # AI Analysis
            if AI_AVAILABLE:
                with st.spinner("🤖 AI analyzing your complaint..."):
                    analysis = analyze_complaint_with_ai(chief_complaint)
                    if analysis:
                        st.session_state.ai_analysis = analysis
                        with st.expander("🤖 AI Analysis of Your Complaint"):
                            st.markdown(analysis)
            
            st.session_state.step = 3
            st.rerun()

# ============================================
# STEP 3: Detailed History
# ============================================
elif st.session_state.step == 3:
    chief_complaint = st.session_state.patient_data.get('chief_complaint', '')
    
    st.markdown("## Step 3: Detailed History")
    st.markdown(f"### Chief Complaint: **{chief_complaint}**")
    
    # Show AI Analysis if available
    if st.session_state.ai_analysis:
        with st.expander("🤖 AI Insights (Click to view)"):
            st.markdown(st.session_state.ai_analysis)
    
    st.markdown("---")
    
    # Duration
    st.markdown("### ⏰ Duration")
    duration_options = ["Today", "1-2 days", "3-5 days", "1-2 weeks", "More than a month"]
    duration = st.radio("How long?", duration_options, horizontal=True)
    st.session_state.patient_data['duration'] = duration
    
    st.markdown("---")
    
    # Severity
    if any(word in chief_complaint.lower() for word in ['pain', 'ache', 'headache']):
        st.markdown("### 📊 Severity")
        severity = st.slider("Pain level (1-10)", 1, 10, 5)
        st.session_state.patient_data['severity'] = severity
        st.progress(severity / 10)
        st.markdown("---")
    
    # Symptoms
    st.markdown("### 🔍 Associated Symptoms")
    symptom_options = [
        "Nausea", "Dizziness", "Sweating", "Shortness of breath",
        "Cough", "Body ache", "Fatigue", "Loss of appetite",
        "Sleep disturbance", "None"
    ]
    symptoms = st.multiselect("Select symptoms:", symptom_options)
    st.session_state.patient_data['symptoms'] = symptoms
    
    st.markdown("---")
    
    # Past history
    st.markdown("### 📋 Past Medical History")
    condition_options = [
        "Diabetes", "High Blood Pressure", "Heart Disease", "Asthma",
        "Thyroid Problems", "Kidney Disease", "Liver Disease", "None"
    ]
    conditions = st.multiselect("Select conditions:", condition_options)
    st.session_state.patient_data['past_history'] = conditions
    
    st.markdown("---")
    
    # Medications
    st.markdown("### 💊 Medications")
    medications = st.text_input("Current medications (comma separated):")
    st.session_state.patient_data['medications'] = medications
    
    st.markdown("---")
    
    # Allergies
    st.markdown("### ⚠️ Allergies")
    allergy_options = ["Penicillin", "Sulfa drugs", "Aspirin", "Other", "No known allergies"]
    allergies = st.radio("Drug allergies:", allergy_options, horizontal=True)
    st.session_state.patient_data['allergies'] = allergies
    
    st.markdown("---")
    
    # Family history
    st.markdown("### 👨‍👩‍👧 Family History")
    family_options = [
        "Heart disease", "Diabetes", "Cancer", 
        "No significant family history"
    ]
    family_history = st.multiselect("Family history:", family_options)
    st.session_state.patient_data['family_history'] = family_history
    
    st.markdown("---")
    
    if st.button("Next →", type="primary", use_container_width=True):
        st.session_state.step = 4
        st.rerun()

# ============================================
# STEP 4: Document Upload
# ============================================
elif st.session_state.step == 4:
    st.markdown("## Step 4: Upload Documents")
    st.markdown("---")
    
    uploaded_files = st.file_uploader(
        "Upload prescriptions or lab reports",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in [doc['filename'] for doc in st.session_state.documents]:
                
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    
                    if uploaded_file.type in ['image/jpeg', 'image/png', 'image/jpg']:
                        image = Image.open(uploaded_file)
                        st.image(image, caption=uploaded_file.name, width=300)
                        
                        extracted_text = extract_text_from_image(image)
                        
                        # AI Analysis of document
                        ai_doc_analysis = analyze_document_with_ai(extracted_text) if AI_AVAILABLE else {}
                        
                        document_data = {
                            'filename': uploaded_file.name,
                            'type': 'image',
                            'extracted_text': extracted_text[:500],
                            'ai_analysis': ai_doc_analysis,
                            'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        st.session_state.documents.append(document_data)
                        
                        with st.expander(f"📄 {uploaded_file.name} - Extracted"):
                            st.text(extracted_text[:300])
                            if ai_doc_analysis:
                                st.markdown("### 🤖 AI Analysis")
                                st.markdown(ai_doc_analysis.get('analysis', ''))
                        
                        st.success(f"✅ Processed {uploaded_file.name}")
                    
                    elif uploaded_file.type == 'application/pdf':
                        document_data = {
                            'filename': uploaded_file.name,
                            'type': 'pdf',
                            'extracted_text': "PDF processing limited in demo",
                            'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.documents.append(document_data)
                        st.warning(f"⚠️ {uploaded_file.name} stored")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col2:
        if st.button("Generate AI Summary →", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating AI-powered summary..."):
                st.session_state.ai_summary = generate_clinical_summary(
                    st.session_state.patient_data,
                    st.session_state.documents
                )
            st.session_state.step = 5
            st.rerun()

# ============================================
# STEP 5: AI-Powered Summary
# ============================================
elif st.session_state.step == 5:
    st.markdown("## 📋 AI-Powered Clinical Summary")
    st.markdown("---")
    
    data = st.session_state.patient_data
    
    # Patient Info
    st.markdown("### 👤 Patient Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Language:** {data.get('language', 'English')}")
    with col2:
        st.write(f"**Consent:** ✅ Given")
    with col3:
        st.write(f"**Time:** {data.get('consent_time', 'N/A')}")
    
    st.markdown("---")
    
    # Basic Info
    st.markdown("### 📋 Basic Information")
    st.write(f"**Chief Complaint:** {data.get('chief_complaint', 'N/A')}")
    st.write(f"**Duration:** {data.get('duration', 'N/A')}")
    if 'severity' in data:
        st.write(f"**Severity:** {data['severity']}/10")
    
    st.markdown("---")
    
    # AI-Generated Summary
    st.markdown("### 🤖 AI-Generated Clinical Summary")
    
    if st.session_state.ai_summary:
        # Display AI summary in a nice box
        st.markdown(
            f"""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #0068c9;'>
                {st.session_state.ai_summary}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("AI summary not generated. Please go back and try again.")
    
    st.markdown("---")
    
    # Red Flags from AI
    st.markdown("### 🚨 Red Flag Detection")
    
    if AI_AVAILABLE:
        red_flags = detect_red_flags_with_ai(
            data.get('chief_complaint', ''),
            data.get('symptoms', []),
            data.get('duration', '')
        )
        st.markdown(red_flags)
    else:
        # Manual red flags
        chief_complaint = data.get('chief_complaint', '').lower()
        if 'chest pain' in chief_complaint:
            st.error("🔴 Chest pain - Requires immediate ECG")
        else:
            st.success("✅ No immediate red flags detected")
    
    st.markdown("---")
    
    # Documents
    if st.session_state.documents:
        st.markdown("### 📚 Uploaded Documents")
        for doc in st.session_state.documents:
            st.write(f"• {doc['filename']}")
    
    st.markdown("---")
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Confirm & Save", type="primary", use_container_width=True):
            st.success("Summary saved!")
            st.balloons()
    
    with col2:
        full_data = {
            'patient_info': data,
            'ai_summary': st.session_state.ai_summary,
            'documents': st.session_state.documents,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.download_button(
            label="📄 Download",
            data=json.dumps(full_data, indent=2),
            file_name=f"medikiosk_ai_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 New Patient", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>MediKiosk v0.3 - AI-Powered Clinical Platform</p>
        <p>Voice Input | Document OCR | AI Analysis | Smart Summaries</p>
    </div>
    """,
    unsafe_allow_html=True
)