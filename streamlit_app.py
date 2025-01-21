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
    escaped_prompt = prompt.replace("'", "''")
    query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mistral-large2',
        'Based on these lyrics, create a new version:\\n\\n{escaped_prompt} \\n Also donot include some of the last lines of the lyrics looking like this \\n ______________ \\n Name      Numb \\n Artist    Linkin Park \\n Album     Meteora \\n Track no  13 \\n Year      2003 \\n for this draft generation task \\n'
    ) AS draft
    """
    return session.sql(query).to_pandas()["DRAFT"][0]


def get_story_from_lyrics(prompt):
    escaped_prompt = prompt.replace("'", "''")
    query = f"""
    SELECT SNOWFLAKE.CORTEX.TRY_COMPLETE(
        'mistral-large2',
        'Based on these lyrics and artists and album details mentioned at the end the lyrics, write the original backstory of the song:\\n\\n{escaped_prompt}'
    ) AS story
    """
    return session.sql(query).to_pandas()["STORY"][0]


def query_cortex_search_service(query, limit=10):
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


def generate_translation(prompt, target_language):
    escaped_prompt = prompt.replace("'", "''")
    query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mistral-large2',
        'Translate these lyrics into {target_language} while preserving poetic structure and meaning:\\n\\n{escaped_prompt} \\n Also donot include some of the last lines of the lyrics looking like this \\n ______________ \\n Name      Numb \\n Artist    Linkin Park \\n Album     Meteora \\n Track no  13 \\n Year      2003 \\n for this translation.'
    ) AS translation
    """
    return session.sql(query).to_pandas()["TRANSLATION"][0]


# Page Configuration
st.set_page_config(
    page_title="Ly-Lyric App",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)


def gradient_text(text, gradient_colors):
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
st.markdown(
    "Find songs, create lyrics, and explore music in a whole new way with Ly-Lyric App! 🎵✨",
    unsafe_allow_html=True
)

# Initialize session state for result
if "search_result" not in st.session_state:
    st.session_state["search_result"] = None

# Tabs for the Application
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "🔍 Search Songs",
        "🎶 Songs with similar lyrics",
        "✍️ Songwriting Assistant",
        "📝 Lyrics Story",
        "🌎 Multi-Language Translation",
        "🎭 Mood-Based Recommendations",
        "🎨 Song to Art Generator"
    ]
)

# Tab 1: Search Songs
with tab1:
    st.subheader("🔍 Search for a Song")
    st.markdown(
        "Find your favorite songs by entering a song title, artist name, or lyrics snippet. Use this as your starting point for creative exploration!"
    )
    song_title = st.text_input(
        "Enter a song title, artist name, or some lyrics to begin:", ""
    )

    if st.button("Search"):
        if not song_title.strip():
            st.warning("Please enter a valid input.")
        else:
            query = f"""
            SELECT song_title, artist, album, lyrics
            FROM LYLYRIC
            WHERE LOWER(lyrics) LIKE '%{song_title.lower()}%'
            LIMIT 1
            """
            try:
                result = session.sql(query).to_pandas()
                if not result.empty:
                    st.session_state["search_result"] = result
                    st.write("🎵 **Song Found:**")
                    st.write(f"**Title:** {result['SONG_TITLE'][0]}")
                    st.write(f"**Artist:** {result['ARTIST'][0]}")
                    st.write(f"**Album:** {result['ALBUM'][0]}")
                else:
                    st.session_state["search_result"] = None
                    st.error(
                        "No matching song found. Try a different search term.")
            except Exception as e:
                st.session_state["search_result"] = None
                st.error(f"An error occurred while fetching data: {e}")

