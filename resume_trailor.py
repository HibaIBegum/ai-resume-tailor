import os
from groq import Groq
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from pdf_extractor import extract_text_from_pdf
import streamlit as st

load_dotenv()

try:
    api_key = st.secrets["Groq_API_Key"]
except Exception:
    api_key = os.getenv("Groq_API_Key")

client = Groq(api_key=api_key)

# sample dataset before UI

sample_resume="""
John Smith
Full Stack .NET Developer | 5 years experience
Newark, NJ | john@gmail.com

EXPERIENCE
Software Developer - HealthCare Systems Inc (2019-2024)
- Build and maintained REST APIs using ASP.NET Core
- Developed patient data management modules in C#
- Worked with SQL Seerver databases for healthcare operations
- Collaborated with cross-functional teams on HIPAA-compliant systems
- Implemented authentication using OAuth 2.0 and JWT tokens

EDUCATION
BS Computer Science - State University 2019

SKILLS
C#, ASP.NET Core, SQL Server, REST APIs,Git, Azure, Python (learning)

RESEARCH
Published paper on lung cancer detection using ML/DL - RCAAI 2025
"""

sample_jd="""
AI Systems Engineer - HealthTech Startup

We are looking for an AI Systems Engineer to build and maintain
AI-powered healthcare applications.

Requirements:
- Experience with Python and REST APIs
- Knowledge of LLMs and prompt engineering 
- Experience with healthcare data formats (FHIR, HL7)
- Familiarity with RAG architectures and vector databases
- Strong understanding if API integration
- Experience with cloud platforms (AWS/ Azure/GCP)
- Ability to build and deploy ML pipelines

Nice to have:
- Healtcare domain knowledge
- Published research in AI/ML
- Experience with Lanchain or similar frameworks
"""
#Core prompt function
def analyze_resume(resume_text, job_description):


    messages=[

        {
            "role":"system", "content":"""You are a expert technical resume analyst and ATS optimization specialist with deep knowledge of AI/ML hiring. 
            Analyze the resume agains the job description and response in this exat XML format only.
            No text before or after the XML.

            <resume_analysis>
            <match_score>
            <percentage>0-100 number only</percentage>
            <summary>once sentence explaining the score</summary>
            </match_score>
            <tailored_bullets>
            <bullet>rewritten bullet point optimized for this JD</bullet>
            <bullet>rewritten bullet point optimized for this JD</bullet>
            <bullet>rewritten bullet point optimized for this JD</bullet>
            <bullet>rewritten bullet point optimized for this JD</bullet>
            <bullet>rewritten bullet point optimized for this JD</bullet>
            <bullet>rewritten bullet point optimized for this JD</bullet>
            </tailored_bullets>
            <ats_keywords>
            <keyword>Keyword from JS that should appear in resume</keyword>
            <keyword>Keyword from JS that should appear in resume</keyword>
            <keyword>Keyword from JS that should appear in resume</keyword>
            <keyword>Keyword from JS that should appear in resume</keyword>
            <keyword>Keyword from JS that should appear in resume</keyword>
            <keyword>Keyword from JS that should appear in resume</keyword>
            </ats_keywords>
            <gaps>
            <gap>[technology name]: found in JD but absent from resume</gap>
            <gap>[technology name]: found in JD but absent from resume</gap>
            <gap>[technology name]: found in JD but absent from resume</gap>
            </gaps>
            <strong_matches>
            <match>something in resume that directly matches JD requirement</match>
            <match>something in resume that directly matches JD requirement</match>
            <match>something in resume that directly matches JD requirement</match>
            </strong_matches>
            </resume_analysis>"""},
            {"role":"user","content":f""" Analyze this resume against the job description.

             Resume:
             {resume_text}

            Job Description:
            {job_description}

            Return the XML analysis only."""}
    ]


    response=client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        stream=True
    )

    print("Analyzing resume ...\n")
    full_response=""

    for chunk in response:
        delta=chunk.choices[0].delta.content
        if delta:
            print(delta,end="",flush=True)
            full_response+=delta

    return full_response

def parse_analysis(xml_string):

    root= ET.fromstring(xml_string)

    score= root.find("match_score/percentage").text
    #print("score from parse_alaysis",score)
    summary= root.find("match_score/summary").text
    bullet= [ b.text for b in root.findall("tailored_bullets/bullet")]
    keywords= [ k.text for k in root.findall("ats_keywords/keyword")]
    gap= [ g.text for g in root.findall("gaps/gap")]
    matches= [ m.text for m in root.findall("strong_matches/match")]


    return{
        "score":score,
        "summary":summary,
        "bullet":bullet,
        "keywords":keywords,
        "gap":gap,
        "matches":matches

    }

if __name__ == "__main__":

    resume_text = extract_text_from_pdf("sample_resume.pdf")
    #step 1 - get raw XML
    raw_xml=analyze_resume(resume_text,sample_jd)
    print("\n\n --- Parsed Results----\n")
    #step 2 - parse it
    result= parse_analysis(raw_xml)

    print(f"Matched Score {result['score']}%")
    print(f"Summary  {result['summary']}")

    print(f"Strong Matches")
    for m in result['matches']:
        print(f"  +{m}")


    print(f"\nTailred Bullets")
    for b in result['bullet']:
        print(f"  +{b}")


    print(f"\nATS Keywords")
    for k in result['keywords']:
        print(f"  +{k}")

    print(f"\nGaps to Address")
    for g in result['gap']:
        print(f"  ! {g}")



