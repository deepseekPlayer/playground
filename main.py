import streamlit as st
import chess
import chess.svg
import base64
import time
from streamlit_js_eval import streamlit_js_eval

# --------------------------------------------------------------------
# Streamlit Page Configuration
# --------------------------------------------------------------------
st.set_page_config(page_title="Deepseek R1 vs Legacy Stockfish", page_icon="♟")
st.title("Deepseek R1 vs Legacy Stockfish")

# --------------------------------------------------------------------
# Session State Initialization
# --------------------------------------------------------------------
if "chess_board" not in st.session_state:
    st.session_state.chess_board = chess.Board()

# Create a placeholder for the chess board display
board_placeholder = st.empty()

# Hardcoded full game (Anderssen’s Immortal Game) as a list of move tuples.
# Each tuple is (white_move, black_move) except the final one which is only White's mate move.
if "hardcoded_moves" not in st.session_state:
    st.session_state.hardcoded_moves = [
        ("e4", "e5"),
        ("f4", "exf4"),
        ("Bc4", "Qh4+"),
        ("Kf1", "b5"),
        ("Bxb5", "Nf6"),
        ("Nf3", "Qh6"),
        ("d3", "Nh5"),
        ("Nh4", "Qg5"),
        ("Nf5", "c6"),
        ("g4", "Nf6"),
        ("Rg1", "cxb5"),
        ("h4", "Qg6"),
        ("h5", "Qg5"),
        ("Qf3", "Ng8"),
        ("Bxf4", "Qf6"),
        ("Nc3", "Bc5"),
        ("Nd5", "Qxb2"),
        ("Bd6", "Bxd6"),
        ("Nxd6+", "Kd8"),
        ("Bc7#",)
    ]

if "current_move_index" not in st.session_state:
    st.session_state.current_move_index = 0

# Hardcoded log messages for each move pair stored as tuples (white_log, black_log).
# These logs simply state the move and a brief reason.
if "move_log_pairs" not in st.session_state:
    st.session_state.move_log_pairs = [
        (
            "Deepseek R1 (White) played e4 to control the center",
            "Legacy Stockfish (Black) played e5 to contest central control"
        ),
        (
            "Deepseek R1 advanced f4 to open lines",
            "Legacy Stockfish captured with exf4 to challenge White's structure"
        ),
        (
            "Deepseek R1 developed bishop to c4 targeting f7",
            "Legacy Stockfish checked with Qh4+ to disturb king safety"
        ),
        (
            "Deepseek R1 moved king to f1 to escape check",
            "Legacy Stockfish pushed b5 to attack the bishop"
        ),
        (
            "Deepseek R1 captured on b5 with the bishop",
            "Legacy Stockfish developed knight to f6 to control key squares"
        ),
        (
            "Deepseek R1 developed knight to f3 for kingside activity",
            "Legacy Stockfish repositioned queen to h6 to support counterplay"
        ),
        (
            "Deepseek R1 played d3 to solidify the center",
            "Legacy Stockfish moved knight to h5 for an aggressive posture"
        ),
        (
            "Deepseek R1 repositioned knight to h4 to increase pressure",
            "Legacy Stockfish moved queen to g5 to keep up the pressure"
        ),
        (
            "Deepseek R1 advanced knight to f5 to intensify the attack",
            "Legacy Stockfish played c6 to challenge White's advanced knight"
        ),
        (
            "Deepseek R1 pushed g4 to support the attack",
            "Legacy Stockfish reactivated knight to f6 for defense"
        ),
        (
            "Deepseek R1 activated the rook along the g-file",
            "Legacy Stockfish captured on b5 with cxb5 to open lines"
        ),
        (
            "Deepseek R1 advanced h4 to restrict enemy moves",
            "Legacy Stockfish shifted queen to g6 to seek counterplay"
        ),
        (
            "Deepseek R1 pushed h5 to further disturb Black's position",
            "Legacy Stockfish moved queen to g5, maintaining pressure"
        ),
        (
            "Deepseek R1 centralized the queen on f3 for coordination",
            "Legacy Stockfish retreated knight to g8 for regrouping"
        ),
        (
            "Deepseek R1 captured with bishop on f4 to remove a pawn",
            "Legacy Stockfish centralized queen to f6 to contest the board"
        ),
        (
            "Deepseek R1 developed knight to c3 to bolster central control",
            "Legacy Stockfish developed bishop to c5 to target weaknesses"
        ),
        (
            "Deepseek R1 moved knight to d5 to create threats",
            "Legacy Stockfish captured on b2 with the queen to gain material"
        ),
        (
            "Deepseek R1 advanced bishop to d6 to increase pressure",
            "Legacy Stockfish exchanged bishop on d6 to ease the tension"
        ),
        (
            "Deepseek R1 captured on d6 with knight delivering check",
            "Legacy Stockfish moved king to d8 to escape the check"
        ),
        (
            "Deepseek R1 delivered checkmate with Bc7#, ending the game",
            ""
        )
    ]

