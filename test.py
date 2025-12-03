import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import time
from PIL import Image
import requests
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Fizik Lab: Final", layout="wide")

st.title("🎓 Fizik Lab: Angry Birds Eğitim Modu")
st.markdown("Atışını yap, **Enerji Değişimini** incele ve soruları çöz!")
st.markdown("---")

# --- SESSION STATE (HAFIZA) ---
if 'prev_x' not in st.session_state: st.session_state.prev_x = None
if 'prev_y' not in st.session_state: st.session_state.prev_y = None

# --- SOL MENÜ ---
st.sidebar.header("🎛️ Deney Parametreleri")
hiz = st.sidebar.slider("Fırlatma Hızı ($V_0$)", 10, 150, 60)
aci = st.sidebar.slider("Fırlatma Açısı ($\\theta$)", 0, 90, 45)
gezegen = st.sidebar.selectbox("Gezegen Seç", ["Dünya (g=9.81)", "Ay (g=1.62)", "Mars (g=3.71)"])

if "Dünya" in gezegen: g = 9.81
elif "Ay" in gezegen: g = 1.62
else: g = 3.71

m = 1.0 # Kütle 1 kg

firlat = st.sidebar.button("🚀 DENEYİ BAŞLAT", type="primary")

# --- HESAPLAMALAR ---
aci_rad = np.radians(aci)
vx = hiz * np.cos(aci_rad)
vy = hiz * np.sin(aci_rad)
t_ucus = (2 * vy) / g
menzil = vx * t_ucus
h_max = (vy**2) / (2 * g)
E_mekanik = 0.5 * m * hiz**2 

# Grafik Verileri
x_yol = vx * np.linspace(0, t_ucus, num=100)
y_yol = vy * np.linspace(0, t_ucus, num=100) - 0.5 * g * np.linspace(0, t_ucus, num=100)**2

# ==========================================
# 🖼️ RESİM YÜKLEME ROBOTU (YENİ KISIM)
# ==========================================
bird_img = None
kaynak = "Yok"

# 1. Önce Masaüstündeki 'test.png'ye bak
try:
    bird_img = Image.open("test.png")
    kaynak = "Masaüstü (test.png)"
except FileNotFoundError:
    # 2. Bulamazsan İnternetten İndir
    try:
        url = "https://upload.wikimedia.org/wikipedia/en/9/9b/Red_Angry_Bird.png"
        response = requests.get(url, timeout=3)
        bird_img = Image.open(BytesIO(response.content))
        kaynak = "İnternet (Otomatik)"
    except:
        bird_img = None
        kaynak = "Kırmızı Top (Yedek)"

# --- EKRAN DÜZENİ ---
col_grafik, col_veri = st.columns([2.5, 1])

# --- SAĞ TARAF: BİLGİ KUTUSU ---
with col_veri:
    st.subheader("📊 Deney Verileri")
    st.metric("Menzil", f"{menzil:.1f} m")
    st.metric("Maks. Yükseklik", f"{h_max:.1f} m")
    st.info(f"Görsel Kaynağı: **{kaynak}**") # Hangi resmin kullanıldığını yazar
    st.caption("Aşağıdaki soruları çözmeyi unutma! 👇")

# --- GRAFİK FONKSİYONU ---
grafik_yeri = col_grafik.empty()

