import streamlit as st
from snowflake.snowpark import Session
from snowflake.core import Root

# Snowflake connection
connection_parameters = {
    "account": st.secrets["snowflakeconnection"]["account"],
    "user": st.secrets["snowflakeconnection"]["user"],
    "password": st.secrets["snowflakeconnection"]["password"],
    "warehouse": st.secrets["snowflakeconnection"]["warehouse"],
    "database": st.secrets["snowflakeconnection"]["database"],
    "schema": st.secrets["snowflakeconnection"]["schema"],
}

session = Session.builder.configs(connection_parameters).create()
root = Root(session)


def generate_draft(prompt):
    # Escape any single quotes in the prompt
    escaped_prompt = prompt.replace("'", "''")

    # query = f"""
    # SELECT SNOWFLAKE.CORTEX.COMPLETE(
    #     PARSE_JSON('{{"model": "mistral-large2", "prompt": "Based on these lyrics, create a new version:\\n\\n{escaped_prompt}"}}'::string)
    # ) AS draft
    # """
    query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', 'Based on these lyrics, create a new version:\\n\\n{escaped_prompt}') AS draft
    """
    return session.sql(query).to_pandas()["DRAFT"][0]


def get_story_from_lyrics(prompt):
    # Escape any single quotes in the prompt
    escaped_prompt = prompt.replace("'", "''")

    query = f"""
    SELECT SNOWFLAKE.CORTEX.TRY_COMPLETE('mistral-large2', 'Based on these lyrics and artists and album details mentioned at the end the lyrics, write the original backstory of the song:\\n\\n{escaped_prompt}') AS story
    """
    return session.sql(query).to_pandas()["STORY"][0]


def query_cortex_search_service(query, limit=10):
    """
    Query the Cortex Search Service for similar lyrics.
    """
    cortex_search_service = (
        root.databases[st.secrets["snowflakeconnection"]["database"]]
        .schemas[st.secrets["snowflakeconnection"]["schema"]]
        .cortex_search_services[st.secrets["snowflakeconnection"]["service_lyr"]]
    )
    results = cortex_search_service.search(
        query=query,
        columns=["lyrics", "song_title", "artist", "album"],
        limit=limit
    )
    return results.results


# Page Configuration
st.set_page_config(
    page_title="Ly-Lyric App",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)


def gradient_text(text, gradient_colors):
    """
    Display gradient-styled text for headers.
    """
    html_code = f"""
    <h1 style="
    background: linear-gradient(to right, {', '.join(gradient_colors)});
    -webkit-background-clip: text;
    color: transparent;
    font-size: 3rem;
    font-weight: bold;
    text-align: center;
    margin: 0;">
    {text}
    </h1>
    """
    st.markdown(html_code, unsafe_allow_html=True)


# App Title
gradient_text("🎶 Ly-Lyric App 🎶", ["#ff512f", "#dd2476", "#8e44ad"])

# Initialize global variable for result
result = None

# Tabs for the Application
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Search Songs", "🎶 Songs with similar lyrics",
        "✍️ Songwriting Assistant", "📝 Lyrics Story"]
)

# Tab 1: Search Songs
with tab1:
    st.subheader("🔍 Search for a Song")
    song_title = st.text_input(
        "Enter a song title or artist name or some lyrics words to begin:", "")

    if st.button("Search"):
        if not song_title.strip():
            st.warning("Please enter a valid song title or artist name.")
        else:
            # query = f"""
            # SELECT song_title, artist, album, lyrics
            # FROM LYLYRIC
            # WHERE LOWER(song_title) LIKE '%{song_title.lower()}%'
            # OR LOWER(artist) LIKE '%{song_title.lower()}%'
            # OR LOWER(album) LIKE '%{song_title.lower()}%'
            # LIMIT 1
            # """
            query = f"""
            SELECT song_title, artist, album, lyrics
            FROM LYLYRIC
            WHERE LOWER(lyrics) LIKE '%{song_title.lower()}%'
            LIMIT 1
            """
            try:
                result = session.sql(query).to_pandas()

                if not result.empty:
                    st.write("🎵 **Song Found:**")
                    st.write(f"**Title:** {result['SONG_TITLE'][0]}")
                    st.write(f"**Artist:** {result['ARTIST'][0]}")
                    st.write(f"**Album:** {result['ALBUM'][0]}")
                else:
                    result = None
                    st.error(
                        "No matching song found. Try a different search term.")
            except Exception as e:
                result = None
                st.error(f"An error occurred while fetching data: {e}")

