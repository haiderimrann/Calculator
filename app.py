import ast
import html

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Simple Calculator", page_icon=":abacus:")

st.markdown(
    """
<style>
:root {
    --bg-a: #041124;
    --bg-b: #0b2445;
    --bg-c: #113f67;
    --text-main: #eef6ff;
    --text-soft: #bfd4ff;
    --glass: rgba(8, 18, 38, 0.72);
    --glass-border: rgba(125, 211, 252, 0.32);
    --btn-a: #0ea5e9;
    --btn-b: #2563eb;
}

@keyframes aurora {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes titlePulse {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-2px); }
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 85% 5%, rgba(14, 165, 233, 0.22), transparent 32%),
                radial-gradient(circle at 12% 90%, rgba(34, 211, 238, 0.16), transparent 28%),
                linear-gradient(130deg, var(--bg-a), var(--bg-b), var(--bg-c), #06213f);
    background-size: 240% 240%;
    animation: aurora 16s ease infinite;
}

[data-testid="stHeader"] {
    background: transparent;
}

.hero {
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.82), var(--glass));
    backdrop-filter: blur(8px);
    padding: 1rem 1.05rem 0.9rem;
    margin-bottom: 0.7rem;
}

.hero .hero-title {
    margin: 0;
    color: #f8fbff !important;
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: 0.01em;
    text-shadow: 0 0 18px rgba(56, 189, 248, 0.45);
    animation: titlePulse 3.2s ease-in-out infinite;
}

.hero-sub {
    margin: 0.35rem 0 0;
    color: var(--text-soft);
    font-size: 0.93rem;
}

.display-box {
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    background: rgba(10, 20, 40, 0.8);
    color: #f8fbff;
    padding: 18px 20px;
    font-size: 2rem;
    text-align: right;
    margin-bottom: 0.55rem;
    word-break: break-all;
}

.stTextInput label {
    color: #dbeafe !important;
    font-weight: 600 !important;
}

.stTextInput input {
    background: rgba(15, 23, 42, 0.82) !important;
    color: #f8fafc !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 10px !important;
}

.stButton button {
    height: 58px;
    font-size: 1.08rem !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: 1px solid rgba(125, 211, 252, 0.45) !important;
    background: linear-gradient(90deg, var(--btn-a), var(--btn-b)) !important;
    color: #eff6ff !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}

.stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(14, 165, 233, 0.32);
}

[data-testid="stAlert"] {
    border-radius: 10px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1 class="hero-title">&#129518; Simple Calculator</h1>
     
    </div>
    """,
    unsafe_allow_html=True,
)

if "expression" not in st.session_state:
    st.session_state.expression = ""
if "error_text" not in st.session_state:
    st.session_state.error_text = ""


def normalize_expression(text: str) -> str:
    cleaned = text.replace(" ", "").replace("X", "x")
    allowed = set("0123456789.+-*/()=x")
    return "".join(ch for ch in cleaned if ch in allowed)


def safe_eval(expression: str) -> float:
    parsed = ast.parse(expression, mode="eval")

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval(node.body)

        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            operand = _eval(node.operand)
            return operand if isinstance(node.op, ast.UAdd) else -operand

        if isinstance(node, ast.BinOp) and isinstance(
            node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)
        ):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if right == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            return left / right

        raise ValueError("Invalid expression.")

    return _eval(parsed)


def format_result(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.10f}".rstrip("0").rstrip(".")


def evaluate_current_expression() -> None:
    expression = st.session_state.expression
    if not expression:
        return

    normalized = normalize_expression(expression).replace("x", "*")
    if not normalized:
        return

    try:
        result = safe_eval(normalized)
        formatted = format_result(result)
        st.session_state.expression = formatted
        st.session_state.error_text = ""
    except ZeroDivisionError as err:
        st.session_state.error_text = str(err)
    except Exception:
        st.session_state.error_text = "Invalid expression."


def press(value: str) -> None:
    if value == "C":
        st.session_state.expression = ""
        st.session_state.error_text = ""
        return

    if value == "BACK":
        st.session_state.expression = st.session_state.expression[:-1]
        st.session_state.error_text = ""
        return

    if value == "=":
        evaluate_current_expression()
        return

    if value == "*":
        value = "x"
    st.session_state.expression += value
    st.session_state.error_text = ""


st.markdown(
    f"<div class='display-box'>{html.escape(st.session_state.expression or '0')}</div>",
    unsafe_allow_html=True,
)

if st.session_state.error_text:
    st.error(st.session_state.error_text)

buttons = [
    [("7", "7"), ("8", "8"), ("9", "9"), ("/", "/")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("x", "x")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("\\-", "-")],
    [("0", "0"), (".", "."), ("=", "="), ("\\+", "+")],
    [("C", "C"), ("<-", "BACK")],
]

for row_index, row in enumerate(buttons):
    cols = st.columns(len(row))
    for col_index, (label, value) in enumerate(row):
        cols[col_index].button(
            label,
            key=f"btn_{row_index}_{col_index}",
            on_click=press,
            args=(value,),
            use_container_width=True,
        )

components.html(
    """
    <script>
    (() => {
      const doc = window.parent.document;

      function norm(text) {
        return (text || "").replace(/\\s+/g, " ").trim();
      }

      function findButtonByLabel(label) {
        const buttons = Array.from(doc.querySelectorAll("button"));
        return buttons.find((btn) => norm(btn.innerText) === label);
      }

      function mapKeyToLabel(key) {
        if (/^[0-9]$/.test(key)) return key;
        if (key === ".") return ".";
        if (key === "+") return "+";
        if (key === "-") return "-";
        if (key === "/") return "/";
        if (key === "*" || key === "x" || key === "X") return "x";
        if (key === "Enter" || key === "=") return "=";
        if (key === "Backspace") return "<-";
        if (key === "Escape") return "C";
        return null;
      }

      function onKeydown(event) {
        const tag = (event.target && event.target.tagName || "").toLowerCase();
        if (tag === "input" || tag === "textarea") return;

        const label = mapKeyToLabel(event.key);
        if (!label) return;

        const btn = findButtonByLabel(label);
        if (!btn) return;
        event.preventDefault();
        btn.click();
      }

      if (window.parent.__calcKeyboardClickListener) {
        doc.removeEventListener("keydown", window.parent.__calcKeyboardClickListener);
      }
      doc.addEventListener("keydown", onKeydown);
      window.parent.__calcKeyboardClickListener = onKeydown;
    })();
    </script>
    """,
    height=0,
)