def plot_lab_mode(t_limit=None):
    fig, (ax_main, ax_energy) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={'width_ratios': [3, 1]})
    
    # --- 1. SOL GRAFİK: YÖRÜNGE ---
    ax_main.axhline(0, color='black', linewidth=3)
    
    # Hafızadaki Önceki Atış (Gri İz)
    if st.session_state.prev_x is not None:
        ax_main.plot(st.session_state.prev_x, st.session_state.prev_y, color='gray', linestyle='--', alpha=0.4, label="Önceki Deney")
        ax_main.legend(loc="upper right")

    # Mevcut Atışın Hedef Yolu (Silik)
    ax_main.plot(x_yol, y_yol, 'k:', alpha=0.2)
    
    kus_boyutu = max(menzil, 50) * 0.08 

    if t_limit is not None:
        x_now = vx * t_limit
        y_now = vy * t_limit - 0.5 * g * t_limit**2
        vy_now = vy - g * t_limit
        
        # Kırmızı Yol Çizimi
        t_past = np.linspace(0, t_limit, num=int(t_limit*40)+2)
        ax_main.plot(vx * t_past, vy * t_past - 0.5 * g * t_past**2, 'r-', linewidth=3)
        
        # GÖRSELİ KOY (TEST.PNG veya İNTERNET)
        if bird_img:
            ax_main.imshow(bird_img, extent=(x_now-kus_boyutu/2, x_now+kus_boyutu/2, y_now-kus_boyutu/2, y_now+kus_boyutu/2), zorder=10)
        else:
            ax_main.scatter(x_now, y_now, color='red', s=200, zorder=10, edgecolors='black')

        # VEKTÖRLER (OKLAR)
        v_scale = hiz * 2.0 # Ok boyutu ölçeği
        # Mavi Ok: Yatay Hız (Vx)
        ax_main.quiver(x_now, y_now, vx, 0, color='blue', scale=v_scale, width=0.015, label='$V_x$')
        # Yeşil Ok: Dikey Hız (Vy)
        ax_main.quiver(x_now, y_now, 0, vy_now, color='green', scale=v_scale, width=0.015, label='$V_y$')

        # Enerji Değerleri
        v_total = np.sqrt(vx**2 + vy_now**2)
        ke_now = 0.5 * m * v_total**2
        pe_now = m * g * y_now
    else:
        # Başlangıç
        x_now, y_now = 0, 0
        ke_now = 0.5 * m * hiz**2
        pe_now = 0
        if bird_img:
            ax_main.imshow(bird_img, extent=(-kus_boyutu/2, kus_boyutu/2, 0, kus_boyutu), zorder=10)

    # Eksen Ayarları
    ax_main.set_xlim(-kus_boyutu, max(menzil * 1.2, 50))
    ax_main.set_ylim(-kus_boyutu, max(h_max * 1.5, 30))
    ax_main.grid(True, linestyle='--', alpha=0.5)
    ax_main.set_title(f"Canlı Simülasyon ({t_limit:.2f}s)" if t_limit else "Deney Hazır")
    ax_main.set_xlabel("Mesafe (m)")
    ax_main.set_ylabel("Yükseklik (m)")

    # --- 2. SAĞ GRAFİK: ENERJİ BARLARI ---
    ax_energy.bar(['KE', 'PE'], [ke_now, pe_now], color=['#1f77b4', '#ff7f0e'])
    ax_energy.axhline(E_mekanik, color='green', linestyle='--', linewidth=2, label="Toplam")
    ax_energy.set_ylim(0, E_mekanik * 1.2)
    ax_energy.set_title("Enerji (Joule)")
    
    # Barların içine değer yaz
    ax_energy.text(0, ke_now, f"{int(ke_now)}", ha='center', va='bottom', fontweight='bold', color='black')
    ax_energy.text(1, pe_now, f"{int(pe_now)}", ha='center', va='bottom', fontweight='bold', color='black')
    ax_energy.set_yticks([]) # Yandaki sayıları temizle
    
    plt.tight_layout()
    return fig

# --- ANİMASYON OYNATICI ---
if firlat:
    # 25 Karelik Hızlı Animasyon
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
# 📚 FİZİK DEFTERİ & QUIZ
# ==========================================
st.write("---")
st.header("📚 Fizik Defteri: Enerji ve Hız")

col_f1, col_f2, col_q = st.columns([1, 1, 1.2])

with col_f1:
    st.subheader("🔵 Kinetik Enerji (Hareket)")
    st.latex(r"KE = \frac{1}{2} m V^2")
    st.caption("Mavi sütun neden yukarı çıkarken azalıyor? Çünkü hız azalıyor!")
    st.code(f"KE = 0.5 * {m} * {hiz}^2 = {0.5*m*hiz**2:.0f} J")

with col_f2:
    st.subheader("🟠 Potansiyel Enerji (Yükseklik)")
    st.latex(r"PE = m g h")
    st.caption("Turuncu sütun tepe noktasında en yüksektir.")
    st.code(f"PE_max = {m} * {g} * {h_max:.1f} = {m*g*h_max:.0f} J")

with col_q:
    st.error("📝 SIRA SENDE")
    st.write(f"Soru: Tepe noktasında dikey hız (yeşil ok) ne olur?")
    
    cevap = st.radio("Cevabını Seç:", ["Maksimum olur", "Sıfır olur", "Değişmez"])
    
    if st.button("Kontrol Et"):
        if cevap == "Sıfır olur":
            st.balloons()
            st.success("DOĞRU! 🎉 Tepe noktasında cisim bir anlığına dikeyde durur.")
        else:
            st.warning("Yanlış. Tepe noktasında cisim daha fazla yükselemez, yani dikey hızı biter.")
