import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import os

# ====================== 【可配置区】 ======================
QR_CODE_CONFIG = {
    "二维码1": "校边店海报1",
    "二维码2": "校边店海报2",
    "二维码3": "校边店海报3",
    "二维码4": "校边店海报4"
}
YEAR_DEFAULT = 2026
EXCEL_FILE = "AI大阅读抽奖数据.xlsx"
# =========================================================

st.set_page_config(page_title="活动数据看板", layout="wide")
st.markdown("""
<style>
    .metric-card {
        background-color: #f7f8fa;
        padding: 16px;
        border-radius: 10px;
        border:1px solid #e9ecef;
    }
    h2{
        margin-top:10px;
    }
</style>
""", unsafe_allow_html=True)
st.title("📊 活动数据看板")

# ====== 自动加载内置Excel，上传框保留备用 ======
data_source = None
if os.path.exists(EXCEL_FILE):
    data_source = open(EXCEL_FILE, "rb")
    st.success("✅ 已自动加载数据，直接查看看板")
else:
    st.warning("未找到内置Excel，请在下方上传")

upload_file = st.file_uploader("【可选】上传新版Excel覆盖", type="xlsx")
if upload_file is not None:
    data_source = upload_file
    st.info("已切换为你上传的文件")

if data_source is None:
    st.stop()


def parse_date(mmdd_str):
    if pd.isna(mmdd_str):
        return None
    s = str(int(mmdd_str)).zfill(4)
    mm = int(s[:2])
    dd = int(s[2:])
    return datetime(YEAR_DEFAULT, mm, dd).date()


def mask_user_id(uid):
    if pd.isna(uid):
        return ""
    s = str(uid)
    if len(s) > 6:
        return s[:4] + "*****" + s[-2:]
    return s


@st.cache_data
def load_metric_data(file):
    dfs = []
    for qr_name, sheet_name in QR_CODE_CONFIG.items():
        try:
            df = pd.read_excel(file, sheet_name=sheet_name)
            df["二维码名称"] = qr_name
            if "日期" in df.columns:
                df["dt"] = df["日期"].apply(parse_date)
            dfs.append(df)
        except Exception as e:
            st.warning(f"读取sheet {sheet_name} 失败:{e}")
    if len(dfs) == 0:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


@st.cache_data
def load_lottery_data(file):
    try:
        df_lot = pd.read_excel(file, sheet_name="抽奖记录")
        if "日期" in df_lot.columns:
            df_lot["dt"] = df_lot["日期"].apply(parse_date)
        if "用户id" in df_lot.columns:
            df_lot["用户id脱敏"] = df_lot["用户id"].apply(mask_user_id)
        return df_lot
    except Exception as e:
        st.error(f"读取抽奖记录sheet失败：{e}")
        return pd.DataFrame()


df_metric = load_metric_data(data_source)
df_lottery = load_lottery_data(data_source)

if df_metric.empty:
    st.error("指标数据为空，请检查Excel工作表名称是否匹配代码配置")
    st.stop()

count_metrics = [
    "落地页浏览", "选择年级", "下单页浏览", "发送验证码",
    "登陆成功", "创建订单", "支付成功"
]
pct_metrics = ["落地页转化率", "下单页转化率", "支付成功率", "成单率"]
all_metrics = count_metrics + pct_metrics
existing_metrics = [c for c in all_metrics if c in df_metric.columns]

all_dates = sorted(df_metric["dt"].dropna().unique())
start_dt, end_dt = st.date_input(
    "全局日期范围",
    value=(all_dates[0], all_dates[-1]) if all_dates else None
)
df_filter = df_metric[
    (df_metric["dt"] >= start_dt) & (df_metric["dt"] <= end_dt)
].copy()

day_list = sorted(df_filter["dt"].dropna().unique())
sel_day = st.selectbox(
    "选择单日", day_list,
    index=len(day_list) - 1 if day_list else 0
)
df_day = df_filter[df_filter["dt"] == sel_day].copy()

