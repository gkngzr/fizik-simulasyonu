import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image
import os

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Fizik Lab: Eğitim Modu", layout="wide")

st.title("🎓 Fizik Lab: Enerji ve Hesaplamalar")
st.markdown("Atışını yap, enerjini analiz et ve **soruları çözerek kendini test et!**")
st.markdown("---")

# --- SESSION STATE (HAFIZA) ---
if 'prev_x' not in st.session_state: st.session_state.prev_x = None
if 'prev_y' not in st.session_state: st.session_state.prev_y = None

# --- SOL MENÜ ---
st.sidebar.header("🎛️ Deney Parametreleri")
hiz = st.sidebar.slider("Fırlatma Hızı ($V_0$)", 10, 150, 50)
aci = st.sidebar.slider("Fırlatma Açısı ($\\theta$)", 0, 90, 60)
gezegen = st.sidebar.selectbox("Gezegen Seç", ["Dünya (g=9.81)", "Ay (g=1.62)", "Mars (g=3.71)"])

if "Dünya" in gezegen: g = 9.81
elif "Ay" in gezegen: g = 1.62
else: g = 3.71

m = 1.0 # Kütle 1 kg varsayıyoruz (Hesap kolaylığı için)

firlat = st.sidebar.button("🚀 DENEYİ BAŞLAT", type="primary")

# --- HESAPLAMALAR ---
aci_rad = np.radians(aci)
vx = hiz * np.cos(aci_rad)
vy = hiz * np.sin(aci_rad)
t_ucus = (2 * vy) / g
menzil = vx * t_ucus
h_max = (vy**2) / (2 * g)
E_mekanik = 0.5 * m * hiz**2 # Başlangıç toplam enerji

# Grafik Verileri
x_yol = vx * np.linspace(0, t_ucus, num=100)
y_yol = vy * np.linspace(0, t_ucus, num=100) - 0.5 * g * np.linspace(0, t_ucus, num=100)**2

# --- RESİM YÜKLEME ---
try:
    bird_img = Image.open("test.png")
except FileNotFoundError:
    bird_img = None

# --- EKRAN DÜZENİ ---
col_grafik, col_veri = st.columns([2.5, 1])

# --- SAĞ TARAF: ÖZET BİLGİ ---
with col_veri:
    st.subheader("📊 Hızlı Bakış")
    st.metric("Menzil", f"{menzil:.1f} m")
    st.metric("Maksimum Yükseklik", f"{h_max:.1f} m")
    st.info(f"Cisim Kütlesi: **{m} kg**")
    st.write("---")
    st.caption("Aşağıdaki alıştırmaları çözmeyi unutma! 👇")

# --- GRAFİK FONKSİYONU (V9 ile Aynı - Vektörlü) ---
grafik_yeri = col_grafik.empty()

def plot_lab_mode(t_limit=None):
    fig, (ax_main, ax_energy) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [3, 1]})
    
    # 1. YÖRÜNGE GRAFİĞİ
    ax_main.axhline(0, color='black', linewidth=3)
    if st.session_state.prev_x is not None:
        ax_main.plot(st.session_state.prev_x, st.session_state.prev_y, color='gray', linestyle='--', alpha=0.4, label="Önceki")
        ax_main.legend()

    ax_main.plot(x_yol, y_yol, 'k:', alpha=0.2)
    kus_boyutu = max(menzil, 50) * 0.08 

    if t_limit is not None:
        x_now = vx * t_limit
        y_now = vy * t_limit - 0.5 * g * t_limit**2
        vy_now = vy - g * t_limit
        
        # Kırmızı Yol
        t_past = np.linspace(0, t_limit, num=int(t_limit*40)+2)
        ax_main.plot(vx * t_past, vy * t_past - 0.5 * g * t_past**2, 'r-', linewidth=3)
        
        # Görsel
        if bird_img:
            ax_main.imshow(bird_img, extent=(x_now-kus_boyutu/2, x_now+kus_boyutu/2, y_now-kus_boyutu/2, y_now+kus_boyutu/2), zorder=10)
        else:
            ax_main.scatter(x_now, y_now, color='red', s=200, zorder=10, edgecolors='black')

        # Enerji Hesabı (Anlık)
        v_total = np.sqrt(vx**2 + vy_now**2)
        ke_now = 0.5 * m * v_total**2
        pe_now = m * g * y_now
    else:
        x_now, y_now = 0, 0
        ke_now = 0.5 * m * hiz**2
        pe_now = 0
        if bird_img:
            ax_main.imshow(bird_img, extent=(-kus_boyutu/2, kus_boyutu/2, 0, kus_boyutu), zorder=10)

    ax_main.set_xlim(-kus_boyutu, max(menzil * 1.2, 50))
    ax_main.set_ylim(-kus_boyutu, max(h_max * 1.5, 30))
    ax_main.grid(True, linestyle='--', alpha=0.5)
    ax_main.set_title("Canlı Simülasyon")

    # 2. ENERJİ GRAFİĞİ
    ax_energy.bar(['KE', 'PE'], [ke_now, pe_now], color=['#1f77b4', '#ff7f0e'])
    ax_energy.axhline(E_mekanik, color='green', linestyle='--', linewidth=2, label="Toplam")
    ax_energy.set_ylim(0, E_mekanik * 1.2)
    ax_energy.set_title("Canlı Enerji (Joule)")
    ax_energy.text(0, ke_now, f"{int(ke_now)}", ha='center', va='bottom', fontweight='bold')
    ax_energy.text(1, pe_now, f"{int(pe_now)}", ha='center', va='bottom', fontweight='bold')
    ax_energy.set_yticks([])
    
    plt.tight_layout()
    return fig

