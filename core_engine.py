import numpy as np
import pandas as pd

class StellarEngine:
    """
    Delta Scuti yıldızları için astrofiziksel hesaplamaları, veri temizlemeyi
    ve hata yayılımını gerçekleştiren çekirdek SaaS motoru.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.raw_data = df.copy()
        self.cleaned_data = None
        self.rejected_data = None  # YENİ: Çöpe atılan verilerin kaydı
        self.results = None

    def validate_and_clean(self) -> pd.DataFrame:
        df = self.raw_data.copy()
        df.columns = [col.strip().lower() for col in df.columns]
        
        required_cols = ['star_id', 'teff', 'log_g', 'fe_h']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Eksik zorunlu veri kolonu: {col}")

        # Sayısal formata çevir, okunamayanları NaN yap
        numeric_cols = ['teff', 'log_g', 'fe_h']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # YENİ: Elenen verileri ve sebeplerini tespit et
        rejection_log = []
        
        for index, row in df.iterrows():
            star_id = row['star_id'] if pd.notna(row['star_id']) else f"Satır {index}"
            
            # 1. Eksik Veri Kontrolü
            if pd.isna(row['teff']) or pd.isna(row['log_g']) or pd.isna(row['fe_h']):
                rejection_log.append({'Yıldız_ID': star_id, 'Eleme Sebebi': 'Eksik veya Okunamayan Veri (NaN)'})
                continue
                
            # 2. Fiziksel Sınır Kontrolleri (Astrofizik Filtresi)
            reasons = []
            if not (6000 <= row['teff'] <= 9000):
                reasons.append(f"Teff Sınır Dışı ({row['teff']} K)")
            if not (3.0 <= row['log_g'] <= 4.6):
                reasons.append(f"log_g Sınır Dışı ({row['log_g']})")
            if not (-1.5 <= row['fe_h'] <= 0.8):
                reasons.append(f"Fe/H Sınır Dışı ({row['fe_h']})")
                
            if reasons:
                rejection_log.append({'Yıldız_ID': star_id, 'Eleme Sebebi': " | ".join(reasons)})

        self.rejected_data = pd.DataFrame(rejection_log)

        # Temiz veriyi filtrele
        df_clean = df.dropna(subset=numeric_cols)
        mask = (
            (df_clean['teff'] >= 6000) & (df_clean['teff'] <= 9000) &
            (df_clean['log_g'] >= 3.0) & (df_clean['log_g'] <= 4.6) &
            (df_clean['fe_h'] >= -1.5) & (df_clean['fe_h'] <= 0.8)
        )
        self.cleaned_data = df_clean[mask].reset_index(drop=True)
        return self.cleaned_data

    def run_pipeline(self) -> pd.DataFrame:
        if self.cleaned_data is None:
            self.validate_and_clean()
            
        df = self.cleaned_data.copy()
        
        # 1. Yaş Hesaplaması
        teff_factor = (8000.0 - df['teff']) / 1000.0
        logg_factor = (4.2 - df['log_g']) * 2.5
        feh_factor = df['fe_h'] * 0.7
        
        df['age_gyr'] = np.clip(1.2 + teff_factor + logg_factor + feh_factor, 0.1, 3.0)
        
        # 2. Gauss Hata Yayılımı
        if 'teff_err' not in df.columns: df['teff_err'] = df['teff'] * 0.02
        if 'log_g_err' not in df.columns: df['log_g_err'] = 0.05
        if 'fe_h_err' not in df.columns: df['fe_h_err'] = 0.08
        
        d_age_d_teff = -1.0 / 1000.0
        d_age_d_logg = -2.5
        d_age_d_feh = 0.7
        
        df['age_err_gyr'] = np.sqrt(
            (d_age_d_teff * df['teff_err'])**2 +
            (d_age_d_logg * df['log_g_err'])**2 +
            (d_age_d_feh * df['fe_h_err'])**2
        )
        
        df['age_gyr'] = df['age_gyr'].round(2)
        df['age_err_gyr'] = df['age_err_gyr'].round(2)
        
        self.results = df
        return self.results