# 🎶 Ly-Lyric App

Ly-Lyric App is an interactive platform powered by **Snowflake Cortex Search**, **Mistral-large2** and **Streamlit** designed for music enthusiasts and lyricists. Discover songs, generate creative lyrics, explore stories behind songs, translate lyrics into multiple languages, and much more.

While the app leverages advanced **LLM (Large Language Model)** capabilities for creative generation and translations, some outputs may vary in accuracy and should be considered as creative suggestions rather than absolute interpretations.

> Data used for this project is from the github repo [Open Lyrics Database](https://github.com/Lyrics/lyrics-database). Being used for experimental purpose in this project.

> Submission for hackathon - RAG 'n' ROLL Amp up Search with Snowflake & Mistral ( https://snowflake-mistral-rag.devpost.com/ )
---

## 🌟 Features

1. **Search Songs**
   Find songs by title, artist, or lyrics.

2. **Songs with Similar Lyrics**
   Discover songs with lyrics similar in theme or tone to your search, enabled by **semantic search capabilities** of Cortex.

3. **Songwriting Assistant**
   Generate multiple drafts of lyrics inspired by your favorite songs. These drafts are created using the **Mistral-large2** model, offering various tones and styles.

4. **Lyrics Story**
   Dive into the backstory and inspiration behind the lyrics of a song, crafted using the **Mistral-large2** model.

5. **Multi-Language Lyrics Translation**
   Translate lyrics into popular languages like Spanish, French, German, Japanese, and Nepali. While the translations use advanced **LLM technology**, the poetic and contextual accuracy may not always be perfect.

6. **Mood-Based Recommendations (Coming Soon)**
   Describe your mood, and we'll recommend songs that resonate with your feelings, using **Cortex Search** and **LLM-based interpretations**.

7. **Song to Art Generator (Coming Soon)**
   Generate stunning artwork inspired by song lyrics and mood, offering a visual representation of the song's essence.

---

## 🚀 How to Run It on Your Machine

### Prerequisites

- Python 3.8+
- Snowflake account with **Cortex Search** and **LLM capabilities enabled**
- API keys or secret configurations stored in `secrets.toml` (as used in Streamlit)

### Steps

1. Clone this repository:

   > git clone https://github.com/yourusername/ly-lyric-app.git

2. Navigate to the project directory:

   > cd ly-lyric-app

3. Install the dependencies:

   > pip install -r requirements.txt

4. Run the app:

   > streamlit run streamlit_app.py

5. Open your browser and navigate to: http://localhost:8501

> Note: Features and entire project is being developed experimentally.
