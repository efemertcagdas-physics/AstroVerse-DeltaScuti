import pandas as pd
import numpy as np
import io
from typing import Tuple, Optional

class DataHandler:
    @staticmethod
    def load_user_file(file_buffer, file_name: str) -> Tuple[Optional[pd.DataFrame], str]:
        try:
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_buffer, sep=None, engine='python')
            elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                df = pd.read_excel(file_buffer)
            else:
                return None, "Desteklenmeyen dosya formatı. Lütfen .csv veya .xlsx yükleyin."
                
            df = df.dropna(how='all').dropna(axis=1, how='all')
            if df.empty: return None, "Yüklenen dosya boş veya okunamadı."
            return df, "Başarılı"
        except Exception as e:
            return None, f"Dosya okuma hatası: {str(e)}"

    @staticmethod
    def generate_synthetic_catalog(num_stars: int = 25) -> pd.DataFrame:
        np.random.seed(42)
        prefixes = ['KIC-', 'TIC-', 'HD-', 'CoRoT-']
        star_ids = [f"{np.random.choice(prefixes)}{np.random.randint(100000, 999999)}" for _ in range(num_stars)]
        
        teff = np.random.normal(loc=7400, scale=450, size=num_stars).round(1)
        log_g = np.random.normal(loc=3.85, scale=0.15, size=num_stars).round(2)
        fe_h = np.random.normal(loc=-0.1, scale=0.25, size=num_stars).round(2)
        main_freq = np.random.uniform(6.0, 28.0, size=num_stars).round(2)
        
        df = pd.DataFrame({
            'star_id': star_ids, 'teff': teff, 'teff_err': teff * 0.02,
            'log_g': log_g, 'log_g_err': 0.05, 'fe_h': fe_h,
            'fe_h_err': 0.08, 'main_freq_cd': main_freq
        })
        
        # YENİ: Raporu test etmek için kasıtlı olarak eklenmiş hatalı veriler
        bad_data = pd.DataFrame({
            'star_id': ['B-Tipi Dev (Hatalı)', 'Eksik Sensör Verisi', 'Soğuk Cüce (Hatalı)'],
            'teff': [18000, np.nan, 4200],  # 18000 çok yüksek, 4200 çok düşük
            'teff_err': [300, np.nan, 50],
            'log_g': [2.1, 4.0, 4.9],       # 2.1 çok düşük, 4.9 çok yüksek
            'log_g_err': [0.1, 0.05, 0.02],
            'fe_h': [0.1, 0.0, -2.5],       # -2.5 sınır dışı
            'fe_h_err': [0.05, 0.08, 0.1],
            'main_freq_cd': [2.0, 15.0, 4.0]
        })
        
        return pd.concat([df, bad_data], ignore_index=True)

    @staticmethod
    def prepare_export_buffer(df: pd.DataFrame, file_type: str = "csv") -> bytes:
        if file_type == "csv": return df.to_csv(index=False).encode('utf-8')
        elif file_type == "excel":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='AstroVerse_Results')
            return output.getvalue()
        return b""