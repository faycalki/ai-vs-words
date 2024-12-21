# Author: Faycal Kilali
# Version: 0.1

import streamlit as st
import pandas as pd
import plotly.express as px
from aivswords_backend import (
    make_word_list,
    check_letters,
    calculate_entropy,
    simulate_guess_patterns,
    is_consistent,
    get_wrong_letters
)


def initialize_session_state():
    if 'word_list' not in st.session_state:
        st.session_state.word_list = make_word_list("linuxwords.txt", 5, False)
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_solution_space' not in st.session_state:
        st.session_state.current_solution_space = st.session_state.word_list.copy()
    if 'guesses_made' not in st.session_state:
        st.session_state.guesses_made = []
    if 'target_word' not in st.session_state:
        st.session_state.target_word = None


def reset_game():
    st.session_state.current_solution_space = st.session_state.word_list.copy()
    st.session_state.history = []
    st.session_state.guesses_made = []
    st.session_state.target_word = None


def display_header():
    st.title("Information Theory Word Solver")
    st.markdown("""
    This application demonstrates how Information Theory can be used to solve Word puzzles efficiently.
    The solver uses entropy and information gain to make optimal guesses.
    """)


def display_word_input():
    col1, col2 = st.columns([3, 1])
    with col1:
        target_word = st.text_input(
            "Enter a 5-letter target word:",
            key="word_input",
            max_chars=5
        ).lower()
    with col2:
        if st.button("Start New Game"):
            reset_game()
    return target_word


def display_game_stats():
    st.subheader("Game Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Remaining Words", len(st.session_state.current_solution_space))
    with col2:
        st.metric("Guesses Made", len(st.session_state.guesses_made))
    with col3:
        if st.session_state.current_solution_space:
            entropy = calculate_entropy(st.session_state.current_solution_space)
            st.metric("Current Entropy", f"{entropy:.2f} bits")


def display_guess_history():
    if st.session_state.history:
        st.subheader("Guess History")
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df)


def display_solution_space_viz():
    if st.session_state.current_solution_space:
        st.subheader("Solution Space Distribution")
        # Create a simple visualization of first letters distribution
        first_letters = pd.DataFrame(
            [word[0] for word in st.session_state.current_solution_space],
            columns=['First Letter']
        )
        letter_counts = first_letters['First Letter'].value_counts()
        fig = px.bar(
            x=letter_counts.index,
            y=letter_counts.values,
            title="Distribution of First Letters in Remaining Words",
            labels={'x': 'Letter', 'y': 'Count'}
        )
        st.plotly_chart(fig)


def make_guess():
    if st.session_state.target_word and st.session_state.current_solution_space:
        # Simulate the next best guess
        next_guess = None
        max_entropy = float('-inf')

        # Take a sample of words for efficiency in the UI
        sample_size = min(100, len(st.session_state.current_solution_space))
        sample_words = st.session_state.current_solution_space[:sample_size]

        for candidate in sample_words:
            _, entropy = simulate_guess_patterns(candidate, st.session_state.current_solution_space)
            if entropy > max_entropy:
                max_entropy = entropy
                next_guess = candidate

        if next_guess:
            clue = check_letters(st.session_state.target_word, next_guess)
            st.session_state.guesses_made.append(next_guess)

            # Update history
            st.session_state.history.append({
                'Guess': next_guess,
                'Clue': clue,
                'Remaining Words': len(st.session_state.current_solution_space),
                'Information Gain': max_entropy
            })

            # Update solution space
            new_space = [
                word for word in st.session_state.current_solution_space
                if is_consistent(word, clue, get_wrong_letters(next_guess, clue))
            ]
            st.session_state.current_solution_space = new_space

            return next_guess, clue
    return None, None


def main():
    initialize_session_state()
    display_header()

    target_word = display_word_input()

    if target_word and len(target_word) == 5 and target_word.isalpha():
        st.session_state.target_word = target_word

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Make Guess"):
                guess, clue = make_guess()
                if guess:
                    if clue == target_word.upper():
                        st.success(f"Solved in {len(st.session_state.guesses_made)} guesses!")
                    elif len(st.session_state.guesses_made) >= 6:
                        st.error("Out of guesses!")

        display_game_stats()
        display_guess_history()
        display_solution_space_viz()

        with st.expander("View Current Solution Space"):
            st.write(st.session_state.current_solution_space)

    elif target_word:
        st.error("Please enter a valid 5-letter word.")


if __name__ == "__main__":
    main()