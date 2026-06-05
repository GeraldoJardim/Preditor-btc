import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

st.set_page_config(page_title="Preditor de Ciclos — Crypto", layout="wide")

# ── Lista das 100 principais criptos (ticker yfinance : nome) ──────────────────
TOP_100 = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "USDT-USD": "Tether",
    "BNB-USD": "BNB",
    "SOL-USD": "Solana",
    "XRP-USD": "XRP",
    "USDC-USD": "USD Coin",
    "DOGE-USD": "Dogecoin",
    "ADA-USD": "Cardano",
    "AVAX-USD": "Avalanche",
    "TRX-USD": "TRON",
    "SHIB-USD": "Shiba Inu",
    "DOT-USD": "Polkadot",
    "LINK-USD": "Chainlink",
    "TON11419-USD": "Toncoin",
    "MATIC-USD": "Polygon",
    "LTC-USD": "Litecoin",
    "BCH-USD": "Bitcoin Cash",
    "UNI7083-USD": "Uniswap",
    "NEAR-USD": "NEAR Protocol",
    "ICP-USD": "Internet Computer",
    "DAI-USD": "Dai",
    "APT21794-USD": "Aptos",
    "ETC-USD": "Ethereum Classic",
    "XLM-USD": "Stellar",
    "OKB-USD": "OKB",
    "STX4847-USD": "Stacks",
    "ATOM-USD": "Cosmos",
    "FIL-USD": "Filecoin",
    "HBAR-USD": "Hedera",
    "ARB11841-USD": "Arbitrum",
    "VET-USD": "VeChain",
    "MKR-USD": "Maker",
    "OP-USD": "Optimism",
    "GRT6719-USD": "The Graph",
    "AAVE-USD": "Aave",
    "ALGO-USD": "Algorand",
    "EGLD-USD": "MultiversX",
    "XMR-USD": "Monero",
    "THETA-USD": "Theta Network",
    "SAND-USD": "The Sandbox",
    "AXS-USD": "Axie Infinity",
    "EOS-USD": "EOS",
    "XTZ-USD": "Tezos",
    "MANA-USD": "Decentraland",
    "CHZ-USD": "Chiliz",
    "FLOW-USD": "Flow",
    "ENJ-USD": "Enjin Coin",
    "ZEC-USD": "Zcash",
    "CAKE-USD": "PancakeSwap",
    "DASH-USD": "Dash",
    "NEO-USD": "NEO",
    "WAVES-USD": "Waves",
    "BAT-USD": "Basic Attention Token",
    "HOT-USD": "Holo",
    "ZIL-USD": "Zilliqa",
    "ENS-USD": "Ethereum Name Service",
    "1INCH-USD": "1inch",
    "COMP-USD": "Compound",
    "YFI-USD": "yearn.finance",
    "SUSHI-USD": "SushiSwap",
    "CRV-USD": "Curve DAO",
    "SNX-USD": "Synthetix",
    "REN-USD": "Ren",
    "LRC-USD": "Loopring",
    "BAL-USD": "Balancer",
    "UMA-USD": "UMA",
    "OCEAN-USD": "Ocean Protocol",
    "FET-USD": "Fetch.ai",
    "AGIX-USD": "SingularityNET",
    "INJ-USD": "Injective",
    "SUI20947-USD": "Sui",
    "SEI-USD": "Sei",
    "TIA22861-USD": "Celestia",
    "PYTH-USD": "Pyth Network",
    "JTO-USD": "Jito",
    "WIF-USD": "dogwifhat",
    "BONK-USD": "Bonk",
    "PEPE24478-USD": "Pepe",
    "FLOKI-USD": "FLOKI",
    "IMX10603-USD": "Immutable X",
    "BLUR-USD": "Blur",
    "CFX-USD": "Conflux",
    "LUNC-USD": "Terra Classic",
    "KAVA-USD": "Kava",
    "ROSE-USD": "Oasis Network",
    "ONE-USD": "Harmony",
    "SKL-USD": "SKALE",
    "ICX-USD": "ICON",
    "ZRX-USD": "0x Protocol",
    "STORJ-USD": "Storj",
    "RVN-USD": "Ravencoin",
    "SC-USD": "Siacoin",
    "DGB-USD": "DigiByte",
    "XDC-USD": "XDC Network",
    "IOTA-USD": "IOTA",
    "NANO-USD": "Nano",
    "QNT-USD": "Quant",
    "FTM-USD": "Fantom",
}

# ── Interface ──────────────────────────────────────────────────────────────────
st.title("📊 Preditor de Ciclos — Top 100 Criptos")
st.write("Mapeamento de ondas temporais por Fourier • Escala logarítmica")

# Busca por texto
busca = st.text_input("🔍 Buscar cripto por nome ou símbolo:", placeholder="Ex: Bitcoin, ETH, Solana...")

