import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(
    page_title="Apex PMS Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏆 Apex Portfolio Management System")
st.markdown("### Advanced Analytics Dashboard")

with st.sidebar:
    st.header("Portfolio Selection")
    portfolio_id = st.number_input("Portfolio ID", min_value=1, value=1)
    
    st.header("Date Range")
    end_date = st.date_input("End Date", value=date.today())
    start_date = st.date_input("Start Date", value=end_date - timedelta(days=365))
    
    st.header("Analysis Options")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Performance", "Risk", "Attribution", "Optimization"]
    )

tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "⚠️ Risk", "🎯 Attribution", "🔧 Optimization"])

with tab1:
    st.header("Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Return", "12.5%", "+2.3%")
    with col2:
        st.metric("Sharpe Ratio", "1.45", "+0.15")
    with col3:
        st.metric("Max Drawdown", "-8.2%", "+1.1%")
    with col4:
        st.metric("Alpha", "3.2%", "+0.5%")
    
    st.subheader("Cumulative Returns")
    
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    returns = np.random.randn(len(dates)).cumsum() * 0.01
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=returns,
        mode='lines',
        name='Portfolio',
        line=dict(color='#00ff88', width=2)
    ))
    
    benchmark_returns = np.random.randn(len(dates)).cumsum() * 0.008
    fig.add_trace(go.Scatter(
        x=dates,
        y=benchmark_returns,
        mode='lines',
        name='Benchmark',
        line=dict(color='#ff6b6b', width=2, dash='dash')
    ))
    
    fig.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Returns")
        monthly_data = pd.DataFrame({
            'Month': pd.date_range(start=start_date, periods=12, freq='M'),
            'Return': np.random.randn(12) * 0.05
        })
        fig_monthly = px.bar(monthly_data, x='Month', y='Return', template="plotly_dark")
        st.plotly_chart(fig_monthly, use_container_width=True)
    
    with col2:
        st.subheader("Rolling Sharpe Ratio")
        rolling_data = pd.DataFrame({
            'Date': dates,
            'Sharpe': np.random.randn(len(dates)).cumsum() * 0.05 + 1.5
        })
        fig_sharpe = px.line(rolling_data, x='Date', y='Sharpe', template="plotly_dark")
        st.plotly_chart(fig_sharpe, use_container_width=True)

with tab2:
    st.header("Risk Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Volatility", "15.2%", "-1.2%")
    with col2:
        st.metric("95% VaR (1D)", "$45,230", "+$1,200")
    with col3:
        st.metric("Beta", "0.92", "-0.03")
    
    st.subheader("Value at Risk Distribution")
    
    var_data = np.random.normal(0, 1, 10000) * 50000
    fig_var = go.Figure()
    fig_var.add_trace(go.Histogram(x=var_data, nbinsx=50, name='VaR Distribution'))
    fig_var.add_vline(x=np.percentile(var_data, 5), line_dash="dash", line_color="red")
    fig_var.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_var, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Correlation Matrix")
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA']
        corr_matrix = np.random.rand(5, 5)
        corr_matrix = (corr_matrix + corr_matrix.T) / 2
        np.fill_diagonal(corr_matrix, 1)
        
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=tickers,
            y=tickers,
            colorscale='RdBu',
            zmid=0
        ))
        fig_corr.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with col2:
        st.subheader("Stress Test Results")
        stress_scenarios = pd.DataFrame({
            'Scenario': ['2008 Crisis', 'COVID Crash', 'Black Monday', 'Dotcom Bubble'],
            'Impact': [-35, -28, -18, -42]
        })
        fig_stress = px.bar(stress_scenarios, x='Scenario', y='Impact', template="plotly_dark")
        st.plotly_chart(fig_stress, use_container_width=True)

