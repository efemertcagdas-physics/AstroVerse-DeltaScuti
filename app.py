import streamlit as st
import pandas as pd
import plotly.express as px
from core_engine import StellarEngine
from data_handler import DataHandler

st.set_page_config(page_title="ASTROVERSE | Delta Scuti Analiz Portalı", page_icon="🌌", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .reportview-container { background: #0d1117; }
    .big-title { font-size: 2.4rem; font-weight: 700; color: #58a6ff; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; color: #8b949e; margin-top: 5px; margin-bottom: 25px; }
    .metric-card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 18px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
    .metric-title { font-size: 0.85rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .metric-val { font-size: 1.8rem; font-weight: bold; color: #c9d1d9; }
    .metric-unit { font-size: 1rem; color: #58a6ff; font-weight: normal; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🌌 ASTROVERSE : DeepTech Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">TÜBİTAK 1001 Projesi & BİGG 1512 İçin Geliştirilmiş Bulut Tabanlı Delta Scuti Evrim Modelleme Arayüzü (MVP v1.1)</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🛸 Katalog Yöneticisi")
    data_source = st.radio("Veri Besleme Yöntemi:", ["Sentetik TÜBİTAK Test Kataloğu (25+3 Yıldız)", "Özel Katalog Yükle (.CSV / .XLSX)"], index=0)
    st.markdown("---")
    st.info("💡 **Astroinformatik Notu:** Bu panel arkada veri temizleme algoritmalarını şeffaf bir şekilde yönetir.")

df_raw = None
if data_source == "Sentetik TÜBİTAK Test Kataloğu (25+3 Yıldız)":
    df_raw = DataHandler.generate_synthetic_catalog(num_stars=25)
else:
    uploaded_file = st.file_uploader("Yıldız Kataloğunuzu Sürükleyin (.csv veya .xlsx)", type=['csv', 'xlsx'])
    if uploaded_file is not None:
        df_raw, status_msg = DataHandler.load_user_file(uploaded_file, uploaded_file.name)
        if df_raw is None: st.error(f"❌ {status_msg}")

if df_raw is not None:
    try:
        engine = StellarEngine(df_raw)
        results_df = engine.run_pipeline()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-card"><div class="metric-title">İncelenen Yıldız</div><div class="metric-val">{len(results_df)} <span class="metric-unit">Adet</span></div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-card"><div class="metric-title">Ort. Metal Bolluğu</div><div class="metric-val">{results_df["fe_h"].mean():+.2f} <span class="metric-unit">[Fe/H]</span></div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="metric-card"><div class="metric-title">Ortalama Yaş</div><div class="metric-val">{results_df["age_gyr"].mean():.2f} <span class="metric-unit">Gyr</span></div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="metric-card"><div class="metric-title">Elenen Hatalı Veri</div><div class="metric-val">{len(engine.rejected_data)} <span class="metric-unit">Adet</span></div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # YENİ SEKMELER
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Evrim Diyagramları", "🗄️ Detaylı Veri Tabanı", "🗑️ Veri Ayıklama (Şeffaflık Raporu)", "🚀 BİGG Özet Raporu"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                fig_hr = px.scatter(results_df, x="teff", y="log_g", color="age_gyr", size="age_err_gyr", hover_name="star_id", title="H-R Evrim Paneli", template="plotly_dark")
                fig_hr.update_xaxes(autorange="reversed")
                fig_hr.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_hr, use_container_width=True)
            with col2:
                fig_corr = px.scatter(results_df, x="fe_h", y="age_gyr", error_y="age_err_gyr", color="teff", hover_name="star_id", title="Metal Bolluğu Korelasyonu", template="plotly_dark")
                st.plotly_chart(fig_corr, use_container_width=True)

        with tab2:
            st.dataframe(results_df.style.background_gradient(subset=['age_gyr'], cmap='Blues'), use_container_width=True)

        # YENİ: ŞEFFAFLIK RAPORU SEKMESİ
        with tab3:
            st.subheader("🗑️ Elenen Yıldızlar ve Fiziksel Sebepleri")
            st.write("Aşağıdaki tablo, Delta Scuti kararsızlık kuşağı parametrelerine uymadığı veya eksik veriye sahip olduğu için veri tabanından silinen satırları gösterir.")
            if engine.rejected_data is not None and not engine.rejected_data.empty:
                st.dataframe(engine.rejected_data, use_container_width=True)
                st.info("📌 **Araştırmacı Notu:** Elenen verileri inceleyerek, teleskop sensörlerinizdeki veya katalog algoritmalarındaki sistematik hataları tespit edebilirsiniz.")
            else:
                st.success("Harika! Yüklenen katalogdaki tüm yıldızlar geçerli kriterlere uyuyor. Hiç veri elenmedi.")

        with tab4:
            st.subheader("💡 TÜBİTAK 1512 BİGG & Ticarileştirme Vizyonu")
            
            st.markdown("""
            Bu platform, astrofizik araştırmalarındaki veri işleme darboğazını çözmek üzere **"DeepTech SaaS"** (Derin Teknoloji Yazılım Hizmeti) modeline uygun olarak tasarlanmıştır.

            ### 🎯 Çözülen Problem
            Astronomların binlerce yıldız verisi üzerinde manuel olarak yaptığı fiziksel filtreleme, eksik veri ayıklama ve özellikle **Gauss hata yayılımı (error propagation)** gibi zorlu matematiksel hesaplamalar haftalar sürmektedir. Akademik süreçlerdeki bu manuel veri temizliği insan hatasına açık, yavaş ve araştırmacıların asıl bilime ayıracakları vakti çalan verimsiz bir süreç yaratır.

            ### 🚀 İnovasyon ve Çözüm (Ürün Vizyonu)
            Geliştirilen bu arayüz, araştırmacıların ham gözlem verilerini saniyeler içinde uluslararası hakemli dergi standartlarında yayınlanabilir hale getirir. Arka plandaki otonom algoritma:
            * Sadece hedef kararsızlık kuşağındaki yıldızları izole eder.
            * Veri temizleme sürecini şeffaf log kayıtlarıyla bilimsel denetime açar.
            * Yaş ve hata türevlerini analitik olarak hesaplayıp interaktif evrim diyagramları (H-R) çizer.

            ### 🌍 Ölçeklenebilirlik ve Hedef Pazar
            Projenin üniversite öğretim üyeleri gözetiminde test edilmesi, yazılımın bilimsel geçerliliğini (validation) sağlar. Bu MVP (Minimum Uygulanabilir Ürün), ilk etapta ulusal çaptaki projelerde kullanılmak üzere tasarlanmış olsa da, sistemin çekirdek hesaplama mimarisi sadece astrofizik değil, hata analizi gerektiren global çaptaki tüm laboratuvar süreçlerine uyarlanabilecek esnekliğe sahiptir.
            """)
            
            st.info("🚀 **Sonraki Adım:** Bu MVP'nin bulut sunuculara taşınarak canlıya alınması ve akademik işbirlikleri ile pazar doğrulamasının (market validation) yapılması planlanmaktadır.")

    except Exception as e:
        st.error(f"⚠️ Analiz motoru çalışırken bir hata oluştu: {str(e)}")