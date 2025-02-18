import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from fredapi import Fred
import os
from dotenv import load_dotenv

# Cargar clave de API desde .env
load_dotenv()
API_KEY = os.getenv('FRED_API_KEY')
fred = Fred(api_key=API_KEY)

# Descargar datos del S&P 500
def download_sp500():
    sp500 = yf.download('^GSPC', start='2015-01-01', interval='1mo')
    sp500['Monthly Return'] = sp500['Adj Close'].pct_change()
    return sp500

# Descargar datos macroeconómicos de FRED
def download_macro_data():
    unemployment = fred.get_series('UNRATE')
    inflation = fred.get_series('CPIAUCSL')
    interest_rate = fred.get_series('FEDFUNDS')

    macro = pd.DataFrame({
        'Unemployment Rate': unemployment,
        'Inflation (CPI)': inflation,
        'Interest Rate': interest_rate
    })
    macro.index = pd.to_datetime(macro.index)
    macro = macro.resample('M').last()
    macro['Inflation Rate'] = macro['Inflation (CPI)'].pct_change() * 100
    return macro

@st.cache_data
def get_combined_data():
    sp500 = download_sp500()
    macro = download_macro_data()
    combined = pd.merge(sp500[['Monthly Return']], macro, left_index=True, right_index=True, how='inner')
    return combined

def plot_data(data):
    st.subheader("Evolución del S&P 500 y Variables Macroeconómicas")
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(data.index, data['Monthly Return'], color='blue', label='S&P 500 Return')
    ax1.set_ylabel('Rendimiento Mensual del S&P 500', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    ax2 = ax1.twinx()
    ax2.plot(data.index, data['Unemployment Rate'], color='green', linestyle='--', label='Unemployment Rate')
    ax2.plot(data.index, data['Inflation Rate'], color='red', linestyle='--', label='Inflation Rate')
    ax2.plot(data.index, data['Interest Rate'], color='purple', linestyle='--', label='Interest Rate')
    ax2.set_ylabel('Tasas e Inflación (%)', color='black')

    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.85))
    st.pyplot(fig)

def main():
    st.title("Dashboard de Análisis del S&P 500 y Variables Macroeconómicas")

    data = get_combined_data()

    st.write("Vista previa de los datos:")
    st.write(data.tail())

    plot_data(data)

    st.subheader("Análisis de Correlación")
    correlation = data.corr()
    st.write(correlation)

    st.subheader("Insights Clave")
    st.write("- ¿Hay una correlación negativa entre el desempleo y el S&P 500?",
             "¿Cómo reaccionan los rendimientos ante una subida de tasas de interés?")

if __name__ == '__main__':
    main()
