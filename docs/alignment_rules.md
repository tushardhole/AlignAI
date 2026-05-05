# Resume/Cover Letter Alignment Rules

## Overview

AlignAI uses a two-phase approach to align resumes and cover letters to
target job opportunities:

1. **Alignment Phase**: Rewrite resume/cover letter using LLM agents
   (single-pass or chunked based on document size)
2. **Structuring Phase**: Extract aligned content into JSON schema for
   PDF/HTML rendering

## Single-Pass vs Chunked Decision

The system chooses between two alignment strategies based on combined
document size:

```text
combined_length = len(resume.content) + len(job.description)

if combined_length <= 12,000 chars:
  → Single-pass alignment (faster, one LLM call per section)
else:
  → Chunked alignment (handles large docs, 3 LLM calls)
```

### Single-Pass (≤ 12,000 chars combined)

- **Speed**: ~12-15 seconds
- **Flow**: Resume → AlignedResumeFields → StructuredResumeFields
- **Quality**: Full context for alignment, best coherence
- **Agents**: JobAnalyst, ResumeAligner, Structurers (5 agents)

### Chunked (> 12,000 chars combined)

- **Speed**: ~20-25 seconds (parallel section alignment)
- **Flow**: Parse sections → Align each (parallel) → Merge → Structure
- **Quality**: Focused section-level changes, handles large documents
- **Agents**: JobAnalyst, ResumeParser, ResumeSectionAligner (parallel),
  ResumeMerger, Structurers (8 agents)

## Agent Rules & Responsibilities

### 1. JobAnalyst

- **Persona**: Expert ATS analyst
- **Input**: Job URL, title, description (truncated to 18,000 chars)
- **Output**: `JobBriefFields` with title, summary, must_have_skills (≤15),
  nice_to_have_skills (≤10)
- **Key Rules**:
  - Do not invent requirements
  - Prioritize technical/domain-specific skills over soft skills
  - Be specific: "AWS EC2, S3, RDS" not "Cloud"
  - Select MOST RELEVANT skills if over limit, not just first 15
  - Distinguish must-have (explicit requirements) from nice-to-have
    (mentioned as "preferred")

### 2. ResumeAligner (Single-Pass)

- **Persona**: Expert ATS analyst and resume writer
- **Input**: Resume text, job brief, job description
- **Output**: Plain text aligned resume
- **Key Rules**:
  - Keep facts truthful; rephrase ONLY for clarity
  - Keep 4-8 bullets per role (prefer 4-6, but don't force if all
    relevant)
  - PRESERVE ALL Tech/Tools/Stack lines exactly (these become meta array)
  - Remove ONLY truly redundant/irrelevant bullets (decision tree approach)
  - Plain UTF-8 only (no markdown)
  - Preserve Open Source/Personal Projects sections as-is

### 3. ResumeSectionAligner (Chunked)

- **Input**: Section heading, content, job brief, job description
  ([:12,000])
- **Output**: `SectionAlignedFields` with aligned content
- **Key Rules**:
  - Preserve employers, dates, degrees exactly
  - Rewrite bullet points for alignment
  - Keep section structure/order

### 4. ResumeMerger (Chunked)

- **Input**: Stitched sections, job brief, job description ([:4,000])
- **Output**: `MergedResumeFields` with single "content" key
- **Key Rules**:
  - Remove redundancy between sections
  - Never invent employers/dates/achievements
  - Ensure natural flow across sections
  - Output MUST be: `{"content": "...full resume text..."}`

### 5. ResumeStructurer

- **Input**: Plain text aligned resume
- **Output**: `StructuredResumeFields` with JSON schema (name, email,
  skills, experience, etc.)
- **Key Rules**:
  - Include ALL bullet points exactly as written
  - Extract EVERY Tech/Tools/Stack/Environment/Platforms line as
    separate meta entry
  - Preserve professional summary word-for-word, no shortening
  - Detect and extract extra sections (Open Source, Personal Projects)
    with correct titles
  - Do NOT modify, rephrase, or drop any content

### 6. CoverLetterAligner

- **Input**: Base cover letter, job brief, job description
- **Output**: Plain text tailored cover letter
- **Key Rules**:
  - Professional tone
  - No "Dear Hiring Manager" placeholders
  - Reference relevant skills/projects from brief
  - 2-3 paragraphs, concise

### 7. CoverLetterStructurer

- **Input**: Plain text cover letter
- **Output**: `StructuredCoverLetterFields` with candidate_name and
  paragraphs array
