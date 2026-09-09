import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import pytesseract
from google import genai
import google.genai as genai

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
# NAVIGATION FUNCTIONS
# ============================================
def go_to_step(step):
    """Navigate to a specific step"""
    if 1 <= step <= 5:
        st.session_state.step = step
        st.rerun()

def go_back():
    """Go to previous step"""
    if st.session_state.step > 1:
        st.session_state.step -= 1
        st.rerun()

def go_next():
    """Go to next step"""
    if st.session_state.step < 5:
        st.session_state.step += 1
        st.rerun()

# ============================================
# CONFIGURE GEMINI API
# ============================================
# Get API key from environment variable (recommended)
# Or hardcode for testing (not recommended for production)
GEMINI_API_KEY = "AQ.Ab8RN6LMb1Tt3hKx7yVmfqKEYyxORP-7Q7plNiSoqtIa5fTKWw"  # ← PUT YOUR API KEY HERE (replace abcdefg with your real key, keep the quotes)

if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        AI_AVAILABLE = True
    except Exception as e:
        AI_AVAILABLE = False
        st.error(f"⚠️ Gemini setup failed: {e}")
else:
    AI_AVAILABLE = False
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        st.warning("⚠️ Please set your Gemini API key in the code or use environment variables.")

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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API call failed: {e}")
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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API call failed: {e}")
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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API call failed: {e}")
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
        response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        return {'analysis': response.text}
    except Exception as e:
        st.error(f"Gemini API call failed: {e}")
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
if 'selected_symptoms' not in st.session_state:
    st.session_state.selected_symptoms = []
if 'custom_problem' not in st.session_state:
    st.session_state.custom_problem = ""

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
        2: "📍 Step 2: Symptoms",
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
            go_to_step(2)
    else:
        st.warning("⚠️ Please provide consent")

