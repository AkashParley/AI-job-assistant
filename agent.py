from pathlib import Path
import json
import re
import asyncio

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv


def truncate(text, max_chars=2000):
    return text[:max_chars] + "..." if len(text) > max_chars else text


load_dotenv(Path(__file__).resolve().parent / ".env")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=2000,
)


async def async_invoke(chain, inputs):
    return await chain.ainvoke(inputs)


def analyze_gap(resume_text, jd_text):
    prompt = PromptTemplate.from_template("""
You are a senior hiring consultant with 15 years of experience shortlisting candidates.

Carefully read the FULL resume and FULL job description below. 
Do not just match keywords — reason about actual experience, years of work, project depth, and seniority level.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Think step by step:
1. What experience level does the JD require? (junior/mid/senior, years)
2. What experience level does the candidate actually have?
3. Which JD requirements are met by real experience vs just keyword mentions?
4. Which requirements are completely missing?

Then return your analysis in EXACTLY this format — no extra text, no meta-instructions:

## ✅ Matching Skills
- [Skill/Experience]: [Why it matches — reference actual resume content and JD requirement]

## ❌ Missing Skills  
- [Skill/Experience]: 🔴 Critical / 🟡 Important / 🟢 Minor — [why it's missing]

## 💡 What To Highlight
- [Specific actionable advice referencing actual resume content]

## 📊 Match Score
**Score: XX/100** — [honest reasoning based on experience depth, not just keywords]

## 🎯 Verdict
[2-3 sentences: direct advice on whether to apply and what to do first]
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": truncate(resume_text), "jd": truncate(jd_text)})


def analyze_gap_scores(resume_text, jd_text):
    prompt = PromptTemplate.from_template("""
You are a hiring analyst. Evaluate this candidate's resume against the job description.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Score each dimension honestly based on ACTUAL EXPERIENCE, not just keyword presence:

- overall_score: overall fit considering experience depth, skills, seniority match (0-100)
- technical_skills: how well technical skills match JD requirements (0-100)
- experience_match: does their years/depth of experience match what JD asks for (0-100)
- education_match: does education background fit the role (0-100)  
- soft_skills: leadership, communication, teamwork evidence in resume vs JD needs (0-100)

Rules:
- A fresher applying to a senior role should score 20-35 on experience_match
- Keyword present but no real project/work evidence = max 50 on that dimension
- Strong project evidence with measurable results = 75-90
- Do NOT default to 60 — actually reason through each score
- Vary scores meaningfully — not all the same number

Also extract:
- matching_skills: list of 5 skills/experiences that genuinely match
- missing_skills: list of 4 skills/experiences that are clearly absent
- critical_gaps: count of 🔴 critical missing requirements
- important_gaps: count of 🟡 important missing requirements  
- minor_gaps: count of 🟢 minor missing requirements

Return ONLY a valid JSON object, no markdown, no backticks, no explanation:

{{
  "overall_score": <integer>,
  "technical_skills": <integer>,
  "experience_match": <integer>,
  "education_match": <integer>,
  "soft_skills": <integer>,
  "matching_skills": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "missing_skills": ["skill1", "skill2", "skill3", "skill4"],
  "critical_gaps": <integer>,
  "important_gaps": <integer>,
  "minor_gaps": <integer>
}}
""")
    chain = prompt | llm | StrOutputParser()
    result = chain.invoke({"resume": truncate(resume_text), "jd": truncate(jd_text)})

    cleaned = re.sub(r"```json|```", "", result).strip()
    return json.loads(cleaned)


def generate_cover_letter(resume_text, jd_text):
    prompt = PromptTemplate.from_template("""
You are an expert cover letter writer who has helped 500+ candidates get shortlisted.

Write a powerful, specific cover letter based on this resume and job description.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Rules:
- 3 paragraphs only
- Never use: "I am passionate", "I am excited", "I believe", "I am a quick learner"
- Open with a specific achievement or skill, not "I am applying for..."
- Middle paragraph: connect 2-3 specific resume points to JD requirements
- Close with confidence, not desperation
- Maximum 250 words

Write the cover letter now:
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": truncate(resume_text), "jd": truncate(jd_text)})


def generate_resume_suggestions(resume_text, jd_text):
    prompt = PromptTemplate.from_template("""
You are an expert ATS resume coach and career strategist.

Analyze this resume against the job description and give highly specific, actionable suggestions to improve the resume so it gets past ATS filters and impresses human reviewers.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Return ONLY the suggestions below in this EXACT format:

## 🔑 Missing Keywords to Add
List the exact keywords/phrases from the JD missing in the resume.
For each, tell WHERE to add it in the resume (Skills section, Experience bullet, Summary etc).
- [Keyword]: Add to [section] — [one line why it matters for this role]

## 📝 Resume Bullets to Rewrite
Pick 3 weak resume bullets and rewrite them to be stronger and JD-aligned.
Use the format:
**Before:** [original weak bullet]
**After:** [improved bullet with metrics and JD keywords]

## 🛠️ Skills Section Gaps
List specific skills/tools to add to the Skills section immediately.
Rate each by impact: 🔴 High / 🟡 Medium / 🟢 Low
- [Skill/Tool]: [impact] — [where to learn it: specific free resource]

## 📚 Quick Wins (Do This Week)
List 3-4 concrete actions the candidate can take THIS WEEK to strengthen their profile for this role.
- [Action]: [expected impact on application]

## ⚡ ATS Score Boosters
List 5 exact phrases from the JD to copy-paste into the resume naturally.
- "[exact phrase from JD]" → Add to [section]
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": truncate(resume_text), "jd": truncate(jd_text)})


def generate_interview_questions(resume_text, jd_text):
    prompt = PromptTemplate.from_template("""
You are a senior technical interviewer preparing a candidate for this exact role.

RESUME:
{resume}

JOB DESCRIPTION:
{jd}

Generate 10 interview questions tailored specifically to THIS candidate applying for THIS role.
Mix: 4 technical, 3 behavioral, 2 situational, 1 curveball.

For each question:
- Write the question
- Explain WHY the interviewer is asking it
- Give a specific strategy to answer it well based on the candidate's background

Use this EXACT format:

### Q1: [Technical] Question here
**Why they ask this:** One sentence explanation
**How to answer:** Specific strategy using the candidate's actual experience

### Q2: [Behavioral] Question here
...and so on for all 10 questions.
""")
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": truncate(resume_text), "jd": truncate(jd_text)})


async def run_all_analysis(resume_text, jd_text):
    r, j = truncate(resume_text), truncate(jd_text)
    inputs = {"resume": r, "jd": j}

    gap_prompt = PromptTemplate.from_template("""
You are a senior hiring consultant with 15 years of experience shortlisting candidates.
Carefully read the FULL resume and FULL job description below.
Do not just match keywords — reason about actual experience, years of work, project depth, and seniority level.

RESUME: {resume}
JOB DESCRIPTION: {jd}

Think step by step:
1. What experience level does the JD require?
2. What experience level does the candidate actually have?
3. Which JD requirements are met by real experience vs just keyword mentions?
4. Which requirements are completely missing?

Return ONLY in this format — no extra text:

## ✅ Matching Skills
- [Skill/Experience]: [Why it matches — reference actual resume content]

## ❌ Missing Skills
- [Skill/Experience]: 🔴 Critical / 🟡 Important / 🟢 Minor — [why]

## 💡 What To Highlight
- [Specific actionable advice referencing actual resume content]

## 📊 Match Score
**Score: XX/100** — [honest reasoning based on experience depth]

## 🎯 Verdict
[2-3 sentences of direct advice]
""")

    scores_prompt = PromptTemplate.from_template("""
You are a hiring analyst. Score this candidate honestly based on ACTUAL EXPERIENCE, not just keywords.

RESUME: {resume}
JOB DESCRIPTION: {jd}

Rules:
- Fresher applying to senior role = 20-35 on experience_match
- Keyword present but no real project evidence = max 50
- Strong project evidence with measurable results = 75-90
- Do NOT default to 60 — reason through each score independently
- Vary scores meaningfully — not all the same number

Return ONLY valid JSON, no markdown, no backticks:
{{
  "overall_score": <integer>,
  "technical_skills": <integer>,
  "experience_match": <integer>,
  "education_match": <integer>,
  "soft_skills": <integer>,
  "matching_skills": ["skill1","skill2","skill3","skill4","skill5"],
  "missing_skills": ["skill1","skill2","skill3","skill4"],
  "critical_gaps": <integer>,
  "important_gaps": <integer>,
  "minor_gaps": <integer>
}}
""")

    cover_prompt = PromptTemplate.from_template("""
You are an expert cover letter writer who has helped 500+ candidates get shortlisted.
Write a powerful, specific cover letter based on this resume and job description.

RESUME: {resume}
JOB DESCRIPTION: {jd}

Rules:
- 3 paragraphs only
- Never use: "I am passionate", "I am excited", "I believe", "I am a quick learner"
- Open with a specific achievement or skill, not "I am applying for..."
- Middle paragraph: connect 2-3 specific resume points to JD requirements
- Close with confidence, not desperation
- Maximum 250 words
""")

    suggestions_prompt = PromptTemplate.from_template("""
You are an expert ATS resume coach and career strategist.
Analyze this resume against the job description and give highly specific, actionable suggestions.

RESUME: {resume}
JOB DESCRIPTION: {jd}

Return ONLY in this EXACT format:

## 🔑 Missing Keywords to Add
- [Keyword]: Add to [section] — [why it matters]

## 📝 Resume Bullets to Rewrite
**Before:** [original weak bullet]
**After:** [improved bullet with metrics and JD keywords]

## 🛠️ Skills Section Gaps
- [Skill/Tool]: 🔴 High / 🟡 Medium / 🟢 Low — [free resource to learn it]

## 📚 Quick Wins (Do This Week)
- [Action]: [expected impact]

## ⚡ ATS Score Boosters
- "[exact phrase from JD]" → Add to [section]
""")

    interview_prompt = PromptTemplate.from_template("""
You are a senior technical interviewer preparing a candidate for this exact role.

RESUME: {resume}
JOB DESCRIPTION: {jd}

Generate 10 interview questions tailored to THIS candidate for THIS role.
Mix: 4 technical, 3 behavioral, 2 situational, 1 curveball.

Format:
### Q1: [Technical] Question
**Why they ask this:** One sentence
**How to answer:** Strategy using candidate's actual experience

### Q2: [Behavioral] Question
...and so on for all 10 questions.
""")

    gap_chain         = gap_prompt         | llm | StrOutputParser()
    scores_chain      = scores_prompt      | llm | StrOutputParser()
    cover_chain       = cover_prompt       | llm | StrOutputParser()
    suggestions_chain = suggestions_prompt | llm | StrOutputParser()
    interview_chain   = interview_prompt   | llm | StrOutputParser()

    # ⚡ All 5 LLM calls fire in parallel
    results = await asyncio.gather(
        async_invoke(gap_chain,          inputs),
        async_invoke(scores_chain,       inputs),
        async_invoke(cover_chain,        inputs),
        async_invoke(suggestions_chain,  inputs),
        async_invoke(interview_chain,    inputs),
    )

    analysis, scores_raw, cover_letter, suggestions, questions = results

    # Parse scores JSON safely
    cleaned = re.sub(r"```json|```", "", scores_raw).strip()
    scores = json.loads(cleaned)

    return analysis, scores, cover_letter, suggestions, questions