- **Key Rules**:
  - Extract candidate name from letterhead/greeting/signature
  - Paragraphs: body only, omit greeting/closing
  - If name not found, leave empty string

### 8. ATSScorer

- **Persona**: Expert ATS analyst
- **Input**: Resume ([:12,000]), cover letter ([:8,000]), job ([:8,000])
- **Output**: `AtsScoreFields` with score 1-100
- **Key Rules**:
  - Use full 1-100 scale (not compressed to 50-100)
  - Consider keyword match density, technical terminology, formatting
    clarity
  - 80+ likely passes ATS, <50 likely fails

### 9. MatchScorer

- **Input**: Resume ([:12,000]), cover letter ([:8,000]), job ([:8,000])
- **Output**: `MatchScoreFields` with score 1-5 + MatchLabel enum
- **Key Rules**:
  - 5 = excellent match (most skills present, strong alignment)
  - 3 = fair match (some skills, moderate alignment)
  - 1 = poor match (few skills, low alignment)

## Character Limits & Truncation

| Component | Limit | Purpose |
| --- | --- | --- |
| Job description (job_brief) | 18,000 chars | JobAnalyst context |
| Resume (ATS/Match scorer) | 12,000 chars | Token budget |
| Cover letter (ATS/Match scorer) | 8,000 chars | Token budget |
| Job description (ATS/Match scorer) | 8,000 chars | Token budget |
| Resume (section aligner, chunked) | 12,000 chars | Section context |
| Job description (merger) | 4,000 chars | Merger context |

**Truncation Strategy**: If content exceeds limit, take first N chars
and append marker.

### ⚠️ Token Budget Trade-off: ATS/Match Scoring on Truncated Resume

**Current Design**: ATS and Match scorers receive only first 12,000 chars
of resume (if longer).

**Why?** LLM token budget constraint:

- Resume (12K) + Cover letter (8K) + Job (8K) = ~28K tokens
- Prevents context overflow while keeping scores fast (~2-3 seconds)
- Groq context limit blocks full resume + cover + job for longer docs

**Impact on Scoring Accuracy**:

- Resumes > 12K chars lose information: experience, skills, awards,
  publications, extra sections
- ATS/Match scores reflect only beginning of resume, not complete
  picture
- **Result**: Potentially **underestimated fit scores** for longer
  resumes

**Mitigation**:

- Resume alignment (single-pass or chunked) produces plain text with
  only relevant content
- Aligned resume is typically < 12K chars even if original was longer
- In practice: aligned resume usually fits within 12K, scores accurate

**Future Improvement**:

- Implement smart truncation: take first 10K + last 2K chars
- Or: conditionally truncate only if actual length exceeds limit
- Or: use hierarchical scoring (quick pass on truncated, detailed on
  full if needed)

## Prompt Management

All LLM agent instructions live in `src/alignai/agents/prompts/` as
separate `.txt` files:

```text
src/alignai/agents/prompts/
├── job_analyst.txt
├── resume_aligner.txt
├── cover_letter_aligner.txt
├── ats_scorer.txt
├── match_scorer.txt
├── resume_structurer.txt
├── cover_letter_structurer.txt
├── resume_parser.txt
├── resume_section_aligner.txt
├── resume_merger.txt
└── schema_hints/
    ├── job_brief_shape.txt
    ├── resume_structure.txt
    ├── cover_letter_structure.txt
    ├── resume_parser_shape.txt
    └── merger_output.txt
```

Prompts are loaded via `alignai.agents.prompts.load_prompt(name)` and
`load_schema_hint(name)`.

## Quality Assurance Checklist

Before shipping alignment result, verify:

- [ ] All original bullets preserved (not shortened without reason)
- [ ] Tech/Tools/Stack lines in meta array
- [ ] Professional summary preserved word-for-word
- [ ] Extra sections (Open Source, etc.) present with correct titles
- [ ] Cover letter has correct candidate name extracted
- [ ] Cover letter has no greeting/closing boilerplate
- [ ] ATS score on full 1-100 scale
- [ ] Match score reflects true fit (5=excellent, 1=poor)
- [ ] PDF renders without formatting issues (margins, spacing, links clickable)

## Maintenance & Documentation

When modifying alignment logic, update this document if you change:

- Agent instructions (update corresponding .txt file AND this doc)
- Character thresholds (update all 3 locations: code, this doc, commit
  message)
- JSON schemas (update schema hint files AND this doc)
- Chunking decision logic (update this doc's decision tree)

This ensures docs stay in sync with code.
