import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Try to import the processor - handle both possible locations
try:
    from sg_job_data_processor import JobDataProcessor
except ImportError:
    # If in different directory, add path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sg_job_data_processor import JobDataProcessor

from datetime import datetime

# Page configuration
st.set_page_config(page_title="SG Job Market Intelligence", layout="wide")

# Load data
@st.cache_resource
def load_data():
    csv_path = "SGJobData.csv"
    return JobDataProcessor(csv_path)

try:
    processor = load_data()
    df = processor.df
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please ensure SGJobData.csv is in the correct location: ntu-data-science-ai/lesson_1_6/SGJobData.csv")
    st.stop()

# Title and introduction
st.title("🇸🇬 Singapore Job Market Intelligence Dashboard")
st.markdown("""
**Help job seekers and career changers make informed decisions** with real-time insights from 1M+ Singapore job postings.
Discover in-demand roles, salary benchmarks, and emerging opportunities.
""")

# Sidebar filters
st.sidebar.header("🔍 Filters")
selected_industries = st.sidebar.multiselect(
    "Industries",
    options=sorted(df['main_category'].unique()),
    default=[]
)

salary_range = st.sidebar.slider(
    "Salary Range (Monthly SGD)",
    min_value=0,
    max_value=int(df['salary_maximum'].max()),
    value=(0, int(df['salary_maximum'].quantile(0.9))),
    step=500
)

selected_positions = st.sidebar.multiselect(
    "Position Level",
    options=sorted(df['positionLevels'].unique()),
    default=[]
)

employment_type = st.sidebar.multiselect(
    "Employment Type",
    options=sorted(df['employmentTypes'].unique()),
    default=['Permanent', 'Full Time']
)

# Apply filters
filtered_df = df.copy()
if selected_industries:
    filtered_df = filtered_df[filtered_df['main_category'].str.contains('|'.join(selected_industries), case=False, na=False)]
if selected_positions:
    filtered_df = filtered_df[filtered_df['positionLevels'].isin(selected_positions)]
if salary_range:
    filtered_df = filtered_df[
        (filtered_df['average_salary'] >= salary_range[0]) &
        (filtered_df['average_salary'] <= salary_range[1])
    ]
if employment_type:
    filtered_df = filtered_df[filtered_df['employmentTypes'].isin(employment_type)]

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📊 Market Overview", "💼 Role Intelligence", "🏢 Industry Trends", "🎯 Skills Analysis", "💰 Salary Insights"]
)

# ===== TAB 1: MARKET OVERVIEW =====
with tab1:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Jobs Posted", f"{len(filtered_df):,}")
    with col2:
        median_sal = filtered_df['average_salary'].median()
        st.metric("Median Salary", f"${median_sal:,.0f}" if not pd.isna(median_sal) else "N/A")
    with col3:
        avg_apps = filtered_df['metadata_totalNumberJobApplication'].mean()
        st.metric("Avg Applications/Job", f"{avg_apps:.1f}" if not pd.isna(avg_apps) else "N/A")
    with col4:
        st.metric("Total Vacancies", f"{filtered_df['numberOfVacancies'].sum():,}")

    # Employment type distribution
    col1, col2 = st.columns(2)
    with col1:
        emp_dist = filtered_df['employmentTypes'].value_counts()
        if len(emp_dist) > 0:
            fig_emp = px.pie(values=emp_dist.values, names=emp_dist.index, title="Employment Type Distribution")
            st.plotly_chart(fig_emp, use_container_width=True)
        else:
            st.info("No data available for this filter combination")

    with col2:
        # Top companies
        top_companies = filtered_df['postedCompany_name'].value_counts().head(10)
        if len(top_companies) > 0:
            fig_comp = px.bar(y=top_companies.index, x=top_companies.values, orientation='h',
                             title="Top 10 Hiring Companies", labels={'x': 'Number of Jobs', 'y': 'Company'})
            fig_comp.update_layout(showlegend=False)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("No company data available")

    # Salary distribution
    if len(filtered_df) > 0 and filtered_df['average_salary'].notna().sum() > 0:
        fig_salary = px.histogram(filtered_df, x='average_salary', nbins=50,
                                 title="Salary Distribution", labels={'average_salary': 'Salary (SGD)', 'count': 'Jobs'})
        fig_salary.update_layout(showlegend=False)
        st.plotly_chart(fig_salary, use_container_width=True)

