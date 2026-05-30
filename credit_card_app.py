# -*- coding: utf-8 -*-
"""
Created on Sun May 24 21:56:32 2026

@author: nikit
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# PAGE CONFIGURATIONS

st.set_page_config(
    page_title="GoldsberryFinance",
    layout="wide"
)

with st.sidebar:
    st.caption(
        "Educational tool only. Not financial, legal, or credit advice."
    )

# HELPER FUNCTIONS

def money(x):
    if x is None or pd.isna(x):
        return "N/A"
    return f"${x:,.2f}"


def percent(x):
    if x is None or pd.isna(x):
        return "N/A"
    return f"{x:.2f}%"


def months_text(x):
    if x is None or pd.isna(x):
        return "N/A"
    return f"{int(x)} months"


def apr_risk(apr):
    if apr < 0.10:
        return "Low"
    elif apr < 0.20:
        return "Moderate"
    elif apr < 0.30:
        return "High"
    else:
        return "Very High"


def style_risk(val):
    if val == "Low":
        return "background-color: #1f7a1f; color: white; font-weight: bold;"
    elif val == "Moderate":
        return "background-color: #b8860b; color: white; font-weight: bold;"
    elif val == "High":
        return "background-color: #b22222; color: white; font-weight: bold;"
    elif val == "Very High":
        return "background-color: #800000; color: white; font-weight: bold;"
    return ""


def format_money_df(df, cols):
    df = df.copy()
    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(money)
    return df


def create_pdf_report(results, notes, first_month, total_balance, monthly_budget):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "GoldsberryFinance Debt Payoff Report")

    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Generated: {datetime.today().strftime('%B %d, %Y')}")

    y -= 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Debt Overview")

    y -= 20
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Total Balance: {money(total_balance)}")
    y -= 16
    c.drawString(50, y, f"Monthly Payment Budget: {money(monthly_budget)}")

    y -= 30
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Strategy Comparison")

    y -= 20
    c.setFont("Helvetica", 10)

    for _, row in results.iterrows():
        line = (
            f"{row['method']}: Status={row['status']}, "
            f"Months={row['payoff_months']}, "
            f"Payoff={row['payoff_date']}, "
            f"Interest={money(row['total_interest'])}"
        )

        c.drawString(50, y, line)
        y -= 15

        if y < 70:
            c.showPage()
            y = height - 50

    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Recommended Payments This Month")

    y -= 20
    c.setFont("Helvetica", 10)

    for _, row in first_month.iterrows():
        c.drawString(50, y, f"{row['card']}: {money(row['payment'])}")
        y -= 15

        if y < 70:
            c.showPage()
            y = height - 50

    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Advisor Notes")

    y -= 20
    c.setFont("Helvetica", 10)

    for note in notes:
        if y < 70:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

        c.drawString(50, y, f"- {note[:95]}")
        y -= 15

    c.save()
    buffer.seek(0)

    return buffer



# THEME

theme = st.sidebar.radio(
    "Theme",
    ["Light", "Dark"],
    horizontal=True
)

if theme == "Dark":
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: #f5f5f5;
        }

        div[data-testid="stMetricValue"] {
            color: #f5d76e;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# HEADER

st.markdown(
    """
    <div style="
        padding:18px;
        border-radius:16px;
        background:linear-gradient(90deg,#b8860b,#f5d76e);
        margin-bottom:20px;">
        <h1 style="color:black; margin:0;">GoldsberryFinance</h1>
        <p style="color:black; margin:0; font-size:18px;">Credit Card Payoff Advisor</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write(
    "Compare avalanche, snowball, and minimum-only strategies. "
    "Get a practical payoff plan, advisor notes, graphs, and downloadable reports."
)



# SIDEBAR INPUTS

st.sidebar.header("Financial Profile")

monthly_income = st.sidebar.number_input(
    "Monthly after-tax income",
    min_value=0.0,
    value=4000.0,
    step=100.0
)

essential_expenses = st.sidebar.number_input(
    "Monthly essential expenses",
    min_value=0.0,
    value=2500.0,
    step=100.0
)

emergency_savings = st.sidebar.number_input(
    "Current emergency savings",
    min_value=0.0,
    value=1000.0,
    step=100.0
)

monthly_budget = st.sidebar.number_input(
    "Amount available for credit card payments",
    min_value=0.0,
    value=600.0,
    step=50.0
)

available_cash_flow = monthly_income - essential_expenses

st.sidebar.metric("Available Cash Flow", money(available_cash_flow))



# CARD INPUTS

num_cards = st.number_input(
    "How many credit cards?",
    min_value=1,
    max_value=15,
    value=3
)

issuer_options = [
    "American Express",
    "Chase",
    "Capital One",
    "Discover",
    "Citi",
    "Bank of America",
    "Wells Fargo",
    "Synchrony",
    "Apple Card",
    "Navy Federal",
    "Other"
]

cards_list = []

for i in range(num_cards):
    with st.expander(f"Card {i + 1} Details", expanded=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            issuer = st.selectbox(
                "Issuer",
                issuer_options,
                key=f"issuer_{i}"
            )

        with col2:
            nickname = st.text_input(
                "Card nickname",
                value=f"Card {i + 1}",
                key=f"nickname_{i}",
                help="Example: Cash card, work card, travel card"
            )

        with col3:
            if issuer == "Other":
                custom_issuer = st.text_input(
                    "Custom issuer",
                    value="",
                    key=f"custom_issuer_{i}"
                )
            else:
                custom_issuer = issuer

        if custom_issuer.strip() == "":
            custom_issuer = "Other"

        card_name = f"{custom_issuer} - {nickname}"

        col4, col5, col6, col7 = st.columns(4)

        with col4:
            balance = st.number_input(
                "Balance",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                key=f"balance_{i}"
            )

        with col5:
            apr = st.number_input(
                "APR (%)",
                min_value=0.0,
                value=24.99,
                step=0.25,
                key=f"apr_{i}"
            )

        with col6:
            minimum = st.number_input(
                "Minimum payment",
                min_value=0.0,
                value=50.0,
                step=10.0,
                key=f"minimum_{i}"
            )

        with col7:
            credit_limit = st.number_input(
                "Credit limit",
                min_value=0.0,
                value=3000.0,
                step=100.0,
                key=f"limit_{i}"
            )

        cards_list.append({
            "card": card_name,
            "issuer": custom_issuer,
            "nickname": nickname,
            "balance": balance,
            "apr": apr / 100,
            "minimum": minimum,
            "credit_limit": credit_limit
        })

selected_method = st.radio(
    "Choose method to view in detail",
    ["Avalanche", "Snowball", "Minimum Only"],
    index=0,
    horizontal=True
)


# SIMULATION FUNCTION

def simulate_payoff(cards_input, monthly_budget, method):
    cards = cards_input.copy()

    month = 0
    history = []
    balance_history = []
    payment_history = []

    previous_total_balance = cards["balance"].sum()
    stuck_counter = 0

    while cards["balance"].sum() > 0.01:
        month += 1

        cards["interest"] = cards["balance"] * (cards["apr"] / 12)
        cards["balance"] += cards["interest"]

        active = cards["balance"] > 0.01
        total_minimums = cards.loc[active, "minimum"].sum()

        if monthly_budget < total_minimums:
            return (
                pd.DataFrame(history),
                pd.DataFrame(balance_history),
                pd.DataFrame(payment_history),
                {
                    "method": method,
                    "payoff_months": None,
                    "payoff_date": "Not possible",
                    "total_interest": None,
                    "status": "Budget below minimums"
                }
            )

        cards["payment"] = 0.0
        cards.loc[active, "payment"] = cards.loc[active, "minimum"]

        if method != "Minimum Only":
            extra_payment = monthly_budget - total_minimums

            while extra_payment > 0.01 and (cards["balance"] > cards["payment"] + 0.01).any():
                active = cards["balance"] > cards["payment"] + 0.01

                if method == "Avalanche":
                    target_index = (
                        cards.loc[active]
                        .sort_values(["apr", "balance"], ascending=[False, False])
                        .index[0]
                    )
                else:
                    target_index = (
                        cards.loc[active]
                        .sort_values(["balance", "apr"], ascending=[True, False])
                        .index[0]
                    )

                remaining_balance = (
                    cards.loc[target_index, "balance"]
                    - cards.loc[target_index, "payment"]
                )

                extra_to_apply = min(extra_payment, remaining_balance)

                if extra_to_apply <= 0:
                    break

                cards.loc[target_index, "payment"] += extra_to_apply
                extra_payment -= extra_to_apply

        cards["payment"] = cards[["payment", "balance"]].min(axis=1)

        for _, row in cards.iterrows():
            payment_history.append({
                "month": month,
                "card": row["card"],
                "payment": row["payment"],
                "method": method
            })

        cards["balance"] -= cards["payment"]
        cards["balance"] = cards["balance"].clip(lower=0)

        current_total_balance = cards["balance"].sum()

        history.append({
            "month": month,
            "total_balance": current_total_balance,
            "total_interest": cards["interest"].sum(),
            "method": method
        })

        for _, row in cards.iterrows():
            balance_history.append({
                "month": month,
                "card": row["card"],
                "balance": row["balance"],
                "method": method
            })

        if current_total_balance >= previous_total_balance - 0.01:
            stuck_counter += 1
        else:
            stuck_counter = 0

        previous_total_balance = current_total_balance

        if stuck_counter >= 3:
            summary = pd.DataFrame(history)

            return (
                summary,
                pd.DataFrame(balance_history),
                pd.DataFrame(payment_history),
                {
                    "method": method,
                    "payoff_months": None,
                    "payoff_date": "Not paid off",
                    "total_interest": summary["total_interest"].sum(),
                    "status": "Debt not decreasing"
                }
            )

        if month >= 600:
            summary = pd.DataFrame(history)

            return (
                summary,
                pd.DataFrame(balance_history),
                pd.DataFrame(payment_history),
                {
                    "method": method,
                    "payoff_months": None,
                    "payoff_date": "Over 50 years",
                    "total_interest": summary["total_interest"].sum(),
                    "status": "Too long"
                }
            )

    summary = pd.DataFrame(history)

    return (
        summary,
        pd.DataFrame(balance_history),
        pd.DataFrame(payment_history),
        {
            "method": method,
            "payoff_months": month,
            "payoff_date": (datetime.today() + relativedelta(months=month)).strftime("%B %Y"),
            "total_interest": summary["total_interest"].sum(),
            "status": "Paid off"
        }
    )



# MAIN APP LOGIC

if st.button("Analyze Debt Plan", use_container_width=True):

    cards = pd.DataFrame(cards_list)

    total_balance = cards["balance"].sum()
    total_minimums = cards["minimum"].sum()

    cards["utilization"] = cards.apply(
        lambda row: row["balance"] / row["credit_limit"] if row["credit_limit"] > 0 else 0,
        axis=1
    )

    cards["apr_risk"] = cards["apr"].apply(apr_risk)

    if total_balance <= 0:
        st.error("Enter at least one credit card balance.")

    elif monthly_budget < total_minimums:
        st.error("Your monthly budget is below your required minimum payments.")

    else:
        avalanche_summary, avalanche_balances, avalanche_payments, avalanche_result = simulate_payoff(
            cards,
            monthly_budget,
            "Avalanche"
        )

        snowball_summary, snowball_balances, snowball_payments, snowball_result = simulate_payoff(
            cards,
            monthly_budget,
            "Snowball"
        )

        minimum_summary, minimum_balances, minimum_payments, minimum_result = simulate_payoff(
            cards,
            total_minimums,
            "Minimum Only"
        )

        results = pd.DataFrame([
            avalanche_result,
            snowball_result,
            minimum_result
        ])

        results["total_interest"] = pd.to_numeric(
            results["total_interest"],
            errors="coerce"
        ).round(2)

        
        # DEBT OVERVIEW

        st.subheader("Debt Overview")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Balance", money(total_balance))
        c2.metric("Total Minimums", money(total_minimums))
        c3.metric("Monthly Budget", money(monthly_budget))

        if monthly_income > 0:
            c4.metric("Debt / Monthly Income", f"{total_balance / monthly_income:.1%}")
        else:
            c4.metric("Debt / Monthly Income", "N/A")

       
        # CARD RISK TABLE

        st.subheader("Card Risk Table")

        risk_display = cards[[
            "card",
            "issuer",
            "balance",
            "apr",
            "minimum",
            "credit_limit",
            "utilization",
            "apr_risk"
        ]].copy()

        for col in ["balance", "minimum", "credit_limit"]:
            risk_display[col] = risk_display[col].apply(money)

        risk_display["apr"] = (risk_display["apr"] * 100).apply(percent)
        risk_display["utilization"] = (risk_display["utilization"] * 100).apply(percent)

        styled_risk = risk_display.style.map(
            style_risk,
            subset=["apr_risk"]
        )

        st.dataframe(
            styled_risk,
            use_container_width=True
        )


        # STRATEGY COMPARISON

        st.subheader("Strategy Comparison")

        comparison_display = results.copy()
        comparison_display["total_interest"] = comparison_display["total_interest"].apply(money)

        st.dataframe(
            comparison_display,
            use_container_width=True
        )

        paid_off_results = results[results["status"] == "Paid off"]

        advisor_notes = []

        if len(paid_off_results) > 0:
            best_method = paid_off_results.sort_values(
                ["total_interest", "payoff_months"]
            ).iloc[0]

            st.success(
                f"Recommended strategy: **{best_method['method']}**. "
                f"Estimated payoff: **{int(best_method['payoff_months'])} months**, "
                f"around **{best_method['payoff_date']}**, with about "
                f"**{money(best_method['total_interest'])}** in total interest."
            )
        else:
            st.error("None of the strategies fully pay off the debt. Increase your monthly payment budget.")

       
        # SAVINGS VS MINIMUM

        if avalanche_result["status"] == "Paid off" and minimum_result["status"] == "Paid off":
            time_saved = minimum_result["payoff_months"] - avalanche_result["payoff_months"]
            interest_saved = minimum_result["total_interest"] - avalanche_result["total_interest"]

            st.subheader("Savings vs Minimum Payments")

            s1, s2 = st.columns(2)
            s1.metric("Time Saved", months_text(time_saved))
            s2.metric("Interest Saved", money(interest_saved))

            advisor_notes.append(
                f"Compared with only paying minimums, avalanche saves about {months_text(time_saved)} and {money(interest_saved)} in interest."
            )

        elif minimum_result["status"] != "Paid off":
            st.warning("Minimum-only payments do not reliably pay off the debt in this scenario.")

            advisor_notes.append(
                "Minimum-only payments do not reliably pay off the debt in this scenario."
            )

        
        # ADVISOR NOTES

        st.subheader("Financial Advisor Notes")

        if monthly_budget > available_cash_flow:
            advisor_notes.append(
                "Your planned credit card payment is higher than your estimated available cash flow. This may not be sustainable."
            )

        elif monthly_budget > available_cash_flow * 0.85:
            advisor_notes.append(
                "Your payment plan is aggressive. Keep an emergency buffer so you do not need to reuse credit cards."
            )

        emergency_target_low = essential_expenses * 1
        emergency_target_high = essential_expenses * 3

        if emergency_savings < emergency_target_low:
            advisor_notes.append(
                f"Emergency fund recommendation: build at least 1 month of essential expenses first, about {money(emergency_target_low)}."
            )

        elif emergency_savings < emergency_target_high:
            advisor_notes.append(
                f"Emergency fund recommendation: you have some cushion, but a stronger target is 3 months of expenses, about {money(emergency_target_high)}."
            )

        else:
            advisor_notes.append(
                "Emergency fund looks solid relative to essential monthly expenses."
            )

        recommended_low = max(total_minimums, available_cash_flow * 0.50)
        recommended_high = max(total_minimums, available_cash_flow * 0.85)

        advisor_notes.append(
            f"Recommended payment range based on your cash flow: {money(recommended_low)} to {money(recommended_high)} per month."
        )

        high_apr_cards = cards[cards["apr"] >= 0.25]

        if len(high_apr_cards) > 0:
            names = ", ".join(high_apr_cards["card"].tolist())

            advisor_notes.append(
                f"High APR warning: {names}. These cards should be prioritized early."
            )

        high_util_cards = cards[cards["utilization"] >= 0.70]

        if len(high_util_cards) > 0:
            names = ", ".join(high_util_cards["card"].tolist())

            advisor_notes.append(
                f"High utilization warning: {names}. These cards may be hurting your credit profile."
            )

        if avalanche_result["status"] == "Paid off" and snowball_result["status"] == "Paid off":
            if avalanche_result["total_interest"] < snowball_result["total_interest"]:
                advisor_notes.append(
                    "Avalanche is mathematically better here because it targets the highest APR debt first."
                )

            if snowball_result["payoff_months"] <= avalanche_result["payoff_months"]:
                advisor_notes.append(
                    "Snowball may feel more motivating because it eliminates smaller balances faster."
                )

        for note in advisor_notes:
            st.info(note)

        
        # SELECT METHOD DETAILS

        if selected_method == "Avalanche":
            summary = avalanche_summary
            balances = avalanche_balances
            payments = avalanche_payments
            result = avalanche_result

        elif selected_method == "Snowball":
            summary = snowball_summary
            balances = snowball_balances
            payments = snowball_payments
            result = snowball_result

        else:
            summary = minimum_summary
            balances = minimum_balances
            payments = minimum_payments
            result = minimum_result

        st.divider()

        st.subheader(f"{selected_method} Payment Plan")

        if result["status"] != "Paid off":
            st.warning(f"This strategy status: **{result['status']}**.")

        else:
            st.write(
                f"Debt paid off in **{result['payoff_months']} months**. "
                f"Estimated payoff date: **{result['payoff_date']}**."
            )

            st.write(f"Total interest paid: **{money(result['total_interest'])}**")

        
        # PAYMENT TABLES

        if len(payments) > 0:
            first_month = payments[
                payments["month"] == 1
            ][["card", "payment"]].copy()

            st.subheader("Recommended Payments This Month")

            st.dataframe(
                format_money_df(first_month, ["payment"]),
                use_container_width=True
            )

            payment_table = payments.pivot(
                index="month",
                columns="card",
                values="payment"
            ).round(2)

            st.subheader("Full Monthly Payment Schedule")

            st.dataframe(
                payment_table,
                use_container_width=True
            )

            st.download_button(
                "Download Payment Schedule CSV",
                data=payment_table.to_csv(),
                file_name=f"{selected_method.lower().replace(' ', '_')}_payment_schedule.csv",
                mime="text/csv",
                use_container_width=True
            )

        
        # BALANCE CHARTS

        if len(balances) > 0:
            st.subheader("Balance Over Time")

            fig, ax = plt.subplots(figsize=(10, 6))

            for card in balances["card"].unique():
                card_data = balances[balances["card"] == card]

                ax.plot(
                    card_data["month"],
                    card_data["balance"],
                    label=card
                )

            ax.set_xlabel("Month")
            ax.set_ylabel("Balance ($)")
            ax.set_title(f"Credit Card Balances Over Time - {selected_method}")
            ax.legend()
            ax.grid(True)

            st.pyplot(fig)

            st.subheader("Stacked Balance Area Chart")

            stacked = balances.pivot(
                index="month",
                columns="card",
                values="balance"
            ).fillna(0)

            fig_stack, ax_stack = plt.subplots(figsize=(10, 6))

            ax_stack.stackplot(
                stacked.index,
                stacked.T
            )

            ax_stack.set_xlabel("Month")
            ax_stack.set_ylabel("Balance ($)")
            ax_stack.set_title(f"Stacked Debt Balance Over Time - {selected_method}")
            ax_stack.legend(stacked.columns, loc="upper right")
            ax_stack.grid(True)

            st.pyplot(fig_stack)

        if len(summary) > 0:
            st.subheader("Total Debt Over Time")

            fig2, ax2 = plt.subplots(figsize=(10, 6))

            ax2.plot(
                summary["month"],
                summary["total_balance"]
            )

            ax2.set_xlabel("Month")
            ax2.set_ylabel("Total Balance ($)")
            ax2.set_title(f"Total Debt Over Time - {selected_method}")
            ax2.grid(True)

            st.pyplot(fig2)

        
        # WHAT IF SCENARIOS

        st.subheader("What If I Pay More Each Month?")

        scenarios = []

        for extra in [0, 100, 200, 300, 500]:
            scenario_budget = monthly_budget + extra

            _, _, _, sim_result = simulate_payoff(
                cards,
                scenario_budget,
                "Avalanche"
            )

            scenarios.append({
                "Monthly Payment": scenario_budget,
                "Status": sim_result["status"],
                "Payoff Months": sim_result["payoff_months"],
                "Payoff Date": sim_result["payoff_date"],
                "Total Interest": sim_result["total_interest"]
            })

        scenario_df = pd.DataFrame(scenarios)

        scenario_display = scenario_df.copy()
        scenario_display["Monthly Payment"] = scenario_display["Monthly Payment"].apply(money)
        scenario_display["Total Interest"] = scenario_display["Total Interest"].apply(money)

        st.dataframe(
            scenario_display,
            use_container_width=True
        )

        
        # PDF REPORT

        if len(payments) > 0:
            first_month_pdf = payments[
                payments["month"] == 1
            ][["card", "payment"]].copy()

            pdf_buffer = create_pdf_report(
                results,
                advisor_notes,
                first_month_pdf,
                total_balance,
                monthly_budget
            )

            st.download_button(
                "Export PDF Report",
                data=pdf_buffer,
                file_name="goldsberryfinance_debt_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        
        # MONTHLY SUMMARY

        if len(summary) > 0:
            st.subheader("Monthly Summary")

            display_summary = summary.copy()
            display_summary["total_balance"] = display_summary["total_balance"].apply(money)
            display_summary["total_interest"] = display_summary["total_interest"].apply(money)

            st.dataframe(
                display_summary,
                use_container_width=True
            )

            st.download_button(
                "Download Monthly Summary CSV",
                data=summary.to_csv(index=False),
                file_name=f"{selected_method.lower().replace(' ', '_')}_monthly_summary.csv",
                mime="text/csv",
                use_container_width=True
            )
