import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Set page configuration
st.set_page_config(
    page_title="Real Estate Investment Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 1rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5;
        color: white;
    }
    h1, h2, h3 {
        padding-top: 1rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .risk-low {color: green;}
    .risk-medium {color: orange;}
    .risk-high {color: red;}
    </style>
""", unsafe_allow_html=True)

# Sample property database
SAMPLE_PROPERTIES = [
    {
        "name": "Downtown Apartment",
        "price": 250000,
        "rental_income": 2000,
        "expenses": 600,
        "location": "Urban",
        "property_type": "Apartment",
        "area": 850,
        "age": 15,
        "vacancy_rate": 5,
        "appreciation_rate": 3.5,
    },
    {
        "name": "Suburban House",
        "price": 350000,
        "rental_income": 2500,
        "expenses": 800,
        "location": "Suburban",
        "property_type": "Single Family",
        "area": 1800,
        "age": 12,
        "vacancy_rate": 4,
        "appreciation_rate": 3.0,
    },
    {
        "name": "Beach Condo",
        "price": 400000,
        "rental_income": 3200,
        "expenses": 1100,
        "location": "Coastal",
        "property_type": "Condo",
        "area": 1100,
        "age": 5,
        "vacancy_rate": 8,
        "appreciation_rate": 4.2,
    },
    {
        "name": "Rural Farm House",
        "price": 180000,
        "rental_income": 1400,
        "expenses": 500,
        "location": "Rural",
        "property_type": "Single Family",
        "area": 1600,
        "age": 35,
        "vacancy_rate": 6,
        "appreciation_rate": 2.0,
    },
]

# Define market conditions
MARKET_CONDITIONS = {
    "Strong Growth": {"vacancy_impact": -2, "appreciation_impact": 2, "price_trend": 5},
    "Stable": {"vacancy_impact": 0, "appreciation_impact": 0, "price_trend": 2},
    "Declining": {"vacancy_impact": 3, "appreciation_impact": -2, "price_trend": -3},
    "Volatile": {"vacancy_impact": 2, "appreciation_impact": 1, "price_trend": 0},
}

def calculate_metrics(price, rental_income, expenses, down_payment, loan_rate, loan_term, 
                    vacancy_rate, appreciation_rate, tax_rate, closing_costs, renovation_costs, 
                    annual_income_growth=2, annual_expense_growth=3):
    """Calculate key real estate investment metrics."""
    
    # Initial investment calculation
    initial_investment = down_payment + closing_costs + renovation_costs
    
    # Loan details
    loan_amount = price - down_payment
    monthly_interest_rate = loan_rate / 12 / 100 if loan_rate > 0 else 0
    num_payments = loan_term * 12 if loan_term > 0 else 0
    
    # Monthly mortgage payment (Principal and Interest)
    if loan_amount > 0 and monthly_interest_rate > 0 and num_payments > 0:
        mortgage_payment = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**num_payments) / \
                        ((1 + monthly_interest_rate)**num_payments - 1)
    else:
        mortgage_payment = 0
    
    # Effective rental income (accounting for vacancy)
    effective_rental_income = rental_income * (1 - vacancy_rate / 100)
    
    # Monthly cash flow
    monthly_cash_flow = effective_rental_income - expenses - mortgage_payment
    annual_cash_flow = monthly_cash_flow * 12
    
    # ROI (Return on Investment)
    roi = (annual_cash_flow / initial_investment) * 100 if initial_investment > 0 else 0
    
    # Cap Rate
    cap_rate = ((effective_rental_income - expenses) * 12 / price) * 100 if price > 0 else 0
    
    # Cash-on-Cash Return
    cash_on_cash = (annual_cash_flow / initial_investment) * 100 if initial_investment > 0 else 0
    
    # Break-even point (months)
    break_even = initial_investment / monthly_cash_flow if monthly_cash_flow > 0 else float('inf')
    
    # Tax calculations
    depreciation_period = 27.5  # years for residential real estate
    annual_depreciation = (price - (price * 0.2)) / depreciation_period  # assuming land is 20% of property value
    
    taxable_income = effective_rental_income * 12 - expenses * 12 - annual_depreciation - mortgage_payment * 12 * loan_rate / 100
    tax_savings = max(0, taxable_income * tax_rate / 100)
    
    # After-tax cash flow
    after_tax_cash_flow = annual_cash_flow + tax_savings
    
    # Property appreciation
    future_value_5yr = price * (1 + appreciation_rate / 100) ** 5
    future_value_10yr = price * (1 + appreciation_rate / 100) ** 10
    future_value_20yr = price * (1 + appreciation_rate / 100) ** 20
    
    # Loan amortization
    remaining_balance = loan_amount
    total_equity_5yr = future_value_5yr - remaining_balance if loan_term >= 5 else future_value_5yr
    total_equity_10yr = future_value_10yr - remaining_balance if loan_term >= 10 else future_value_10yr
    
    return {
        "monthly_cash_flow": monthly_cash_flow,
        "annual_cash_flow": annual_cash_flow,
        "roi": roi,
        "cap_rate": cap_rate,
        "cash_on_cash": cash_on_cash,
        "mortgage_payment": mortgage_payment,
        "break_even_months": break_even,
        "tax_savings": tax_savings,
        "after_tax_cash_flow": after_tax_cash_flow,
        "future_value_5yr": future_value_5yr,
        "future_value_10yr": future_value_10yr,
        "future_value_20yr": future_value_20yr,
        "total_equity_5yr": total_equity_5yr,
        "total_equity_10yr": total_equity_10yr,
        "initial_investment": initial_investment,
    }

def calculate_cash_flow_projection(price, rental_income, expenses, down_payment, loan_rate, loan_term, 
                                vacancy_rate, appreciation_rate, years=10, 
                                annual_income_growth=2, annual_expense_growth=3):
    """Generate cash flow projections over time."""
    
    # Initial values
    loan_amount = price - down_payment
    monthly_interest_rate = loan_rate / 12 / 100
    num_payments = loan_term * 12
    
    # Calculate mortgage payment
    if loan_amount > 0 and monthly_interest_rate > 0 and num_payments > 0:
        mortgage_payment = (loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**num_payments) / \
                        ((1 + monthly_interest_rate)**num_payments - 1)
    else:
        mortgage_payment = 0
        
    projection_data = []
    
    for year in range(1, years + 1):
        # Adjusted for growth
        year_rental_income = rental_income * ((1 + annual_income_growth / 100) ** (year - 1))
        year_expenses = expenses * ((1 + annual_expense_growth / 100) ** (year - 1))
        
        # Account for vacancy
        effective_rental_income = year_rental_income * (1 - vacancy_rate / 100)
        
        # Calculate annual values
        annual_mortgage = mortgage_payment * 12
        annual_income = effective_rental_income * 12
        annual_expenses = year_expenses * 12
        annual_cash_flow = annual_income - annual_expenses - annual_mortgage
        
        # Property value with appreciation
        property_value = price * ((1 + appreciation_rate / 100) ** year)
        
        projection_data.append({
            "year": year,
            "property_value": property_value,
            "annual_income": annual_income,
            "annual_expenses": annual_expenses,
            "annual_mortgage": annual_mortgage,
            "annual_cash_flow": annual_cash_flow,
            "cumulative_cash_flow": annual_cash_flow * year  # Simplified cumulative
        })
        
    return projection_data

def analyze_risk(price, vacancy_rate, expenses, rental_income, market_condition, property_age, location):
    """Analyze investment risk based on multiple factors."""
    
    # Adjust vacancy rate based on market conditions
    adjusted_vacancy = vacancy_rate + MARKET_CONDITIONS[market_condition]["vacancy_impact"]
    
    # Price to rent ratio (annual)
    price_to_rent = price / (rental_income * 12)
    
    # Expense ratio
    expense_ratio = (expenses * 12) / (rental_income * 12) * 100
    
    # Risk factors
    risk_factors = {
        "Vacancy Risk": {
            "score": 1 if adjusted_vacancy < 5 else (2 if adjusted_vacancy < 8 else 3),
            "description": f"Adjusted vacancy rate of {adjusted_vacancy}% indicates "
                        f"{'low' if adjusted_vacancy < 5 else ('moderate' if adjusted_vacancy < 8 else 'high')} risk."
        },
        "Price to Rent Ratio": {
            "score": 1 if price_to_rent < 15 else (2 if price_to_rent < 20 else 3),
            "description": f"Price to annual rent ratio of {price_to_rent:.1f} indicates "
                        f"{'good' if price_to_rent < 15 else ('fair' if price_to_rent < 20 else 'poor')} cash flow potential."
        },
        "Expense Ratio": {
            "score": 1 if expense_ratio < 35 else (2 if expense_ratio < 45 else 3),
            "description": f"Expense ratio of {expense_ratio:.1f}% is "
                        f"{'favorable' if expense_ratio < 35 else ('typical' if expense_ratio < 45 else 'concerning')}."
        },
        "Market Condition": {
            "score": 1 if market_condition in ["Strong Growth", "Stable"] else (2 if market_condition == "Volatile" else 3),
            "description": f"{market_condition} market suggests {('low' if market_condition in ['Strong Growth', 'Stable'] else ('moderate' if market_condition == 'Volatile' else 'high'))} risk."
        },
        "Property Age": {
            "score": 1 if property_age < 10 else (2 if property_age < 30 else 3),
            "description": f"{property_age} year old property has {('low' if property_age < 10 else ('moderate' if property_age < 30 else 'high'))} maintenance risk."
        }
    }
    
    # Overall risk score (1-3 scale where 1 is low risk, 3 is high risk)
    avg_score = sum(factor["score"] for factor in risk_factors.values()) / len(risk_factors)
    
    if avg_score < 1.7:
        risk_level = "Low"
        risk_class = "risk-low"
    elif avg_score < 2.3:
        risk_level = "Medium"
        risk_class = "risk-medium"
    else:
        risk_level = "High"
        risk_class = "risk-high"
        
    return {
        "overall_risk": risk_level,
        "risk_class": risk_class,
        "risk_score": avg_score,
        "factors": risk_factors
    }

def display_metrics_dashboard(metrics):
    """Display investment metrics in a nice dashboard layout."""
    
    # Top row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Monthly Cash Flow", f"${metrics['monthly_cash_flow']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Cash-on-Cash Return", f"{metrics['cash_on_cash']:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Cap Rate", f"{metrics['cap_rate']:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col4:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("ROI", f"{metrics['roi']:.2f}%")
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Second row of metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        if metrics['break_even_months'] != float('inf'):
            st.metric("Break-Even (months)", f"{metrics['break_even_months']:.1f}")
        else:
            st.metric("Break-Even", "N/A")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Initial Investment", f"${metrics['initial_investment']:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='metric-container'>", unsafe_allow_html=True)
        st.metric("Monthly Mortgage", f"${metrics['mortgage_payment']:.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

def main():
    """Main application function for the Real Estate Investment Analyzer."""
    
    # App title and introduction
    st.title("Real Estate Investment Analyzer")
    st.markdown("""
    This tool helps you analyze potential real estate investments by calculating key metrics, 
    projecting future cash flows, and assessing investment risks.
    
    Enter your property details below to get started.
    """)
    
    # Create tabs for different sections
    tabs = st.tabs(["Property Details", "Analysis Results", "Cash Flow Projections", "Risk Assessment"])
    
    with tabs[0]:
        st.header("Property Details")
        
        # Option to use sample property or enter custom details
        use_sample = st.checkbox("Use sample property data")
        
        if use_sample:
            sample_property = st.selectbox(
                "Select a sample property", 
                options=[prop["name"] for prop in SAMPLE_PROPERTIES],
                index=0
            )
            
            # Get selected property data
            selected_property = next(prop for prop in SAMPLE_PROPERTIES if prop["name"] == sample_property)
            
            # Display sample property details
            st.write("##### Property Information")
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Purchase Price ($)", value=selected_property["price"], min_value=0)
                rental_income = st.number_input("Monthly Rental Income ($)", value=selected_property["rental_income"], min_value=0)
                expenses = st.number_input("Monthly Expenses ($)", value=selected_property["expenses"], min_value=0)
            with col2:
                property_type = st.text_input("Property Type", value=selected_property["property_type"])
                area = st.number_input("Area (sq ft)", value=selected_property["area"], min_value=0)
                property_age = st.number_input("Property Age (years)", value=selected_property["age"], min_value=0)
                
            st.write("##### Financial Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                down_payment_percent = st.slider("Down Payment (%)", min_value=1, max_value=100, value=20)
                down_payment = price * down_payment_percent / 100
                st.write(f"Down Payment: ${down_payment:,.2f}")
            with col2:
                loan_rate = st.number_input("Loan Interest Rate (%)", value=5.5, min_value=0.0, max_value=20.0, step=0.1)
            with col3:
                loan_term = st.number_input("Loan Term (years)", value=30, min_value=1, max_value=50)
            
            st.write("##### Market Conditions")
            col1, col2, col3 = st.columns(3)
            with col1:
                vacancy_rate = st.number_input("Vacancy Rate (%)", value=selected_property["vacancy_rate"], min_value=0.0, max_value=100.0, step=0.5)
            with col2:
                appreciation_rate = st.number_input("Annual Appreciation Rate (%)", value=selected_property["appreciation_rate"], min_value=-10.0, max_value=20.0, step=0.1)
            with col3:
                market_condition = st.selectbox("Market Condition", options=list(MARKET_CONDITIONS.keys()), index=1)
            
            st.write("##### Additional Costs")
            col1, col2, col3 = st.columns(3)
            with col1:
                closing_costs = st.number_input("Closing Costs ($)", value=round(price * 0.03), min_value=0)
            with col2:
                renovation_costs = st.number_input("Renovation Costs ($)", value=0, min_value=0)
            with col3:
                tax_rate = st.number_input("Income Tax Rate (%)", value=25.0, min_value=0.0, max_value=50.0, step=0.5)
        
        else:
            # Custom input fields if not using sample data
            st.write("##### Property Information")
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Purchase Price ($)", value=300000, min_value=0)
                rental_income = st.number_input("Monthly Rental Income ($)", value=2000, min_value=0)
                expenses = st.number_input("Monthly Expenses ($)", value=600, min_value=0)
            with col2:
                property_type = st.selectbox("Property Type", options=["Single Family", "Apartment", "Condo", "Multi-Family", "Commercial"])
                area = st.number_input("Area (sq ft)", value=1500, min_value=0)
                property_age = st.number_input("Property Age (years)", value=15, min_value=0)
                
            st.write("##### Financial Details")
            col1, col2, col3 = st.columns(3)
            with col1:
                down_payment_percent = st.slider("Down Payment (%)", min_value=1, max_value=100, value=20)
                down_payment = price * down_payment_percent / 100
                st.write(f"Down Payment: ${down_payment:,.2f}")
            with col2:
                loan_rate = st.number_input("Loan Interest Rate (%)", value=5.5, min_value=0.0, max_value=20.0, step=0.1)
            with col3:
                loan_term = st.number_input("Loan Term (years)", value=30, min_value=1, max_value=50)
            
            st.write("##### Market Conditions")
            col1, col2, col3 = st.columns(3)
            with col1:
                vacancy_rate = st.number_input("Vacancy Rate (%)", value=5.0, min_value=0.0, max_value=100.0, step=0.5)
            with col2:
                appreciation_rate = st.number_input("Annual Appreciation Rate (%)", value=3.0, min_value=-10.0, max_value=20.0, step=0.1)
            with col3:
                market_condition = st.selectbox("Market Condition", options=list(MARKET_CONDITIONS.keys()), index=1)
            
            st.write("##### Additional Costs")
            col1, col2, col3 = st.columns(3)
            with col1:
                closing_costs = st.number_input("Closing Costs ($)", value=round(price * 0.03), min_value=0)
            with col2:
                renovation_costs = st.number_input("Renovation Costs ($)", value=0, min_value=0)
            with col3:
                tax_rate = st.number_input("Income Tax Rate (%)", value=25.0, min_value=0.0, max_value=50.0, step=0.5)
            
        # Advanced options (optional, collapses by default)
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                annual_income_growth = st.number_input("Annual Income Growth (%)", value=2.0, min_value=0.0, max_value=10.0, step=0.1)
            with col2:
                annual_expense_growth = st.number_input("Annual Expense Growth (%)", value=3.0, min_value=0.0, max_value=10.0, step=0.1)
                
        # Calculate button
        analyze_button = st.button("Analyze Investment", type="primary")
        
    # Results section
    with tabs[1]:
        if 'analyze_button' in locals() and analyze_button:
            st.header("Investment Analysis Results")
            
            # Calculate metrics
            metrics = calculate_metrics(
                price, rental_income, expenses, down_payment, loan_rate, loan_term,
                vacancy_rate, appreciation_rate, tax_rate, closing_costs, renovation_costs, 
                annual_income_growth, annual_expense_growth
            )
            
            # Display metrics dashboard
            display_metrics_dashboard(metrics)
            
            # Show detailed metrics
            with st.expander("View Detailed Metrics", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Cash Flow Metrics")
                    st.write(f"Monthly Cash Flow: ${metrics['monthly_cash_flow']:.2f}")
                    st.write(f"Annual Cash Flow: ${metrics['annual_cash_flow']:.2f}")
                    st.write(f"After-Tax Cash Flow: ${metrics['after_tax_cash_flow']:.2f}")
                    st.write(f"Monthly Mortgage Payment: ${metrics['mortgage_payment']:.2f}")
                    
                with col2:
                    st.subheader("Investment Return Metrics")
                    st.write(f"Cash-on-Cash Return: {metrics['cash_on_cash']:.2f}%")
                    st.write(f"Cap Rate: {metrics['cap_rate']:.2f}%")
                    st.write(f"ROI: {metrics['roi']:.2f}%")
                    if metrics['break_even_months'] != float('inf'):
                        st.write(f"Break-Even Point: {metrics['break_even_months']:.1f} months")
                    else:
                        st.write("Break-Even Point: N/A (negative cash flow)")
                        
                st.subheader("Future Value Projections")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("5-Year Value", f"${metrics['future_value_5yr']:,.2f}", 
                            f"{((metrics['future_value_5yr'] - price) / price) * 100:.1f}%")
                with col2:
                    st.metric("10-Year Value", f"${metrics['future_value_10yr']:,.2f}", 
                            f"{((metrics['future_value_10yr'] - price) / price) * 100:.1f}%")
                with col3:
                    st.metric("20-Year Value", f"${metrics['future_value_20yr']:,.2f}", 
                            f"{((metrics['future_value_20yr'] - price) / price) * 100:.1f}%")
                
                st.write(f"Total Equity (5 years): ${metrics['total_equity_5yr']:,.2f}")
                st.write(f"Total Equity (10 years): ${metrics['total_equity_10yr']:,.2f}")
                
        else:
            st.info("Complete the property details in the 'Property Details' tab and click 'Analyze Investment' to view results.")
    
    # Cash Flow Projections
    with tabs[2]:
        if 'analyze_button' in locals() and analyze_button:
            st.header("Cash Flow Projections")
            
            # Calculate projections
            projection_years = st.slider("Projection Period (years)", min_value=5, max_value=30, value=10)
            projections = calculate_cash_flow_projection(
                price, rental_income, expenses, down_payment, loan_rate, loan_term,
                vacancy_rate, appreciation_rate, projection_years, 
                annual_income_growth, annual_expense_growth
            )
            
            # Convert projections to DataFrame
            df_projections = pd.DataFrame(projections)
            
            # Display cash flow chart
            st.subheader("Annual Cash Flow")
            fig = px.bar(
                df_projections, 
                x="year", 
                y="annual_cash_flow",
                labels={"year": "Year", "annual_cash_flow": "Cash Flow ($)"},
                color_discrete_sequence=["#4e8df5"]
            )
            fig.update_layout(
                title="Annual Cash Flow Projection",
                xaxis_title="Year",
                yaxis_title="Cash Flow ($)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display property value chart
            st.subheader("Property Value Appreciation")
            fig = px.line(
                df_projections, 
                x="year", 
                y="property_value",
                labels={"year": "Year", "property_value": "Property Value ($)"},
                color_discrete_sequence=["#4CAF50"]
            )
            fig.update_layout(
                title="Property Value Projection",
                xaxis_title="Year",
                yaxis_title="Property Value ($)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed projection data
            with st.expander("View Detailed Projection Data"):
                # Format columns for display
                display_df = df_projections.copy()
                for col in ['property_value', 'annual_income', 'annual_expenses', 
                        'annual_mortgage', 'annual_cash_flow', 'cumulative_cash_flow']:
                    display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
                
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("Complete the property details in the 'Property Details' tab and click 'Analyze Investment' to view projections.")
    
    # Risk Assessment
    with tabs[3]:
        if 'analyze_button' in locals() and analyze_button:
            st.header("Risk Assessment")
            
            # Calculate risk metrics
            # Determine location based on property type if not explicitly provided
            location = "Urban" if property_type in ["Apartment", "Condo"] else "Suburban"
            risk_analysis = analyze_risk(price, vacancy_rate, expenses, rental_income, 
                                        market_condition, property_age, location)
            
            # Display overall risk
            st.subheader("Overall Investment Risk")
            risk_level = risk_analysis["overall_risk"]
            risk_class = risk_analysis["risk_class"]
            
            st.markdown(f"<h3 class='{risk_class}'>Risk Level: {risk_level}</h3>", unsafe_allow_html=True)
            st.write(f"Risk Score: {risk_analysis['risk_score']:.2f} / 3.00")
            
            # Display risk factors
            st.subheader("Risk Factors")
            
            # Create columns to display risk factors
            col1, col2 = st.columns(2)
            
            with col1:
                for i, (factor_name, factor_data) in enumerate(list(risk_analysis["factors"].items())[:3]):
                    risk_class = "risk-low" if factor_data["score"] == 1 else ("risk-medium" if factor_data["score"] == 2 else "risk-high")
                    st.markdown(f"<div class='metric-container'>", unsafe_allow_html=True)
                    st.markdown(f"<h4>{factor_name}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p class='{risk_class}'>Risk Level: {'Low' if factor_data['score'] == 1 else ('Medium' if factor_data['score'] == 2 else 'High')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p>{factor_data['description']}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                for i, (factor_name, factor_data) in enumerate(list(risk_analysis["factors"].items())[3:]):
                    risk_class = "risk-low" if factor_data["score"] == 1 else ("risk-medium" if factor_data["score"] == 2 else "risk-high")
                    st.markdown(f"<div class='metric-container'>", unsafe_allow_html=True)
                    st.markdown(f"<h4>{factor_name}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p class='{risk_class}'>Risk Level: {'Low' if factor_data['score'] == 1 else ('Medium' if factor_data['score'] == 2 else 'High')}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p>{factor_data['description']}</p>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            
            # Display recommendations based on risk
            st.subheader("Investment Recommendations")
            if risk_level == "Low":
                st.success("This property appears to be a low-risk investment with good potential returns. Consider proceeding with the investment after verifying all information.")
            elif risk_level == "Medium":
                st.warning("This property has moderate risk. Consider negotiating a better price or finding ways to increase income or reduce expenses before proceeding.")
            else:
                st.error("This property has high risk factors. Consider looking for alternative investments unless you have a specific strategy to mitigate these risks.")
        else:
            st.info("Complete the property details in the 'Property Details' tab and click 'Analyze Investment' to view risk assessment.")

# Execute the main function
if __name__ == "__main__":
    main()