# ===== TAB 2: ROLE INTELLIGENCE =====
with tab2:
    st.subheader("Top In-Demand Roles")

    role_stats = processor.get_top_roles(top_n=20)
    if len(role_stats) > 0:
        role_stats_reset = role_stats.reset_index()
        role_stats_reset.columns = ['Role', 'Salary Min', 'Count', 'Salary Max', 'Applications', 'Views', 'Competition', 'Min Exp']

        # Top roles by count
        col1, col2 = st.columns(2)
        with col1:
            fig_roles = px.bar(role_stats_reset.head(10), x='Count', y='Role', orientation='h',
                              title="Top 10 Roles by Job Count")
            st.plotly_chart(fig_roles, use_container_width=True)

        with col2:
            fig_comp_roles = px.bar(role_stats_reset.head(10), x='Competition', y='Role', orientation='h',
                                   title="Top 10 Roles by Competition Level")
            st.plotly_chart(fig_comp_roles, use_container_width=True)

        # Role comparison table
        st.subheader("Role Statistics (Top 20)")
        display_cols = ['Role', 'Count', 'Salary Min', 'Salary Max', 'Applications', 'Competition', 'Min Exp']
        st.dataframe(role_stats_reset[display_cols].head(20), use_container_width=True, hide_index=True)

        # Role salary benchmark
        st.subheader("Role Salary Benchmark")
        role_search = st.selectbox("Select a role to see salary details", role_stats_reset['Role'].head(20).tolist())
        role_data = filtered_df[filtered_df['title'] == role_search]

        if len(role_data) > 0:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Salary", f"${role_data['average_salary'].mean():,.0f}")
            with col2:
                st.metric("Min-Max Range", f"${role_data['salary_minimum'].mean():,.0f}-${role_data['salary_maximum'].mean():,.0f}")
            with col3:
                st.metric("Jobs Posted", len(role_data))
            with col4:
                avg_app = role_data['metadata_totalNumberJobApplication'].mean()
                st.metric("Avg Applications", f"{avg_app:.1f}")

            # Salary distribution for selected role
            if role_data['average_salary'].notna().sum() > 0:
                fig_role_salary = px.histogram(role_data, x='average_salary', nbins=20,
                                              title=f"Salary Distribution - {role_search}")
                st.plotly_chart(fig_role_salary, use_container_width=True)
    else:
        st.info("No role data available for the selected filters")

# ===== TAB 3: INDUSTRY TRENDS =====
with tab3:
    st.subheader("Industry Statistics")

    industry_stats = processor.get_industry_stats()
    if len(industry_stats) > 0:
        industry_stats_reset = industry_stats.reset_index()
        industry_stats_reset.columns = ['Industry', 'Jobs', 'Salary Min', 'Salary Max', 'Vacancies', 'Competition', 'Min Exp']

        # Industry distribution
        col1, col2 = st.columns(2)
        with col1:
            fig_ind = px.bar(industry_stats_reset.head(15), x='Jobs', y='Industry', orientation='h',
                            title="Top 15 Industries by Job Count")
            st.plotly_chart(fig_ind, use_container_width=True)

        with col2:
            fig_ind_sal = px.bar(industry_stats_reset.head(15), x='Salary Max', y='Industry', orientation='h',
                                title="Top Industries by Salary Ceiling")
            st.plotly_chart(fig_ind_sal, use_container_width=True)

        # Industry table
        st.subheader("Industry Details (Top 25)")
        st.dataframe(industry_stats_reset.head(25), use_container_width=True, hide_index=True)

        # Employment type by industry
        st.subheader("Employment Type Distribution by Industry")
        emp_by_ind = pd.crosstab(df['main_category'], df['employmentTypes'])
        if len(emp_by_ind) > 0:
            fig_emp_ind = px.bar(emp_by_ind.head(10), title="Employment Types by Top Industries",
                                labels={'value': 'Count', 'main_category': 'Industry'})
            st.plotly_chart(fig_emp_ind, use_container_width=True)
    else:
        st.info("No industry data available")