# --- ANİMASYON OYNATICI ---
if firlat:
    frame_steps = np.linspace(0, t_ucus, num=25)
    for t_step in frame_steps:
        fig = plot_lab_mode(t_step)
        grafik_yeri.pyplot(fig)
        time.sleep(0.01)
        plt.close(fig)
    
    grafik_yeri.pyplot(plot_lab_mode(t_ucus))
    st.session_state.prev_x = x_yol
    st.session_state.prev_y = y_yol
else:
    grafik_yeri.pyplot(plot_lab_mode(None))

# ==========================================
# 🧠 EĞİTİM BÖLÜMÜ (YENİ EKLENEN KISIM)
# ==========================================
st.write("---")
st.header("📚 Fizik Defteri: Enerji Nasıl Hesaplanır?")

col_formul1, col_formul2, col_soru = st.columns([1, 1, 1.2])

with col_formul1:
    st.subheader("🔵 Kinetik Enerji (Hız)")
    st.write("Cismin hareketinden kaynaklanan enerjidir.")
    st.latex(r"KE = \frac{1}{2} \cdot m \cdot V^2")
    st.markdown("**Başlangıç Anı İçin Hesap:**")
    st.code(f"""
KE = 0.5 * {m} * ({hiz})^2
KE = {0.5 * m * hiz**2:.1f} Joule
    """)
    st.info("Hız arttıkça karesi oranında artar!")

with col_formul2:
    st.subheader("🟠 Potansiyel Enerji (Yükseklik)")
    st.write("Cismin yüksekliğinden kaynaklanan enerjidir.")
    st.latex(r"PE = m \cdot g \cdot h")
    st.markdown("**Tepe Noktası İçin Hesap:**")
    st.code(f"""
PE = {m} * {g} * {h_max:.1f}
PE = {m * g * h_max:.1f} Joule
    """)
    st.info("En tepede PE maksimumdur.")

# --- İNTERAKTİF SORU KISMI ---
with col_soru:
    st.error("📝 SIRA SENDE: Kendini Dene!")
    
    # Soruyu dinamik olarak üretiyoruz
    st.write(f"Soru: Cisim **{hiz} m/s** hızla fırlatıldı. Sence tepe noktasında **Kinetik Enerjisi (KE)** kaç Joule olur?")
    
    # Doğru Cevap: Tepe noktasında sadece Yatay Hız (Vx) vardır. Vy sıfırdır.
    # KE_tepe = 0.5 * m * (Vx)^2
    dogru_cevap = 0.5 * m * vx**2
    
    kullanici_cevabi = st.number_input("Cevabını buraya yaz (Joule):", step=1.0)
    
    if st.button("Cevabı Kontrol Et"):
        # Küçük hesaplama farklarını tolere et (0.5 farka kadar)
        if abs(kullanici_cevabi - dogru_cevap) <= 1.0:
            st.balloons()
            st.success(f"BRAVO! 🎉 Doğru bildin. Tepe noktasında sadece yatay hız ({vx:.1f} m/s) kaldığı için KE sıfırlanmaz, azalır.")
        else:
            st.warning("Maalesef yanlış. 😔 İpucu: Tepe noktasında cisim durmaz, yatayda gitmeye devam eder!")
            with st.expander("Çözümü Gör"):
                st.write(f"Tepe noktasında dikey hız 0 olur ama yatay hız ($V_x$) değişmez.")
                st.write(f"1. Yatay Hız ($V_x$) = {vx:.2f} m/s")
                st.write(f"2. Formül: $KE = 0.5 \\cdot m \\cdot (V_x)^2$")
                st.write(f"3. Hesap: $0.5 \\cdot 1 \\cdot {vx:.2f}^2 = {dogru_cevap:.1f}$ Joule")
