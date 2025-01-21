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
tab1, tab2, tab3 = st.tabs(
    ["🔍 Search Songs", "✍️ Songs with similar lyrics", "✍️ Songwriting Assistant"]
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
    st.subheader("✍️ Songs with similar lyrics")
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
            search_term = result['LYRICS'][0]
            st.write(
                f"Generating lyrics inspired by: **{result['SONG_TITLE'][0]}**")

            generated_lyrics = """
            Imagine a world without any walls,
            Where everyone can stand tall.
            No borders, no fights, just love in sight,
            Together we build a brighter light.
            """
            st.text_area("Generated Lyrics", generated_lyrics, height=150)

            st.markdown("### ✏️ Edit the Generated Lyrics")
            edited_lyrics = st.text_area(
                "Edit Lyrics Below:", generated_lyrics, height=150)
            if st.button("Save Changes"):
                st.success("Your changes have been saved!")
                st.text_area("Final Lyrics", edited_lyrics, height=150)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.info("Please search for a song in the **Search Songs** tab first.")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit", unsafe_allow_html=True)
