import streamlit as st
import pandas as pd
import numpy as np
import datetime
import uuid
import base64
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# Set page configuration
st.set_page_config(
    page_title="P2P Pro Factoring Web3 Platform",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hide Streamlit style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Simulated databases using session state
if 'users' not in st.session_state:
    st.session_state.users = {}

if 'invoices' not in st.session_state:
    st.session_state.invoices = {}

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# Utility Functions
def generate_id():
    return str(uuid.uuid4())

def risk_assessment(amount, due_date):
    # Simple risk assessment based on amount and due date
    days_to_due = (due_date - datetime.date.today()).days
    risk_score = np.clip(100 - (amount / 1000) - days_to_due, 0, 100)
    return round(risk_score, 2)

def format_currency(amount):
    return "${:,.2f}".format(amount)

def check_kyc(user):
    # Simulated KYC check
    return user.get('kyc_verified', False)

# User Authentication
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        user = st.session_state.users.get(username)
        if user and user['password'] == password:
            st.session_state.current_user = user
            st.success(f"Logged in as {username}")
            try:
                st.rerun()
            except AttributeError:
                pass
        else:
            st.error("Invalid credentials")

def signup():
    st.subheader("Sign Up")
    username = st.text_input("Choose a Username", key="signup_username")
    password = st.text_input("Choose a Password", type="password", key="signup_password")
    user_type = st.selectbox("Sign up as", ['Business', 'Investor'])
    if st.button("Sign Up"):
        if username in st.session_state.users:
            st.error("Username already exists")
        else:
            new_user = {
                'id': generate_id(),
                'username': username,
                'password': password,
                'user_type': user_type,
                'kyc_verified': False
            }
            st.session_state.users[username] = new_user
            st.success("Account created successfully! Please complete KYC verification.")
            st.session_state.current_user = new_user
            try:
                st.rerun()
            except AttributeError:
                pass

def kyc_verification():
    st.subheader("KYC Verification")
    st.write("Please upload your identification documents for verification.")
    uploaded_file = st.file_uploader("Upload ID Document", type=["png", "jpg", "jpeg", "pdf"])
    if st.button("Submit for Verification"):
        if uploaded_file is not None:
            # Simulate KYC verification process
            st.session_state.current_user['kyc_verified'] = True
            st.success("KYC Verification Successful!")
            try:
                st.rerun()
            except AttributeError:
                pass
        else:
            st.error("Please upload a document.")

def business_dashboard():
    st.title("🏢 Business Dashboard")
    tabs = st.tabs(["List New Invoice", "Your Invoices", "Messages"])
    with tabs[0]:
        st.header("List a New Invoice")
        invoice_id = generate_id()
        amount = st.number_input("Invoice Amount", min_value=0.0, step=1000.0)
        due_date = st.date_input("Due Date", min_value=datetime.date.today())
        discount_rate = st.number_input("Discount Rate (%)", min_value=0.0, max_value=100.0, step=0.1)

        if st.button("List Invoice"):
            risk_score = risk_assessment(amount, due_date)
            new_invoice = {
                'invoice_id': invoice_id,
                'business': st.session_state.current_user['username'],
                'amount': amount,
                'due_date': due_date,
                'discount_rate': discount_rate,
                'risk_score': risk_score,
                'status': 'Open',
                'investor': None
            }
            st.session_state.invoices[invoice_id] = new_invoice
            st.success("Invoice listed successfully!")
            st.balloons()

    with tabs[1]:
        st.header("Your Listed Invoices")
        business_invoices = [inv for inv in st.session_state.invoices.values() if inv['business'] == st.session_state.current_user['username']]
        if business_invoices:
            df = pd.DataFrame(business_invoices)
            st.dataframe(df)
            st.subheader("Invoice Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Invoices", len(business_invoices))
            with col2:
                total_amount = sum(inv['amount'] for inv in business_invoices)
                st.metric("Total Amount", format_currency(total_amount))
        else:
            st.info("You have no listed invoices.")

    with tabs[2]:
        st.header("Messages")
        user_messages = [msg for msg in st.session_state.messages if msg['to'] == st.session_state.current_user['username']]
        if user_messages:
            for msg in user_messages:
                st.write(f"From: {msg['from']}")
                st.write(f"Message: {msg['message']}")
                st.write("---")
        else:
            st.info("No messages.")

def investor_dashboard():
    st.title("💼 Investor Dashboard")
    tabs = st.tabs(["Available Invoices", "Your Investments", "Messages"])
    with tabs[0]:
        st.header("Available Invoices")
        open_invoices = [inv for inv in st.session_state.invoices.values() if inv['status'] == 'Open']
        if open_invoices:
            for invoice in open_invoices:
                with st.expander(f"Invoice ID: {invoice['invoice_id']}"):
                    st.write(f"**Business:** {invoice['business']}")
                    st.write(f"**Amount:** {format_currency(invoice['amount'])}")
                    st.write(f"**Due Date:** {invoice['due_date']}")
                    st.write(f"**Discount Rate:** {invoice['discount_rate']}%")
                    st.write(f"**Risk Score:** {invoice['risk_score']}%")
                    if st.button(f"Fund Invoice {invoice['invoice_id']}", key=invoice['invoice_id']):
                        invoice['status'] = 'Funded'
                        invoice['investor'] = st.session_state.current_user['username']
                        st.success(f"Funded Invoice {invoice['invoice_id']} successfully!")
                        try:
                            st.rerun()
                        except AttributeError:
                            pass
        else:
            st.info("No available invoices at the moment.")

    with tabs[1]:
        st.header("Your Investments")
        investor_invoices = [inv for inv in st.session_state.invoices.values() if inv['investor'] == st.session_state.current_user['username']]
        if investor_invoices:
            df = pd.DataFrame(investor_invoices)
            st.dataframe(df)
            st.subheader("Investment Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Investments", len(investor_invoices))
            with col2:
                total_amount = sum(inv['amount'] for inv in investor_invoices)
                st.metric("Total Amount", format_currency(total_amount))
        else:
            st.info("You have no investments.")

    with tabs[2]:
        st.header("Messages")
        user_messages = [msg for msg in st.session_state.messages if msg['to'] == st.session_state.current_user['username']]
        if user_messages:
            for msg in user_messages:
                st.write(f"From: {msg['from']}")
                st.write(f"Message: {msg['message']}")
                st.write("---")
        else:
            st.info("No messages.")

def send_message():
    st.header("Send a Message")
    recipient = st.text_input("Recipient Username")
    message = st.text_area("Message")
    if st.button("Send Message"):
        if recipient in st.session_state.users:
            new_message = {
                'from': st.session_state.current_user['username'],
                'to': recipient,
                'message': message
            }
            st.session_state.messages.append(new_message)
            st.success("Message sent!")
        else:
            st.error("Recipient not found.")

def main():
    st.sidebar.image("piezhi2.jpg", use_column_width=True)
    st.sidebar.title("Navigation")
    if st.session_state.current_user is None:
        menu = ["Home", "Login", "Sign Up"]
    else:
        menu = ["Home", "Dashboard", "Send Message", "KYC Verification", "Logout"]
    choice = st.sidebar.radio("Go to", menu)

    if choice == "Home":
        st.title("💰 P2P Pro Factoring Web3 Platform")
        st.write("""
            Welcome to the P2P Pro Factoring Web3 Platform. Connect businesses seeking liquidity with investors looking for opportunities.
        """)
        st.image("piezhi.jpg", use_column_width=True)

    elif choice == "Login":
        login()

    elif choice == "Sign Up":
        signup()

    elif choice == "KYC Verification" and st.session_state.current_user is not None:
        if not check_kyc(st.session_state.current_user):
            kyc_verification()
        else:
            st.success("KYC already verified.")

    elif choice == "Dashboard" and st.session_state.current_user is not None:
        if not check_kyc(st.session_state.current_user):
            st.warning("Please complete KYC verification to access the dashboard.")
            kyc_verification()
        else:
            if st.session_state.current_user['user_type'] == 'Business':
                business_dashboard()
            else:
                investor_dashboard()

    elif choice == "Send Message" and st.session_state.current_user is not None:
        send_message()

    elif choice == "Logout":
        st.session_state.current_user = None
        st.success("Logged out successfully!")
        try:
            st.rerun()
        except AttributeError:
            pass

    else:
        st.error("Please login to access this page.")

if __name__ == "__main__":
    main()
