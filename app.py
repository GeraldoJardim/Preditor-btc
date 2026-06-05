import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="Preditor de Ciclos do Bitcoin", layout="wide")

st.title("📊 Preditor de Ciclos do Bitcoin")
st.write("Mapeamento de ondas temporais por Fourier — escala logarítmica.")

# ── Controles ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
with col1:
    dias_previsao = st.slider("Dias para prever:", min_value=30, max_value=120, value=60, step=30)
with col2:
    harmonicos = st.slider("Quantidade de Ciclos:", min_value=5, max_value=60, value=20, step=5)

st.caption(
    "⚠️ Modelo exploratório baseado em padrões históricos de frequência. "
    "Não constitui recomendação financeira. A banda cinza representa ±1σ do erro histórico."
)

# ── Lógica principal ───────────────────────────────────────────────────────────
try:
    dados = yf.download('BTC-USD', start='2022-01-01', progress=False)
    y = dados['Close'].values.flatten()
    x = np.arange(len(y))

    # CORREÇÃO 1: trabalhar em escala logarítmica (crescimento exponencial do BTC)
    log_y = np.log(y)

    # CORREÇÃO 2: tendência linear no espaço log (equivale a tendência exponencial no preço)
    tendencia_coefs = np.polyfit(x, log_y, 1)
    log_y_detrended = log_y - np.polyval(tendencia_coefs, x)

    # FFT no resíduo logarítmico
    fft_res = np.fft.fft(log_y_detrended)
    freqs = np.fft.fftfreq(len(log_y_detrended))

    # CORREÇÃO 3: filtrar frequências de ruído diário (só ciclos com período >= 7 dias)
    f_abs = np.abs(fft_res)
    indices = np.argsort(f_abs)[::-1]
    indices_ciclos = [
        i for i in indices
        if 0 < freqs[i] < (1 / 7)  # exclui ruído de alta frequência
    ][:harmonicos]

    # Reconstrução das ondas
    x_futuro = np.arange(len(y) + dias_previsao)
    ondas_reconstruidas = np.zeros(len(x_futuro))

    for i in indices_ciclos:
        amplitude = f_abs[i] / len(y)
        fase = np.angle(fft_res[i])
        # CORREÇÃO 4: removido o `* 2` arbitrário
        ondas_reconstruidas += amplitude * np.cos(2 * np.pi * freqs[i] * x_futuro + fase)

    # Projeção no espaço log, depois revertida para preço
    log_projecao = ondas_reconstruidas + np.polyval(tendencia_coefs, x_futuro)
    projecao_final = np.exp(log_projecao)

    # CORREÇÃO 5: banda de incerteza ±1σ calculada sobre o erro histórico
    residuo_historico = log_y - (ondas_reconstruidas[:len(y)] + np.polyval(tendencia_coefs, x))
    sigma = np.std(residuo_historico)

    banda_superior = np.exp(log_projecao + sigma)
    banda_inferior = np.exp(log_projecao - sigma)

    # ── Preço atual e alvo ────────────────────────────────────────────────────
    preco_atual = float(y[-1])
    preco_alvo   = float(projecao_final[-1])
    variacao_pct = (preco_alvo / preco_atual - 1) * 100

    m1, m2, m3 = st.columns(3)
    m1.metric("Preço Atual (BTC)", f"${preco_atual:,.0f}")
    m2.metric(f"Projeção em {dias_previsao} dias", f"${preco_alvo:,.0f}", f"{variacao_pct:+.1f}%")
    m3.metric("Ciclos usados", str(len(indices_ciclos)))

    # ── Gráfico ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor('#111317')
    ax.set_facecolor('#171a21')
    ax.tick_params(colors='white')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'${v:,.0f}'))
    ax.grid(True, color='#2c323f', alpha=0.5)

    # Janela visível
    janela_inicio = max(0, len(y) - 300)
    vis_x = slice(janela_inicio, len(y) + dias_previsao)

    ax.plot(x, y, label="Preço Real", color='#00ffcc', alpha=0.6, linewidth=1)
    ax.plot(
        x_futuro, projecao_final,
        label="Previsão de Ciclos", color='#9b5de5', linestyle='--', linewidth=2
    )
    ax.fill_between(
        x_futuro, banda_inferior, banda_superior,
        color='#9b5de5', alpha=0.15, label='Banda ±1σ'
    )
    ax.axvline(x=len(y), color='#ff4757', linestyle=':', linewidth=2, label='Hoje')

    ax.set_xlim(janela_inicio, len(y) + dias_previsao)
    precos_janela = y[janela_inicio:]
    ax.set_ylim(
        min(precos_janela) * 0.85,
        max(max(precos_janela), banda_superior[-1]) * 1.1
    )

    ax.legend(facecolor='#171a21', labelcolor='white', loc='upper left')
    ax.set_title(
        f"BTC-USD — FFT (log) | {len(indices_ciclos)} ciclos | {dias_previsao}d à frente",
        color='white', fontsize=11
    )

    st.pyplot(fig)
    plt.close(fig)

    # ── Aviso de confiança ────────────────────────────────────────────────────
    if abs(variacao_pct) > 50:
        st.warning(
            f"⚠️ A variação projetada ({variacao_pct:+.1f}%) é muito alta. "
            "Reduza os dias de previsão ou o número de ciclos para resultados mais conservadores."
        )
    else:
        st.success("Gráfico gerado com sucesso!")

except Exception as e:
    st.error(f"Erro ao buscar dados: {e}")
    st.info("Verifique sua conexão ou tente novamente em alguns instantes.")
