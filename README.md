# Singapore Job Market Intelligence Dashboard

A data-driven interactive dashboard analyzing 1M+ Singapore job postings to help job seekers and career changers make informed career decisions.

## Business Case

**Target Users:** Job seekers and career changers in Singapore

**Problem Solved:**
Career changers and mid-career professionals struggle to make informed job transition decisions because they lack real-time insights into Singapore's actual job market. They don't know which roles are genuinely in demand, what realistic salary expectations are, or how competitive different roles are.

**Solution:**
This dashboard provides comprehensive market intelligence by analyzing 1M+ real Singapore job postings, helping users:
- Identify emerging roles aligned with market demand
- Understand realistic salary expectations for different roles and experience levels
- Discover which skills employers actively seek and which command higher pay
- Benchmark competition levels to gauge role difficulty
- Make evidence-based career transition and skill development plans

## Dashboard Features

### 📊 Market Overview
- Total jobs posted and trends
- Employment type distribution (Permanent, Full-time, Contract, etc.)
- Top 10 hiring companies
- Salary distribution across market
- Key market metrics (vacancies, applications, views)

### 💼 Role Intelligence
- Top 20 in-demand roles by frequency
- Salary benchmarks (min, max, average) for each role
- Competition levels for each role
- Experience requirements
- Detailed role salary analysis & distribution
- Apply filters to see specific role data

### 🏢 Industry Trends
- Top 15 industries by job volume
- Salary ceilings by industry
- Vacancies and competition by industry
- Employment type breakdown by industry
- Industry statistics table with key metrics

### 🎯 Skills Analysis
- Top 20 most in-demand skills (parsed from job titles)
- Skill frequency distribution
- Experience level requirements distribution
- Average salary by top skills
- Identify which skills command premium salaries

### 💰 Salary Insights
- Average salary by position level (Executive, Manager, etc.)
- Salary by experience requirement
- Salary ranges and medians across positions
- Industry salary comparison
- Find highest/lowest paying roles by category

## Interactive Filters

All data can be filtered by:
- **Industries**: Select multiple job categories
- **Position Level**: Filter by seniority (Entry Level, Executive, etc.)
- **Salary Range**: Slider to set min/max monthly income (SGD)
- **Employment Type**: Permanent, Full-time, Contract, Part-time, etc.

Filters work across all tabs for focused analysis.

## Setup & Installation

### Prerequisites
- Python 3.8+
- Miniconda

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd /path/to/project/sg-market-insights
   ```

2. **Install dependencies**
   ```bash
   conda env create -f environment.yml
   ```

3. **Prepare the data**

This project now supports using a DuckDB database for faster loading of the ~1M row CSV. You have two options:

- Quick (recommended): create a DuckDB file from the CSV so the dashboard loads faster:

  ```bash
  # from the project root (sg-market-insights)
  python3 scripts/migrate_to_duckdb.py
  ```

  This will create `data/sg_jobs.duckdb` containing the table `sg_jobs`.

- Fallback: place the raw CSV next to `app.py` (or run the project from the directory that contains `SGJobData.csv`):

  ```text
  SGJobData.csv
  ```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`.

### Streamlit Cloud
```link
https://sg-job-market-insight-napltmpzajpd3fzjewntna.streamlit.app
```

## Files Overview

- **app.py** - Main Streamlit dashboard application with 5 tabs
- **sg_job_data_processor.py** - Data loading, cleaning, and analytics module
- **requirements.txt** - Python package dependencies
- **README.md** - This file

## Data Source

- **Dataset**: SGJobData.csv
- **Records**: ~1M job postings
- **Fields**: 22 columns including job title, salary, company, categories, employment type, experience requirements, applications, views, dates, etc.

## Key Insights You Can Find

- **Career Transitions**: Which roles are easiest to transition into from your background?
- **Salary Benchmarks**: What should you earn for your role and experience level?
- **Skill Gaps**: Which in-demand skills should you develop to improve earnings?
- **Market Heat**: Which roles have low competition vs high demand?
- **Industry Trends**: Which industries are hiring most and paying best?
- **Entry Points**: Where can career changers realistically start?

## How to Use

1. **Start with Market Overview** tab to see overall market trends
2. **Go to Role Intelligence** to find and benchmark your target role
3. **Check Industry Trends** to see which sectors are hiring
4. **Review Skills Analysis** to identify valuable skills to develop
5. **Use Salary Insights** to set realistic compensation expectations
6. **Apply filters** to focus on specific segments relevant to you

## Example Queries You Can Answer

- "What are the top 10 highest salary roles right now?"
- "How competitive is the Software Engineer role?"
- "What skills are most in-demand for high salaries?"
- "Which industries have the most entry-level jobs?"
- "What's the average salary for a Senior Manager in Singapore?"
- "Are there more Permanent or Full-time positions?"
- "Which companies are hiring the most?"

## Technical Stack

- **Framework**: Streamlit (Python web framework)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Data Source**: CSV file (~273MB, 1M+ rows)

## Performance Notes

- Initial load may take 1-2 minutes to process all 1M+ records
- Data is cached after first load for faster interactions
- Streamlit caches results for responsive filtering

## Future Enhancements

- Time-series trend analysis (track role popularity over time)
- Salary prediction modeling by role and experience
- Company comparison tools
- Job posting text analysis for detailed skill extraction
- Recommendation engine for career transitions
- Export capability for detailed reports

## Troubleshooting

**Error: "File not found" for SGJobData.csv**
- Ensure the CSV file is in: `SGJobData.csv`
- Check file path is relative to your working directory

**Error: "ModuleNotFoundError" for pandas, streamlit, etc.**
- Run: `pip install -r requirements.txt`

**Dashboard runs slowly**
- This is normal on first load due to processing 1M rows
- Subsequent interactions are cached and faster
- Close and reopen the page if it becomes unresponsive

## Contact & Support

This dashboard was designed for job seekers and career changers in Singapore seeking data-driven career decision support.

---

**Last Updated:** February 2025
