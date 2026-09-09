import streamlit as st
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="MediKiosk - AI Clinical History Assistant",
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

# Main title
st.title("🏥 MediKiosk")
st.markdown("### AI-Powered Clinical History Assistant")
st.markdown("---")

# Sidebar with information
with st.sidebar:
    st.title("About MediKiosk")
    st.info(
        """
        **MediKiosk** is an AI-powered clinical 
        history taking platform for Indian hospitals.
        
        **Features:**
        - Multilingual support
        - Voice & touch input
        - Structured summaries
        - Red flag detection
        - ABDM integration ready
        
        **Version:** 0.1 (Hackathon Demo)
        """
    )
    
    st.markdown("---")
    st.markdown("### Patient Journey")
    journey_progress = st.session_state.step
    st.progress(journey_progress / 4)
    
    if journey_progress == 1:
        st.write("📍 Step 1: Consent")
    elif journey_progress == 2:
        st.write("📍 Step 2: Chief Complaint")
    elif journey_progress == 3:
        st.write("📍 Step 3: Detailed History")
    elif journey_progress == 4:
        st.write("📍 Step 4: Summary Generated")

# ============================================
# STEP 1: Welcome, Language & Consent
# ============================================
if st.session_state.step == 1:
    st.markdown("## Step 1: Welcome")
    st.markdown("---")
    
    # Language selection
    st.markdown("### Select Your Language / अपनी भाषा चुनें")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("English 🇬🇧", use_container_width=True):
            st.session_state.language = "English"
            st.session_state.patient_data['language'] = "English"
            st.success("English selected")
    
    with col2:
        if st.button("हिंदी 🇮🇳", use_container_width=True):
            st.session_state.language = "Hindi"
            st.session_state.patient_data['language'] = "Hindi"
            st.success("हिंदी चयनित")
    
    with col3:
        if st.button("தமிழ் 🏳️", use_container_width=True):
            st.session_state.language = "Tamil"
            st.session_state.patient_data['language'] = "Tamil"
            st.success("தமிழ் தேர்ந்தெடுக்கப்பட்டது")
    
    with col4:
        if st.button("తెలుగు 🏳️", use_container_width=True):
            st.session_state.language = "Telugu"
            st.session_state.patient_data['language'] = "Telugu"
            st.success("తెలుగు ఎంచుకోబడింది")
    
    st.markdown("---")
    
    # Consent section
    st.markdown("### Patient Consent / रोगी की सहमति")
    
    consent_text = """
    I understand that:
    1. My health information will be recorded digitally
    2. This information will be shared with my treating physician
    3. My data will be stored securely and kept confidential
    4. I can withdraw my consent at any time
    
    मैं समझता/समझती हूं कि:
    1. मेरी स्वास्थ्य जानकारी डिजिटल रूप से दर्ज की जाएगी
    2. यह जानकारी मेरे इलाज करने वाले डॉक्टर के साथ साझा की जाएगी
    3. मेरा डेटा सुरक्षित रूप से संग्रहीत और गोपनीय रखा जाएगा
    4. मैं किसी भी समय अपनी सहमति वापस ले सकता/सकती हूं
    """
    
    st.info(consent_text)
    
    consent_given = st.checkbox(
        "I give my consent to proceed / मैं आगे बढ़ने के लिए सहमति देता/देती हूं",
        key="consent_checkbox"
    )
    
    st.markdown("---")
    
    # Start button
    if consent_given:
        if st.button("Start History Taking →", type="primary", use_container_width=True):
            st.session_state.patient_data['consent_given'] = True
            st.session_state.patient_data['consent_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.step = 2
            st.rerun()
    else:
        st.warning("⚠️ Please provide consent to continue")

# ============================================
# STEP 2: Chief Complaint
# ============================================
elif st.session_state.step == 2:
    st.markdown("## Step 2: What is your main problem?")
    st.markdown("### आपकी मुख्य समस्या क्या है?")
    st.markdown("---")
    
    # Quick selection options
    st.markdown("### Quick Selection / त्वरित चयन")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💔 Chest Pain\nसीने में दर्द", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = "Chest Pain"
            st.session_state.step = 3
            st.rerun()
        
        if st.button("🤕 Headache\nसिरदर्द", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = "Headache"
            st.session_state.step = 3
            st.rerun()
    
    with col2:
        if st.button("🤒 Fever\nबुखार", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = "Fever"
            st.session_state.step = 3
            st.rerun()
        
        if st.button("😤 Breathing Issue\nसांस लेने में समस्या", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = "Breathing Difficulty"
            st.session_state.step = 3
            st.rerun()
    
    with col3:
        if st.button("🤢 Nausea/Vomiting\nमतली/उल्टी", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = "Nausea/Vomiting"
            st.session_state.step = 3
            st.rerun()
        
        if st.button("🦴 Joint Pain\nजोड़ों का दर्द", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = "Joint Pain"
            st.session_state.step = 3
            st.rerun()
    
    st.markdown("---")
    
    # Free text input
    st.markdown("### Or type your problem / या अपनी समस्या लिखें")
    
    chief_complaint_input = st.text_input(
        "Describe your main problem in your own words:",
        placeholder="Example: I have pain in my stomach since yesterday..."
    )
    
    if chief_complaint_input:
        if st.button("Submit Complaint", type="primary", use_container_width=True):
            st.session_state.patient_data['chief_complaint'] = chief_complaint_input
            st.session_state.step = 3
            st.rerun()

# ============================================
# STEP 3: Detailed History Taking
# ============================================
elif st.session_state.step == 3:
    chief_complaint = st.session_state.patient_data.get('chief_complaint', '')
    
    st.markdown("## Step 3: Tell us more about your problem")
    st.markdown(f"### Chief Complaint: **{chief_complaint}**")
    st.markdown("---")
    
    # Duration
    st.markdown("### ⏰ Duration")
    st.markdown("How long have you had this problem?")
    
    duration_options = ["Today", "1-2 days", "3-5 days", "1-2 weeks", "More than a month"]
    duration = st.radio(
        "Select duration:",
        duration_options,
        horizontal=True,
        key="duration"
    )
    st.session_state.patient_data['duration'] = duration
    
    st.markdown("---")
    
    # Severity (show for pain-related complaints)
    if any(word in chief_complaint.lower() for word in ['pain', 'ache', 'दर्द', 'headache']):
        st.markdown("### 📊 Severity")
        st.markdown("Rate your pain on a scale of 1-10:")
        
        severity = st.slider(
            "Pain scale (1 = mild, 10 = severe)",
            min_value=1,
            max_value=10,
            value=5,
            key="severity"
        )
        st.session_state.patient_data['severity'] = severity
        
        # Visual pain scale
        pain_level = "🟢 Mild" if severity <= 3 else "🟡 Moderate" if severity <= 7 else "🔴 Severe"
        st.markdown(f"**Pain Level:** {pain_level}")
        
        st.markdown("---")
    
    # Associated symptoms
    st.markdown("### 🔍 Associated Symptoms")
    st.markdown("Do you have any other symptoms? (Select all that apply)")
    
    symptom_options = [
        "Nausea", "Dizziness", "Sweating", "Shortness of breath",
        "Cough", "Body ache", "Fatigue", "Loss of appetite",
        "Sleep disturbance", "None"
    ]
    
    symptoms = st.multiselect(
        "Select symptoms:",
        symptom_options,
        key="symptoms"
    )
    st.session_state.patient_data['symptoms'] = symptoms
    
    st.markdown("---")
    
    # Past medical history
    st.markdown("### 📋 Past Medical History")
    st.markdown("Do you have any of these conditions?")
    
    condition_options = [
        "Diabetes", "High Blood Pressure", "Heart Disease", "Asthma",
        "Thyroid Problems", "Kidney Disease", "Liver Disease", "None"
    ]
    
    conditions = st.multiselect(
        "Select conditions:",
        condition_options,
        key="conditions"
    )
    st.session_state.patient_data['past_history'] = conditions
    
    st.markdown("---")
    
    # Medications
    st.markdown("### 💊 Current Medications")
    
    medications = st.text_input(
        "Are you taking any medications? (Separate with commas)",
        placeholder="Example: Metformin 500mg, Amlodipine 5mg",
        key="medications"
    )
    st.session_state.patient_data['medications'] = medications
    
    st.markdown("---")
    
    # Allergies
    st.markdown("### ⚠️ Allergies")
    
    allergy_options = ["Penicillin", "Sulfa drugs", "Aspirin", "Other", "No known allergies"]
    allergies = st.radio(
        "Do you have any drug allergies?",
        allergy_options,
        horizontal=True,
        key="allergies"
    )
    st.session_state.patient_data['allergies'] = allergies
    
    st.markdown("---")
    
    # Generate Summary button
    if st.button("📋 Generate Clinical Summary", type="primary", use_container_width=True):
        st.session_state.step = 4
        st.rerun()

# ============================================
# STEP 4: Display Summary
# ============================================
elif st.session_state.step == 4:
    st.markdown("## 📋 Patient History Summary")
    st.markdown("---")
    
    data = st.session_state.patient_data
    
    # Header with patient info
    st.markdown("### Patient Information")
    st.markdown(f"**Language:** {data.get('language', 'English')}")
    st.markdown(f"**Consent Given:** ✅ Yes")
    st.markdown(f"**Time:** {data.get('consent_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")
    
    st.markdown("---")
    
    # Chief Complaint
    st.markdown("### 🎯 Chief Complaint")
    st.info(data.get('chief_complaint', 'Not provided'))
    
    # Duration
    st.markdown("### ⏰ Duration")
    st.write(data.get('duration', 'Not provided'))
    
    # Severity
    if 'severity' in data:
        st.markdown("### 📊 Severity")
        severity = data['severity']
        st.write(f"**Pain Score:** {severity}/10")
        st.progress(severity / 10)
        if severity <= 3:
            st.success("Mild pain")
        elif severity <= 7:
            st.warning("Moderate pain")
        else:
            st.error("Severe pain")
    
    # Associated Symptoms
    st.markdown("### 🔍 Associated Symptoms")
    if data.get('symptoms'):
        for symptom in data['symptoms']:
            st.write(f"• {symptom}")
    else:
        st.write("None reported")
    
    # Past Medical History
    st.markdown("### 📋 Past Medical History")
    if data.get('past_history'):
        for condition in data['past_history']:
            st.write(f"• {condition}")
    else:
        st.write("None reported")
    
    # Medications
    st.markdown("### 💊 Current Medications")
    if data.get('medications'):
        st.write(data['medications'])
    else:
        st.write("None reported")
    
    # Allergies
    st.markdown("### ⚠️ Allergies")
    st.write(data.get('allergies', 'Not specified'))
    
    st.markdown("---")
    
    # Red Flag Detection
    st.markdown("### 🚨 Red Flag Assessment")
    
    chief_complaint = data.get('chief_complaint', '').lower()
    symptoms = [s.lower() for s in data.get('symptoms', [])]
    
    red_flags = []
    
    # Check for dangerous combinations
    if 'chest pain' in chief_complaint:
        if 'shortness of breath' in symptoms:
            red_flags.append("🔴 URGENT: Chest pain with shortness of breath - Possible cardiac emergency")
            red_flags.append("🔴 URGENT: Immediate ECG and cardiac evaluation required")
        else:
            red_flags.append("🟡 Chest pain - ECG recommended")
    
    if 'breathing' in chief_complaint or 'breath' in chief_complaint:
        red_flags.append("🔴 Breathing difficulty - Check oxygen saturation immediately")
    
    if any(word in chief_complaint for word in ['fever', 'बुखार']):
        if 'severe' in data.get('duration', '').lower():
            red_flags.append("🟡 Prolonged fever - Consider infectious workup")
    
    if 'headache' in chief_complaint:
        if 'dizziness' in symptoms:
            red_flags.append("🟡 Headache with dizziness - Neurological evaluation advised")
    
    if not red_flags:
        st.success("✅ No immediate red flags detected - Routine evaluation")
    else:
        for flag in red_flags:
            if flag.startswith("🔴"):
                st.error(flag)
            else:
                st.warning(flag)
    
    st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Confirm & Save", type="primary", use_container_width=True):
            st.success("Summary confirmed and saved to patient record!")
            st.balloons()
            
            # Here you would push to HIS/EMR
            # This is where FHIR bundle creation would go
    
    with col2:
        if st.button("📄 Download JSON", use_container_width=True):
            json_str = json.dumps(data, indent=2)
            st.download_button(
                label="Download Summary",
                data=json_str,
                file_name=f"medikiosk_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col3:
        if st.button("🔄 New Patient", use_container_width=True):
            st.session_state.step = 1
            st.session_state.patient_data = {}
            st.rerun()
    
    # Display raw data (for demo purposes)
    with st.expander("🔍 View Raw Data (Developer View)"):
        st.json(data)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>MediKiosk v0.1 - AI-Powered Clinical History Platform</p>
        <p>Built for Hackathon Demo | ABDM Integration Ready</p>
    </div>
    """,
    unsafe_allow_html=True
)