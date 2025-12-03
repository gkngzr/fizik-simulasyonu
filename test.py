import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Fizik Lab: Atışlar", layout="wide")

st.title("🏹 Atış Hareketleri: Hem Oyna Hem Öğren")
st.markdown("Aşağıdaki parametreleri değiştir, hem grafiği hem de **hesaplama adımlarını** canlı izle.")
st.markdown("---")

# --- SOL MENÜ (AYARLAR) ---
st.sidebar.header("🎛️ Kontrol Paneli")
hiz = st.sidebar.slider("Fırlatma Hızı ($V_0$)", 10, 100, 50)
aci = st.sidebar.slider("Fırlatma Açısı ($\\theta$)", 0, 90, 45)
gezegen = st.sidebar.selectbox("Gezegen Seç", ["Dünya (g=9.81)", "Ay (g=1.62)", "Mars (g=3.71)"])

# Yerçekimi seçimi
if "Dünya" in gezegen: g = 9.81
elif "Ay" in gezegen: g = 1.62
else: g = 3.71

# --- HESAPLAMALAR ---
# 1. Radyan Dönüşümü (Bilgisayar dereceyi anlamaz)
aci_rad = np.radians(aci)

# 2. Hız Bileşenleri (Vektörleri Ayırma)
vx = hiz * np.cos(aci_rad) # Yatay Hız
vy = hiz * np.sin(aci_rad) # Dikey Hız

# 3. Uçuş Süresi (Havada kalma)
t_ucus = (2 * vy) / g

# 4. Menzil ve Yükseklik
menzil = vx * t_ucus
h_max = (vy**2) / (2 * g)

# 5. Grafik Verileri
t = np.linspace(0, t_ucus, num=100)
x_yol = vx * t
y_yol = vy * t - 0.5 * g * t**2

# --- EKRAN DÜZENİ (2 Sütun) ---
col_grafik, col_hesap = st.columns([1.5, 1]) # Grafik kısmı biraz daha geniş olsun

# --- SOL SÜTUN: GRAFİK ---
with col_grafik:
    st.subheader("👀 Simülasyon Ekranı")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_yol, y_yol, linewidth=3, color='#FF4B4B', label='Topun Yörüngesi')
    
    # Zemin ve Süslemeler
    ax.axhline(0, color='black', linewidth=2)
    ax.fill_between(x_yol, 0, y_yol, alpha=0.1, color='#FF4B4B') # Altını boya
    
    # Bilgi Kutusu (Grafik Üzerine)
    info_text = f"Menzil: {menzil:.1f} m\nYükseklik: {h_max:.1f} m\nSüre: {t_ucus:.1f} sn"
    ax.text(menzil/2, h_max/2, info_text, ha='center', bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'))
    
    ax.set_xlabel("Mesafe (m)")
    ax.set_ylabel("Yükseklik (m)")
    ax.set_title(f"V={hiz} m/s, Açı={aci}°, Yer={gezegen}")
    ax.grid(True, linestyle='--')
    ax.set_ylim(bottom=0)
    st.pyplot(fig)

# --- SAĞ SÜTUN: ADIM ADIM HESAPLAMA (ÖĞRETMEN MODU) ---
with col_hesap:
    st.subheader("🧠 İşin Matematiği (Nasıl Hesaplandı?)")
    
    # Adım 1: Hız Bileşenleri
    with st.expander("1. Adım: Hızı Parçalara Ayır", expanded=True):
        st.write("Topu çapraz attığın için hızı ikiye ayırmalıyız: İleri giden güç ($V_x$) ve yukarı çeken güç ($V_y$).")
        st.latex(r"V_x = V_0 \cdot \cos(\theta)")
        st.write(f"👉 $V_x = {hiz} \cdot \cos({aci}^\circ) = {vx:.2f} \, m/s$")
        st.markdown("---")
        st.latex(r"V_y = V_0 \cdot \sin(\theta)")
        st.write(f"👉 $V_y = {hiz} \cdot \sin({aci}^\circ) = {vy:.2f} \, m/s$")
    
    # Adım 2: Uçuş Süresi
    with st.expander("2. Adım: Top Ne Kadar Havada Kaldı?", expanded=False):
        st.write("Yerçekimi ($g$) topu aşağı çeker. Topun havada kalma süresini dikey hız ($V_y$) belirler.")
        st.latex(r"t_{uçuş} = \frac{2 \cdot V_y}{g}")
        st.write(f"👉 $t = (2 \cdot {vy:.2f}) / {g} = {t_ucus:.2f} \, saniye$")

    # Adım 3: Menzil
    with st.expander("3. Adım: Ne Kadar Uzağa Gitti?", expanded=False):
        st.write("Yatay hız ($V_x$) hiç değişmez (sürtünme yok). Bu yüzden yatay hız ile süreyi çarparız.")
        st.latex(r"Menzil (R) = V_x \cdot t_{uçuş}")
        st.write(f"👉 $R = {vx:.2f} \cdot {t_ucus:.2f} = \mathbf{{{menzil:.2f} \, metre}}$")

    st.success("İşte fizik bu kadar basit! Değerleri değiştir, hesaplamanın nasıl güncellendiğini gör.")