# Filtrar lista pelo campo de busca
opcoes_filtradas = {
    ticker: nome for ticker, nome in TOP_100.items()
    if busca.lower() in nome.lower() or busca.lower() in ticker.lower()
} if busca else TOP_100

# Dropdown com resultado filtrado
labels = [f"{nome} ({ticker.replace('-USD','')})" for ticker, nome in opcoes_filtradas.items()]
tickers_lista = list(opcoes_filtradas.keys())

if not labels:
    st.warning("Nenhuma cripto encontrada com esse nome. Tente outro termo.")
    st.stop()

escolha_label = st.selectbox("📌 Selecione a criptomoeda:", labels)
idx = labels.index(escolha_label)
ticker_escolhido = tickers_lista[idx]
nome_escolhido = opcoes_filtradas[ticker_escolhido]

st.divider()

# Controles
col1, col2 = st.columns(2)
with col1:
    dias_previsao = st.slider("Dias para prever:", min_value=30, max_value=120, value=60, step=30)
with col2:
    harmonicos = st.slider("Quantidade de Ciclos:", min_value=5, max_value=60, value=20, step=5)

st.caption("⚠️ Modelo exploratório. Não constitui recomendação financeira. Banda cinza = ±1σ do erro histórico.")

# ── Download e cálculo ─────────────────────────────────────────────────────────
try:
    with st.spinner(f"Buscando dados de {nome_escolhido}..."):
        dados = yf.download(ticker_escolhido, start='2022-01-01', progress=False)

    if dados.empty or len(dados) < 60:
        st.error(f"Dados insuficientes para {nome_escolhido}. Tente outra cripto.")
        st.stop()

    y       = dados['Close'].values.flatten()
    vol     = dados['Volume'].values.flatten()
    x       = np.arange(len(y))

    # Info de mercado via yfinance
    info = {}
    try:
        ticker_obj = yf.Ticker(ticker_escolhido)
        info = ticker_obj.fast_info
    except Exception:
        pass

    preco_atual   = float(y[-1])
    preco_ontem   = float(y[-2]) if len(y) > 1 else preco_atual
    variacao_24h  = (preco_atual / preco_ontem - 1) * 100
    vol_medio     = float(np.mean(vol[-30:]))

    market_cap = None
    try:
        market_cap = float(info.market_cap)
    except Exception:
        pass

    # FFT em escala log
    log_y             = np.log(y)
    tendencia_coefs   = np.polyfit(x, log_y, 1)
    log_y_detrended   = log_y - np.polyval(tendencia_coefs, x)

    fft_res  = np.fft.fft(log_y_detrended)
    freqs    = np.fft.fftfreq(len(log_y_detrended))
    f_abs    = np.abs(fft_res)
    indices  = np.argsort(f_abs)[::-1]

    # Filtro: apenas ciclos com período ≥ 7 dias
    indices_ciclos = [i for i in indices if 0 < freqs[i] < (1/7)][:harmonicos]

    x_futuro             = np.arange(len(y) + dias_previsao)
    ondas_reconstruidas  = np.zeros(len(x_futuro))

    for i in indices_ciclos:
        amplitude = f_abs[i] / len(y)
        fase      = np.angle(fft_res[i])
        ondas_reconstruidas += amplitude * np.cos(2 * np.pi * freqs[i] * x_futuro + fase)

    log_projecao   = ondas_reconstruidas + np.polyval(tendencia_coefs, x_futuro)
    projecao_final = np.exp(log_projecao)

    # Banda ±1σ
    residuo_hist  = log_y - (ondas_reconstruidas[:len(y)] + np.polyval(tendencia_coefs, x))
    sigma         = np.std(residuo_hist)
    banda_sup     = np.exp(log_projecao + sigma)
    banda_inf     = np.exp(log_projecao - sigma)

    preco_alvo    = float(projecao_final[-1])
    variacao_proj = (preco_alvo / preco_atual - 1) * 100

    # ── Métricas ───────────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(f"💰 Preço Atual", f"${preco_atual:,.4f}" if preco_atual < 1 else f"${preco_atual:,.2f}")
    m2.metric(f"🎯 Projeção {dias_previsao}d", f"${preco_alvo:,.4f}" if preco_alvo < 1 else f"${preco_alvo:,.2f}", f"{variacao_proj:+.1f}%")
    m3.metric("📈 Variação 24h", f"{variacao_24h:+.2f}%")
    if market_cap:
        if market_cap >= 1e9:
            m4.metric("🏦 Market Cap", f"${market_cap/1e9:.2f}B")
        else:
            m4.metric("🏦 Market Cap", f"${market_cap/1e6:.0f}M")
    else:
        m4.metric("📊 Ciclos usados", str(len(indices_ciclos)))

    # ── Gráfico principal ──────────────────────────────────────────────────────
    fig, axes = plt.subplots(3, 1, figsize=(13, 12), gridspec_kw={'height_ratios': [3, 1, 1]})
    fig.patch.set_facecolor('#111317')
    fig.suptitle(f"{nome_escolhido} — FFT (log) | {len(indices_ciclos)} ciclos | {dias_previsao}d à frente",
                 color='white', fontsize=13, y=0.98)

    janela = max(0, len(y) - 300)

    # — Painel 1: Preço + Projeção ——————————————————————————————————————————
    ax1 = axes[0]
    ax1.set_facecolor('#171a21')
    ax1.tick_params(colors='white', labelsize=8)
    ax1.grid(True, color='#2c323f', alpha=0.5)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f'${v:,.4f}' if v < 1 else f'${v:,.0f}'
    ))

    ax1.plot(x, y, label="Preço Real", color='#00ffcc', alpha=0.7, linewidth=1)
    ax1.plot(x_futuro, projecao_final, label="Previsão FFT", color='#9b5de5', linestyle='--', linewidth=2)
    ax1.fill_between(x_futuro, banda_inf, banda_sup, color='#9b5de5', alpha=0.12, label='Banda ±1σ')
    ax1.axvline(x=len(y), color='#ff4757', linestyle=':', linewidth=1.5, label='Hoje')

    # Anotação do preço atual e alvo
    ax1.annotate(f'${preco_atual:,.2f}' if preco_atual >= 1 else f'${preco_atual:,.4f}',
                 xy=(len(y)-1, preco_atual), color='#00ffcc', fontsize=8,
                 xytext=(10, 5), textcoords='offset points')
    ax1.annotate(f'${preco_alvo:,.2f}' if preco_alvo >= 1 else f'${preco_alvo:,.4f}',
                 xy=(len(x_futuro)-1, preco_alvo), color='#9b5de5', fontsize=8,
                 xytext=(-60, 5), textcoords='offset points')

    precos_janela = y[janela:]
    ax1.set_xlim(janela, len(y) + dias_previsao)
    ax1.set_ylim(min(precos_janela) * 0.85, max(max(precos_janela), float(banda_sup[-1])) * 1.1)
    ax1.legend(facecolor='#171a21', labelcolor='white', loc='upper left', fontsize=8)
    ax1.set_ylabel("Preço (USD)", color='white', fontsize=9)

    # — Painel 2: Volume ————————————————————————————————————————————————————
    ax2 = axes[1]
    ax2.set_facecolor('#171a21')
    ax2.tick_params(colors='white', labelsize=8)
    ax2.grid(True, color='#2c323f', alpha=0.3)

    cores_vol = ['#ff4757' if i > 0 and y[i] < y[i-1] else '#00b894' for i in range(len(vol))]
    ax2.bar(x[janela:], vol[janela:], color=cores_vol[janela:], alpha=0.8, width=1)
    ax2.axhline(y=vol_medio, color='#fdcb6e', linestyle='--', linewidth=1, label=f'Média 30d')
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f'{v/1e9:.1f}B' if v >= 1e9 else f'{v/1e6:.0f}M'
    ))
    ax2.set_xlim(janela, len(y) + dias_previsao)
    ax2.set_ylabel("Volume", color='white', fontsize=9)
    ax2.legend(facecolor='#171a21', labelcolor='white', fontsize=8)

    # — Painel 3: Variação % diária ————————————————————————————————————————
    ax3 = axes[2]
    ax3.set_facecolor('#171a21')
    ax3.tick_params(colors='white', labelsize=8)
    ax3.grid(True, color='#2c323f', alpha=0.3)

    retornos = np.diff(y) / y[:-1] * 100
    x_ret    = x[1:]
    cores_ret = ['#ff4757' if r < 0 else '#00b894' for r in retornos]
    ax3.bar(x_ret[janela:], retornos[janela:], color=cores_ret[janela:], alpha=0.8, width=1)
    ax3.axhline(y=0, color='white', linewidth=0.5)
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.1f}%'))
    ax3.set_xlim(janela, len(y) + dias_previsao)
    ax3.set_ylabel("Variação %", color='white', fontsize=9)

    # Destaque variação 24h
    ax3.annotate(f'Hoje: {variacao_24h:+.2f}%',
                 xy=(len(y)-1, variacao_24h),
                 color='#fdcb6e', fontsize=8,
                 xytext=(5, 5), textcoords='offset points')

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    st.pyplot(fig)
    plt.close(fig)

    # ── Aviso de confiança ─────────────────────────────────────────────────────
    if abs(variacao_proj) > 60:
        st.warning(f"⚠️ Projeção muito agressiva ({variacao_proj:+.1f}%). Reduza os dias ou ciclos para resultado mais conservador.")
    else:
        st.success(f"✅ Gráfico gerado com sucesso para {nome_escolhido}!")

except Exception as e:
    st.error(f"Erro ao processar {nome_escolhido}: {e}")
    st.info("Tente selecionar outra criptomoeda ou aguarde alguns instantes.")
