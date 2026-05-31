# Project: AI Resume Analysis
# Author: Imtiaz Adar
# Contact: imtiazadarofficial@gmail.com

# Importing Libraries
import streamlit as st
from pypdf import PdfReader
import json
from google import genai
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
import datetime
from gtts import gTTS

# Setting All The Configurations
st.set_page_config(page_title="AI Resume Analyzer - Imtiaz Adar", page_icon="cv.png",
    layout="wide")

st.markdown("""
<style>

/* Analyze Resume Button */

div.stButton > button {
    background: linear-gradient(135deg, #d32f2f, #b71c1c);
    color: white;
    font-weight: 700;
    font-size: 16px;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0px 4px 12px rgba(183, 28, 28, 0.35);
}

/* Hover Effect */

div.stButton > button:hover {
    background: linear-gradient(135deg, #e53935, #c62828);
    transform: translateY(-2px);
    box-shadow: 0px 8px 18px rgba(183, 28, 28, 0.45);
}

/* Click Effect */

div.stButton > button:active {
    transform: translateY(1px);
}

</style>
""", unsafe_allow_html=True)
# st.title("AI Resume Analyzer - Imtiaz Adar")
st.markdown("""
<h1>
AI Resume Analyzer
</h1>

<h4 style='color:#888888;'>
Built by <span style='color:#00BFFF;'>Imtiaz Adar</span>
</h4>
""", unsafe_allow_html=True)
st.caption(f"Analysis Date: {datetime.date.today()}")
st.write("Upload your resume in PDF format and get the feedback.")
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# Gemini API Key
api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)

job_description = st.text_area(
    "Job Description (Optional)",
    height=200
)

# Text Extracting Method
def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    return text

# Colored Score Method
def get_score_color(score):
    if score >= 80:
        return "green"
    elif score >= 60:
        return "orange"
    else:
        return "red"
    
# PDF downloading method    
def create_pdf(data):
    pdf_file = "resume_analysis.pdf"

    doc = SimpleDocTemplate(pdf_file)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "AI Resume Analysis Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph(
            f"ATS Score: {data['ats_score']}/100",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Job Match Score: {data['job_match_score']}/100",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 12))

    content.append(
        Paragraph("Strengths", styles["Heading2"])
    )

    for item in data["strengths"]:
        content.append(
            Paragraph(f"• {item}", styles["Normal"])
        )

    content.append(
        Paragraph("Weaknesses", styles["Heading2"])
    )

    for item in data["weaknesses"]:
        content.append(
            Paragraph(f"• {item}", styles["Normal"])
        )

    content.append(
        Paragraph("Recommendations", styles["Heading2"])
    )

    for item in data["recommendations"]:
        content.append(
            Paragraph(f"• {item}", styles["Normal"])
        )

    content.append(
        Paragraph("Detailed Analysis", styles["Heading2"])
    )

    content.append(
        Paragraph(
            data["full_analysis"],
            styles["Normal"]
        )
    )

    doc.build(content)

    return pdf_file

