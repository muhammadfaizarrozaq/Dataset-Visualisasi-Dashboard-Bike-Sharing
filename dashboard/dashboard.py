import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman
st.set_page_config(
    page_title="Bike Sharing Dashboard (2011–2012)",
    page_icon="🚲",
    layout="wide"
)

sns.set_theme(style="whitegrid")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    day_df = pd.read_csv(os.path.join(base_dir, "day_clean.csv"))
    hour_df = pd.read_csv(os.path.join(base_dir, "hour_clean.csv"))
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    return day_df, hour_df

df_day, df_hour = load_data()

# ==========================================
# SIDEBAR FILTER
# ==========================================
st.sidebar.header("🚲 Filter Data")

min_date = df_day["dteday"].min().date()
max_date = df_day["dteday"].max().date()

date_range = st.sidebar.date_input(
    label="Pilih Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

selected_seasons = st.sidebar.multiselect(
    label="Pilih Musim (Season)",
    options=["Spring", "Summer", "Fall", "Winter"],
    default=["Spring", "Summer", "Fall", "Winter"]
)

# Terapkan filter ke dataset
filtered_day = df_day[
    (df_day["dteday"].dt.date >= start_date) &
    (df_day["dteday"].dt.date <= end_date) &
    (df_day["season"].isin(selected_seasons))
]

filtered_hour = df_hour[
    (df_hour["dteday"].dt.date >= start_date) &
    (df_hour["dteday"].dt.date <= end_date) &
    (df_hour["season"].isin(selected_seasons))
]

# ==========================================
# HEADER & KPI METRICS
# ==========================================
st.title("🚲 Dashboard Analisis Penyewaan Sepeda (2011–2012)")
st.markdown("Eksplorasi pola jam sibuk pengguna serta pengaruh musim dan cuaca terhadap volume penyewaan sepeda.")

if filtered_day.empty:
    st.warning("Tidak ada data untuk kombinasi filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = int(filtered_day["cnt"].sum())
    st.metric("Total Penyewaan", f"{total_rentals:,}")
with col2:
    total_registered = int(filtered_day["registered"].sum())
    st.metric("Pengguna Member (Registered)", f"{total_registered:,}")
with col3:
    total_casual = int(filtered_day["casual"].sum())
    st.metric("Pengguna Biasa (Casual)", f"{total_casual:,}")

st.divider()

# ==========================================
# VISUALISASI 1: POLA JAM PUNCAK (PEAK HOURS)
# ==========================================
st.subheader("1. Pola Jam Puncak: Hari Kerja vs Akhir Pekan / Libur")

fig1, axes1 = plt.subplots(1, 2, figsize=(16, 5.5), sharey=True)
kategori_hari = ["Hari Kerja", "Akhir Pekan / Libur"]

for idx, kategori in enumerate(kategori_hari):
    subset = filtered_hour[filtered_hour["workingday"] == kategori]
    hourly_avg = (
        subset.groupby("hr")[["registered", "casual", "cnt"]]
        .mean()
        .reindex(range(24), fill_value=0)
        .reset_index()
    )

    ax = axes1[idx]
    sns.lineplot(data=hourly_avg, x="hr", y="cnt", ax=ax, label="Total Penyewa (cnt)", color="#1f77b4", linewidth=2.5, marker="o")
    sns.lineplot(data=hourly_avg, x="hr", y="registered", ax=ax, label="Member (registered)", color="#2ca02c", linewidth=2, linestyle="--")
    sns.lineplot(data=hourly_avg, x="hr", y="casual", ax=ax, label="Pengguna Biasa (casual)", color="#ff7f0e", linewidth=2, linestyle=":")

    ax.set_title(f"Pola pada {kategori}", fontsize=12, fontweight="bold")
    ax.set_xlabel("Jam (00:00 - 23:00)")
    ax.set_xticks(range(0, 24, 2))
    if idx == 0:
        ax.set_ylabel("Rata-rata Penyewa per Jam")
    ax.legend(loc="upper left")

plt.tight_layout()
st.pyplot(fig1)

st.divider()

# ==========================================
# VISUALISASI 2: PENGARUH MUSIM & CUACA
# ==========================================
st.subheader("2. Pengaruh Musim & Kondisi Cuaca terhadap Penyewaan Harian")

fig2, axes2 = plt.subplots(1, 2, figsize=(16, 5.5))

# Grafik Kiri: Musim
urutan_musim = ["Fall", "Summer", "Winter", "Spring"]
musim_avg = filtered_day.groupby("season")["cnt"].mean().reindex(urutan_musim, fill_value=0).reset_index()
warna_musim = ["#1f77b4", "#4a90d9", "#7fb3e6", "#b3d4f2"]

bars1 = axes2[0].bar(musim_avg["season"], musim_avg["cnt"], color=warna_musim, width=0.55)
axes2[0].set_title("Rata-rata Penyewaan Berdasarkan Musim", fontsize=12, fontweight="bold")
axes2[0].set_xlabel("Musim")
axes2[0].set_ylabel("Rata-rata Penyewaan per Hari")
axes2[0].bar_label(bars1, fmt="%.0f", padding=4, fontweight="bold")
axes2[0].set_ylim(0, max(musim_avg["cnt"].max() * 1.18, 100))

# Grafik Kanan: Cuaca
urutan_cuaca = ["Cerah / Berawan", "Berkabut / Mendung", "Hujan / Salju Ringan"]
cuaca_avg = filtered_day.groupby("weathersit")["cnt"].mean().reindex(urutan_cuaca, fill_value=0).reset_index()
warna_cuaca = ["#2ca02c", "#ffbb78", "#d62728"]

bars2 = axes2[1].bar(cuaca_avg["weathersit"], cuaca_avg["cnt"], color=warna_cuaca, width=0.5)
axes2[1].set_title("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca", fontsize=12, fontweight="bold")
axes2[1].set_xlabel("Kondisi Cuaca")
axes2[1].bar_label(bars2, fmt="%.0f", padding=4, fontweight="bold")
axes2[1].set_ylim(0, max(cuaca_avg["cnt"].max() * 1.18, 100))

plt.tight_layout()
st.pyplot(fig2)

st.divider()

# ==========================================
# VISUALISASI 3: KLASTER WAKTU (ANALISIS LANJUTAN)
# ==========================================
st.subheader("3. Analisis Lanjutan: Klaster Segmen Waktu")

def kategori_waktu(hr):
    if 0 <= hr <= 5:
        return "Dini Hari (00:00–05:00)"
    elif 6 <= hr <= 10:
        return "Pagi (06:00–10:00)"
    elif 11 <= hr <= 14:
        return "Siang (11:00–14:00)"
    elif 15 <= hr <= 18:
        return "Sore (15:00–18:00)"
    else:
        return "Malam (19:00–23:00)"

filtered_hour = filtered_hour.copy()
filtered_hour["klaster_waktu"] = filtered_hour["hr"].apply(kategori_waktu)

urutan_waktu = [
    "Dini Hari (00:00–05:00)",
    "Pagi (06:00–10:00)",
    "Siang (11:00–14:00)",
    "Sore (15:00–18:00)",
    "Malam (19:00–23:00)"
]

cluster_waktu = (
    filtered_hour.groupby(["klaster_waktu", "workingday"])["cnt"]
    .mean()
    .unstack(fill_value=0)
    .reindex(urutan_waktu, fill_value=0)
)

fig3, ax3 = plt.subplots(figsize=(12, 4.8))
cluster_waktu.plot(kind="bar", ax=ax3, color=["#ff7f0e", "#1f77b4"], width=0.7)
ax3.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Klaster Waktu", fontsize=12, fontweight="bold")
ax3.set_xlabel("Klaster Waktu")
ax3.set_ylabel("Rata-rata Penyewaan per Jam")
ax3.tick_params(axis="x", rotation=15)
ax3.set_ylim(0, max(cluster_waktu.max().max() * 1.18, 50))
ax3.legend(title="Tipe Hari")

for container in ax3.containers:
    ax3.bar_label(container, fmt="%.0f", padding=3, fontsize=9, fontweight="bold")

plt.tight_layout()
st.pyplot(fig3)

st.caption("Copyright © 2026 - Proyek Analisis Data Bike Sharing")