# ============================================
# STEP 2: Chief Complaint (with Common Symptoms Only)
# ============================================
elif st.session_state.step == 2:
    st.markdown("## Step 2: What are your symptoms?")
    st.markdown("### Select all that apply / जो लागू हो उन्हें चुनें")
    st.markdown("---")
    
    # Voice input
    st.markdown("### 🎤 Speak Your Symptoms")
    
    if st.button("🎤 Click to Speak", type="primary", use_container_width=True):
        text, error = record_voice(st.session_state.voice_lang)
        if error:
            st.error(error)
        elif text:
            st.session_state.patient_data['chief_complaint'] = text
            st.success(f"Recognized: {text}")
            
            # AI Analysis of complaint
            if AI_AVAILABLE:
                with st.spinner("🤖 AI analyzing your symptoms..."):
                    analysis = analyze_complaint_with_ai(text)
                    if analysis:
                        st.session_state.ai_analysis = analysis
                        with st.expander("🤖 AI Analysis"):
                            st.markdown(analysis)
            
            go_to_step(3)
    
    st.markdown("---")
    
    # ============================================
    # COMMON SYMPTOMS ONLY
    # ============================================
    st.markdown("### 🔍 Select Your Symptoms")
    st.markdown("Choose all symptoms that apply to you:")
    
    # Store selected symptoms
    selected_symptoms = []
    
    # MOST COMMON SYMPTOMS - Grouped by type
    st.markdown("#### 🩺 Common Symptoms")
    col1, col2, col3 = st.columns(3)
    
    common_symptoms = {
        "🤕 Headache": "Headache",
        "🤒 Fever": "Fever",
        "🤧 Cough": "Cough",
        "😷 Sore Throat": "Sore Throat",
        "🤢 Nausea": "Nausea",
        "😤 Shortness of Breath": "Shortness of Breath"
    }
    
    for i, (label, value) in enumerate(common_symptoms.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.checkbox(label, key=f"common_{i}"):
                selected_symptoms.append(value)
    
    st.markdown("---")
    st.markdown("#### 💪 Pain Symptoms")
    col1, col2, col3 = st.columns(3)
    
    pain_symptoms = {
        "💔 Chest Pain": "Chest Pain",
        "🔪 Abdominal Pain": "Abdominal Pain",
        "🦴 Joint Pain": "Joint Pain",
        "💪 Muscle Pain": "Muscle Pain",
        "🦷 Tooth Pain": "Tooth Pain",
        "🔙 Back Pain": "Back Pain"
    }
    
    for i, (label, value) in enumerate(pain_symptoms.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.checkbox(label, key=f"pain_{i}"):
                selected_symptoms.append(value)
    
    st.markdown("---")
    st.markdown("#### 🫁 Respiratory & GI")
    col1, col2, col3 = st.columns(3)
    
    resp_gi_symptoms = {
        "👃 Runny Nose": "Runny Nose",
        "🫁 Wheezing": "Wheezing",
        "🤮 Vomiting": "Vomiting",
        "💩 Diarrhea": "Diarrhea",
        "🔥 Heartburn": "Heartburn",
        "😋 Loss of Appetite": "Loss of Appetite"
    }
    
    for i, (label, value) in enumerate(resp_gi_symptoms.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.checkbox(label, key=f"respgi_{i}"):
                selected_symptoms.append(value)
    
    st.markdown("---")
    st.markdown("#### 🧠 Neurological & General")
    col1, col2, col3 = st.columns(3)
    
    neuro_general = {
        "😵 Dizziness": "Dizziness",
        "😴 Fatigue": "Fatigue",
        "💧 Sweating": "Sweating",
        "😵‍💫 Confusion": "Confusion",
        "🤲 Skin Rash": "Skin Rash",
        "⚖️ Weight Loss": "Weight Loss"
    }
    
    for i, (label, value) in enumerate(neuro_general.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.checkbox(label, key=f"neuro_{i}"):
                selected_symptoms.append(value)
    
    st.markdown("---")
    st.markdown("#### 🩺 Other")
    col1, col2, col3 = st.columns(3)
    
    other_symptoms = {
        "🩸 Bleeding": "Bleeding",
        "🌀 Vertigo": "Vertigo",
        "🔄 None of the Above": "None"
    }
    
    for i, (label, value) in enumerate(other_symptoms.items()):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.checkbox(label, key=f"other_{i}"):
                selected_symptoms.append(value)
    
    st.markdown("---")
    
    # ============================================
    # SHOW SELECTED SYMPTOMS SUMMARY
    # ============================================
    if selected_symptoms:
        st.markdown("### ✅ Your Selected Symptoms")
        
        # Remove "None" if other symptoms are selected
        if "None" in selected_symptoms and len(selected_symptoms) > 1:
            selected_symptoms.remove("None")
        
        # Display as nice pills/tags
        st.markdown(
            f"""
            <div style='display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0;'>
                {''.join([f'<span style="background-color: #0068c9; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px;">{symptom}</span>' for symptom in selected_symptoms])}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Store in session state
        st.session_state.selected_symptoms = selected_symptoms
        st.session_state.patient_data['symptoms'] = selected_symptoms
        
        # Store as combined complaint for AI
        combined_complaint = ", ".join(selected_symptoms)
        st.session_state.patient_data['chief_complaint'] = combined_complaint
        
        # AI Analysis of combined symptoms
        if AI_AVAILABLE and len(selected_symptoms) > 0:
            with st.spinner("🤖 AI analyzing your symptoms..."):
                analysis = analyze_complaint_with_ai(combined_complaint)
                if analysis:
                    st.session_state.ai_analysis = analysis
                    with st.expander("🤖 AI Analysis of Your Symptoms"):
                        st.markdown(analysis)
    
    # ============================================
    # FREE TEXT INPUT (For additional details)
    # ============================================
    st.markdown("---")
    st.markdown("### ✏️ Tell us more")
    
    additional_details = st.text_area(
        "Describe any additional symptoms or details:",
        placeholder="Example: The pain started yesterday, gets worse when I bend over...",
        height=80
    )
    
    if additional_details:
        st.session_state.patient_data['additional_details'] = additional_details
    
    st.markdown("---")
    
    # ============================================
    # NAVIGATION BUTTONS
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Consent", use_container_width=True):
            go_to_step(1)
    
    with col2:
        if selected_symptoms or additional_details:
            if st.button("Continue →", type="primary", use_container_width=True):
                # Combine all symptoms
                all_complaints = []
                if selected_symptoms:
                    all_complaints.extend(selected_symptoms)
                if additional_details:
                    all_complaints.append(additional_details)
                
                st.session_state.patient_data['chief_complaint'] = ", ".join(all_complaints)
                go_to_step(3)
        else:
            st.warning("⚠️ Please select at least one symptom or describe your problem")

# ============================================
# STEP 3: Detailed History (with conditional custom problem input)
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
    
    # Symptoms (already selected, but can add more)
    st.markdown("### 🔍 Additional Symptoms")
    symptom_options = [
        "Nausea", "Dizziness", "Sweating", "Shortness of breath",
        "Cough", "Body ache", "Fatigue", "Loss of appetite",
        "Sleep disturbance", "None"
    ]
    
    # FIXED: Pre-select symptoms using actual values, not indices
    existing_symptoms = st.session_state.patient_data.get('symptoms', [])
    default_values = [s for s in existing_symptoms if s in symptom_options]
    
    additional_symptoms = st.multiselect(
        "Add any additional symptoms not listed above:",
        symptom_options,
        default=default_values
    )
    
    # Check if "None" is selected
    none_selected = False
    if "None" in additional_symptoms:
        if len(additional_symptoms) > 1:
            st.warning("⚠️ You selected 'None' along with other symptoms. 'None' will be removed.")
            additional_symptoms.remove("None")
        else:
            none_selected = True
    
    # Merge with existing symptoms
    all_symptoms = list(set(existing_symptoms + additional_symptoms))
    
    # Remove "None" if there are other symptoms
    if "None" in all_symptoms and len(all_symptoms) > 1:
        all_symptoms.remove("None")
    
    st.session_state.patient_data['symptoms'] = all_symptoms
    
    # ============================================
    # CONDITIONAL CUSTOM PROBLEM INPUT
    # Only show if "None" is selected
    # ============================================
    if none_selected:
        st.markdown("---")
        st.markdown("### ✏️ Describe Your Problem")
        st.markdown("Since you selected 'None', please describe your problem in detail:")
        
        custom_problem = st.text_area(
            "What brings you here today?",
            placeholder="Example: I have a sharp pain in my lower abdomen that gets worse when I eat...",
            height=100,
            value=st.session_state.custom_problem
        )
        
        if custom_problem:
            st.session_state.custom_problem = custom_problem
            st.session_state.patient_data['custom_problem'] = custom_problem
    
    st.markdown("---")
    
    # Past history
    st.markdown("### 📋 Past Medical History")
    condition_options = [
        "Diabetes", "High Blood Pressure", "Heart Disease", "Asthma",
        "Thyroid Problems", "Kidney Disease", "Liver Disease", "None"
    ]
    conditions = st.multiselect("Select conditions:", condition_options)
    
    # Handle "None" selection
    if "None" in conditions and len(conditions) > 1:
        st.warning("⚠️ You selected 'None' along with other conditions. 'None' will be removed.")
        conditions.remove("None")
    
    if "None" in conditions and len(conditions) == 1:
        conditions = []
    
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
    
    # Handle "No significant family history" selection
    if "No significant family history" in family_history and len(family_history) > 1:
        st.warning("⚠️ You selected 'No significant family history' along with other options. It will be removed.")
        family_history.remove("No significant family history")
    
    if "No significant family history" in family_history and len(family_history) == 1:
        family_history = []
    
    st.session_state.patient_data['family_history'] = family_history
    
    st.markdown("---")
    
    # ============================================
    # NAVIGATION BUTTONS
    # ============================================
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back to Symptoms", use_container_width=True):
            go_to_step(2)
    
    with col2:
        if st.button("Next →", type="primary", use_container_width=True):
            # Combine all symptoms and custom problem for the final complaint
            final_complaint = []
            
            if all_symptoms:
                final_complaint.extend(all_symptoms)
            
            if none_selected and st.session_state.custom_problem:
                final_complaint.append(st.session_state.custom_problem)
            
            if final_complaint:
                st.session_state.patient_data['chief_complaint'] = ", ".join(final_complaint)
            else:
                st.session_state.patient_data['chief_complaint'] = "No specific complaint provided"
            
            go_to_step(4)

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
        if st.button("← Back to History", use_container_width=True):
            go_to_step(3)
    
    with col2:
        if st.button("Generate AI Summary →", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating AI-powered summary..."):
                st.session_state.ai_summary = generate_clinical_summary(
                    st.session_state.patient_data,
                    st.session_state.documents
                )
            go_to_step(5)

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
    
    # Actions with Back button
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            go_to_step(4)
    
    with col2:
        if st.button("✅ Confirm & Save", type="primary", use_container_width=True):
            st.success("Summary saved!")
            st.balloons()
    
    with col3:
        full_data = {
            'patient_info': data,
            'ai_summary': st.session_state.ai_summary,
            'documents': st.session_state.documents,
            'custom_problem': st.session_state.custom_problem,
            'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.download_button(
            label="📄 Download",
            data=json.dumps(full_data, indent=2),
            file_name=f"medikiosk_ai_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col4:
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