if "current_white_log" not in st.session_state:
    st.session_state.current_white_log = ""
if "current_black_log" not in st.session_state:
    st.session_state.current_black_log = ""

if "error_message" not in st.session_state:
    st.session_state.error_message = ""

# Logo URLs for each side (replace with your own images if desired).
deepseek_logo_url = "https://images.seeklogo.com/logo-png/61/3/deepseek-ai-icon-logo-png_seeklogo-611473.png?v=1956059979301376232"
stockfish_logo_url = "https://preview.redd.it/hl0tiwfkdjc71.png?width=330&format=png&auto=webp&s=68da8eb870d174dac66f3a7ab79ca677cf13945d"


# --------------------------------------------------------------------
# Helper Function: Render SVG for Streamlit
# --------------------------------------------------------------------
def render_svg(svg_string: str) -> str:
    """
    Converts an SVG string to an HTML <img> tag for display.
    """
    b64 = base64.b64encode(svg_string.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}"/>'

# --------------------------------------------------------------------
# Function to Process the Next Move Pair and Update the Logs
# --------------------------------------------------------------------
def process_next_move_pair():
    time.sleep(2)
    try:
        board = st.session_state.chess_board
        moves = st.session_state.hardcoded_moves
        idx = st.session_state.current_move_index

        if idx >= len(moves):
            st.session_state.error_message = "Game is already over!"
            return

        move_pair = moves[idx]
        log_pair = st.session_state.move_log_pairs[idx]

        # Process White's move (Deepseek R1)
        white_move = move_pair[0]
        board.push_san(white_move)
        st.session_state.current_white_log = log_pair[0]
        st.session_state.current_black_log = ""

        # Update the board placeholder after White's move
        board_svg = chess.svg.board(board=board)
        board_placeholder.write(render_svg(board_svg), unsafe_allow_html=True)
        time.sleep(2)  # Pause to visualize White's move

        # Process Black's move (Legacy Stockfish) if available
        if len(move_pair) == 2:
            black_move = move_pair[1]
            board.push_san(black_move)
            st.session_state.current_black_log = log_pair[1]

            # Update the board placeholder after Black's move
            board_svg = chess.svg.board(board=board)
            board_placeholder.write(render_svg(board_svg), unsafe_allow_html=True)
            # time.sleep(2)  # Pause to visualize Black's move

        st.session_state.current_move_index += 1
        st.session_state.error_message = ""
    except Exception as e:
        st.session_state.error_message = f"Error: {e}"
        st.session_state.current_white_log = ""
        st.session_state.current_black_log = ""


# --------------------------------------------------------------------
# Button: Advance the Game with the Next Move Pair
# --------------------------------------------------------------------
st.button("Advance Move Pair (White & Black)", on_click=process_next_move_pair)

if st.button("Reset Board"):
    streamlit_js_eval(js_expressions="parent.window.location.reload()")

# --------------------------------------------------------------------
# Error / Status Display
# --------------------------------------------------------------------
if st.session_state.error_message:
    st.error(st.session_state.error_message, icon="🚨")

# --------------------------------------------------------------------
# Render the Current Board
# --------------------------------------------------------------------
board_svg = chess.svg.board(board=st.session_state.chess_board)
st.write(render_svg(board_svg), unsafe_allow_html=True)

if st.session_state.chess_board.is_game_over():
    st.info("Game Over!", icon="🏁")

# --------------------------------------------------------------------
# Display the Current Move Log with Logos
# --------------------------------------------------------------------
if st.session_state.current_white_log or st.session_state.current_black_log:
    st.markdown("### Current Move")
    cols = st.columns(2)
    with cols[0]:
        st.image(deepseek_logo_url, width=50)
        st.write(st.session_state.current_white_log)
    with cols[1]:
        if st.session_state.current_black_log:
            st.image(stockfish_logo_url, width=50)
            st.write(st.session_state.current_black_log)

# --------------------------------------------------------------------
# Move History Display (Chronological Order)
# --------------------------------------------------------------------
st.markdown("### Move Log")

# Display the entire move history dynamically
if "move_history" not in st.session_state:
    st.session_state.move_history = []

# Append the latest move logs if not already added
if st.session_state.current_white_log and (st.session_state.current_white_log not in st.session_state.move_history):
    st.session_state.move_history.append(st.session_state.current_white_log)
if st.session_state.current_black_log and (st.session_state.current_black_log not in st.session_state.move_history):
    st.session_state.move_history.append(st.session_state.current_black_log)

# Show the move log in a scrollable format
with st.expander("📜 View Move Log", expanded=True):
    for move_log in st.session_state.move_history:
        st.markdown(f"- {move_log}")
