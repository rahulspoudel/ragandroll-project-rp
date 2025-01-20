import streamlit as st

st.title("Ly-Lyric App")

st.sidebar.title("Ly-Lyric")
options = st.sidebar.radio("Go to", [
                           "Lyric Analysis", "Mood-Based Recommendations", "Music Theory Explanation"])

if options == "Lyric Analysis":
    st.header("Lyric Analysis and Generation")

    sample_lyrics = "Here comes the sun, doo-doo-doo-doo..."
    st.text_area("Sample Lyrics", sample_lyrics, height=200)

    if st.button("Analyze Lyrics"):
        st.write("Analysis: The lyrics convey a positive and uplifting mood.")

    if st.button("Generate New Verse"):
        st.write("Generated Verse: And I say, it's all right...")

if options == "Mood-Based Recommendations":
    st.header("Mood-Based Song Recommendations")

    mood = st.text_input("Enter your current mood:", "happy")

    if st.button("Get Recommendations"):
        st.write(f"Songs that match the mood '{mood}':")
        st.write("- 'Happy' by Pharrell Williams")
        st.write("- 'Walking on Sunshine' by Katrina and the Waves")

if options == "Music Theory Explanation":
    st.header("Music Theory Explanation")

    term = st.text_input("Enter a musical term:", "cadence")

    if st.button("Explain Term"):
        st.write(f"Explanation of '{term}':")
        st.write(
            "A cadence is a sequence of chords that brings a phrase, section, or piece of music to a close.")
