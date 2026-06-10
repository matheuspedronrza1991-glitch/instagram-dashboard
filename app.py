import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd

import data as d
import charts as c
import ai_insights as ai

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Instagram Dashboard — Leticia Sganzerla",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg, #833AB4 0%, #E1306C 100%); }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] input { color: #333 !important; background: white !important; }
[data-testid="stSidebar"] .stSelectbox div { color: #333 !important; }
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    text-align: center;
    border-top: 4px solid #E1306C;
}
.metric-value { font-size: 2rem; font-weight: 700; color: #E1306C; margin: 0; }
.metric-label { font-size: 0.85rem; color: #666; margin: 0; }
.post-card {
    background: white;
    border-radius: 10px;
    padding: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}
div[data-testid="stTabs"] button { font-size: 1rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Instagram Dashboard")
    st.markdown("**@lesganzerlla**")
    st.markdown("---")

    st.markdown("### 🔑 Configuração")
    windsor_key = st.text_input("Windsor API Key", type="password",
                                 value=st.session_state.get("windsor_key", ""),
                                 help="Acesse windsor.ai > Settings > API Key")
    anthropic_key = st.text_input("Anthropic API Key", type="password",
                                   value=st.session_state.get("anthropic_key", ""),
                                   help="A mesma chave usada no projeto Antonella")

    if windsor_key:
        st.session_state["windsor_key"] = windsor_key
    if anthropic_key:
        st.session_state["anthropic_key"] = anthropic_key

    st.markdown("---")
    st.markdown("### 📅 Período")
    preset = st.selectbox("Período rápido", [
        "Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias", "Personalizado"
    ], index=1)

    today = date.today()
    if preset == "Últimos 7 dias":
        date_from = today - timedelta(days=7)
        date_to = today
    elif preset == "Últimos 30 dias":
        date_from = today - timedelta(days=30)
        date_to = today
    elif preset == "Últimos 90 dias":
        date_from = today - timedelta(days=90)
        date_to = today
    else:
        date_from = st.date_input("De", value=today - timedelta(days=30))
        date_to = st.date_input("Até", value=today)

    date_from_str = date_from.strftime("%Y-%m-%d")
    date_to_str = date_to.strftime("%Y-%m-%d")

    st.markdown("---")
    if st.button("🔄 Atualizar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Dados via Windsor.ai · IA via Anthropic")


# ─── Main content ────────────────────────────────────────────────────────────
if not windsor_key:
    st.markdown("""
    ## Bem-vinda à sua Dashboard do Instagram! 🎉

    Para começar, insira suas chaves na barra lateral:

    **1. Windsor API Key**
    - Acesse: [windsor.ai/app/api-key](https://onboard.windsor.ai/app/api-key)
    - Copie sua API Key e cole no campo ao lado

    **2. Anthropic API Key**
    - Use a mesma chave do projeto Antonella

    Depois que inserir as chaves, os dados aparecerão automaticamente.
    """)
    st.stop()


# ─── Load data ───────────────────────────────────────────────────────────────
with st.spinner("Carregando dados do Instagram..."):
    try:
        profile = d.get_profile_info(windsor_key)
        daily_df = d.get_daily_insights(windsor_key, date_from_str, date_to_str)
        posts_df = d.get_posts(windsor_key, date_from_str, date_to_str)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}\n\nVerifique sua Windsor API Key.")
        st.stop()


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Visão Geral",
    "📸 Conteúdo",
    "👥 Audiência",
    "📈 Tendências",
    "🤖 Insights IA",
    "💡 Ideias de Post",
])


