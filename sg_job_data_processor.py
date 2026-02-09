import pandas as pd
import numpy as np
import json
from collections import Counter
from datetime import datetime
import re

class JobDataProcessor:
    def __init__(self, csv_path):
        """Initialize processor and load data"""
        self.df = pd.read_csv(csv_path)
        self.clean_data()
        self.extract_categories()
        self.calculate_metrics()

    def clean_data(self):
        """Clean and prepare data"""
        # Handle salary
        self.df['salary_minimum'] = pd.to_numeric(self.df['salary_minimum'], errors='coerce')
        self.df['salary_maximum'] = pd.to_numeric(self.df['salary_maximum'], errors='coerce')
        self.df['average_salary'] = self.df['average_salary'].fillna(
            (self.df['salary_minimum'] + self.df['salary_maximum']) / 2
        )

        # Handle dates
        self.df['metadata_newPostingDate'] = pd.to_datetime(
            self.df['metadata_newPostingDate'], errors='coerce'
        )

        # Clean position levels - handle NaN and empty strings
        self.df['positionLevels'] = self.df['positionLevels'].fillna('Unknown')
        self.df.loc[self.df['positionLevels'] == '', 'positionLevels'] = 'Unknown'

        # Clean employment types
        self.df['employmentTypes'] = self.df['employmentTypes'].fillna('Unknown')
        self.df.loc[self.df['employmentTypes'] == '', 'employmentTypes'] = 'Unknown'

    def extract_categories(self):
        """Extract job categories from JSON"""
        categories_list = []
        for cats in self.df['categories']:
            try:
                parsed = json.loads(cats) if isinstance(cats, str) else []
                cat_names = [cat.get('category', 'Others') for cat in parsed]
                categories_list.append(', '.join(cat_names) if cat_names else 'Others')
            except:
                categories_list.append('Others')

        self.df['main_category'] = pd.Series(categories_list, index=self.df.index)

    def calculate_metrics(self):
        """Calculate competition and engagement metrics"""
        # Handle NaN for competition metric
        self.df['metadata_totalNumberJobApplication'] = pd.to_numeric(
            self.df['metadata_totalNumberJobApplication'], errors='coerce'
        ).fillna(0)
        self.df['metadata_totalNumberOfView'] = pd.to_numeric(
            self.df['metadata_totalNumberOfView'], errors='coerce'
        ).fillna(0)
        self.df['numberOfVacancies'] = pd.to_numeric(
            self.df['numberOfVacancies'], errors='coerce'
        ).fillna(1)

        # Competition score: engagement per vacancy
        self.df['engagement_score'] = (
            self.df['metadata_totalNumberJobApplication'] +
            self.df['metadata_totalNumberOfView']
        ) / self.df['numberOfVacancies'].clip(lower=1)

        # Categorize experience level
        self.df['exp_category'] = pd.cut(
            self.df['minimumYearsExperience'],
            bins=[-1, 0, 2, 5, 10, 100],
            labels=['Entry Level', 'Junior (0-2y)', 'Mid (2-5y)', 'Senior (5-10y)', 'Expert (10y+)']
        )

    def get_top_roles(self, top_n=20):
        """Get top N roles by frequency"""
        role_stats = self.df.groupby('title').agg({
            'salary_minimum': ['mean', 'count'],
            'salary_maximum': 'mean',
            'metadata_totalNumberJobApplication': 'sum',
            'metadata_totalNumberOfView': 'sum',
            'engagement_score': 'mean',
            'minimumYearsExperience': 'mean'
        }).round(2)

        role_stats.columns = ['salary_min', 'count', 'salary_max', 'apps', 'views', 'competition', 'min_exp']
        role_stats = role_stats[role_stats['count'] >= 3].sort_values('count', ascending=False)

        return role_stats.head(top_n)

    def get_industry_stats(self):
        """Get statistics by industry"""
        industry_stats = self.df.groupby('main_category').agg({
            'title': 'count',
            'salary_minimum': 'mean',
            'salary_maximum': 'mean',
            'numberOfVacancies': 'sum',
            'engagement_score': 'mean',
            'minimumYearsExperience': 'mean'
        }).round(2)

        industry_stats.columns = ['jobs_count', 'salary_min', 'salary_max', 'vacancies', 'competition', 'min_exp']
        industry_stats = industry_stats.sort_values('jobs_count', ascending=False)
        return industry_stats

    def get_salary_by_position(self):
        """Get salary statistics by position level"""
        pos_stats = self.df.groupby('positionLevels').agg({
            'salary_minimum': ['mean', 'median', 'count'],
            'salary_maximum': ['mean', 'median'],
            'average_salary': 'mean'
        }).round(0)

        pos_stats.columns = ['salary_min_avg', 'salary_min_median', 'count', 'salary_max_avg', 'salary_max_median', 'avg_salary']
        pos_stats = pos_stats[pos_stats['count'] >= 10].sort_values('avg_salary', ascending=False)
        return pos_stats

    def get_skill_keywords(self, top_n=30):
        """Extract skill keywords from job titles"""
        # Common tech and skill keywords
        tech_keywords = {
            'Python', 'Java', 'JavaScript', 'SQL', 'C#', 'C++', 'PHP', 'React', 'Node.js',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Git', 'Linux', 'Windows',
            'Data Science', 'Machine Learning', 'AI', 'Analytics', 'BI', 'SAP', 'Salesforce',
            'Oracle', 'MySQL', 'MongoDB', '.NET', 'Angular', 'Vue', 'Django', 'Flask',
            'Tableau', 'Power BI', 'Excel', 'VBA', 'R', 'Scala', 'Golang', 'Rust',
            'DevOps', 'Cloud', 'Cybersecurity', 'Security', 'Network', 'System Admin',
            'Manager', 'Lead', 'Engineer', 'Developer', 'Analyst', 'Consultant',
            'Accountant', 'Auditor', 'Finance', 'Marketing', 'Sales', 'HR', 'Recruiter',
            'Project Manager', 'Product Manager', 'Business Analyst', 'QA', 'Testing'
        }

        skill_counter = Counter()
        for title in self.df['title'].dropna():
            for keyword in tech_keywords:
                if keyword.lower() in title.lower():
                    skill_counter[keyword] += 1

        return dict(skill_counter.most_common(top_n))

    def get_market_overview(self):
        """Get key market statistics"""
        return {
            'total_jobs': len(self.df),
            'median_salary': self.df['average_salary'].median(),
            'avg_salary': self.df['average_salary'].mean(),
            'top_company': self.df['postedCompany_name'].value_counts().index[0] if len(self.df) > 0 else 'N/A',
            'avg_applications': self.df['metadata_totalNumberJobApplication'].mean(),
            'avg_views': self.df['metadata_totalNumberOfView'].mean(),
            'total_vacancies': self.df['numberOfVacancies'].sum()
        }

    def filter_data(self, roles=None, industries=None, salary_range=None, exp_level=None, position=None):
        """Filter data based on criteria"""
        filtered = self.df.copy()

        if roles:
            filtered = filtered[filtered['title'].isin(roles)]
        if industries:
            filtered = filtered[filtered['main_category'].str.contains('|'.join(industries), case=False, na=False)]
        if salary_range:
            filtered = filtered[
                (filtered['average_salary'] >= salary_range[0]) &
                (filtered['average_salary'] <= salary_range[1])
            ]
        if exp_level:
            filtered = filtered[filtered['exp_category'].isin(exp_level)]
        if position:
            filtered = filtered[filtered['positionLevels'].isin(position)]

        return filtered
