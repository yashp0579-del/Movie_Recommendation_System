# 🎬 CineMatch - Rule-Based Movie Recommendation System

An AI mini project that recommends movies using hand-written IF-THEN rules (no machine learning). Built with Python and Streamlit.

**Live demo:** PASTE-YOUR-STREAMLIT-LINK-HERE

![App screenshot](screenshot.png)

## Features
- 200 movies across Hollywood, Bollywood, South Indian, Korean, Japanese and European cinema
- Recommendations by mood, genre, language, era, minimum rating and maximum duration
- "Similar to a movie" mode
- Match percentage and a reason for every recommendation
- Real posters, overviews and streaming platforms from the TMDB API
- Dark, colourful interface

## How it works
**Hard rules** (a movie is rejected if it fails any one):
- Language matches the user's choice
- Rating is at least the minimum
- Duration is within the limit
- Release year falls in the chosen era

**Scoring rules** (decide the ranking):
| Rule | Points |
|---|---|
| Each matching genre | +3 |
| Each matching mood | +3 |
| Rating 8.5 or above | +2 |
| Rating 8.0 to 8.4 | +1 |
| Rating ÷ 10 | tie-breaker |

**Similar-movie rules:** same director +4, shared genre +3 each, shared mood +2 each, same language +1.

## Tech stack
Python, Streamlit, Pandas, Requests, CSS, TMDB API

## Project structure
```
├── app.py            # Streamlit interface
├── recommender.py    # Rule-based engine
├── tmdb.py           # Poster and streaming data from TMDB
├── movies.csv        # Dataset of 200 movies
└── requirements.txt  # Python packages
```

## Run it locally
```bash
git clone https://github.com/YOUR-USERNAME/Movie_Recommendation_System.git
cd Movie_Recommendation_System
pip install -r requirements.txt
streamlit run app.py
```

## Posters (optional)
1. Get a free API key at [themoviedb.org](https://www.themoviedb.org/) (Settings, then API).
2. Paste it into the sidebar box in the app, or create `.streamlit/secrets.toml` containing:
```
TMDB_API_KEY = "your_key_here"
```

## Limitations
- Rules are written by hand, so the system doesn't learn from user behaviour
- Limited to 200 movies
- Posters and streaming info need internet and a TMDB key

## Future scope
- Add machine learning (collaborative filtering)
- User accounts and watch history
- A much larger dataset

## Author
YOUR NAME - YOUR COLLEGE, YOUR COURSE
This product uses the TMDB API but is not endorsed or certified by TMDB.
