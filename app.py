
import re
import joblib
import streamlit as st
import pytesseract

from PIL import Image, ImageOps, ImageEnhance

st.set_page_config(
    page_title="SMS Scam Shield",
    page_icon="🛡️",
    layout="centered"
)


# Load existing machine learning model
@st.cache_resource
def load_model():
    return joblib.load("spam_model.joblib")


model = load_model()


# App heading
st.title("🛡️ SMS Scam Shield")
st.subheader("AI-Powered SMS Fraud Screening")
st.write(
    "Scan SMS text or upload a screenshot to check "
    "for potential spam and suspicious patterns."
)

st.info(
    "This tool provides screening results, not a guarantee "
    "that a message or sender is genuine."
)


# Detect common suspicious patterns
def check_warnings(text):
    rules = {
        "Suspicious link": (
            r"https?://|www\.|bit\.ly|tinyurl|"
            r"\b[a-z0-9-]+\.(com|in|net|org)\b"
        ),
        "OTP, PIN, CVV or password mentioned": (
            r"\b(otp|upi pin|cvv|password)\b"
        ),
        "Urgency or account threat": (
            r"\b(urgent|blocked|suspended|expire|"
            r"kyc|immediately|verify your account)\b"
        ),
        "Prize or reward offer": (
            r"\b(winner|prize|lottery|claim reward|"
            r"cashback|free gift)\b"
        ),
        "Payment or money request": (
            r"\b(send money|pay now|payment pending|"
            r"refund|bank account)\b"
        )
    }

    return [
        name for name, pattern in rules.items()
        if re.search(pattern, text, re.I)
    ]


# Estimate the message category from its wording
def get_category(text):
    categories = {
        "Banking / RBI-related claim":
            r"\b(rbi|bank|account|ifsc|credit card|"
            r"debit card|loan|kyc)\b",

        "Recharge / Telecom":
            r"\b(recharge|mobile plan|data pack|"
            r"sim card|prepaid|postpaid|airtel|jio|vi)\b",

        "Shopping / Offers":
            r"\b(order|shopping|discount|sale|"
            r"amazon|flipkart|delivery offer|coupon)\b",

        "Courier / Delivery":
            r"\b(courier|parcel|shipment|delivery|"
            r"tracking|customs)\b",

        "UPI / Digital Payment":
            r"\b(upi|gpay|phonepe|paytm|transaction|"
            r"payment|collect request)\b",

        "Lottery / Prize":
            r"\b(lottery|winner|prize|reward|"
            r"lucky draw|jackpot)\b",

        "Job / Employment":
            r"\b(job offer|recruitment|salary|"
            r"work from home|hiring|vacancy)\b"
    }

    matches = [
        category
        for category, pattern in categories.items()
        if re.search(pattern, text, re.I)
    ]

    if not matches:
        return ["General / Unknown"]

    return matches


# Basic format checks, not identity verification
def check_sender(sender):
    sender = sender.strip()

    if not sender:
        return "Not provided"

    if re.fullmatch(r"\+?91[\s-]?[6-9]\d{9}", sender):
        return (
            "Indian mobile-number format detected. "
            "The owner's identity is not verified."
        )

    if re.fullmatch(r"[6-9]\d{9}", sender):
        return (
            "Indian mobile-number format detected. "
            "The owner's identity is not verified."
        )

    if re.fullmatch(r"[A-Za-z0-9 -]{2,20}", sender):
        return (
            "Sender ID or other identifier entered. "
            "Its authenticity has not been verified."
        )

    return (
        "The format could not be confidently recognized. "
        "The sender is unverified."
    )


# OCR: extract text from an uploaded screenshot
def extract_text(uploaded_file):
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    # Improve contrast for OCR
    image = ImageEnhance.Contrast(image).enhance(1.5)

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text.strip()


# Display analysis results
def analyze_message(message):
    if not message.strip():
        st.warning("No message text was found. Please enter or upload a clearer message.")
        return

    prediction = str(model.predict([message])[0]).lower()
    warnings = check_warnings(message)
    categories = get_category(message)

    st.markdown("---")
    st.subheader("🔎 Scan Results")

    if prediction == "spam":
        st.error("⚠️ The ML model classifies this message as SPAM.")
    else:
        st.success(
            "✅ The ML model does not classify this message as SPAM."
        )

    st.write("**Estimated message category:**")
    for category in categories:
        st.write(f"- {category}")

    st.caption(
        "Categories are estimated from message wording. "
        "They do not confirm that a message really came from a bank, "
        "RBI, telecom operator, or other organization."
    )

    if warnings:
        st.warning("Potential warning indicators:")
        for warning in warnings:
            st.write(f"- {warning}")
    else:
        st.info("No listed suspicious patterns were detected.")

    st.caption(
        "Even a message classified as not spam can be fraudulent. "
        "Do not share OTPs, UPI PINs, CVVs or passwords."
    )


# Tabs for text, image and sender checks
text_tab, image_tab, sender_tab = st.tabs(
    ["📝 Scan SMS Text", "📷 Upload Screenshot", "📱 Sender Check"]
)


with text_tab:
    st.write("Paste the SMS you want to check.")

    message = st.text_area(
        "SMS message",
        placeholder="Paste your SMS here...",
        height=160,
        key="sms_text"
    )

    if st.button("🔍 Scan Message", type="primary", key="scan_text"):
        analyze_message(message)


with image_tab:
    st.write("Upload a screenshot or photo containing an SMS.")

    uploaded_image = st.file_uploader(
        "Choose screenshot",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if uploaded_image is not None:
        st.image(
            uploaded_image,
            caption="Uploaded SMS screenshot",
            use_container_width=True
        )

        if st.button("🔎 Extract & Scan", type="primary"):
            try:
                extracted_text = extract_text(uploaded_image)

                if extracted_text:
                    st.subheader("Extracted Text")
                    st.text_area(
                        "Review the detected text",
                        value=extracted_text,
                        height=160
                    )
                    analyze_message(extracted_text)
                else:
                    st.warning(
                        "No text could be extracted. Try a clearer screenshot."
                    )

            except Exception as error:
                st.error(
                    "Could not read the image. Try another clear screenshot."
                )
                st.caption(f"Technical detail: {error}")


with sender_tab:
    st.write(
        "Enter a sender number or SMS sender ID for a basic format check."
    )

    sender = st.text_input(
        "Sender phone number or ID",
        placeholder="Example: +919876543210 or BANKAL"
    )

    if st.button("Check Sender Format"):
        result = check_sender(sender)
        st.info(result)

        st.caption(
            "This check does not verify ownership, identify the sender, "
            "or establish that the sender is legitimate. Phone numbers "
            "and sender IDs can be spoofed."
        )


st.divider()
st.caption("SMS Scam Shield | Machine Learning Project")
st.caption("Made with ❤️ by Praveen")
