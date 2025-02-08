import base64
import chess
import chess.svg
import re
from stockfish import Stockfish
from openai import OpenAI
import os
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate

# --------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------
CHARACTER = "robo"

# Prompt template for commentary
character_prompt = PromptTemplate(
    input_variables=["character", "white_move", "black_move"],
    template="""
You are playing a game of chess and responding to each pair of moves. The moves
are being computed by the Stockfish chess engine. I want you to focus on
communicating with me in the voice of {character}. 
Don't comment on overall strategy or the state of the game as you cannot know
the game better than Stockfish. Make sure you talk like {character}.
After you respond, explicitly mention the two moves that were just played in
your text. Write at least 6 sentences in your response. Do not include any
explanatory text or quotes.
White's move: {white_move}
Black's move: {black_move}
"""
)

# Regular expression to remove chain-of-thought or hidden text if the LLM produces any
chain_of_thought_regex = re.compile(r"<think>.*?</think>", flags=re.DOTALL)

# --------------------------------------------------------------------
# Streamlit & OpenAI initialization
# --------------------------------------------------------------------
st.set_page_config(page_title="robo chess", page_icon="♟")
st.title("robo Chess: (No User Moves)")

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.environ["E2E_TIR_ACCESS_TOKEN"],
    base_url="https://infer.e2enetworks.net/project/p-4827/genai/deepseek_r1/v1"
)

# --------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------
def render_svg(svg_string: str) -> str:
    """
    Converts an SVG string to HTML <img> so Streamlit can display it.
    """
    b64 = base64.b64encode(svg_string.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}"/>'

def get_language_response(prompt: str) -> str:
    """
    Sends the prompt to the R1 model and returns its text response.
    """
    response = client.chat.completions.create(
        model="deepseek_r1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.8
    )
    # Remove chain-of-thought tags, if any
    text = chain_of_thought_regex.sub("", response.choices[0].message.content)
    return text.strip()

# --------------------------------------------------------------------
# Session State: Board, Stockfish, Moves, Chat History
# --------------------------------------------------------------------
if "stockfish_engine" not in st.session_state:
    # Point to your Stockfish binary
    stockfish_path = r"C:\Users\ALL\Downloads\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
    if not os.path.isfile(stockfish_path):
        raise FileNotFoundError(
            f"Stockfish binary not found at path: {stockfish_path}. "
            "Please ensure the Stockfish engine is present at the specified path."
        )
    # Create engine
    st.session_state.stockfish_engine = Stockfish(path=stockfish_path)

    # Create fresh board
    st.session_state.board = chess.Board()

    # Initialize list to store LLM commentary
    st.session_state.commentaries = []
    st.session_state.error_message = ""

engine = st.session_state.stockfish_engine
board = st.session_state.board

# Keep engine in sync with current board
engine.set_fen_position(board.fen())

# --------------------------------------------------------------------
# Button to Make Next Moves (White then Black), then get commentary
# --------------------------------------------------------------------
def make_pair_of_moves():
    """
    1. White move by Stockfish
    2. Check if game is over; if not, Black move
    3. Get commentary from R1 (Yoda) based on these two moves
    """
    try:
        if board.is_game_over():
            st.session_state.error_message = "Game is already over!"
            return

        # -----------------------------
        # White's move
        # -----------------------------
        white_move_uci = engine.get_best_move()
        if not white_move_uci:
            st.session_state.error_message = "No valid move returned by Stockfish (White)."
            return
        white_move_obj = chess.Move.from_uci(white_move_uci)
        board.push(white_move_obj)
        white_san = board.san(white_move_obj)

        # Check if the game ended right after White's move
        if board.is_game_over():
            engine.set_fen_position(board.fen())
            st.session_state.error_message = "Game ended after White's move!"
            return

        # -----------------------------
        # Black's move
        # -----------------------------
        engine.set_fen_position(board.fen())  # Sync engine
        black_move_uci = engine.get_best_move()
        if not black_move_uci:
            st.session_state.error_message = "No valid move returned by Stockfish (Black)."
            return
        black_move_obj = chess.Move.from_uci(black_move_uci)
        board.push(black_move_obj)
        black_san = board.san(black_move_obj)

        # Sync engine again
        engine.set_fen_position(board.fen())

        # -----------------------------
        # Now get Yoda commentary
        # -----------------------------
        prompt = character_prompt.format(
            character=CHARACTER,
            white_move=white_san,
            black_move=black_san
        )
        commentary_text = get_language_response(prompt)

        # Add commentary to session
        st.session_state.commentaries.append(commentary_text)
        st.session_state.error_message = ""

    except Exception as e:
        st.session_state.error_message = f"Error: {e}"

st.button("Make next moves (White & Black)", on_click=make_pair_of_moves)

# --------------------------------------------------------------------
# Error / Status Display
# --------------------------------------------------------------------
if st.session_state.error_message:
    st.error(st.session_state.error_message, icon="🚨")

# --------------------------------------------------------------------
# Render the current board
# --------------------------------------------------------------------
board_svg = chess.svg.board(board=board)
st.write(render_svg(board_svg), unsafe_allow_html=True)

# If the game ended, let the user know
if board.is_game_over():
    st.info("Game Over!", icon="🏁")

# --------------------------------------------------------------------
# Show the commentary in descending order (most recent first)
# --------------------------------------------------------------------
if st.session_state.commentaries:
    st.markdown("### Commentary")
    for i in range(len(st.session_state.commentaries) - 1, -1, -1):
        message(st.session_state.commentaries[i], key=str(i))
