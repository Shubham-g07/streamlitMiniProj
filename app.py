"""PeoplePulse — a small Streamlit employee dashboard backed by SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


DATABASE_PATH = Path(__file__).with_name("peoplepulse.db")
DOMAINS = ["Engineering", "Design", "Marketing", "Sales", "People Ops"]
SEED_EMPLOYEES = [
    ("Aarav Mehta", 28, 84000, "Engineering"),
    ("Ananya Iyer", 31, 91000, "Engineering"),
    ("Rohan Kapoor", 26, 68000, "Design"),
    ("Maya Nair", 29, 76000, "Marketing"),
    ("Vivaan Shah", 34, 105000, "Sales"),
    ("Isha Verma", 27, 72000, "People Ops"),
    ("Kabir Singh", 32, 97000, "Engineering"),
    ("Diya Patel", 25, 64000, "Design"),
    ("Arjun Rao", 30, 86000, "Marketing"),
    ("Kiara Gupta", 35, 112000, "Sales"),
    ("Neil Joshi", 24, 59000, "People Ops"),
    ("Sana Khan", 33, 99000, "Engineering"),
    ("Reyansh Das", 29, 79000, "Design"),
    ("Tara Menon", 28, 74000, "Marketing"),
    ("Aditya Bose", 36, 118000, "Sales"),
    ("Meera Reddy", 31, 81000, "People Ops"),
    ("Ira Chawla", 27, 88000, "Engineering"),
    ("Dev Malhotra", 30, 71000, "Design"),
    ("Nisha Kulkarni", 26, 69000, "Marketing"),
    ("Yash Sethi", 38, 124000, "Sales"),
]
PALETTE = ["#8b5cf6", "#22c55e", "#06b6d4", "#f59e0b", "#ec4899"]


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection with rows accessible by column name."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialise_database() -> None:
    """Create and seed the employee table once."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age BETWEEN 18 AND 70),
                salary REAL NOT NULL CHECK(salary >= 0),
                domain TEXT NOT NULL
            )
            """
        )
        current_count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
        if current_count == 0:
            connection.executemany(
                "INSERT INTO employees (name, age, salary, domain) VALUES (?, ?, ?, ?)",
                SEED_EMPLOYEES,
            )


def load_employees() -> pd.DataFrame:
    with get_connection() as connection:
        return pd.read_sql_query(
            "SELECT id, name, age, salary, domain FROM employees ORDER BY name", connection
        )


def add_employee(name: str, age: int, salary: float, domain: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO employees (name, age, salary, domain) VALUES (?, ?, ?, ?)",
            (name.strip(), age, salary, domain),
        )


def update_employee(employee_id: int, name: str, age: int, salary: float, domain: str) -> None:
    with get_connection() as connection:
        connection.execute(
            "UPDATE employees SET name = ?, age = ?, salary = ?, domain = ? WHERE id = ?",
            (name.strip(), age, salary, domain, employee_id),
        )


def delete_employee(employee_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM employees WHERE id = ?", (employee_id,))


def inject_css() -> None:
    st.markdown(
        """
        <style>
            .stApp { background: #f7f8fc; color: #1e1b4b; }
            [data-testid="stSidebar"] { background: linear-gradient(180deg, #21154f 0%, #43227d 100%); }
            [data-testid="stSidebar"] * { color: #f8f7ff !important; }
            [data-testid="stSidebar"] .stRadio label { padding: .35rem 0; }
            .hero { background: linear-gradient(115deg, #321a6f 0%, #6d35ba 54%, #14b8a6 150%); border-radius: 22px; padding: 2rem 2.2rem; color: white; margin-bottom: 1.4rem; box-shadow: 0 14px 30px rgba(67, 34, 125, .2); }
            .hero h1 { color: white; margin: 0; font-size: 2.2rem; }
            .hero p { margin: .5rem 0 0; opacity: .9; font-size: 1rem; }
            .metric-card { background: white; border: 1px solid #eceaf5; padding: 1rem 1.1rem; border-radius: 16px; box-shadow: 0 8px 18px rgba(41, 26, 91, .06); }
            .eyebrow { font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: #786f98; font-weight: 700; }
            .metric-number { font-size: 1.55rem; font-weight: 750; color: #2b185f; margin-top: .15rem; }
            div[data-testid="stForm"] { background: white; border: 1px solid #e8e5f2; border-radius: 18px; padding: 1rem 1.15rem .4rem; }
            .stButton > button { border-radius: 10px; border: 0; font-weight: 650; }
            .stDownloadButton > button { border-radius: 10px; }
            .company-card { background: white; border-radius: 18px; padding: 1.3rem; border-left: 5px solid #8b5cf6; box-shadow: 0 7px 20px rgba(41, 26, 91, .06); height: 100%; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str, icon: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{icon} {title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def metric_card(column, label: str, value: str) -> None:
    column.markdown(
        f'<div class="metric-card"><div class="eyebrow">{label}</div><div class="metric-number">{value}</div></div>',
        unsafe_allow_html=True,
    )


def display_page(employees: pd.DataFrame) -> None:
    page_header("Team constellation", "A live view of the people shaping PeoplePulse.", "✦")
    total_payroll = employees["salary"].sum()
    avg_salary = employees["salary"].mean()
    metric_columns = st.columns(4)
    metric_card(metric_columns[0], "Team members", f"{len(employees):02d}")
    metric_card(metric_columns[1], "Domains", str(employees["domain"].nunique()))
    metric_card(metric_columns[2], "Average salary", f"₹{avg_salary / 1000:.1f}K")
    metric_card(metric_columns[3], "Annual payroll", f"₹{total_payroll / 1_000_000:.2f}M")
    st.markdown("<br>", unsafe_allow_html=True)

    search_column, domain_column = st.columns([2, 1])
    search = search_column.text_input("Search the team", placeholder="Find a name...")
    selected_domains = domain_column.multiselect("Filter by domain", DOMAINS, placeholder="All domains")
    filtered = employees.copy()
    if search:
        filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
    if selected_domains:
        filtered = filtered[filtered["domain"].isin(selected_domains)]

    st.subheader("Employee directory")
    table = filtered.rename(
        columns={"id": "ID", "name": "Name", "age": "Age", "salary": "Salary (₹)", "domain": "Domain"}
    )
    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config={"Salary (₹)": st.column_config.NumberColumn(format="₹%d")},
    )
    st.download_button(
        "Download filtered directory",
        table.to_csv(index=False).encode("utf-8"),
        "peoplepulse_directory.csv",
        "text/csv",
    )


def employee_page(employees: pd.DataFrame) -> None:
    page_header("Employee studio", "Add, edit, and curate your team from one focused workspace.", "✎")
    action = st.selectbox("Choose an action", ["Add employee", "Edit employee", "Remove employee"])

    if action == "Add employee":
        with st.form("add_employee_form", clear_on_submit=True):
            name = st.text_input("Full name", placeholder="e.g. Aanya Sharma")
            age_column, salary_column = st.columns(2)
            age = age_column.number_input("Age", min_value=18, max_value=70, value=25, step=1)
            salary = salary_column.number_input("Annual salary (₹)", min_value=0, value=65000, step=1000)
            domain = st.selectbox("Domain", DOMAINS)
            submitted = st.form_submit_button("Add to team", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Please enter the employee's name.")
            else:
                add_employee(name, int(age), float(salary), domain)
                st.success(f"{name.strip()} was added to the team.")
                st.rerun()

    elif action == "Edit employee":
        employee_options = {f"{row.name} · #{row.id}": row for row in employees.itertuples()}
        choice = st.selectbox("Select employee", employee_options.keys())
        selected = employee_options[choice]
        with st.form("edit_employee_form"):
            name = st.text_input("Full name", value=selected.name)
            age_column, salary_column = st.columns(2)
            age = age_column.number_input("Age", 18, 70, int(selected.age), step=1)
            salary = salary_column.number_input("Annual salary (₹)", 0, value=int(selected.salary), step=1000)
            domain = st.selectbox("Domain", DOMAINS, index=DOMAINS.index(selected.domain))
            submitted = st.form_submit_button("Save changes", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Please enter the employee's name.")
            else:
                update_employee(selected.id, name, int(age), float(salary), domain)
                st.success(f"Updated {name.strip()}.")
                st.rerun()

    else:
        employee_options = {f"{row.name} · #{row.id}": row for row in employees.itertuples()}
        choice = st.selectbox("Select employee", employee_options.keys())
        selected = employee_options[choice]
        st.warning(f"You are about to remove **{selected.name}** from the directory.")
        confirm = st.checkbox("I understand this cannot be undone")
        if st.button("Remove employee", disabled=not confirm, type="primary"):
            delete_employee(selected.id)
            st.success(f"Removed {selected.name}.")
            st.rerun()


def salary_graph_page(employees: pd.DataFrame) -> None:
    page_header("Salary signals", "Explore compensation patterns across the PeoplePulse universe.", "◌")
    domain_summary = employees.groupby("domain", as_index=False).agg(
        average_salary=("salary", "mean"), total_salary=("salary", "sum"), headcount=("id", "count")
    )
    domain_order = domain_summary.sort_values("average_salary", ascending=False)["domain"].tolist()
    base_color = alt.Color("domain:N", scale=alt.Scale(domain=DOMAINS, range=PALETTE), legend=None)

    left, right = st.columns(2)
    with left:
        st.subheader("Average salary by domain")
        salary_bars = (
            alt.Chart(domain_summary)
            .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8)
            .encode(
                x=alt.X("average_salary:Q", title="Average annual salary (₹)", axis=alt.Axis(format="~s")),
                y=alt.Y("domain:N", sort=domain_order, title=None),
                color=base_color,
                tooltip=["domain:N", alt.Tooltip("average_salary:Q", format=",.0f")],
            )
            .properties(height=300)
        )
        st.altair_chart(salary_bars, use_container_width=True)
    with right:
        st.subheader("Payroll share")
        payroll_donut = (
            alt.Chart(domain_summary)
            .mark_arc(innerRadius=65, outerRadius=120)
            .encode(
                theta=alt.Theta("total_salary:Q"),
                color=base_color,
                tooltip=["domain:N", alt.Tooltip("total_salary:Q", format=",.0f")],
            )
            .properties(height=300)
        )
        st.altair_chart(payroll_donut, use_container_width=True)

    st.subheader("Experience & compensation map")
    scatter = (
        alt.Chart(employees)
        .mark_circle(size=170, opacity=0.84)
        .encode(
            x=alt.X("age:Q", title="Age"),
            y=alt.Y("salary:Q", title="Annual salary (₹)", axis=alt.Axis(format="~s")),
            color=base_color,
            size=alt.Size("salary:Q", legend=None),
            tooltip=["name:N", "domain:N", "age:Q", alt.Tooltip("salary:Q", format=",.0f")],
        )
        .interactive()
        .properties(height=360)
    )
    st.altair_chart(scatter, use_container_width=True)


def about_page() -> None:
    page_header("About PeoplePulse", "A creative employee-management mini project built with Streamlit.", "☼")
    first, second, third = st.columns(3)
    first.markdown('<div class="company-card"><h3>Our idea</h3><p>Make people data feel clear, friendly, and useful—not like a spreadsheet.</p></div>', unsafe_allow_html=True)
    second.markdown('<div class="company-card"><h3>Our values</h3><p>Curiosity, thoughtful growth, and a workplace where each voice counts.</p></div>', unsafe_allow_html=True)
    third.markdown('<div class="company-card"><h3>Our stack</h3><p>Streamlit for the experience, SQLite for persistence, and Altair for visual storytelling.</p></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("What this project demonstrates")
    st.info("✓ SQLite database integration  •  ✓ Full employee CRUD  •  ✓ Search and filtering  •  ✓ Three interactive salary charts")
    st.caption("The database is automatically populated with 20 sample employees the first time the app runs.")


def main() -> None:
    st.set_page_config(page_title="PeoplePulse", page_icon="✦", layout="wide")
    initialise_database()
    inject_css()
    st.sidebar.markdown("# ✦ PeoplePulse")
    st.sidebar.caption("PEOPLE, WITH PULSE")
    page = st.sidebar.radio(
        "Navigate",
        ["Display page", "Employee section", "Salary graph page", "About company page"],
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Database:** SQLite connected")
    st.sidebar.caption("Built as a Streamlit mini project")

    employees = load_employees()
    if page == "Display page":
        display_page(employees)
    elif page == "Employee section":
        employee_page(employees)
    elif page == "Salary graph page":
        salary_graph_page(employees)
    else:
        about_page()


if __name__ == "__main__":
    main()