# ===== TAB 4: SKILLS ANALYSIS =====
with tab4:
    st.subheader("In-Demand Skills & Keywords")

    skills = processor.get_skill_keywords(top_n=25)
    if len(skills) > 0:
        skills_df = pd.DataFrame(list(skills.items()), columns=['Skill', 'Frequency'])
        skills_df = skills_df.sort_values('Frequency', ascending=False)

        # Skills bar chart
        fig_skills = px.bar(skills_df.head(20), x='Frequency', y='Skill', orientation='h',
                           title="Top 20 Most In-Demand Skills (from job titles)")
        st.plotly_chart(fig_skills, use_container_width=True)

        # Skills table
        st.subheader("Skill Frequency")
        st.dataframe(skills_df, use_container_width=True, hide_index=True)

        # Experience requirement distribution
        st.subheader("Experience Requirements Distribution")
        exp_dist = filtered_df['exp_category'].value_counts().sort_index()
        if len(exp_dist) > 0:
            fig_exp = px.bar(x=exp_dist.index.astype(str), y=exp_dist.values,
                             labels={'x': 'Experience Level', 'y': 'Number of Jobs'},
                             title="Jobs by Experience Requirement")
            st.plotly_chart(fig_exp, use_container_width=True)

        # Skills by salary (top skills and their average salary)
        st.subheader("Average Salary by Top Skills")
        top_skills_list = list(skills.keys())[:10]
        salary_by_skill = []

        for skill in top_skills_list:
            skill_jobs = filtered_df[filtered_df['title'].str.contains(skill, case=False, na=False)]
            if len(skill_jobs) > 0:
                salary_by_skill.append({
                    'Skill': skill,
                    'Avg Salary': skill_jobs['average_salary'].mean(),
                    'Count': len(skill_jobs)
                })

        if len(salary_by_skill):
            skill_salary_df = pd.DataFrame(salary_by_skill).sort_values('Avg Salary', ascending=False)
            fig_skill_sal = px.bar(skill_salary_df, x='Avg Salary', y='Skill', orientation='h',
                                  title="Average Salary by Top Skills")
            st.plotly_chart(fig_skill_sal, use_container_width=True)
    else:
        st.info("No skill data available")

# ===== TAB 5: SALARY INSIGHTS =====
with tab5:
    st.subheader("Salary by Position Level")

    pos_stats = processor.get_salary_by_position()
    if len(pos_stats) > 0:
        pos_stats_reset = pos_stats.reset_index()
        pos_stats_reset.columns = ['Position', 'Salary Min Avg', 'Salary Min Median', 'Count', 'Salary Max Avg', 'Salary Max Median', 'Avg Salary']

        # Salary by position
        fig_pos_sal = px.bar(pos_stats_reset, x='Avg Salary', y='Position', orientation='h',
                            title="Average Salary by Position Level",
                            labels={'Avg Salary': 'Average Salary (SGD)', 'Position': 'Position Level'})
        st.plotly_chart(fig_pos_sal, use_container_width=True)

        # Position salary details table
        st.subheader("Position Level Salary Benchmarks")
        st.dataframe(pos_stats_reset, use_container_width=True, hide_index=True)

    # Salary by experience level
    st.subheader("Salary by Experience Requirement")
    exp_salary = filtered_df.groupby('exp_category').agg({
        'average_salary': ['mean', 'median', 'min', 'max', 'count']
    }).round(0)
    exp_salary.columns = ['Mean', 'Median', 'Min', 'Max', 'Count']
    exp_salary = exp_salary[exp_salary['Count'] >= 5]

    if len(exp_salary) > 0:
        fig_exp_sal = px.bar(exp_salary.reset_index(), x='exp_category', y='Mean',
                            title="Average Salary by Experience Level",
                            labels={'exp_category': 'Experience Level', 'Mean': 'Average Salary (SGD)'})
        st.plotly_chart(fig_exp_sal, use_container_width=True)

        st.dataframe(exp_salary, use_container_width=True)

    # Salary trends by industry
    st.subheader("Salary Range by Industry")
    ind_salary = df.groupby('main_category').agg({
        'average_salary': 'mean',
        'salary_minimum': 'mean',
        'salary_maximum': 'mean'
    }).round(0).sort_values('average_salary', ascending=False).head(15)

    if len(ind_salary) > 0:
        fig_ind_sal_dist = px.bar(ind_salary.reset_index().head(15), x='average_salary', y='main_category', orientation='h',
                                  title="Average Salary by Industry (Top 15)")
        st.plotly_chart(fig_ind_sal_dist, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"""
**📌 About This Dashboard:**
- Data: ~1M Singapore job postings
- Last Updated: {datetime.now().strftime("%B %d, %Y")}
- **For Job Seekers & Career Changers:** Use this market intelligence to make informed career decisions.
- **Salary Benchmarks:** Compare roles, industries, and experience levels to understand market expectations.
- **Skills Demand:** Identify which skills command higher salaries and are most in-demand.
""")
