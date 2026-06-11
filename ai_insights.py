import anthropic
import pandas as pd
import json


def _client(api_key: str) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key)


def _summarize_posts(posts_df: pd.DataFrame) -> str:
    if posts_df.empty:
        return "Sem posts no período."
    top = posts_df.nlargest(5, "media_engagement")[
        ["media_type", "media_caption", "media_like_count",
         "media_comments_count", "media_saved", "media_reach"]
    ].to_dict("records")
    summary = []
    for p in top:
        caption = str(p.get("media_caption", ""))[:120]
        summary.append(
            f"- Tipo: {p['media_type']} | Curtidas: {p['media_like_count']:.0f} | "
            f"Comentários: {p['media_comments_count']:.0f} | Salvamentos: {p['media_saved']:.0f} | "
            f"Alcance: {p['media_reach']:.0f} | Legenda: {caption}"
        )
    return "\n".join(summary)


def _summarize_metrics(daily_df: pd.DataFrame) -> str:
    if daily_df.empty:
        return "Sem dados de métricas."
    total = daily_df[["reach_1d", "likes", "comments", "saves", "shares", "views",
                       "total_interactions", "follower_count_1d"]].sum()
    avg = daily_df[["reach_1d", "total_interactions"]].mean()
    return (
        f"Período analisado: {len(daily_df)} dias\n"
        f"Alcance total: {total.get('reach_1d', 0):,.0f}\n"
        f"Novos seguidores: {total.get('follower_count_1d', 0):,.0f}\n"
        f"Curtidas: {total.get('likes', 0):,.0f}\n"
        f"Comentários: {total.get('comments', 0):,.0f}\n"
        f"Salvamentos: {total.get('saves', 0):,.0f}\n"
        f"Compartilhamentos: {total.get('shares', 0):,.0f}\n"
        f"Views totais: {total.get('views', 0):,.0f}\n"
        f"Interações totais: {total.get('total_interactions', 0):,.0f}\n"
        f"Alcance médio diário: {avg.get('reach_1d', 0):,.0f}\n"
        f"Interações médias diárias: {avg.get('total_interactions', 0):,.0f}"
    )


