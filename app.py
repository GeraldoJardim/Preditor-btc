import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

st.title("📊 Preditor de Ciclos do Bitcoin")
st.write("Mapeamento de ondas temporais por Fourier.")

dias_previsao = st.slider("Dias para prever:", min_value=30, max_value=120, value=90, step=30)
harmonicos = st.slider("Quantidade de Ciclos:", min_value=20, max_value=140, value=120, step=10)

try:
    dados = yf.download('BTC-USD', start='2022-01-01')
    y = dados['Close'].values.flatten()
    x = np.arange(len(y))

    tendencia_linear = np.polyfit(x, y, 1)
    y_detrended = y - np.polyval(tendencia_linear, x)

    fft_res = np.fft.fft(y_detrended)
    freqs = np.fft.fftfreq(len(y_detrended))

    f_abs = np.abs(fft_res)
    indices = np.argsort(f_abs)[::-1]
    indices_ciclos = [i for i in indices if freqs[i] > 0][:harmonicos]

    x_futuro = np.arange(len(y) + dias_previsao)
    ondas_reconstruidas = np.zeros(len(x_futuro))

    for i in indices_ciclos:
        amplitude = f_abs[i] / len(y)
        fase = np.angle(fft_res[i])
        ondas_reconstruidas += amplitude * np.cos(2 * np.pi * freqs[i] * x_futuro + fase)

    ondas_reconstruidas *= 2
    projecao_final = ondas_reconstruidas + np.polyval(tendencia_linear, x_futuro)

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#111317')
    ax.set_facecolor('#171a21')
    ax.tick_params(colors='white')
    ax.grid(True, color='#2c323f', alpha=0.5)

    ax.plot(x, y, label="Preço Real", color='#00ffcc', alpha=0.5)
    ax.plot(x_futuro, projecao_final, label="Previsão de Ciclos", color='#9b5de5', linestyle='--', linewidth=2)
    ax.axvline(x=len(y), color='#ff4757', linestyle=':', linewidth=2, label='Momento Atual')

    ax.set_xbound(len(y) - 250, len(y) + dias_previsao)
    precos_recentes = y[-250:]
    ax.set_ybound(min(precos_recentes) * 0.85, max(precos_recentes) * 1.2)

    ax.legend(facecolor='#171a21', labelcolor='white', loc='upper left')
    st.pyplot(fig)
    st.success("Gráfico gerado com sucesso!")

except Exception as e:
    st.info("Buscando cotações atualizadas... Aguarde.")