st.subheader(f"🔹核心数据（{sel_day}）")
row_sum = df_day[count_metrics].sum(numeric_only=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("落地页浏览", int(row_sum.get("落地页浏览", 0)))
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("下单页浏览", int(row_sum.get("下单页浏览", 0)))
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("创建订单", int(row_sum.get("创建订单", 0)))
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("支付成功", int(row_sum.get("支付成功", 0)))
    st.markdown('</div>', unsafe_allow_html=True)
with c5:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    if "成单率" in df_day.columns:
        v = df_day["成单率"].replace("-", None).dropna().astype(float).mean()
        st.metric("成单率", f"{v*100:.2f}%" if v < 1.5 else f"{v:.2f}%")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

st.subheader("🔹二维码横向对比")
qr_cols = list(QR_CODE_CONFIG.keys())
for c in pct_metrics:
    if c in df_day.columns:
        df_day[c] = pd.to_numeric(df_day[c].replace("-", None), errors="coerce")

compare_rows = []
for m in existing_metrics:
    row = {"指标": m}
    vals = []
    for qr in qr_cols:
        val = df_day[df_day["二维码名称"] == qr][m].sum()
        vals.append(val)
        if m in pct_metrics:
            row[qr] = "—" if (pd.isna(val) or val == 0) else f"{val*100:.2f}%"
        else:
            row[qr] = "—" if pd.isna(val) else int(val)
    total = sum(v for v in vals if not pd.isna(v))
    if m in pct_metrics:
        row["合计"] = "—" if total == 0 else f"{total*100:.2f}%"
    else:
        row["合计"] = int(total)
    compare_rows.append(row)
compare_df = pd.DataFrame(compare_rows).set_index("指标")
st.dataframe(compare_df, use_container_width=True)

st.divider()

st.subheader("🔹各指标环比增长率（当日 vs 前一日）")
ring_c1, ring_c2 = st.columns(2)
with ring_c1:
    sel_ring_metric = st.selectbox("选择指标", count_metrics, index=0, key="ring_metric_select")
with ring_c2:
    sel_ring_qr = st.multiselect("选择二维码（不选=全部）", qr_cols, default=qr_cols)

daily = df_filter.groupby(["dt", "二维码名称"])[sel_ring_metric].sum().reset_index()
daily = daily.sort_values(["二维码名称", "dt"]).reset_index(drop=True)
daily["昨日值"] = daily.groupby("二维码名称")[sel_ring_metric].shift(1)
daily["变化量"] = daily[sel_ring_metric] - daily["昨日值"]

def growth_pct(row):
    if pd.isna(row["昨日值"]) or row["昨日值"] == 0:
        return None
    return (row[sel_ring_metric] - row["昨日值"]) / row["昨日值"]

daily["环比"] = daily.apply(growth_pct, axis=1)
daily_view = daily[daily["二维码名称"].isin(sel_ring_qr)].copy()
daily_view = daily_view.sort_values(["dt", "二维码名称"], ascending=[False, True])

daily_view_display = daily_view.rename(columns={
    "dt": "日期", "二维码名称": "二维码", sel_ring_metric: "今日值",
})
daily_view_display["昨日值"] = daily_view_display["昨日值"].apply(
    lambda x: "—" if pd.isna(x) else f"{int(x)}"
)
daily_view_display["变化量"] = daily_view_display["变化量"].apply(
    lambda x: "—" if pd.isna(x) else f"{int(x):+d}"
)
daily_view_display["环比"] = daily_view_display["环比"].apply(
    lambda x: "—" if pd.isna(x) else f"{x*100:+.2f}%"
)

def color_growth(val):
    if val == "—":
        return ""
    if val.startswith("-"):
        return "color: #d33"
    elif val.startswith("+"):
        return "color: #0a0"
    return ""

st.dataframe(
    daily_view_display.style.map(color_growth, subset=["环比"]),
    use_container_width=True, height=400
)

st.divider()

st.subheader("🔹每日趋势")
trend_metric = st.selectbox("选择指标", count_metrics, key="trend_select")
trend_df = df_filter.groupby(["dt", "二维码名称"])[trend_metric].sum().reset_index()
trend_df["日期文本"] = trend_df["dt"].apply(lambda d: d.strftime("%m-%d"))

chart = alt.Chart(trend_df, title=f"{trend_metric} 每日趋势").mark_line(point=True).encode(
    x=alt.X("日期文本:N", title="日期", axis=alt.Axis(labelAngle=0)),
    y=alt.Y(f"{trend_metric}:Q", title="数值"),
    color=alt.Color("二维码名称:N", title="二维码"),
).properties(width="container", height=320)
st.altair_chart(chart, use_container_width=True)

st.divider()

st.subheader("🔹抽奖记录明细")
if not df_lottery.empty:
    lt1, lt2, lt3, lt4, lt5 = st.columns(5)
    with lt1:
        lot_dates = st.date_input("抽奖日期筛选", key="lotdate")
    with lt2:
        sel_ak = st.multiselect("活动key", df_lottery["活动key"].dropna().unique().tolist())
    with lt3:
        sel_sk = st.multiselect("场次key", df_lottery["场次key"].dropna().unique().tolist())
    with lt4:
        sel_gift = st.multiselect("礼品", df_lottery["礼品"].dropna().unique().tolist())
    with lt5:
        sel_res = st.multiselect("抽奖结果", df_lottery["抽奖结果"].dropna().unique().tolist())

    df_lot_filter = df_lottery.copy()
    if isinstance(lot_dates, tuple) and len(lot_dates) == 2 and lot_dates[0] is not None:
        s, e = lot_dates
        df_lot_filter = df_lot_filter[(df_lot_filter["dt"] >= s) & (df_lot_filter["dt"] <= e)]
    if sel_ak:
        df_lot_filter = df_lot_filter[df_lot_filter["活动key"].isin(sel_ak)]
    if sel_sk:
        df_lot_filter = df_lot_filter[df_lot_filter["场次key"].isin(sel_sk)]
    if sel_gift:
        df_lot_filter = df_lot_filter[df_lot_filter["礼品"].isin(sel_gift)]
    if sel_res:
        df_lot_filter = df_lot_filter[df_lot_filter["抽奖结果"].isin(sel_res)]

    search_uid = st.text_input("搜索用户ID")
    if search_uid.strip():
        df_lot_filter = df_lot_filter[
            df_lot_filter["用户id"].astype(str).str.contains(search_uid.strip())
        ]

    show_cols = [c for c in [
        "dt", "用户id脱敏", "活动key", "场次key", "礼品",
        "礼品类型", "抽奖结果", "抽奖时间"
    ] if c in df_lot_filter.columns]
    st.dataframe(df_lot_filter[show_cols], use_container_width=True, height=300)
else:
    st.info("抽奖记录数据为空，请确认Excel存在【抽奖记录】工作表")

st.markdown("---")
st.caption("说明：打开网页自动加载内置数据；如需更新，替换Excel后git push即可。")
