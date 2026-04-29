---
name: resume-builder
description: Comprehensive resume creation, revision, and tailoring. Use when the user wants to build a resume from scratch, improve an existing one, or tailor it for a specific job posting.
argument-hint: "[job title, role, or paste job description]"
---

Build or refine a resume based on $ARGUMENTS.

## Modes — detect from input

- **Build from scratch**: User provides their background (role, years of experience, skills, education)
- **Revise existing**: User provides a current resume — improve clarity, impact, and formatting
- **Tailor for a job**: User provides a job description — align resume to match keywords and requirements

## Process

### 1. Gather info (if building from scratch)
Ask for:
- Target role and industry
- Years of experience + key roles held
- Top 3–5 technical skills or tools
- Notable achievements with measurable outcomes (if any)
- Education and certifications

### 2. Write the resume sections

**Header**: Name, email, phone, LinkedIn/GitHub (if provided)

**Summary** (2–3 lines): Who you are + what you bring + target role. Action-oriented. No "I".

**Experience**: For each role:
- Company, Title, Dates
- 3–5 bullet points starting with strong action verbs
- Quantify where possible: "Reduced API latency by 40%" not "Improved performance"

**Skills**: Grouped by category (e.g., Languages, Frameworks, Tools, Cloud)

**Education**: Degree, Institution, Year

**Projects / Certifications** (if relevant)

### 3. Tailor for job description
- Extract keywords from the job posting
- Mirror language from the posting in bullets (naturally, not keyword-stuffed)
- Prioritize experience most relevant to the role
- Flag any gaps between the role requirements and the resume

## Output format
Return the full resume as clean markdown. Provide a second block with 3 specific suggestions to strengthen it further.

## Notes
- Never fabricate achievements — ask the user if specifics are missing
- ATS-friendly: avoid tables, columns, graphics in the text output
- Keep to one page unless 10+ years of experience