# Showing The Extracted Text
if uploaded_file:
    resume_text = extract_text(uploaded_file)
    st.subheader("Extracted Resume Text")
    st.text_area("Resume Content", resume_text, height=300)
    
    if st.button("Analyze Resume"):
        prompt = f"""
You are a professional ATS Resume Reviewer and Senior Technical Recruiter.

Analyze the candidate's resume and compare it against the provided job description.

Instructions:

1. Evaluate the resume's ATS compatibility and assign an ATS Score between 0 and 100.
2. If a job description is provided, evaluate the candidate's suitability for that role and assign a Job Match Score between 0 and 100.
3. If no job description is provided, set Job Match Score to 0.
4. Identify the candidate's key strengths.
5. Identify weaknesses that may negatively impact hiring decisions.
6. Identify missing skills, keywords, or technologies.
7. Identify grammar, spelling, or language issues.
8. Identify formatting and resume structure issues.
9. Provide practical and actionable recommendations for improvement.
10. ATS Score and Job Match Score must be integers only.
11. All list fields should contain concise, meaningful, and professional entries.
12. The full_analysis field must contain a detailed professional report written directly for the candidate.
13. Be objective, realistic, and constructive.
14. Return ONLY valid JSON.
15. Do NOT include markdown code blocks.
16. Do NOT include explanations, comments, or text outside the JSON response.

Return exactly the following JSON structure:

{{
    "ats_score": 0,
    "job_match_score": 0,
    "strengths": [],
    "weaknesses": [],
    "missing_skills": [],
    "grammar_issues": [],
    "formatting_suggestions": [],
    "recommendations": [],
    "full_analysis": ""
}}

Job Description:
{job_description if job_description.strip() else "Not Provided"}

Resume:
{resume_text}
"""
        # prompt = f"""
        # Your are an expert ATS Resume Reviewer.
        
        # Analyze this resume and provide:
        
        # 1. Overall ATS Score (0-100)
        # 2. Strengths
        # 3. Weaknesses
        # 4. Missing Skills
        # 5. Grammar Issues
        # 6. Formatting Suggestions
        # 7. Important Recommendations
        
        # Resume:
        
        # {resume_text}
        # """
        with st.spinner("Analyzing..."):
            # response = ollama.chat(model="llama3.2:3b", messages=[{"role": "user", "content": prompt}])
            # print(response["message"])
            # print("done...")
            # print(response["message"]["content"])
            # result = response["message"]["content"]
            try:
            
                response = client.models.generate_content(model="gemini-2.5-flash",contents=prompt)
                print(response)
                
                clean_text = response.text.strip()
                clean_text = clean_text.replace("```json", "").replace("```", "").strip()
                
                data = json.loads(clean_text)
                ats_score = int(data["ats_score"])
                job_match_score = int(data["job_match_score"])
                result = response.text
                # st.subheader("Analysis Result")
                # st.markdown(result)
                full_analysis = data["full_analysis"]
                with st.expander("📄 Detailed Analysis"):
                    st.markdown(data["full_analysis"])
                st.success("Analysis completed...")
                st.subheader("Audio Analysis")
                tts = gTTS(text=data["full_analysis"], lang="en")
                tts.save("analysis.mp3")
                st.audio("analysis.mp3")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(
                        f"""
                        <h2 style='color:{get_score_color(ats_score)}'>
                        ATS Score: {ats_score}/100
                        </h2>
                        """,
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        f"""
                        <h2 style='color:{get_score_color(job_match_score)}'>
                        Job Match Score: {job_match_score}/100
                        </h2>
                        """,
                        unsafe_allow_html=True
                    )
                
                st.write("ATS Compatibility")
                st.progress(ats_score / 100)

                st.write("Job Match")
                st.progress(job_match_score / 100)
                st.subheader("Grammar Issues")

                for item in data["grammar_issues"]:
                    st.warning(item)
                
                st.subheader("Formatting Suggestions")

                for item in data["formatting_suggestions"]:
                    st.info(item)
                st.subheader("Strengths")

                for item in data["strengths"]:
                    st.success(item)
                st.subheader("Weaknesses")

                for item in data["weaknesses"]:
                    st.error(item)
                
                st.subheader("Missing Skills")

                for item in data["missing_skills"]:
                    st.warning(item)
                st.subheader("Recommendations")

                for item in data["recommendations"]:
                    st.info(item)
                
                
                pdf_file = create_pdf(data)

                with open(pdf_file, "rb") as file:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=file,
                        file_name="resume_analysis.pdf",
                        mime="application/pdf"
                    )
                with open("analysis.mp3", "rb") as audio:
                    st.download_button(
                        "🎧 Download Audio",
                        audio,
                        file_name="analysis.mp3",
                        mime="audio/mpeg"
                    )
                st.markdown(
    """
    ---
    <div style='text-align:center'>
        Built with Google Gemini • Python
    </div>
    """,
    unsafe_allow_html=True
)
                                                
            except Exception as e:
                st.error(f'Error: {e}')
            