import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="whitegrid")
plt.rcParams.update({"axes.grid.axis": "y", "font.size": 12})

URUTAN_CUACA = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan"]
WARNA_CUACA = ["#1f77b4", "#9ecae1", "#d62728"]


BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def tgl(d):
    return f"{d.day:02d} {BULAN[d.month - 1]} {d.year}"


def rupa(x, desimal=0):
    # Format angka gaya Indonesia: 6.004 dan 16,9
    return f"{x:,.{desimal}f}".replace(",", "_").replace(".", ",").replace("_", ".")


@st.cache_data
def load_data():
    df = pd.read_csv(Path(__file__).parent / "main_data.csv", parse_dates=["dteday"])
    df["tanggal"] = df["dteday"].dt.date
    return df


hour_df = load_data()

# Sidebar: filter rentang tanggal dan jenis hari
with st.sidebar:
    st.title("🚲 Capital Bikeshare")
    st.caption("Washington D.C., 2011 sampai 2012")
    min_date, max_date = hour_df["tanggal"].min(), hour_df["tanggal"].max()
    rentang = st.date_input("Rentang tanggal", value=(pd.Timestamp("2012-01-01").date(), max_date),
                            min_value=min_date, max_value=max_date)
    jenis = st.multiselect("Jenis hari", ["Hari Kerja", "Libur/Akhir Pekan"],
                           default=["Hari Kerja", "Libur/Akhir Pekan"])

if not isinstance(rentang, tuple) or len(rentang) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir di sidebar.")
    st.stop()
if not jenis:
    st.warning("Pilih minimal satu jenis hari.")
    st.stop()

mulai, akhir = rentang
data = hour_df[(hour_df["tanggal"] >= mulai) & (hour_df["tanggal"] <= akhir) & hour_df["jenis_hari"].isin(jenis)]
if data.empty:
    st.warning("Tidak ada data pada filter ini.")
    st.stop()

harian = (data.groupby(["tanggal", "weathersit_harian", "jenis_hari"], as_index=False)
          [["casual", "registered", "cnt"]].sum())

st.header("Dashboard Penyewaan Sepeda")
st.caption(f"Periode {tgl(mulai)} sampai {tgl(akhir)} · {len(harian)} hari · jenis hari: {', '.join(jenis)}")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total penyewaan", rupa(harian["cnt"].sum()))
k2.metric("Rata-rata per hari", rupa(harian["cnt"].mean()))
k3.metric("Porsi pengguna terdaftar", f"{rupa(harian['registered'].sum() / harian['cnt'].sum() * 100, 1)}%")
k4.metric(f"Hari tersibuk ({tgl(harian.loc[harian['cnt'].idxmax(), 'tanggal'])})",
          f"{rupa(harian['cnt'].max())} sepeda")

# Tren harian
st.subheader("Tren penyewaan harian")
fig, ax = plt.subplots(figsize=(14, 4))
seri = harian.groupby("tanggal")["cnt"].sum()
ax.plot(seri.index, seri.values, color="#1f77b4", linewidth=1.2)
ax.set_ylim(0, None)
ax.set_xlim(seri.index.min(), seri.index.max())
ax.set_ylabel("Sepeda disewa per hari")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: rupa(v)))
st.pyplot(fig)

col1, col2 = st.columns(2)

# Pertanyaan 1: cuaca
with col1:
    st.subheader("Dampak cuaca")
    cuaca = harian.groupby("weathersit_harian")["cnt"].agg(["mean", "count"]).reindex(URUTAN_CUACA).dropna()
    fig, ax = plt.subplots(figsize=(7, 5))
    warna = [WARNA_CUACA[URUTAN_CUACA.index(k)] for k in cuaca.index]
    bars = ax.bar([f"{k}\n(n = {int(n)} hari)" for k, n in zip(cuaca.index, cuaca["count"])], cuaca["mean"], color=warna)
    basis = cuaca["mean"].get("Cerah")
    for b, (k, v) in zip(bars, cuaca["mean"].items()):
        teks = rupa(v)
        if basis and k != "Cerah":
            teks += f"\n({rupa((v / basis - 1) * 100, 1)}% vs Cerah)"
        ax.text(b.get_x() + b.get_width() / 2, v * 1.02, teks, ha="center", va="bottom", fontsize=12,
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax.set_ylim(0, cuaca["mean"].max() * 1.3)
    ax.set_ylabel("Rata-rata sepeda disewa per hari")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: rupa(v)))
    st.pyplot(fig)
    if (cuaca["count"] < 10).any():
        st.caption("⚠️ Kategori dengan n < 10 hari: baca selisihnya sebagai arah, bukan angka pasti.")

