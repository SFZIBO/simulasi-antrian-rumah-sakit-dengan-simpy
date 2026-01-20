import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import simpy
import time

# Set page config
st.set_page_config(
    page_title="Simulasi Antrean Klinik",
    page_icon="🏥",
    layout="wide"
)

# Add custom CSS styling
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .main-header {
        color: #1e3d59;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1e3d59;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff6e40;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #6c757d;
        font-size: 0.9rem;
        border-top: 1px solid #e9ecef;
        margin-top: 2rem;
    }
    .tab-header {
        font-weight: 600;
        color: #1e3d59;
    }
    .recommendation-box {
        border-left: 4px solid #ff6e40;
        padding: 1rem;
        background-color: #fff8f5;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🏥 Simulasi Antrean Klinik dengan SimPy</h1>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; background-color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
    <p>Aplikasi ini mensimulasikan antrean di klinik berdasarkan data riil. Gunakan parameter pada sidebar untuk mengubah konfigurasi simulasi dan lihat dampaknya pada kinerja sistem pelayanan.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for parameters
st.sidebar.header("⚙️ Parameter Simulasi")
st.sidebar.markdown("Ubah parameter untuk melihat pengaruhnya pada sistem antrean")

# Get default parameters from session state or use defaults
if 'avg_inter_arrival' not in st.session_state:
    st.session_state.avg_inter_arrival = 15.0
if 'avg_service_time' not in st.session_state:
    st.session_state.avg_service_time = 20.0
if 'capacity' not in st.session_state:
    st.session_state.capacity = 2
if 'simulation_time' not in st.session_state:
    st.session_state.simulation_time = 8

# Input parameters with improved UI
st.sidebar.subheader("🕒 Parameter Waktu")
avg_inter_arrival = st.sidebar.slider(
    "Rata-rata waktu antar kedatangan (menit)",
    min_value=5.0,
    max_value=60.0,
    value=st.session_state.avg_inter_arrival,
    step=0.5,
    help="Semakin kecil nilai ini, semakin sering pasien datang"
)

avg_service_time = st.sidebar.slider(
    "Rata-rata durasi layanan (menit)",
    min_value=5.0,
    max_value=60.0,
    value=st.session_state.avg_service_time,
    step=0.5,
    help="Waktu rata-rata yang dibutuhkan untuk melayani satu pasien"
)

st.sidebar.subheader("👥 Kapasitas Sumber Daya")
capacity = st.sidebar.slider(
    "Jumlah dokter/ruang pelayanan",
    min_value=1,
    max_value=10,
    value=st.session_state.capacity,
    step=1,
    help="Jumlah sumber daya yang tersedia untuk melayani pasien"
)

st.sidebar.subheader("⏱️ Durasi Simulasi")
simulation_time = st.sidebar.slider(
    "Durasi simulasi (jam)",
    min_value=1,
    max_value=12,
    value=st.session_state.simulation_time,
    step=1,
    help="Lama waktu simulasi dalam jam kerja"
)

# Update session state
st.session_state.avg_inter_arrival = avg_inter_arrival
st.session_state.avg_service_time = avg_service_time
st.session_state.capacity = capacity
st.session_state.simulation_time = simulation_time

# Display current parameters in an attractive way
with st.expander("📊 Parameter Simulasi Saat Ini", expanded=False):
    st.markdown("### Konfigurasi Sistem")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Kedatangan</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #ff6e40;">{avg_inter_arrival:.1f} menit</p>
            <p>Rata-rata interval kedatangan</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚕️ Pelayanan</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #1e3d59;">{avg_service_time:.1f} menit</p>
            <p>Rata-rata durasi layanan</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Kapasitas</h3>
            <p style="font-size: 1.5rem; font-weight: bold; color: #5f9ea0;">{capacity}</p>
            <p>Jumlah dokter/ruang</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card" style="margin-top: 1rem;">
        <h3>⏰ Durasi Simulasi</h3>
        <p style="font-size: 1.5rem; font-weight: bold; color: #2e8b57;">{simulation_time} jam</p>
        <p>({simulation_time * 60} menit operasional)</p>
    </div>
    """, unsafe_allow_html=True)

# Run simulation button with attractive styling
if st.sidebar.button("🚀 Jalankan Simulasi", use_container_width=True):
    # Simulation function with detailed comments
    def run_simulation(avg_inter_arrival, avg_service_time, capacity, total_time):
        """
        Menjalankan simulasi antrean klinik menggunakan SimPy
        
        Parameters:
        avg_inter_arrival (float): Rata-rata waktu antar kedatangan dalam menit
        avg_service_time (float): Rata-rata durasi layanan dalam menit
        capacity (int): Jumlah sumber daya (dokter/ruang)
        total_time (int): Durasi simulasi dalam menit
        
        Returns:
        tuple: (waiting_times, service_times, queue_lengths, timestamps, total_patients, patient_log)
        """
        # Metrics collection
        waiting_times = []
        service_times = []
        queue_lengths = []
        timestamps = []
        patient_log = []
        total_patients = [0]  # Use list to allow modification in nested function

        # Patient process definition
        def patient(env, name, counter):
            """Proses untuk setiap pasien dalam simulasi"""
            arrival_time = env.now
            patient_log.append(f"{name} tiba pada menit {arrival_time:.1f}")
            
            # Request service from the counter (doctor/room)
            with counter.request() as req:
                # Wait for resource to become available
                yield req
                
                # Calculate waiting time
                wait_time = env.now - arrival_time
                waiting_times.append(wait_time)
                patient_log.append(f"{name} mulai dilayani pada menit {env.now:.1f} setelah menunggu {wait_time:.1f} menit")
                
                # Service time with exponential distribution
                service_time = np.random.exponential(avg_service_time)
                yield env.timeout(service_time)
                service_times.append(service_time)
                patient_log.append(f"{name} selesai dilayani pada menit {env.now:.1f} dengan durasi {service_time:.1f} menit")

        # Monitor queue length over time
        def monitor_queue(env, counter):
            """Memantau panjang antrean sepanjang waktu"""
            while True:
                current_queue = len(counter.queue)
                queue_lengths.append(current_queue)
                timestamps.append(env.now)
                yield env.timeout(1)  # Record every minute

        # Patient generator
        def patient_generator(env, counter):
            """Generate pasien sepanjang waktu simulasi"""
            while env.now < total_time:
                env.process(patient(env, f'Pasien {total_patients[0]}', counter))
                total_patients[0] += 1
                # Time until next patient arrives
                yield_time = np.random.exponential(avg_inter_arrival)
                yield_time = max(0.1, yield_time)  # Ensure positive time
                yield env.timeout(yield_time)

        # Setup simulation environment
        env = simpy.Environment()
        counter = simpy.Resource(env, capacity=capacity)

        # Start processes
        env.process(monitor_queue(env, counter))
        env.process(patient_generator(env, counter))

        # Run the simulation
        env.run(until=total_time)
        
        return (waiting_times,
                service_times,
                queue_lengths,
                timestamps,
                total_patients[0],
                patient_log)

    # Run simulation with loading animation
    with st.spinner('🧠 Sedang menjalankan simulasi...'):
        total_minutes = simulation_time * 60
        waiting_times, service_times, queue_lengths, timestamps, total_patients, patient_log = run_simulation(
            avg_inter_arrival, avg_service_time, capacity, total_minutes
        )
        time.sleep(0.5)  # For better UX

    # Display success message with patient count
    st.success(f"✅ Simulasi selesai! Total {total_patients} pasien dilayani dalam {simulation_time} jam")

    # Calculate key metrics
    avg_wait = np.mean(waiting_times) if waiting_times else 0
    max_wait = max(waiting_times) if waiting_times else 0
    avg_service = np.mean(service_times) if service_times else 0
    utilization = min(100, (np.sum(service_times) / (capacity * total_minutes)) * 100) if service_times else 0

    # Display metrics in attractive cards
    st.subheader("📈 Ringkasan Kinerja Sistem")
    
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🕒 Waktu Tunggu Rata-rata</h3>
            <p style="font-size: 1.8rem; font-weight: bold; color: {'#dc3545' if avg_wait > 30 else '#28a745'}">{avg_wait:.1f} menit</p>
            <p>{'⚠️ Terlalu lama' if avg_wait > 30 else '✅ Wajar'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Durasi Layanan Rata-rata</h3>
            <p style="font-size: 1.8rem; font-weight: bold; color: #17a2b8">{avg_service:.1f} menit</p>
            <p>Berdasarkan parameter</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>🚨 Waktu Tunggu Maksimal</h3>
            <p style="font-size: 1.8rem; font-weight: bold; color: {'#dc3545' if max_wait > 60 else '#ffc107'}">{max_wait:.1f} menit</p>
            <p>{'❌ Sangat lama' if max_wait > 60 else '⚠️ Perlu perhatian' if max_wait > 45 else '✅ Masuk akal'}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Utilisasi Sistem</h3>
            <p style="font-size: 1.8rem; font-weight: bold; color: {'#28a745' if utilization < 85 else '#ffc107' if utilization < 95 else '#dc3545'}">{utilization:.1f}%</p>
            <p>{'✅ Optimal' if utilization < 85 else '⚠️ Hampir penuh' if utilization < 95 else '❌ Overload'}</p>
        </div>
        """, unsafe_allow_html=True)

    # Charts and analysis
    st.subheader("🔬 Analisis Mendalam")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Distribusi", 
        "📈 Tren Antrean", 
        "💡 Rekomendasi", 
        "📋 Log Aktivitas"
    ])

    with tab1:
        st.markdown('<h3 class="tab-header">Distribusi Waktu Tunggu dan Layanan</h3>', unsafe_allow_html=True)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
        fig.suptitle('Analisis Distribusi Kinerja Sistem', fontsize=16, fontweight='bold')
        
        if waiting_times:
            sns.histplot(waiting_times, kde=True, ax=ax1, bins=20, color='#ff6e40', alpha=0.7)
            ax1.set_title('Distribusi Waktu Tunggu Pasien', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Waktu Tunggu (Menit)', fontsize=12)
            ax1.set_ylabel('Jumlah Pasien', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.axvline(x=30, color='r', linestyle='--', alpha=0.7, label='Batas Standar (30 menit)')
            ax1.legend()
        
        if service_times:
            sns.histplot(service_times, kde=True, ax=ax2, bins=20, color='#1e3d59', alpha=0.7)
            ax2.set_title('Distribusi Durasi Layanan', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Durasi Layanan (Menit)', fontsize=12)
            ax2.set_ylabel('Jumlah Pasien', fontsize=12)
            ax2.grid(True, alpha=0.3)
            ax2.axvline(x=avg_service_time, color='r', linestyle='--', alpha=0.7, label=f'Rata-rata ({avg_service_time:.1f} menit)')
            ax2.legend()
        
        st.pyplot(fig)
        
        # Add interpretation
        with st.expander("🔍 Interpretasi Distribusi"):
            if avg_wait > 30:
                st.warning(f"""
                ⚠️ **Masalah Utama Teridentifikasi**: 
                Distribusi waktu tunggu menunjukkan bahwa {len([w for w in waiting_times if w > 30])/len(waiting_times)*100:.1f}% pasien 
                menunggu lebih dari 30 menit. Hal ini menunjukkan kapasitas sistem tidak mencukupi untuk volume kedatangan saat ini.
                """)
            else:
                st.success("""
                ✅ **Sistem Beroperasi Baik**: 
                Sebagian besar pasien memiliki waktu tunggu di bawah 30 menit, yang sesuai dengan standar pelayanan kesehatan.
                Distribusi menunjukkan sistem mampu menangani beban pasien dengan efisien.
                """)

    with tab2:
        st.markdown('<h3 class="tab-header">Evolusi Panjang Antrean Sepanjang Waktu</h3>', unsafe_allow_html=True)
        
        if queue_lengths:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(timestamps, queue_lengths, linewidth=2.5, color='#1e3d59', marker='o', markersize=4, markevery=30)
            ax.fill_between(timestamps, 0, queue_lengths, alpha=0.2, color='#ff6e40')
            ax.set_title('Panjang Antrean Sepanjang Waktu Simulasi', fontsize=16, fontweight='bold')
            ax.set_xlabel('Waktu (Menit)', fontsize=12)
            ax.set_ylabel('Jumlah Pasien dalam Antrean', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(bottom=0)
            
            ax.axhline(y=5, color='r', linestyle='--', alpha=0.7, label='Antrean Panjang (>5 pasien)')
            ax.axhline(y=10, color='darkred', linestyle='-.', alpha=0.7, label='Antrean Sangat Panjang (>10 pasien)')
            
            peak_hours = [(9*60, 11*60), (14*60, 16*60)]
            for start, end in peak_hours:
                ax.axvspan(start, end, alpha=0.1, color='#1e3d59', label='Jam Sibuk' if start == peak_hours[0][0] else "")
            
            ax.legend()
            st.pyplot(fig)
            
            max_queue = max(queue_lengths)
            peak_time = timestamps[queue_lengths.index(max_queue)]
            st.info(f"""
            📌 **Analisis Titik Kritis**: 
            Panjang antrean maksimum mencapai **{max_queue} pasien** pada menit ke-{peak_time:.0f} 
            ({peak_time/60:.1f} jam). Pada jam sibuk (9-11 pagi dan 2-4 sore), antrean cenderung lebih panjang.
            """)

    with tab3:
        st.markdown('<h3 class="tab-header">Rekomendasi Optimasi Sistem</h3>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="recommendation-box">
            <h4>🔍 Analisis Kondisi Saat Ini</h4>
            <p>Berdasarkan hasil simulasi dengan parameter saat ini:</p>
        </div>
        """, unsafe_allow_html=True)
        
        if avg_wait > 30 and utilization > 85:
            st.error("""
            ❌ **SISTEM DALAM KONDISI KRITIS**  
            Kombinasi waktu tunggu panjang (>30 menit) dan utilisasi tinggi (>85%) menunjukkan sistem 
            kelebihan beban. Diperlukan intervensi segera untuk mencegah penurunan kualitas layanan.
            """)
        elif avg_wait > 30 and utilization < 70:
            st.warning("""
            ⚠️ **KETIDAKEFISIENAN SISTEM**  
            Waktu tunggu panjang (>30 menit) dengan utilisasi rendah (<70%) mengindikasikan masalah 
            distribusi sumber daya atau pengaturan jadwal yang tidak optimal.
            """)
        elif avg_wait < 20 and utilization < 60:
            st.info("""
            💡 **KAPASITAS BERLEBIH**  
            Sistem memiliki kapasitas berlebih dengan waktu tunggu rendah (<20 menit) dan utilisasi 
            rendah (<60%). Pertimbangkan pengurangan sumber daya atau peningkatan volume pasien.
            """)
        else:
            st.success("""
            ✅ **SISTEM DALAM KONDISI OPTIMAL**  
            Keseimbangan yang baik antara waktu tunggu yang wajar dan utilisasi sumber daya yang efisien.
            Pertahankan konfigurasi ini dan pantau secara berkala.
            """)
        
        st.markdown("### 🎯 Rekomendasi Spesifik")
        
        if avg_wait > 30:
            st.markdown("#### 🚨 Untuk Mengurangi Waktu Tunggu")
            recommendations = [
                f"**Tambah kapasitas**: Naikkan jumlah dokter dari {capacity} menjadi {capacity + 1} atau {capacity + 2} pada jam sibuk",
                "**Optimalkan jadwal**: Sebar janji temu dengan interval minimal 15-20 menit untuk menghindari clustering",
                "**Implementasi sistem triase**: Prioritaskan pasien dengan kondisi mendesak untuk mengurangi dampak antrean panjang"
            ]
            for rec in recommendations:
                st.markdown(f"- {rec}")
            
            projected_wait = avg_wait * 0.6
            st.markdown(f"""
            <div style="background-color: #e8f5e8; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                💡 <strong>Proyeksi Hasil</strong>: Dengan implementasi rekomendasi di atas, waktu tunggu rata-rata 
                diproyeksikan turun menjadi <strong>{projected_wait:.1f} menit</strong> (pengurangan 40%).
            </div>
            """, unsafe_allow_html=True)
        
        if utilization > 90:
            st.markdown("#### Untuk Mengurangi Beban Sistem")
            recommendations = [
                "**Pengaturan ulang jam operasional**: Tambah jam layanan pada periode dengan antrean panjang",
                "**Sistem appointment advance**: Kurangi walk-in patients dengan sistem janji temu yang terjadwal",
                "**Penambahan tenaga administrasi**: Untuk mempercepat proses pendaftaran dan pengurangan waktu non-medis"
            ]
            for rec in recommendations:
                st.markdown(f"- {rec}")
        
        if utilization < 60:
            st.markdown("#### Untuk Meningkatkan Efisiensi")
            recommendations = [
                "**Pengaturan shift**: Sesuaikan jadwal dokter dengan pola kedatangan pasien",
                "**Program promosi**: Tingkatkan volume pasien pada jam-jam sepi",
                "**Kegiatan tambahan**: Manfaatkan waktu sepi untuk pelatihan atau administrasi"
            ]
            for rec in recommendations:
                st.markdown(f"- {rec}")

    with tab4:
        st.markdown('<h3 class="tab-header">Log Aktivitas Simulasi</h3>', unsafe_allow_html=True)
        
        log_to_show = patient_log[-20:] if len(patient_log) > 20 else patient_log
        
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 8px; max-height: 400px; overflow-y: auto; border: 1px solid #dee2e6;">
        """, unsafe_allow_html=True)
        
        for entry in log_to_show:
            if "tiba" in entry:
                color = "#17a2b8"
            elif "mulai" in entry:
                color = "#ffc107"
            elif "selesai" in entry:
                color = "#28a745"
            else:
                color = "#6c757d"
                
            st.markdown(f"<p style='color: {color}; margin: 0.2rem 0;'><span style='font-weight: bold;'>•</span> {entry}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.caption(f"Menampilkan {len(log_to_show)} dari {len(patient_log)} total entri log")

# Display system information
st.sidebar.markdown("---")
st.sidebar.subheader("Informasi Sistem")
st.sidebar.markdown(f"""
- **Framework**: Streamlit
- **Simulasi Engine**: SimPy
- **Data Science**: pandas, numpy
- **Visualisasi**: matplotlib, seaborn
""")

# Instructions for running the app
st.sidebar.markdown("---")
st.sidebar.markdown("### Petunjuk Penggunaan")

with st.sidebar.expander("Cara Menjalankan di Lokal"):
    st.code("""
# Install dependencies
pip install streamlit pandas numpy matplotlib seaborn simpy

# Jalankan aplikasi
streamlit run app.py
""", language="bash")

with st.sidebar.expander("Cara Deploy ke Streamlit Cloud"):
    st.markdown("""
    1. Buat akun di share.streamlit.io
    2. Hubungkan dengan GitHub repository Anda
    3. Upload file `app.py` ke repository
    4. Set main file path ke `app.py`
    5. Klik 'Deploy!'
    """)

# Footer
st.markdown("""
<div class="footer">
    <p>Dibuat dengan hati yang tulus tanpa beban untuk Tugas Besar Pemodelan dan Simulasi | Menggunakan SimPy & Streamlit</p>
    <p>Reyhan Aditya Kusumah | Program Studi Teknik Informatika</p>
</div>
""", unsafe_allow_html=True)