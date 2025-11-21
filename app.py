import streamlit as st
import pandas as pd

# ===========================
# 隐藏右上角 GitHub / 菜单
# ===========================
hide_elements = """
<style>
[data-testid="stToolbar"] {visibility: hidden !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
</style>
"""
st.markdown(hide_elements, unsafe_allow_html=True)

# ===========================
# 密码保护
# ===========================
PASSWORD = "mfe2027"

def check_password():
    def password_entered():
        if st.session_state["password"] == PASSWORD:
            st.session_state["authenticated"] = True

    if "authenticated" not in st.session_state:
        st.text_input(
            "请输入访问密码：",
            type="password",
            on_change=password_entered,
            key="password"
        )
        return False

    return st.session_state["authenticated"]

if not check_password():
    st.stop()

# ===========================
# 1. Load Data
# ===========================
df = pd.read_csv("MFE_database.csv")

# ===========================
# emoji → Chinese nationality
# ===========================
major_countries = {
    "🇨🇳": "中国",
    "🇺🇸": "美国",
    "🇯🇵": "日本",
    "🇰🇷": "韩国",
    "🇫🇷": "法国",
    "🇷🇺": "俄罗斯",
    "🇮🇳": "印度",
    "🇮🇹": "意大利",
    "🇨🇦": "加拿大"
}

def map_country(x):
    if x in major_countries:
        return major_countries[x]
    return "其他"

df["nationality_cn"] = df["nationality"].apply(map_country)

# ===========================
# 2. Summarize Function
# ===========================

def summarize(df, row_filter=None, cols=None, stats="mean"):
    
    # --- row filter ---
    if row_filter:
        for k, v in row_filter.items():
            if isinstance(v, list):
                df = df[df[k].isin(v)]
            else:
                df = df[df[k] == v]

    exclude_cols = ["submitted", "days_to_result", "updated"]

    # --- select columns ---
    if cols is None:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in exclude_cols]
        cols = numeric_cols
    else:
        cols = [c for c in cols if c not in exclude_cols]

    # --- aggregation ---
    agg_dict = {}
    for c in cols:
        agg_dict[c] = stats

    # ★ group by school (固定) — program 是加入的字段，不用于 groupby
    grouped = df.groupby("school").agg(agg_dict)

    # ★ 新增：把 program 作为 reference 列
    program_series = df.groupby("school")["program"].agg(lambda x: x.mode()[0] if len(x.mode()) else None)

    # 合并
    grouped.insert(1, "program", program_series)  # 放在第二列（紧挨 school）

    # count
    grouped["count"] = df.groupby("school").size()

    return grouped.reset_index()

# ===========================
# 3. Streamlit UI
# ===========================

st.title("🎓 Unipath Dashboard")

st.sidebar.header("Filters")

# 筛选：nationality
nat_choices = sorted(df["nationality_cn"].unique())
nat_list = st.sidebar.multiselect("Nationality 🌍", nat_choices)

# year
year_list = st.sidebar.multiselect("Year 📅", sorted(df["year"].dropna().unique()))

# result
result_list = st.sidebar.multiselect("Result 🎯", sorted(df["result"].dropna().unique()))

# school
school_list = st.sidebar.multiselect("School 🎓", sorted(df["school"].dropna().unique()))

# program
program_list = st.sidebar.multiselect("Program 📘", sorted(df["program"].dropna().unique()))

# 数字列 + 国籍
cols_list = st.sidebar.multiselect(
    "Columns 📊",
    df.select_dtypes(include="number").columns.tolist() + ["nationality_cn"]
)

# 统计方法
stats = st.sidebar.radio("Statistics Method", ["mean", "median", "max", "min"])

# ===========================
# Run Button
# ===========================

if st.sidebar.button("Run"):
    row_filter = {}

    if nat_list:
        row_filter["nationality_cn"] = nat_list
    if year_list:
        row_filter["year"] = year_list
    if result_list:
        row_filter["result"] = result_list
    if school_list:
        row_filter["school"] = school_list
    if program_list:
        row_filter["program"] = program_list

    out = summarize(df, row_filter=row_filter, cols=cols_list, stats=stats)

    st.subheader("📄 Summary Table")
    st.dataframe(out, use_container_width=True)