# Tab 2: Similar Songs and Lyrics
with tab2:
    st.subheader("🎶 Songs with similar lyrics")
    st.markdown(
        "Discover songs with lyrics similar in theme or tone to your search. Get inspired by related works from other artists!"
    )
    if st.session_state["search_result"] is not None:
        try:
            search_term = st.session_state["search_result"]['LYRICS'][0]
            results = query_cortex_search_service(search_term)

            if results:
                for item in results:
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown(
                                f"### 🎵 {item.get('song_title', 'Unknown Title')}"
                            )
                        with col2:
                            st.markdown(
                                f"**Artist:** {item.get('artist', 'Unknown Artist')}"
                            )
                            st.markdown(
                                f"**Album:** {item.get('album', 'Unknown Album')}"
                            )
                            st.text_area(
                                "Lyrics",
                                item.get('lyrics', 'No lyrics available'),
                                height=100,
                                key=f"lyrics_{item.get('song_title')}",
                            )
                        st.markdown("---")
            else:
                st.error("No similar songs found.")
        except Exception as e:
            st.error(f"An error occurred while fetching similar songs: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Tab 3: Songwriting Assistant
with tab3:
    st.subheader("✍️ Songwriting Assistant")
    st.markdown(
        "Generate new lyric drafts inspired by your selected song. Explore different tones, emotions, or styles to refine your creativity!"
    )
    if st.session_state["search_result"] is not None:
        try:
            search_term = st.session_state["search_result"]['LYRICS'][0]
            st.write(
                f"Generating draft lyrics inspired by: **{st.session_state['search_result']['SONG_TITLE'][0]}** by **{st.session_state['search_result']['ARTIST'][0]}**"
            )

            # Generate drafts using Snowflake Cortex
            st.write("### 🎵 Draft Versions")
            draft_1 = generate_draft(search_term)
            draft_2 = generate_draft(search_term + "\nMake it very funny.")
            draft_3 = generate_draft(
                search_term + "\nMake it simpler and inspiring.")

            # Display drafts for user review
            st.text_area("Draft 1 (Normal)", draft_1,
                         height=300, key="draft_1")
            st.text_area("Draft 2 (Funny)", draft_2, height=300, key="draft_2")
            st.text_area("Draft 3 (Inspiring)", draft_3,
                         height=300, key="draft_3")

            # Placeholder for future editing feature
            st.markdown("### ✏️ Edit and Finalize Your Lyrics")
            st.text("Feature coming soon: Select and finalize your favorite draft.")

        except Exception as e:
            st.error(f"An error occurred while generating lyrics: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Tab 4: Lyrics Story
with tab4:
    st.subheader("📝 Lyrics Story")
    st.markdown(
        "Uncover the story behind the song. Get insights into the inspiration and background that shaped the lyrics."
    )
    if st.session_state["search_result"] is not None:
        try:
            search_term = st.session_state["search_result"]['LYRICS'][0]
            st.write(
                f"Story behind the song: **{st.session_state['search_result']['SONG_TITLE'][0]}** by **{st.session_state['search_result']['ARTIST'][0]}**"
            )

            # Generate story using Snowflake Cortex
            st.write("### 🎵 Story of the Song")
            story = get_story_from_lyrics(search_term)

            # Display the story
            st.text_area("Story", story, height=300, key="story")

        except Exception as e:
            st.error(f"An error occurred while fetching the story: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Tab 5: Multi-Language Lyrics Translation
with tab5:
    st.subheader("🌎 Multi-Language Lyrics Translation")
    st.markdown(
        "Translate lyrics into multiple languages while maintaining their poetic structure and essence. Perfect for reaching a global audience!"
    )
    available_languages = ["Spanish", "French", "German", "Japanese", "Nepali"]

    if st.session_state["search_result"] is not None:
        original_lyrics = st.session_state["search_result"]['LYRICS'][0]
        st.text_area("Original Lyrics", original_lyrics, height=200)

        target_language = st.selectbox(
            "Select a language for translation:", available_languages, key="target_language"
        )

        if st.button("Translate Lyrics", key="translate"):
            try:
                translated_lyrics = generate_translation(
                    original_lyrics, target_language)
                st.text_area(
                    f"Translated Lyrics in {target_language}", translated_lyrics, height=200
                )
            except Exception as e:
                st.error(f"An error occurred while translating lyrics: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Tab 6: Mood-Based Recommendations
with tab6:
    st.subheader("🎭 Mood-Based Recommendations (Comming soon)")
    st.markdown(
        "Describe your mood, and we'll recommend songs that resonate with your feelings. Perfect for curating playlists or finding the right vibe!"
    )

# Tab 7: Song to Art Generation
with tab7:
    st.subheader("🎨 Song to Art Generator (Comming soon)")
    st.markdown(
        "Generate artwork inspired by a song. Use lyrics and mood to create a visual representation of the song's essence. (Coming Soon!)"
    )

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit", unsafe_allow_html=True)