def generate_profile_analysis(
    api_key: str,
    daily_df: pd.DataFrame,
    posts_df: pd.DataFrame,
    profile: dict,
) -> str:
    metrics_summary = _summarize_metrics(daily_df)
    posts_summary = _summarize_posts(posts_df)
    username = profile.get("username", "lesganzerlla")
    followers = profile.get("followers_count", "N/A")

    prompt = f"""Você é um especialista em marketing digital e crescimento no Instagram para o nicho de emagrecimento e saúde feminina.

Analise os dados do perfil @{username} (seguidores: {followers}) e forneça insights acionáveis.

=== MÉTRICAS DO PERÍODO ===
{metrics_summary}

=== TOP 5 POSTS POR ENGAJAMENTO ===
{posts_summary}

Forneça uma análise com:
1. **Pontos Fortes** — o que está funcionando bem (2-3 pontos)
2. **Oportunidades de Melhoria** — o que pode ser melhorado (2-3 pontos)
3. **Ações Prioritárias** — 3 ações concretas para aumentar o alcance e engajamento esta semana
4. **Análise de Conteúdo** — quais tipos de post estão gerando mais resultado e por quê

Seja específico, prático e baseado nos dados. Use linguagem direta e motivadora."""

    client = _client(api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_content_ideas(
    api_key: str,
    posts_df: pd.DataFrame,
    profile: dict,
    quantity: int = 10,
) -> str:
    posts_summary = _summarize_posts(posts_df)
    username = profile.get("username", "lesganzerlla")

    prompt = f"""Você é um especialista em criação de conteúdo para Instagram no nicho de emagrecimento, saúde e bem-estar feminino.

Perfil: @{username} — foco em emagrecimento e transformação física

=== POSTS QUE MAIS ENGAJARAM ===
{posts_summary}

Gere {quantity} ideias de posts para os próximos 30 dias. Para cada ideia inclua:
- **Formato**: Reel / Carrossel / Foto / Stories
- **Tema/Título**: assunto principal
- **Gancho inicial**: primeira frase que prende a atenção
- **Por que vai funcionar**: justificativa baseada no que já performou bem

Organize por semana (4 semanas). Misture formatos e temas.
Foco em: dicas práticas de emagrecimento, motivação, receitas saudáveis, mitos e verdades, transformações, rotina, etc.
Adapte ao estilo do perfil com base nos posts que funcionaram."""

    client = _client(api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_caption_suggestion(
    api_key: str,
    topic: str,
    post_type: str,
    profile: dict,
) -> str:
    username = profile.get("username", "lesganzerlla")

    prompt = f"""Você é um especialista em copywriting para Instagram no nicho de emagrecimento e saúde feminina.

Perfil: @{username}
Tipo de post: {post_type}
Tema: {topic}

Crie 3 opções de legenda para este post. Cada legenda deve ter:
- Gancho forte na primeira linha (sem emojis logo no início — texto puro que para o scroll)
- Conteúdo de valor (2-4 parágrafos curtos)
- CTA claro no final (salva, comenta, compartilha, etc.)
- 5-8 hashtags relevantes no nicho

Varie o tom: 1 mais motivacional, 1 mais educativo/prático, 1 mais pessoal/conectivo."""

    client = _client(api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def analyze_viral_trends(api_key: str, tema: str, search_context: str, profile: dict) -> str:
    username = profile.get("username", "lesganzerlla")
    followers = profile.get("followers_count", "~12.500")

    prompt = f"""Você é uma Estrategista Sênior de Marketing Digital especializada em crescimento no Instagram para o nicho de saúde, emagrecimento e estética feminina no Brasil. Tem 10 anos de experiência gerenciando perfis que cresceram de 0 a 1 milhão de seguidores.

Seu trabalho agora: analisar o que está viralizando sobre "{tema}" no Instagram/TikTok e criar um plano de conteúdo estratégico para o perfil @{username} (clínica de emagrecimento e estética em Ampére-PR, {followers} seguidores).

=== CONTEXTO DO QUE ESTÁ EM ALTA SOBRE "{tema}" ===
{search_context}

=== SUA ANÁLISE DEVE CONTER ===

## 1. O que está viralizando agora
- Quais formatos dominam (Reel curto, carrossel educativo, antes/depois, dia a dia, etc.)
- Gatilhos emocionais mais usados (medo, esperança, curiosidade, pertencimento)
- Padrões de gancho que estão funcionando

## 2. Por que está viralizando (análise de marketing)
- Explique o mecanismo psicológico por trás dos conteúdos em alta
- O que o público realmente quer ver/sentir com esse tema

## 3. Oportunidade para @{username}
- Como a clínica pode se posicionar nessa tendência de forma autêntica
- Ângulo diferenciado que poucos estão explorando

## 4. Plano de 5 Reels prontos para produzir
Para cada Reel:
- **Título do vídeo**
- **Gancho (primeiros 3 segundos)**: texto exato que abre o vídeo
- **Roteiro resumido**: o que mostrar/falar em cada parte
- **CTA final**: o que pedir para o seguidor fazer
- **Hashtags**: 8-10 hashtags estratégicas

## 5. Melhor momento para postar
- Dia da semana e horário recomendado para esse tipo de conteúdo

Seja específico, prático e orientado a resultados. Foco em conteúdo que gera salvamentos e compartilhamentos."""

    client = _client(api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def analyze_competitor_profiles(api_key: str, profiles_data: list[dict], profile: dict) -> str:
    username = profile.get("username", "lesganzerlla")
    followers = profile.get("followers_count", "~12.500")

    perfis_resumo = "\n\n".join(
        f"### @{p['handle']}\n" + "\n".join(f"- {t}" for t in p["titulos"])
        for p in profiles_data if p.get("titulos")
    )

    prompt = f"""Você é uma Estrategista Sênior de Marketing Digital especializada em análise competitiva para Instagram no nicho de saúde e emagrecimento no Brasil.

Perfil analisado: @{username} — clínica de emagrecimento e estética em Ampére-PR ({followers} seguidores)

=== CONTEÚDO RECENTE DOS PERFIS MONITORADOS ===
{perfis_resumo if perfis_resumo else "Dados limitados disponíveis — use seu conhecimento do nicho para complementar."}

=== SUA ANÁLISE DEVE CONTER ===

## 1. Padrões identificados nos perfis
- Temas recorrentes que estão sendo explorados
- Formatos de conteúdo mais usados
- Tom de voz e posicionamento de cada perfil

## 2. O que está funcionando (e por quê)
- Conteúdos com maior potencial viral com base nos títulos/temas
- Gatilhos de engajamento identificados

## 3. Gaps e oportunidades
- O que esses perfis NÃO estão fazendo que @{username} poderia fazer
- Ângulos não explorados no nicho

## 4. Plano de ação: 5 Reels para @{username} inspirados nesses perfis
Para cada Reel:
- **Conceito**: ideia central (adaptada para a realidade da clínica em Ampére-PR)
- **Gancho (primeiros 3 segundos)**: texto exato
- **Roteiro**: estrutura do vídeo
- **Por que vai engajar**: mecanismo de marketing por trás
- **Hashtags**: 8 hashtags estratégicas

## 5. Estratégia de diferenciação
- Como @{username} pode se destacar em relação a esses perfis

Seja cirúrgico e prático. Foco em conteúdo replicável com recursos simples (câmera do celular, clínica, antes/depois)."""

    client = _client(api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
