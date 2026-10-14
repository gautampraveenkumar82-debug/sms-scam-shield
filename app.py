
import re
import joblib
import streamlit as st

st.set_page_config(
    page_title="SMS Scam Shield",
    page_icon="🛡️",
    layout="centered"
)

@st.cache_resource
def load_model():
    return joblib.load("spam_model.joblib")

model = load_model()

st.title("🛡️ SMS Scam Shield")
st.subheader("AI-powered SMS Spam Detection")
st.write(
    "Check suspicious messages before clicking links "
    "or sharing personal information."
)

message = st.text_area(
    "Paste your SMS here",
    placeholder="Example: Congratulations! You won a prize...",
    height=150
)

def check_warnings(text):
    rules = {
        "Suspicious link": r"https?://|www\.|bit\.ly|tinyurl",
        "OTP, PIN or password mentioned":
            r"\b(otp|upi pin|cvv|password)\b",
        "Urgency or account threat":
            r"\b(urgent|blocked|suspended|expire|kyc)\b",
        "Prize or reward offer":
            r"\b(winner|prize|lottery|claim reward)\b"
    }

    return [
        name for name, pattern in rules.items()
        if re.search(pattern, text, re.I)
    ]

if st.button("🔍 Scan Message", type="primary"):
    if not message.strip():
        st.warning("Please enter an SMS first.")
    else:
        prediction = model.predict([message])[0]
        warnings = check_warnings(message)

        if prediction.lower() == "spam":
            st.error("⚠️ Potential Spam Message")
        else:
            st.success("✅ Not classified as Spam")

        if warnings:
            st.warning("Safety warnings detected:")
            for warning in warnings:
                st.write(f"- {warning}")
        else:
            st.info("No obvious warning indicators detected.")

        st.caption(
            "This is a screening tool, not a guarantee of safety. "
            "Never share OTP, UPI PIN, CVV or passwords."
        )

st.divider()
st.caption("SMS Scam Shield | Machine Learning Project")
st.caption("Made with ❤️ by Praveen")