# Tab 2: Similar Songs and Lyrics
with tab2:
    st.subheader("🎶 Songs with similar lyrics")
    if result is not None and not result.empty:
        try:
            search_term = result['LYRICS'][0]
            results = query_cortex_search_service(search_term)

            if results:
                # st.write("🎵 **Similar Songs:**")
                for item in results:
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown(
                                f"### 🎵 {item.get('song_title', 'Unknown Title')}")
                        with col2:
                            st.markdown(
                                f"**Artist:** {item.get('artist', 'Unknown Artist')}")
                            st.markdown(
                                f"**Album:** {item.get('album', 'Unknown Album')}")
                            st.text_area("Lyrics", item.get('lyrics', 'No lyrics available'),
                                         height=100, key=f"lyrics_{item.get('song_title')}")
                        st.markdown("---")  # Divider between cards
            else:
                st.error("No similar songs found.")
        except Exception as e:
            st.error(f"An error occurred while fetching similar songs: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")


# Tab 3: Songwriting Assistant
with tab3:
    st.subheader("✍️ Songwriting Assistant")
    if result is not None and not result.empty:
        try:
            # Use the closest matching lyrics as the search term
            search_term = result['LYRICS'][0]
            st.write(
                f"Generating draft lyrics inspired by: **{result['SONG_TITLE'][0]}** by **{result['ARTIST'][0]}**"
            )

            st.write("### 🎵 Draft Versions")
            draft_1 = generate_draft(search_term)
            draft_2 = generate_draft(search_term + "\nMake it very funny.")
            # draft_3 = generate_draft(
            #     search_term + "\nMake it simpler and inspiring.")

            # Using the same draft for limiting the hits
            # draft_2 = draft_1
            draft_3 = draft_1

            # Display drafts for user review
            st.text_area("Draft 1 (Normal)", draft_1,
                         height=300, key="draft_1")
            st.text_area("Draft 2 (Funny)", draft_2, height=300, key="draft_2")
            st.text_area("Draft 3 (Normal)", draft_3,
                         height=300, key="draft_3")

            st.markdown("### ✏️ Edit and Finalize Your Lyrics")
            st.text("Feature coming soon")
            # selected_draft = st.radio(
            #     "Select a draft to edit:",
            #     options=["Draft 1", "Draft 2", "Draft 3"],
            #     index=0
            # )
            # draft_content = draft_1 if selected_draft == "Draft 1" else (
            #     draft_2 if selected_draft == "Draft 2" else draft_3
            # )

            # edited_lyrics = st.text_area(
            #     "Edit Lyrics Below:",
            #     draft_content,
            #     height=150,
            #     key="edited_lyrics"
            # )

            # if st.button("Save Changes"):
            #     st.success("Your changes have been saved!")
            #     st.text_area("Final Lyrics", edited_lyrics, height=150)

        except Exception as e:
            st.error(f"An error occurred while generating lyrics: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Tab 4: Lyrics Story
with tab4:
    st.subheader("📝 Lyrics Story")
    if result is not None and not result.empty:
        try:
            # Use the closest matching lyrics as the search term
            search_term = result['LYRICS'][0]
            st.write(
                f"Story behind the song: **{result['SONG_TITLE'][0]}** by **{result['ARTIST'][0]}**"
            )

            st.write("### 🎵 Story of the song and lyric")
            draft_story = get_story_from_lyrics(search_term)

            # Display drafts for user review
            st.text_area("", draft_story,
                         height=300, key="draft_story")

        except Exception as e:
            st.error(f"An error occurred while getting story: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit", unsafe_allow_html=True)