# Pertanyaan 2: pola jam
with col2:
    st.subheader("Jam puncak")
    pola = data.pivot_table(index="hr", columns="jenis_hari", values="cnt", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(7, 5))
    gaya = {"Hari Kerja": ("#1f77b4", "-"), "Libur/Akhir Pekan": ("#ff7f0e", "--")}
    for k in pola.columns:
        c, ls = gaya[k]
        ax.plot(pola.index, pola[k], color=c, linestyle=ls, linewidth=2.5, label=k)
        puncak = pola[k].idxmax()
        ax.scatter(puncak, pola[k].max(), color=c, zorder=3)
        # Label libur ditaruh tepat di atas puncaknya: di jam 11-15 garis hari kerja masih rendah (~250)
        posisi = dict(xytext=(puncak, pola.max().max() * 1.12), textcoords="data", ha="center") \
            if k == "Libur/Akhir Pekan" else dict(xytext=(10, 8), textcoords="offset points")
        ax.annotate(f"{rupa(pola[k].max())}/jam\npukul {puncak:02d}.00", (puncak, pola[k].max()), **posisi, fontsize=12, color=c, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=c),
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
    ax.set_xticks(range(0, 24, 2))
    ax.set_xlim(-0.5, 23.5)
    ax.set_ylim(0, pola.max().max() * 1.35)
    ax.set_xlabel("Jam")
    ax.set_ylabel("Rata-rata sepeda disewa per jam")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Terdaftar vs kasual")
    porsi = data.groupby("jenis_hari")[["registered", "casual"]].sum()
    porsi = porsi.div(porsi.sum(axis=1), axis=0) * 100
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(porsi.index, porsi["registered"], color="#1f77b4", label="Terdaftar")
    ax.bar(porsi.index, porsi["casual"], bottom=porsi["registered"], color="#bdbdbd", label="Kasual")
    for i, (r, c) in enumerate(zip(porsi["registered"], porsi["casual"])):
        ax.text(i, r / 2, f"{rupa(r, 1)}%", ha="center", color="white", fontweight="bold")
        ax.text(i, r + c / 2, f"{rupa(c, 1)}%", ha="center")
    ax.set_ylim(0, 100)
    ax.set_ylabel("Porsi penyewaan (%)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False)
    st.pyplot(fig)

# Analisis lanjutan: clustering manual (binning suhu)
with col4:
    st.subheader("Kelompok suhu (binning)")
    suhu_harian = data.groupby("tanggal").agg(cnt=("cnt", "sum"), temp_c=("temp_c_harian", "first"))
    suhu_harian["kelompok"] = pd.cut(suhu_harian["temp_c"], bins=[0, 10, 20, 30, 45],
                                     labels=["Dingin\n(<10°C)", "Sejuk\n(10-20°C)", "Hangat\n(20-30°C)", "Panas\n(>30°C)"])
    suhu = suhu_harian.groupby("kelompok", observed=True)["cnt"].agg(["mean", "count"])
    fig, ax = plt.subplots(figsize=(7, 5))
    warna = ["#1f77b4" if v == suhu["mean"].max() else "#bdbdbd" for v in suhu["mean"]]
    bars = ax.bar(suhu.index.astype(str), suhu["mean"], color=warna)
    for b, (v, n) in zip(bars, suhu.values):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.02, f"{rupa(v)}\n(n = {int(n)} hari)", ha="center", fontsize=12)
    ax.set_ylim(0, suhu["mean"].max() * 1.3)
    ax.set_ylabel("Rata-rata sepeda disewa per hari")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: rupa(v)))
    st.pyplot(fig)

with st.expander("Lihat angka di balik grafik"):
    st.dataframe(harian.sort_values("tanggal"), width="stretch", hide_index=True)

st.caption("Sumber: Bike Sharing Dataset (Fanaee-T & Gama, 2013) · Muhammad Akbar Pradana")