with tab3:
    st.header("Performance Attribution")
    
    st.subheader("Brinson-Fachler Attribution")
    
    attribution_data = pd.DataFrame({
        'Sector': ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy'],
        'Allocation': [0.8, -0.3, 0.5, 0.2, -0.1],
        'Selection': [1.2, 0.5, -0.2, 0.8, 0.3],
        'Interaction': [0.1, -0.1, 0.05, 0.15, -0.05]
    })
    
    fig_attr = go.Figure()
    
    for col in ['Allocation', 'Selection', 'Interaction']:
        fig_attr.add_trace(go.Bar(
            name=col,
            x=attribution_data['Sector'],
            y=attribution_data[col]
        ))
    
    fig_attr.update_layout(
        barmode='group',
        template="plotly_dark",
        height=400,
        yaxis_title="Effect (%)"
    )
    
    st.plotly_chart(fig_attr, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Attribution")
        total_attr = pd.DataFrame({
            'Component': ['Allocation', 'Selection', 'Interaction'],
            'Value': [1.2, 2.3, 0.1]
        })
        fig_total = px.pie(total_attr, values='Value', names='Component', template="plotly_dark")
        st.plotly_chart(fig_total, use_container_width=True)
    
    with col2:
        st.subheader("Security Contribution")
        security_data = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
            'Contribution': [2.1, 1.8, 1.2, 0.9, 3.5]
        })
        fig_contrib = px.bar(security_data, x='Ticker', y='Contribution', template="plotly_dark")
        st.plotly_chart(fig_contrib, use_container_width=True)

with tab4:
    st.header("Portfolio Optimization")
    
    optimization_method = st.selectbox(
        "Optimization Method",
        ["Mean-Variance", "Black-Litterman", "Risk Parity", "HRP"]
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Weights")
        current_weights = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
            'Weight': [0.25, 0.20, 0.18, 0.22, 0.15]
        })
        fig_current = px.pie(current_weights, values='Weight', names='Ticker', template="plotly_dark")
        st.plotly_chart(fig_current, use_container_width=True)
    
    with col2:
        st.subheader("Optimal Weights")
        optimal_weights = pd.DataFrame({
            'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
            'Weight': [0.22, 0.24, 0.19, 0.20, 0.15]
        })
        fig_optimal = px.pie(optimal_weights, values='Weight', names='Ticker', template="plotly_dark")
        st.plotly_chart(fig_optimal, use_container_width=True)
    
    st.subheader("Efficient Frontier")
    
    n_portfolios = 1000
    returns_frontier = np.random.uniform(0.05, 0.20, n_portfolios)
    volatility_frontier = np.random.uniform(0.10, 0.25, n_portfolios)
    sharpe_frontier = returns_frontier / volatility_frontier
    
    fig_frontier = go.Figure()
    fig_frontier.add_trace(go.Scatter(
        x=volatility_frontier,
        y=returns_frontier,
        mode='markers',
        marker=dict(
            size=5,
            color=sharpe_frontier,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sharpe Ratio")
        ),
        name='Efficient Frontier'
    ))
    
    fig_frontier.add_trace(go.Scatter(
        x=[0.15],
        y=[0.12],
        mode='markers',
        marker=dict(size=15, color='red', symbol='star'),
        name='Current Portfolio'
    ))
    
    fig_frontier.update_layout(
        template="plotly_dark",
        height=400,
        xaxis_title="Volatility",
        yaxis_title="Expected Return"
    )
    
    st.plotly_chart(fig_frontier, use_container_width=True)
    
    st.subheader("Rebalancing Trades")
    
    trades_data = pd.DataFrame({
        'Ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'],
        'Action': ['SELL', 'BUY', 'BUY', 'SELL', 'HOLD'],
        'Shares': [150, 200, 75, 100, 0],
        'Value': ['$25,500', '$82,000', '$27,000', '$18,500', '$0']
    })
    
    st.dataframe(trades_data, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Apex PMS v1.0.0 - Institutional Grade Portfolio Management")
