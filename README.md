# 🛡️ SMS Scam Shield

### AI-Powered SMS Spam & Scam Detection

SMS Scam Shield is a machine-learning web application designed to help users identify potentially suspicious SMS messages. It combines a trained machine-learning model, rule-based warning indicators, and OCR technology to extract text from SMS screenshots.

## 🚀 Live Demo

**Try the application here:**  
https://sms-scam-shield-62xbhqymbutemejzwhn2qm.streamlit.app/

## ✨ Features

- **SMS Scanner:** Enter an SMS message and analyze it using a trained machine-learning model.
- **Screenshot Intelligence:** Upload a screenshot of an SMS and extract its text using OCR.
- **Spam Detection:** Classifies messages as spam or non-spam using the trained model.
- **Suspicious Pattern Detection:** Highlights suspicious links, OTP/PIN/CVV requests, urgent language, prize claims, payment requests, and account-verification messages.
- **Message Categorization:** Estimates categories such as Banking, UPI/Digital Payment, Recharge/Telecom, Shopping/Offers, Courier/Delivery, Lottery/Prize, Job/Employment, and OTP/Verification.
- **Sender Format Check:** Checks the basic format of phone numbers and alphanumeric sender IDs.
- **Modern Dark UI:** Provides a clean, modern interface built with Streamlit.

## 🧰 Technologies Used

- Python
- Streamlit
- Scikit-learn
- Machine Learning
- TF-IDF / Text Vectorization (depending on the trained model setup)
- Joblib
- Pillow (PIL)
- Pytesseract
- Tesseract OCR

## 📁 Project Structure

```text
sms-scam-shield/
├── app.py
├── requirements.txt
├── packages.txt
├── spam_model.joblib
└── tfidf_vectorizer.joblib
```

**Note:** The model and vectorizer filenames may differ depending on your training setup. Include the files your application actually loads. A separate vectorizer is needed only if it was saved separately from the model.

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd sms-scam-shield
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a Virtual Environment

For Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file should contain the required libraries:

```text
streamlit
scikit-learn
joblib
pillow
pytesseract
```

### 4. Install Tesseract OCR

Pytesseract is a Python wrapper. The Tesseract OCR program must also be installed for screenshot text extraction to work.

For Streamlit Community Cloud, create a root-level file named `packages.txt` containing:

```text
tesseract-ocr
```

### 5. Run the Application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually:

`http://localhost:8501`

## 🧠 How It Works

1. **Input:** The user pastes an SMS message or uploads a screenshot.
2. **Text Extraction:** OCR attempts to extract text from the uploaded screenshot.
3. **Machine Learning:** The trained model analyzes the message and predicts whether it is spam or non-spam.
4. **Warning Analysis:** Rule-based checks identify common suspicious patterns.
5. **Categorization:** Keyword matching estimates the type of message.
6. **Results:** The application displays the classification, category, and detected warning indicators.

## 📱 How to Use

### SMS Scanner

1. Open the live application.
2. Select the SMS Scanner tab.
3. Paste the SMS text.
4. Click **Analyze SMS**.
5. Review the prediction and warning indicators.

### Screenshot Intelligence

1. Open the Screenshot Intelligence tab.
2. Upload a clear SMS screenshot.
3. Click **Extract Text from Screenshot**.
4. Review or edit the extracted text.
5. Click **Analyze Screenshot Text**.

### Sender Check

1. Open the Sender Check tab.
2. Enter a phone number or sender ID.
3. Click **Check Sender Format**.
4. Review the format-check result.

This feature checks the format only. It does not independently verify the sender's real identity or perform a live Truecaller lookup.

## ☁️ Deployment

The application is deployed using Streamlit Community Cloud.

To deploy your own version:

1. Upload the application code and required model files to GitHub.
2. Ensure `requirements.txt` and `packages.txt` are configured correctly.
3. Open Streamlit Community Cloud.
4. Connect your GitHub repository.
5. Select `app.py` as the main file.
6. Deploy the application.
7. Check the deployment logs if an error occurs.

## 🔐 Privacy and Safety

- Never share real OTPs, passwords, PINs, CVVs, or banking details.
- A non-spam prediction does not guarantee that a message is safe.
- A sender ID or phone number can be spoofed.
- Screenshot OCR can make mistakes with blurry or low-resolution images.
- Do not treat automated predictions as definitive proof of fraud.

## ⚠️ Limitations

- Detection quality depends on the training dataset and trained model.
- Keyword-based warnings and categories are approximate.
- OCR may not recognize every character correctly.
- Model confidence, when available, is not the probability that a message is safe.
- Sender format checking does not establish identity.

## 🔮 Future Improvements

- Improve detection with more diverse SMS datasets.
- Evaluate the model using precision, recall, F1-score, and a confusion matrix.
- Improve OCR for low-quality screenshots.
- Explore authorized URL reputation services.
- Investigate official sender-verification APIs where access is available.
- Add support for more languages and regional scam patterns.

## 👨‍💻 Author

**Praveen**  
Machine Learning Project — SMS Scam Shield

## 📄 Disclaimer

SMS Scam Shield is an educational machine-learning project intended to help users review suspicious messages. It does not guarantee detection of every scam and should not replace independent verification through official channels.

---

**If you find a bug or have a suggestion, open an issue in this GitHub repository. Please do not post private SMS messages or personal information.**
