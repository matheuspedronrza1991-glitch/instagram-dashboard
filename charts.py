import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

BRAND_COLOR = "#E1306C"
COLORS = ["#E1306C", "#833AB4", "#FCAF45", "#405DE6", "#5851DB"]


def trend_chart(df: pd.DataFrame, metrics: list[str], labels: dict[str, str], title: str):
    fig = go.Figure()
    for i, m in enumerate(metrics):
        if m in df.columns:
            fig.add_trace(go.Scatter(
                x=df["date"], y=df[m],
                name=labels.get(m, m),
                line=dict(color=COLORS[i % len(COLORS)], width=2),
                fill="tozeroy" if len(metrics) == 1 else None,
                fillcolor=f"rgba(225,48,108,0.1)" if len(metrics) == 1 else None,
            ))
    fig.update_layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color=BRAND_COLOR):
    fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
    )
    fig.update_yaxes(gridcolor="#f0f0f0")
    return fig


def pie_chart(values: list, names: list, title: str):
    fig = px.pie(
        values=values, names=names, title=title,
        color_discrete_sequence=COLORS,
        hole=0.4,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def content_type_radar(posts_df: pd.DataFrame):
    if posts_df.empty:
        return go.Figure()

    metrics = ["media_like_count", "media_comments_count", "media_saved", "media_shares", "media_reach"]
    labels = ["Curtidas", "Comentários", "Salvamentos", "Compartilhamentos", "Alcance"]

    type_map = {
        "IMAGE": "Feed (Foto)",
        "CAROUSEL_ALBUM": "Carrossel",
        "VIDEO": "Vídeo",
        "REEL": "Reel",
    }

    fig = go.Figure()
    for mtype, label in type_map.items():
        subset = posts_df[posts_df["media_type"] == mtype]
        if subset.empty:
            continue
        means = [subset[m].mean() if m in subset.columns else 0 for m in metrics]
        max_val = max(means) if max(means) > 0 else 1
        normalized = [v / max_val * 100 for v in means]
        fig.add_trace(go.Scatterpolar(
            r=normalized + [normalized[0]],
            theta=labels + [labels[0]],
            fill="toself",
            name=label,
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Comparativo por Tipo de Conteúdo",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def heatmap_weekday_hour(posts_df: pd.DataFrame, metric: str = "media_engagement"):
    if posts_df.empty or "timestamp" not in posts_df.columns:
        return go.Figure()

    df = posts_df.copy()
    df["hora"] = df["timestamp"].dt.hour
    df["dia"] = df["timestamp"].dt.day_name().map({
        "Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
        "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom"
    })
    order = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    pivot = df.pivot_table(values=metric, index="dia", columns="hora", aggfunc="mean").reindex(order)

    fig = px.imshow(
        pivot,
        labels=dict(x="Hora do dia", y="Dia da semana", color="Engajamento"),
        title="Melhor hora/dia para postar",
        color_continuous_scale=[[0, "#fff0f5"], [1, BRAND_COLOR]],
        aspect="auto",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
