import streamlit as st
import tempfile
import os
from pdf_extractor import extract_text_from_pdf
from resume_trailor import analyze_resume, parse_analysis

st.set_page_config(
    page_title="AI Resume Tailor",
    page_icon="📄",
    layout="wide"
)

st.title("AI Resume Trailor")
st.caption("Upload your resume and paste a job description to get tailored recommendations")

col1,col2=st.columns(2)

with col1:

    st.subheader("Your Resume")
    uploaded_file=st.file_uploader("Upload resume PDF",type=["pdf"])

with col2:
    st.subheader("Job Description")
    job_desccription= st.text_area(
        "Paste the job decription here",
        height=300,
        placeholder="Paster the full job description..."
    )

analyze_clicked=st.button("Analyze Resume",type="primary")

if analyze_clicked:
    if not uploaded_file:
        st.error("Please upload a resume PDF")
        st.stop()
    if not job_desccription.strip():
        st.error("Please paster a job description")
        st.stop()

    #Extract PDF Text
    with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    resume_text= extract_text_from_pdf(tmp_path)
    os.unlink(tmp_path)


    #Analyse with Spinner
    with st.spinner("Analyzing your resume..."):
        raw_xml=analyze_resume(resume_text,job_desccription)

    #Parse results
    result = parse_analysis(raw_xml)

    #---Results-------
    st.divider()
    st.subheader("Analysis Results")

    score=int(result['score'])

    if score>= 70:
        st.success(f"Match Score: {score}%")
    elif score>=50:
        st.warning(f"Match score : {score}%")
    else:
        st.error(f"Match Score: {score}%")

    st.caption(result['summary'])

    col3,col4= st.columns(2)

    with col3:
        st.subheader("Strong Matches")
        for m in result['matches']:
            st.success(f"+ {m}")
        
        st.subheader("Gaps to Address")
        for g in result['gap']:
            st.error(f"! {g}")

    with col4:
        st.subheader("ATS Keywords to Add")
        keywords_text= " ".join(f" '{k}' " for k in result['keywords'])
        st.markdown(keywords_text)

        st.subheader("Tailored Bullets")
        for b in result['bullet']:
            st.info(f"• {b}")

