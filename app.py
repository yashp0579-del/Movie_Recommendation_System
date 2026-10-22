import os
import html
import urllib.parse
import streamlit as st
from recommender import load_movies, recommend, similar_movies, ERAS
from tmdb import fetch_many, check_key, clear_cache

st.set_page_config(page_title="CineMatch - Movie Recommender", page_icon="🎬", layout="wide")

# ------------------------------------------------------------------ STYLE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"], .stApp, .stMarkdown { font-family: 'Poppins', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.5rem; max-width: 1400px; }
.stApp { background:
    radial-gradient(900px 600px at 0% 0%, rgba(124,58,237,.38) 0%, transparent 60%),
    radial-gradient(800px 600px at 100% 5%, rgba(236,72,153,.32) 0%, transparent 60%),
    radial-gradient(900px 700px at 100% 60%, rgba(6,182,212,.22) 0%, transparent 60%),
    radial-gradient(900px 700px at 0% 85%, rgba(249,115,22,.22) 0%, transparent 60%),
    radial-gradient(700px 500px at 50% 100%, rgba(34,197,94,.14) 0%, transparent 60%),
    #0a0a14; background-attachment: fixed; color: #eee; }

/* sidebar */
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1030 0%,#0f0f1c 45%,#0b1a24 100%); border-right: 1px solid #2f2f55; }
section[data-testid="stSidebar"] h1 { font-size: 1.3rem; font-weight: 700; }
section[data-testid="stSidebar"] h3 { font-size: 1rem; font-weight: 600; background: linear-gradient(90deg,#c084fc,#f472b6,#fb923c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

/* hero */
.hero { position: relative; padding: 2.2rem 2.4rem; border-radius: 22px; margin-bottom: 1.4rem; overflow: hidden;
        background: linear-gradient(115deg, rgba(124,58,237,.55), rgba(236,72,153,.45) 35%, rgba(249,115,22,.40) 65%, rgba(6,182,212,.45));
        border: 1px solid rgba(255,255,255,.14); box-shadow: 0 20px 60px rgba(124,58,237,.25); }
.hero:after { content: "🎬"; position: absolute; right: 2rem; top: 50%; transform: translateY(-50%);
              font-size: 7rem; opacity: .12; }
.hero h1 { font-size: 3rem; font-weight: 800; margin: 0; letter-spacing: -1px;
           background: linear-gradient(90deg,#fff 0%,#fde68a 35%,#fbcfe8 70%,#a5f3fc 100%); -webkit-background-clip: text;
           -webkit-text-fill-color: transparent; }
.hero p { color: #f0e9ff; margin: .3rem 0 1rem 0; font-size: 1.05rem; }
.stat { display: inline-block; background: rgba(0,0,0,.28); border: 1px solid rgba(255,255,255,.22);
        border-radius: 40px; padding: 6px 16px; margin: 0 8px 6px 0; font-size: .85rem; color: #e8e8f5; }
.stat b { color: #fde047; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: none; }
.stTabs button[data-baseweb="tab"] { background: rgba(255,255,255,.06); border-radius: 40px; padding: 8px 20px; border: 1px solid rgba(255,255,255,.14); height: auto; }
.stTabs button[data-baseweb="tab"] p { font-weight: 500; font-size: .95rem; }
.stTabs button[aria-selected="true"] { background: linear-gradient(90deg,#7c3aed,#ec4899,#f97316); border-color: transparent; box-shadow: 0 6px 20px rgba(236,72,153,.35); }
.stTabs button[aria-selected="true"] p { color: #fff; font-weight: 600; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* section title */
.sec { font-size: 1.25rem; font-weight: 700; margin: 1.3rem 0 .7rem 0; color: #fff; padding-left: 12px; border-left: 4px solid; border-image: linear-gradient(180deg,#a855f7,#ec4899,#f97316) 1; }
.sec span { color: #9a9ab0; font-weight: 400; font-size: .85rem; margin-left: 8px; }

/* spotlight */
.spot { display: flex; gap: 1.6rem; flex-wrap: wrap; background: linear-gradient(135deg,rgba(124,58,237,.28),rgba(20,20,35,.92) 45%,rgba(6,182,212,.20));
        border: 1px solid rgba(255,255,255,.16); border-radius: 22px; padding: 1.2rem; margin-bottom: 1.6rem;
        box-shadow: 0 18px 50px rgba(0,0,0,.45); }
.spot .pw { width: 230px; flex: 0 0 230px; border-radius: 14px; }
.spot .info { flex: 1; min-width: 260px; padding: .3rem .4rem; }
.crown { display: inline-block; background: linear-gradient(90deg,#f59e0b,#ec4899,#8b5cf6); color: #fff; font-weight: 600;
         font-size: .75rem; padding: 4px 12px; border-radius: 30px; letter-spacing: .5px; margin-bottom: .6rem; }
.spot .t { font-size: 1.9rem; font-weight: 700; line-height: 1.2; color: #fff; }
.spot .ov { font-size: .9rem; color: #c3c3d8; margin: .7rem 0; line-height: 1.55; }

/* cards */
.card { background: linear-gradient(180deg,rgba(30,27,52,.92),rgba(16,16,28,.96)); border: 1px solid rgba(255,255,255,.10); border-radius: 18px; overflow: hidden;
        margin-bottom: 1.3rem; transition: transform .25s, box-shadow .25s, border-color .25s; }
.card:hover { transform: translateY(-8px); border-color: rgba(236,72,153,.6); box-shadow: 0 18px 44px rgba(168,85,247,.35); }
.pw { position: relative; overflow: hidden; background: #0e0e16; }
.pw img { width: 100%; aspect-ratio: 2/3; object-fit: cover; display: block; transition: transform .5s; }
.card:hover .pw img { transform: scale(1.07); }
.pw:after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 45%;
            background: linear-gradient(to top, rgba(22,20,40,.95), transparent); pointer-events: none; }
.noposter { width: 100%; aspect-ratio: 2/3; display: flex; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; padding: 1rem; font-weight: 700; font-size: 1.15rem; color: #fff; gap: .4rem; }
.rate { position: absolute; top: 10px; right: 10px; z-index: 2; background: rgba(0,0,0,.72); color: #ffd23f;
        font-weight: 700; font-size: .85rem; padding: 4px 10px; border-radius: 30px; border: 1px solid rgba(255,255,255,.15); }
.lang { position: absolute; top: 10px; left: 10px; z-index: 2; background: linear-gradient(90deg,#7c3aed,#ec4899); color: #fff;
        font-weight: 600; font-size: .7rem; padding: 4px 10px; border-radius: 30px; }
.body { padding: .85rem 1rem 1.1rem 1rem; }
.title { font-size: 1.02rem; font-weight: 600; color: #fff; line-height: 1.3; min-height: 2.6em; }
.meta { color: #9a9ab0; font-size: .78rem; margin: .2rem 0 .55rem 0; }
.chip { display: inline-block; background: rgba(168,85,247,.22); color: #e9d5ff; border-radius: 20px;
        padding: 2px 10px; font-size: .68rem; margin: 0 4px 4px 0; }
.chip:nth-of-type(2n) { background: rgba(236,72,153,.22); color: #fbcfe8; }
.chip.stream { background: rgba(34,197,94,.20); color: #86efac; }
.chip.rent { background: rgba(249,115,22,.22); color: #fdba74; }
.bar { height: 5px; background: #25253a; border-radius: 4px; margin: .6rem 0 .25rem 0; overflow: hidden; }
.bar i { display: block; height: 100%; background: linear-gradient(90deg,#22d3ee,#a855f7,#ec4899,#fb923c); border-radius: 4px; }
.pct { font-size: .72rem; color: #67e8f9; font-weight: 600; }
.why { color: #f9a8d4; font-size: .72rem; margin-top: .2rem; }
.ov { color: #aeaec6; font-size: .75rem; margin-top: .5rem; line-height: 1.5; }
.lbl { color: #6f6f8a; font-size: .65rem; margin-top: .55rem; text-transform: uppercase; letter-spacing: .8px; }
.links a { display: inline-block; font-size: .7rem; margin: 7px 5px 0 0; padding: 4px 10px; border-radius: 8px;
           background: rgba(255,255,255,.10); color: #fff !important; text-decoration: none; transition: background .2s; }
.links a:nth-child(1) { background: linear-gradient(90deg,#ef4444,#f97316); }
.links a:nth-child(2) { background: rgba(245,197,24,.25); }
.links a:nth-child(3) { background: rgba(6,182,212,.28); }
.links a:hover { background: linear-gradient(90deg,#7c3aed,#ec4899); }
.foot { text-align: center; color: #a5a5c8; font-size: .8rem; margin: 2.5rem 0 1rem 0;
        border-top: 1px solid #1f1f33; padding-top: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ DATA
@st.cache_data
def get_data():
    return load_movies(os.path.join(os.path.dirname(__file__), "movies.csv"))

df = get_data()
all_genres = sorted({g for gs in df["genres"] for g in gs})
all_moods = sorted({m for ms in df["moods"] for m in ms})
all_langs = sorted(df["language"].unique())

# ------------------------------------------------------------------ SIDEBAR
st.sidebar.title("🎛️ Preferences")
st.sidebar.markdown("### Tell us what you like")
mood_pick = st.sidebar.multiselect("😊 Your mood", all_moods)
genre_pick = st.sidebar.multiselect("🎭 Genres", all_genres)
lang_pick = st.sidebar.selectbox("🗣️ Language", ["Any"] + all_langs)
era_pick = st.sidebar.selectbox("📅 Era", list(ERAS.keys()))
min_rating = st.sidebar.slider("⭐ Minimum rating", 5.0, 9.0, 7.0, 0.1)
max_dur = st.sidebar.slider("⏱️ Max duration (min)", 80, 330, 200, 5)
top_n = st.sidebar.slider("🎞️ How many results", 4, 24, 12, 4)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖼️ Posters & streaming")
try:
    default_key = st.secrets.get("TMDB_API_KEY", "")
except Exception:
    default_key = ""
api_key = st.sidebar.text_input("TMDB API key (free)", value=default_key or os.getenv("TMDB_API_KEY", ""),
                                type="password",
                                help="Get a free key at themoviedb.org → Settings → API")
region = st.sidebar.selectbox("Streaming region", ["IN", "US", "GB", "CA", "AU"], index=0)
if api_key:
    ok, msg = check_key(api_key.strip())
    (st.sidebar.success if ok else st.sidebar.error)(msg)
if st.sidebar.button("🔄 Reload posters"):
    st.cache_data.clear()
    clear_cache()
    st.rerun()
st.sidebar.caption("Without a key, movies show a styled placeholder and search links.")

# ------------------------------------------------------------------ CARD HELPERS
def gradient_for(title):
    h = sum(ord(c) for c in title)
    a, b = (h * 37) % 360, (h * 91) % 360
    return f"linear-gradient(135deg, hsl({a},55%,32%), hsl({b},60%,16%))"


def poster_html(m, info):
    t = html.escape(m["title"])
    if info and info.get("poster"):
        img = f'<img loading="lazy" src="{info["poster"]}" alt="{t}">'
    else:
        img = f'<div class="noposter" style="background:{gradient_for(m["title"])}"><span style="font-size:2rem">🎬</span>{t}</div>'
    return (f'<div class="pw"><span class="lang">{html.escape(m["language"])}</span>'
            f'<span class="rate">★ {m["rating"]}</span>{img}</div>')


def links_html(m):
    q = urllib.parse.quote_plus(f'{m["title"]} {m["year"]}')
    qt = urllib.parse.quote_plus(m["title"])
    return (
        '<div class="links">'
        f'<a href="https://www.youtube.com/results?search_query={q}+trailer" target="_blank">▶ Trailer</a>'
        f'<a href="https://www.imdb.com/find/?q={q}" target="_blank">IMDb</a>'
        f'<a href="https://www.justwatch.com/in/search?q={qt}" target="_blank">JustWatch</a>'
        f'<a href="https://www.netflix.com/search?q={qt}" target="_blank">Netflix</a>'
        f'<a href="https://www.primevideo.com/search/?phrase={qt}" target="_blank">Prime Video</a>'
        '</div>')


def avail_html(info):
    if not info:
        return ""
    out = ""
    if info["stream"]:
        out += '<div class="lbl">Streaming on</div>' + "".join(
            f'<span class="chip stream">{html.escape(p)}</span>' for p in info["stream"][:5])
    if info["rent"] or info["buy"]:
        names = list(dict.fromkeys(info["rent"] + info["buy"]))
        out += '<div class="lbl">Rent / Buy</div>' + "".join(
            f'<span class="chip rent">{html.escape(p)}</span>' for p in names[:5])
    if not (info["stream"] or info["rent"] or info["buy"]):
        out += '<div class="lbl">Not listed in your region - use the links below</div>'
    return out


def chips_html(m):
    return "".join(f'<span class="chip">{html.escape(g)}</span>' for g in m["genres"])


def match_html(pct, reasons):
    why = f'<div class="why">✔ {html.escape(" • ".join(reasons))}</div>' if reasons else ""
    return (f'<div class="bar"><i style="width:{pct}%"></i></div>'
            f'<div class="pct">{pct}% match</div>{why}')


def card_html(m, score, reasons, info, pct):
    ov = (f'<div class="ov">{html.escape(info["overview"][:140])}…</div>'
          if info and info.get("overview") else "")
    return (f'<div class="card">{poster_html(m, info)}<div class="body">'
            f'<div class="title">{html.escape(m["title"])}</div>'
            f'<div class="meta">{m["year"]} • {m["duration"]} min • Dir. {html.escape(m["director"])}</div>'
            f'{chips_html(m)}{match_html(pct, reasons)}{ov}{avail_html(info)}{links_html(m)}'
            '</div></div>')


def spotlight_html(m, score, reasons, info, pct):
    ov = (f'<div class="ov">{html.escape(info["overview"][:380])}</div>'
          if info and info.get("overview") else "")
    return (f'<div class="spot">{poster_html(m, info)}<div class="info">'
            '<span class="crown">👑 TOP PICK FOR YOU</span>'
            f'<div class="t">{html.escape(m["title"])}</div>'
            f'<div class="meta" style="font-size:.9rem">{m["year"]} • {m["duration"]} min • '
            f'{html.escape(m["language"])} • Dir. {html.escape(m["director"])}</div>'
            f'{chips_html(m)}{match_html(pct, reasons)}{ov}{avail_html(info)}{links_html(m)}'
            '</div></div>')


def show_results(results, spotlight=True, cols=4):
    if not results:
        st.warning("No movies match these rules. Try lowering the rating or removing a filter.")
        return
    infos = {}
    if api_key:
        with st.spinner("Loading posters..."):
            infos = fetch_many([(m["title"], int(m["year"])) for m, _, _ in results], api_key, region)
    top = max(r[1] for r in results) or 1
    pct = lambda s: max(1, min(100, round(s / top * 100)))
    get = lambda m: infos.get((m["title"], int(m["year"])))

    rest = results
    if spotlight:
        m, s, r = results[0]
        st.markdown(spotlight_html(m, s, r, get(m), pct(s)), unsafe_allow_html=True)
        rest = results[1:]
        if rest:
            st.markdown('<div class="sec">More movies you may like</div>', unsafe_allow_html=True)
    columns = st.columns(cols)
    for i, (m, s, r) in enumerate(rest):
        with columns[i % cols]:
            st.markdown(card_html(m, s, r, get(m), pct(s)), unsafe_allow_html=True)


# ------------------------------------------------------------------ HERO
st.markdown(
    '<div class="hero"><h1>CineMatch</h1>'
    '<p>Your rule-based movie guide. Pick a mood, set your rules, and let CineMatch choose.</p>'
    f'<span class="stat"><b>{len(df)}</b> movies</span>'
    f'<span class="stat"><b>{len(all_langs)}</b> languages</span>'
    f'<span class="stat"><b>{len(all_genres)}</b> genres</span>'
    f'<span class="stat"><b>{len(all_moods)}</b> moods</span></div>',
    unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["✨ Recommend for me", "🔁 Similar to a movie", "📚 Browse all"])

with tab1:
    results = recommend(df, genre_pick, mood_pick, lang_pick, min_rating, max_dur, era_pick, top_n)
    st.markdown(f'<div class="sec">Your recommendations<span>{len(results)} movies ranked by rule score</span></div>',
                unsafe_allow_html=True)
    show_results(results)

with tab2:
    choice = st.selectbox("Pick a movie you liked", sorted(df["title"]), index=None,
                          placeholder="Type to search...")
    if choice:
        st.markdown(f'<div class="sec">Because you liked {html.escape(choice)}'
                    '<span>shared genre +3 • similar mood +2 • same director +4 • same language +1</span></div>',
                    unsafe_allow_html=True)
        show_results(similar_movies(df, choice), spotlight=False)

with tab3:
    st.markdown(f'<div class="sec">Full catalogue<span>{len(df)} movies</span></div>', unsafe_allow_html=True)
    st.dataframe(df[["title", "year", "genre", "mood", "language", "rating", "duration", "director"]],
                 use_container_width=True, hide_index=True, height=620)

st.markdown('<div class="foot">CineMatch • Rule-based AI mini project • Python + Streamlit • Data from TMDB</div>',
            unsafe_allow_html=True)