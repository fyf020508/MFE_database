import streamlit as st
import pandas as pd

# 简单密码保护
PASSWORD = "mfe2027"
hide_elements = """

st.markdown(hide_elements, unsafe_allow_html=True)

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


# ============================================
# 1. Load Data
# ============================================
df = pd.read_csv("MFE_database.csv")

# ============================================
# 2. Emoji → 中文（只保留主要国家）
# ============================================

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
    else:
        return "其他"

df["nationality_cn"] = df["nationality"].apply(map_country)


# ============================================
# 3. Summarize Function
# ============================================

def summarize_by_school(df, group_col="school", row_filter=None, cols=None, stats="mean"):

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
        text_cols = ["nationality_cn"]
        cols = numeric_cols + text_cols
    else:
        cols = [c for c in cols if c not in exclude_cols]

    # --- aggregation ---
    agg_dict = {}
    for c in cols:
        if df[c].dtype != "object":
            agg_dict[c] = stats
        else:
            agg_dict[c] = lambda x: x.mode()[0] if len(x.mode()) else None

    out = df.groupby(group_col).agg(agg_dict)
    out["count"] = df.groupby(group_col).size()

    return out.reset_index()


# ============================================
# 4. Streamlit UI
# ============================================

st.title("🎓 Unipath Dashboard")

st.sidebar.header("Filters")

# 国籍过滤（归类后）
nat_choices = sorted(df["nationality_cn"].unique())
nat_list = st.sidebar.multiselect("Nationality 🌍", nat_choices)

# 年份过滤
year_list = st.sidebar.multiselect("Year 📅", sorted(df["year"].dropna().unique()))

# Result 过滤
result_list = st.sidebar.multiselect("Result 🎯", sorted(df["result"].dropna().unique()))

# 数值列选择 + 中文国籍列
cols_list = st.sidebar.multiselect(
    "Columns 📊",
    df.select_dtypes(include="number").columns.tolist() + ["nationality_cn"]
)

# 统计方法
stats = st.sidebar.radio("Statistics Method", ["mean", "median", "max", "min"])

# ============================================
# 5. Run Button
# ============================================

if st.sidebar.button("Run"):
    row_filter = {}

    if nat_list:
        row_filter["nationality_cn"] = nat_list
    if year_list:
        row_filter["year"] = year_list
    if result_list:
        row_filter["result"] = result_list

    out = summarize_by_school(df, row_filter=row_filter, cols=cols_list, stats=stats)

    st.subheader("📄 Summary Table")
    st.dataframe(out, use_container_width=True)