# ══════════════════════════════════════════════════════════════════
# TAB 1 — VISÃO GERAL
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f"## Olá, **{profile.get('name', 'Leticia')}** 👋")
    st.caption(f"@{profile.get('username', 'lesganzerlla')} · Período: {date_from_str} → {date_to_str}")

    # KPI cards
    cols = st.columns(4)
    metrics = [
        ("👤 Seguidores", f"{profile.get('followers_count', 0):,}", None),
        ("👁️ Alcance Total", f"{daily_df['reach_1d'].sum():,.0f}" if not daily_df.empty else "—", None),
        ("❤️ Interações", f"{daily_df['total_interactions'].sum():,.0f}" if not daily_df.empty else "—", None),
        ("📈 Novos seguidores", f"+{daily_df['follower_count_1d'].sum():,.0f}" if not daily_df.empty else "—", None),
    ]
    for col, (label, value, _) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <p class="metric-value">{value}</p>
                <p class="metric-label">{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    cols2 = st.columns(4)
    metrics2 = [
        ("💬 Comentários", f"{daily_df['comments'].sum():,.0f}" if not daily_df.empty else "—"),
        ("🔖 Salvamentos", f"{daily_df['saves'].sum():,.0f}" if not daily_df.empty else "—"),
        ("↗️ Compartilhamentos", f"{daily_df['shares'].sum():,.0f}" if not daily_df.empty else "—"),
        ("▶️ Views", f"{daily_df['views'].sum():,.0f}" if not daily_df.empty else "—"),
    ]
    for col, (label, value) in zip(cols2, metrics2):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top-color: #833AB4;">
                <p class="metric-value" style="color:#833AB4;">{value}</p>
                <p class="metric-label">{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # Mini charts
    col_a, col_b = st.columns(2)
    if not daily_df.empty:
        with col_a:
            fig = c.trend_chart(daily_df, ["reach_1d"], {"reach_1d": "Alcance"}, "Alcance diário")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = c.trend_chart(
                daily_df,
                ["likes", "saves", "comments"],
                {"likes": "Curtidas", "saves": "Salvamentos", "comments": "Comentários"},
                "Interações diárias",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Engagement rate
    if not daily_df.empty and profile.get("followers_count", 0):
        total_int = daily_df["total_interactions"].sum()
        posts_count = len(posts_df) if not posts_df.empty else 1
        eng_rate = (total_int / (profile["followers_count"] * max(posts_count, 1))) * 100
        st.info(f"📊 **Taxa de engajamento média por post:** {eng_rate:.2f}%  "
                f"*(referência boa para o nicho: 1–3%)*")


# ══════════════════════════════════════════════════════════════════
# TAB 2 — CONTEÚDO
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 📸 Desempenho de Conteúdo")

    if posts_df.empty:
        st.info("Nenhum post encontrado no período selecionado.")
    else:
        # Tipo de conteúdo performance
        col_radar, col_type = st.columns([1, 1])
        with col_radar:
            st.plotly_chart(c.content_type_radar(posts_df), use_container_width=True)
        with col_type:
            type_stats = posts_df.groupby("media_type").agg(
                posts=("media_type", "count"),
                avg_engagement=("media_engagement", "mean"),
                avg_reach=("media_reach", "mean"),
                avg_saves=("media_saved", "mean"),
            ).round(0).reset_index()
            type_stats.columns = ["Tipo", "Posts", "Eng. Médio", "Alcance Médio", "Saves Médio"]
            st.markdown("### Por tipo de conteúdo")
            st.dataframe(type_stats, hide_index=True, use_container_width=True)

        # Heatmap
        st.plotly_chart(c.heatmap_weekday_hour(posts_df), use_container_width=True)

        # Top posts
        st.markdown("### 🏆 Top 10 Posts por Engajamento")
        top_posts = posts_df.nlargest(10, "media_engagement")

        for _, row in top_posts.iterrows():
            with st.expander(
                f"{row.get('media_type','—')} · {row.get('timestamp', ''):%d/%m/%Y %H:%M}  "
                f"· ❤️ {row.get('media_like_count',0):.0f}  "
                f"· 💬 {row.get('media_comments_count',0):.0f}  "
                f"· 🔖 {row.get('media_saved',0):.0f}  "
                f"· 👁️ {row.get('media_reach',0):.0f}"
            ):
                cols = st.columns([1, 3])
                img_url = row.get("media_url") or row.get("media_thumbnail_url")
                with cols[0]:
                    if img_url:
                        st.image(img_url, width=200)
                with cols[1]:
                    caption = row.get("media_caption", "")
                    st.write(caption[:500] if caption else "_Sem legenda_")
                    permalink = row.get("media_permalink", "")
                    if permalink:
                        st.markdown(f"[Ver no Instagram]({permalink})")


# ══════════════════════════════════════════════════════════════════
# TAB 3 — AUDIÊNCIA
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 👥 Sua Audiência")

    col1, col2 = st.columns(2)

    with col1:
        age_df = d.get_audience_age(windsor_key)
        if not age_df.empty:
            fig = c.bar_chart(
                age_df.sort_values("audience_age_size", ascending=False),
                "audience_age_name", "audience_age_size",
                "Distribuição por Faixa Etária",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        gender_df = d.get_audience_gender(windsor_key)
        if not gender_df.empty:
            fig = c.pie_chart(
                gender_df["audience_gender_size"].tolist(),
                gender_df["audience_gender_name"].tolist(),
                "Distribuição por Gênero",
            )
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        country_df = d.get_audience_country(windsor_key)
        if not country_df.empty:
            fig = c.bar_chart(
                country_df,
                "audience_country_name", "audience_country_size",
                "Top 10 Países",
                color="#405DE6",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        city_df = d.get_audience_city(windsor_key)
        if not city_df.empty:
            fig = c.bar_chart(
                city_df,
                "city", "audience_city_size",
                "Top 10 Cidades",
                color="#5851DB",
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 4 — TENDÊNCIAS
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📈 Tendências no Tempo")

    if daily_df.empty:
        st.info("Sem dados de tendências no período.")
    else:
        metric_options = {
            "Alcance": "reach_1d",
            "Interações totais": "total_interactions",
            "Curtidas": "likes",
            "Comentários": "comments",
            "Salvamentos": "saves",
            "Compartilhamentos": "shares",
            "Views": "views",
            "Novos seguidores": "follower_count_1d",
        }
        selected = st.multiselect(
            "Selecione as métricas",
            list(metric_options.keys()),
            default=["Alcance", "Interações totais"],
        )

        if selected:
            fields = [metric_options[s] for s in selected]
            labels = {v: k for k, v in metric_options.items()}
            fig = c.trend_chart(daily_df, fields, labels, "Evolução das métricas")
            st.plotly_chart(fig, use_container_width=True)

        # Semana a semana
        st.markdown("### Resumo Semanal")
        weekly = daily_df.copy()
        weekly["semana"] = weekly["date"].dt.to_period("W").astype(str)
        weekly_sum = weekly.groupby("semana")[
            ["reach_1d", "total_interactions", "likes", "saves", "follower_count_1d"]
        ].sum().reset_index()
        weekly_sum.columns = ["Semana", "Alcance", "Interações", "Curtidas", "Saves", "Novos Seguidores"]
        st.dataframe(weekly_sum, hide_index=True, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 5 — INSIGHTS IA
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("## 🤖 Análise com Inteligência Artificial")

    if not anthropic_key:
        st.warning("Insira a Anthropic API Key na barra lateral para usar esta seção.")
    else:
        if st.button("🔍 Analisar meu perfil agora", type="primary", use_container_width=True):
            with st.spinner("Claude está analisando seus dados..."):
                try:
                    analysis = ai.generate_profile_analysis(
                        anthropic_key, daily_df, posts_df, profile
                    )
                    st.session_state["profile_analysis"] = analysis
                except Exception as e:
                    st.error(f"Erro ao gerar análise: {e}")

        if "profile_analysis" in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state["profile_analysis"])


# ══════════════════════════════════════════════════════════════════
# TAB 6 — IDEIAS DE POST
# ══════════════════════════════════════════════════════════════════
with tab6:
    st.markdown("## 💡 Gerador de Ideias e Legendas")

    if not anthropic_key:
        st.warning("Insira a Anthropic API Key na barra lateral para usar esta seção.")
    else:
        col_ideas, col_caption = st.columns([1, 1])

        with col_ideas:
            st.markdown("### 📅 Calendário de Conteúdo (30 dias)")
            qty = st.slider("Quantidade de ideias", 5, 20, 10)
            if st.button("✨ Gerar ideias de posts", type="primary", use_container_width=True):
                with st.spinner("Gerando calendário de conteúdo..."):
                    try:
                        ideas = ai.generate_content_ideas(anthropic_key, posts_df, profile, qty)
                        st.session_state["content_ideas"] = ideas
                    except Exception as e:
                        st.error(f"Erro: {e}")

            if "content_ideas" in st.session_state:
                st.markdown("---")
                st.markdown(st.session_state["content_ideas"])

        with col_caption:
            st.markdown("### ✍️ Gerador de Legenda")
            topic = st.text_input("Tema do post", placeholder="ex: Como perder barriga em 30 dias")
            post_type = st.selectbox("Tipo de post", ["Reel", "Carrossel", "Foto", "Stories"])

            if st.button("📝 Gerar legendas", type="primary", use_container_width=True):
                if not topic:
                    st.warning("Digite um tema para o post.")
                else:
                    with st.spinner("Criando legendas..."):
                        try:
                            captions = ai.generate_caption_suggestion(
                                anthropic_key, topic, post_type, profile
                            )
                            st.session_state["caption_result"] = captions
                        except Exception as e:
                            st.error(f"Erro: {e}")

            if "caption_result" in st.session_state:
                st.markdown("---")
                st.markdown(st.session_state["caption_result"])
