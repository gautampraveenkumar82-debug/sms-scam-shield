
import re
from pathlib import Path

import joblib
import streamlit as st

# Optional screenshot OCR dependencies
try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="SMS Scam Shield | AI Protection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------
# MODERN DARK UI
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at top left, #142b43 0%, transparent 45%),
        linear-gradient(145deg, #08111f, #070b14 65%);
    color: #f1f5f9;
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.hero {
    background: linear-gradient(120deg, #101d30, #102b32);
    border: 1px solid #263d51;
    border-radius: 24px;
    padding: 34px 30px;
    margin-bottom: 20px;
}

.eyebrow {
    color: #42ead6;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 18px;
}

.hero h1 {
    color: #f8fafc;
    font-size: clamp(30px, 4vw, 44px);
    font-weight: 800;
    margin: 0 0 14px 0;
}

.hero p {
    color: #b8c8dc;
    font-size: 14px;
    line-height: 1.8;
    margin-bottom: 0;
}

.metric {
    background: #111e2e;
    border: 1px solid #293e53;
    border-radius: 15px;
    padding: 17px;
    min-height: 95px;
}

.metric-label {
    color: #a6bad2;
    font-size: 10px;
    letter-spacing: 1.2px;
    margin-bottom: 12px;
}

.metric-value {
    color: #f8fafc;
    font-size: 18px;
    font-weight: 800;
}

.panel {
    background: #101b2a;
    border: 1px solid #293e53;
    border-radius: 17px;
    padding: 20px;
    margin: 12px 0;
}

.result-safe {
    background: #102b27;
    border: 1px solid #217b69;
    border-radius: 15px;
    padding: 20px;
}

.result-danger {
    background: #35191f;
    border: 1px solid #a43d4c;
    border-radius: 15px;
    padding: 20px;
}

.result-warning {
    background: #302817;
    border: 1px solid #8d6b2e;
    border-radius: 15px;
    padding: 20px;
}

.result-title {
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}

.small-muted {
    color: #9aa9ba;
    font-size: 12px;
}

.stTextArea textarea, .stTextInput input {
    background: #0b1421 !important;
    color: #f1f5f9 !important;
    border: 1px solid #30465c !important;
    border-radius: 10px !important;
}

.stButton > button {
    background: linear-gradient(100deg, #12c9b9, #159bd4);
    color: #06121c;
    border: 0;
    border-radius: 10px;
    padding: 10px 20px;
    font-weight: 800;
    min-height: 42px;
}

.stButton > button:hover {
    border: 1px solid #75fff0;
    color: #ffffff;
}

div[data-baseweb="tab-list"] {
    gap: 10px;
}

button[data-baseweb="tab"] {
    color: #d4deeb;
}

footer {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# MODEL LOADING
# Supports a pipeline model or a separate vectorizer.
# --------------------------------------------------
@st.cache_resource
def load_ml_files():
    base = Path(__file__).resolve().parent

    model_candidates = [
        base / "spam_model.joblib",
        base / "model.joblib",
        base / "spam_model.pkl",
        base / "model.pkl",
    ]

    vectorizer_candidates = [
        base / "tfidf_vectorizer.joblib",
        base / "vectorizer.joblib",
        base / "tfidf.joblib",
        base / "vectorizer.pkl",
    ]

    model_path = next(
        (p for p in model_candidates if p.exists()), None
    )

    vectorizer_path = next(
        (p for p in vectorizer_candidates if p.exists()), None
    )

    if model_path is None:
        return None, None, (
            "Model file not found. Add your trained model file "
            "to the same folder as app.py."
        )

    try:
        model = joblib.load(model_path)
        vectorizer = (
            joblib.load(vectorizer_path)
            if vectorizer_path is not None
            else None
        )
        return model, vectorizer, None

    except Exception as exc:
        return None, None, f"Could not load model files: {exc}"


model, vectorizer, model_error = load_ml_files()


# --------------------------------------------------
# SMS RULES AND CATEGORY DETECTION
# These rules supplement ML; they are not proof of fraud.
# --------------------------------------------------
def get_warnings(message):
    text = message.lower()
    warnings = []

    patterns = [
        (
            r"https?://|www\.|bit\.ly|tinyurl\.com",
            "Contains a link. Check the website address carefully."
        ),
        (
            r"\botp\b|\bpin\b|\bcvv\b|password|passcode",
            "Mentions sensitive security credentials."
        ),
        (
            r"urgent|immediately|act now|account.*(block|suspend)|"
            r"will be blocked|expire today",
            "Uses urgency or account-threat language."
        ),
        (
            r"won.*prize|you.*winner|lottery|claim.*reward|"
            r"free gift|cash prize",
            "Contains prize, reward, or lottery-style wording."
        ),
        (
            r"send money|pay now|transfer.*money|"
            r"upi.*(payment|collect)|request.*payment",
            "Requests money or a payment action."
        ),
        (
            r"verify.*account|kyc.*update|update.*kyc|"
            r"bank details|click.*verify",
            "Requests account verification or personal details."
        ),
        (
            r"remote access|install.*app|screen sharing",
            "May ask you to install an app or share device access."
        ),
    ]

    for pattern, warning in patterns:
        if re.search(pattern, text):
            warnings.append(warning)

    return warnings


def get_category(message):
    text = message.lower()

    categories = [
        (
            "Banking / Financial",
            r"\bbank\b|\brbi\b|account.*(debit|credit)|"
            r"credit card|debit card|loan|kyc"
        ),
        (
            "UPI / Digital Payment",
            r"\bupi\b|paytm|phonepe|google pay|gpay|"
            r"payment|transaction|wallet"
        ),
        (
            "Recharge / Telecom",
            r"recharge|data pack|prepaid|postpaid|sim card|"
            r"mobile plan|telecom"
        ),
        (
            "Shopping / Offers",
            r"shopping|order discount|sale|coupon|"
            r"amazon|flipkart|shopping offer"
        ),
        (
            "Courier / Delivery",
            r"courier|parcel|delivery|shipment|tracking number"
        ),
        (
            "Lottery / Prize",
            r"lottery|winner|won a prize|reward|lucky draw|"
            r"claim your gift"
        ),
        (
            "Job / Employment",
            r"job offer|work from home|part.?time job|"
            r"salary offer|recruitment|hiring"
        ),
        (
            "OTP / Verification",
            r"\botp\b|verification code|login code|"
            r"one.?time password"
        ),
    ]

    for category, pattern in categories:
        if re.search(pattern, text):
            return category

    return "General / Unknown"


def predict_sms(message):
    """
    Predict with a saved scikit-learn model.
    Supports either:
      1. A complete pipeline model, or
      2. A model plus a separately saved vectorizer.
    """
    if model is None:
        return None, None, model_error

    try:
        if vectorizer is not None:
            features = vectorizer.transform([message])
            prediction = model.predict(features)[0]
            probabilities = (
                model.predict_proba(features)[0]
                if hasattr(model, "predict_proba")
                else None
            )
        else:
            # This works when the saved model is a pipeline
            # that includes its own text vectorizer.
            prediction = model.predict([message])[0]
            probabilities = (
                model.predict_proba([message])[0]
                if hasattr(model, "predict_proba")
                else None
            )

        confidence = None

        if probabilities is not None:
            confidence = float(max(probabilities)) * 100

        label = str(prediction).strip().lower()

        spam_labels = {
            "spam", "1", "true", "fraud", "scam", "phishing"
        }

        safe_labels = {
            "ham", "0", "false", "legitimate", "safe", "not spam"
        }

        if label in spam_labels:
            result = "spam"
        elif label in safe_labels:
            result = "safe"
        else:
            return None, confidence, (
                "Unknown model label. Check the labels used during training."
            )

        return result, confidence, None

    except Exception as exc:
        return None, None, (
            "Prediction failed. Check that the model and vectorizer "
            f"match your training setup. Details: {exc}"
        )


def show_scan_result(message):
    message = message.strip()

    if not message:
        st.warning("Please enter or extract an SMS message first.")
        return

    with st.spinner("Analyzing message with your trained model..."):
        result, confidence, error = predict_sms(message)

    if error:
        st.error(error)
        return

    warnings = get_warnings(message)
    category = get_category(message)

    # Rules add caution when the message contains risk indicators.
    # They do not change the ML prediction itself.
    if result == "spam":
        st.markdown(
            """
            <div class="result-danger">
                <div class="result-title">🚨 Potential Spam</div>
                The trained ML model classified this message as spam.
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif warnings:
        st.markdown(
            """
            <div class="result-warning">
                <div class="result-title">⚠️ Be Careful</div>
                The ML model classified this as non-spam, but the
                message contains suspicious patterns. Verify it independently.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="result-safe">
                <div class="result-title">✅ Classified as Non-Spam</div>
                The trained ML model did not classify this message as spam.
                This does not guarantee that it is safe.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Message category**")
        st.write(f"📂 {category}")

    with col2:
        st.markdown("**Model confidence**")
        if confidence is None:
            st.write("Not available for this model")
        else:
            st.write(f"{confidence:.1f}%")
            st.caption(
                "Model confidence is not the probability that a message is safe."
            )

    st.markdown("#### Suspicious patterns")

    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("No patterns from the built-in warning rules were detected.")

    with st.expander("View scanned SMS"):
        st.write(message)

    st.caption(
        "Results are automated predictions, not a guarantee. "
        "Do not share OTPs, passwords, PINs, or banking details."
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="eyebrow">AI-POWERED SMS PROTECTION</div>
    <h1>🛡️ SMS Scam Shield</h1>
    <p>
        Analyze suspicious messages, detect spam patterns, and review
        potential warning signs with machine learning.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# STATUS CARDS
# --------------------------------------------------
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="metric">
        <div class="metric-label">DETECTION ENGINE</div>
        <div class="metric-value">ML + Rules</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="metric">
        <div class="metric-label">SCREENSHOT SCANNING</div>
        <div class="metric-value">OCR Support</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    status = "Model Ready" if model is not None else "Model Missing"
    st.markdown(f"""
    <div class="metric">
        <div class="metric-label">ML MODEL STATUS</div>
        <div class="metric-value">{status}</div>
    </div>
    """, unsafe_allow_html=True)

if model is None:
    st.error(model_error)


# --------------------------------------------------
# MAIN TABS
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "✉️ SMS Scanner",
    "📷 Screenshot Intelligence",
    "🔎 Sender Check",
])


# --------------------------------------------------
# TAB 1: TEXT SCANNER
# --------------------------------------------------
with tab1:
    st.markdown("### Scan an SMS")
    st.write(
        "Paste a message below to classify it using your trained ML model."
    )

    sms_text = st.text_area(
        "SMS message",
        placeholder=(
            "Example: Your account will be blocked. "
            "Click this link to verify your details..."
        ),
        height=160,
        key="sms_input",
    )

    if st.button("🛡️ Analyze SMS", key="scan_sms", use_container_width=True):
        show_scan_result(sms_text)


# --------------------------------------------------
# TAB 2: SCREENSHOT OCR
# --------------------------------------------------
with tab2:
    st.markdown("### Scan a message screenshot")
    st.write(
        "Upload a screenshot containing an SMS. OCR will try to extract "
        "the text before the ML scan."
    )

    uploaded_image = st.file_uploader(
        "Upload screenshot",
        type=["png", "jpg", "jpeg", "webp"],
        key="sms_screenshot",
    )

    if uploaded_image is not None:
        if OCR_AVAILABLE:
            try:
                image = Image.open(uploaded_image)
                st.image(
                    image,
                    caption="Uploaded screenshot",
                    use_container_width=True,
                )

                if st.button(
                    "📄 Extract Text from Screenshot",
                    key="extract_ocr",
                    use_container_width=True,
                ):
                    extracted_text = pytesseract.image_to_string(image).strip()
                    st.session_state["extracted_sms"] = extracted_text

            except Exception as exc:
                st.error(f"Could not read this image: {exc}")
        else:
            st.error(
                "OCR dependencies are missing. Install Pillow and pytesseract, "
                "and install the Tesseract OCR engine."
            )

    extracted_sms = st.text_area(
        "Extracted SMS text (you can edit it)",
        value=st.session_state.get("extracted_sms", ""),
        height=150,
        key="ocr_text",
    )

    if st.button(
        "🛡️ Analyze Screenshot Text",
        key="scan_ocr",
        use_container_width=True,
    ):
        show_scan_result(extracted_sms)


# --------------------------------------------------
# TAB 3: SENDER FORMAT CHECK
# --------------------------------------------------
with tab3:
    st.markdown("### Sender Check")
    st.write(
        "Review the basic format of a phone number or alphanumeric sender ID."
    )

    sender = st.text_input(
        "Sender number or ID",
        placeholder="Example: +919876543210 or BANKAL",
        key="sender_input",
    )

    if st.button(
        "🔎 Check Sender Format",
        key="check_sender",
        use_container_width=True,
    ):
        value = sender.strip()

        if not value:
            st.warning("Enter a sender number or ID.")
        else:
            cleaned = re.sub(r"[\s\-()]", "", value)

            if re.fullmatch(r"\+?[0-9]{10,15}", cleaned):
                st.info(
                    "This looks like a phone-number format. "
                    "Its ownership or authenticity has not been verified."
                )
            elif re.fullmatch(r"[A-Za-z0-9_-]{2,20}", value):
                st.info(
                    "This looks like an alphanumeric sender ID. "
                    "Its real-world identity has not been verified."
                )
            else:
                st.warning(
                    "This format looks unusual. Check the sender details."
                )

    st.caption(
        "A format check alone cannot establish who sent a message."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; padding:12px 0;">
        <div style="color:#42ead6; font-weight:800; letter-spacing:1px;">
            SMS SCAM SHIELD
        </div>
        <div class="small-muted" style="margin-top:7px;">
            Machine Learning Project • Made with ❤️ by Praveen
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

