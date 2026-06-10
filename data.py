import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

WINDSOR_BASE = "https://connectors.windsor.ai/instagram"
ACCOUNT_ID = "17841403068369487"


def _fetch(api_key: str, fields: list[str], extra_params: dict = None) -> pd.DataFrame:
    params = {
        "api_key": api_key,
        "account_id": ACCOUNT_ID,
        "fields": ",".join(fields),
    }
    if extra_params:
        params.update(extra_params)
    r = requests.get(WINDSOR_BASE, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    rows = data if isinstance(data, list) else data.get("data", [])
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=fields)


@st.cache_data(ttl=3600)
def get_profile_info(api_key: str) -> dict:
    df = _fetch(api_key, ["name", "username", "biography", "website",
                           "followers_count", "follows_count", "media_count"])
    if df.empty:
        return {}
    return df.iloc[0].to_dict()


@st.cache_data(ttl=3600)
def get_daily_insights(api_key: str, date_from: str, date_to: str) -> pd.DataFrame:
    fields = [
        "date", "reach_1d", "follower_count_1d", "likes", "comments",
        "saves", "shares", "views", "total_interactions", "accounts_engaged",
        "profile_links_taps",
    ]
    df = _fetch(api_key, fields, {"date_from": date_from, "date_to": date_to})
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        numeric = df.columns.drop("date")
        df[numeric] = df[numeric].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=3600)
def get_posts(api_key: str, date_from: str, date_to: str) -> pd.DataFrame:
    fields = [
        "timestamp", "media_type", "media_product_type", "media_caption",
        "media_permalink", "media_url", "media_thumbnail_url",
        "media_like_count", "media_comments_count",
        "media_engagement", "media_reach", "media_saved", "media_shares",
        "media_views", "media_reel_avg_watch_time",
    ]
    df = _fetch(api_key, fields, {"date_from": date_from, "date_to": date_to})
    if not df.empty and "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.sort_values("timestamp", ascending=False)
        numeric_cols = [c for c in df.columns if c not in
                        ("timestamp", "media_type", "media_product_type",
                         "media_caption", "media_permalink", "media_url",
                         "media_thumbnail_url")]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=3600)
def get_audience_age(api_key: str) -> pd.DataFrame:
    df = _fetch(api_key, ["audience_age_name", "audience_age_size"])
    if not df.empty:
        df["audience_age_size"] = pd.to_numeric(df["audience_age_size"], errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=3600)
def get_audience_gender(api_key: str) -> pd.DataFrame:
    df = _fetch(api_key, ["audience_gender_name", "audience_gender_size"])
    if not df.empty:
        df["audience_gender_size"] = pd.to_numeric(df["audience_gender_size"], errors="coerce").fillna(0)
    return df


@st.cache_data(ttl=3600)
def get_audience_country(api_key: str) -> pd.DataFrame:
    df = _fetch(api_key, ["audience_country_name", "audience_country_size"])
    if not df.empty:
        df["audience_country_size"] = pd.to_numeric(df["audience_country_size"], errors="coerce").fillna(0)
        df = df.sort_values("audience_country_size", ascending=False).head(10)
    return df


@st.cache_data(ttl=3600)
def get_audience_city(api_key: str) -> pd.DataFrame:
    df = _fetch(api_key, ["city", "audience_city_size"])
    if not df.empty:
        df["audience_city_size"] = pd.to_numeric(df["audience_city_size"], errors="coerce").fillna(0)
        df = df.sort_values("audience_city_size", ascending=False).head(10)
    return df
