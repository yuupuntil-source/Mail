import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Rice Mail", page_icon="📧")

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

if "user" not in st.session_state:
    st.session_state.user = None


def register(email, password):
    res = supabase.auth.sign_up({
        "email": email,
        "password": password
    })
    return res


def login(email, password):
    res = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    st.session_state.user = res.user
    return res


def logout():
    supabase.auth.sign_out()
    st.session_state.user = None


def send_mail(receiver_email, subject, body):
    user = st.session_state.user

    supabase.table("emails").insert({
        "sender_id": user.id,
        "receiver_email": receiver_email,
        "subject": subject,
        "body": body,
        "folder": "inbox"
    }).execute()


def get_inbox():
    user = st.session_state.user

    return supabase.table("emails") \
        .select("*") \
        .eq("receiver_email", user.email) \
        .order("created_at", desc=True) \
        .execute()


def get_sent():
    user = st.session_state.user

    return supabase.table("emails") \
        .select("*") \
        .eq("sender_id", user.id) \
        .order("created_at", desc=True) \
        .execute()


st.title("📧 Rice Mail")

if st.session_state.user is None:
    tab1, tab2 = st.tabs(["登入", "註冊"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("登入"):
            try:
                login(email, password)
                st.success("登入成功")
                st.rerun()
            except Exception as e:
                st.error(f"登入失敗：{e}")

    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")

        if st.button("註冊"):
            try:
                register(email, password)
                
            except Exception as e:
                st.error(f"註冊失敗：{e}")

else:
    user = st.session_state.user

    st.sidebar.write(f"登入中：{user.email}")

    if st.sidebar.button("登出"):
        logout()
        st.rerun()

    page = st.sidebar.radio(
        "功能",
        ["收件匣", "寄信", "寄件備份"]
    )

    if page == "收件匣":
        st.header("📥 收件匣")

        mails = get_inbox().data

        if not mails:
            st.info("目前沒有信")
        else:
            for mail in mails:
                with st.expander(f"{mail['subject']} ｜ from: {mail['sender_id']}"):
                    st.write(mail["body"])
                    st.caption(mail["created_at"])

    elif page == "寄信":
        st.header("✉️ 寄信")

        receiver = st.text_input("收件者 帳號")
        subject = st.text_input("主旨")
        body = st.text_area("內容", height=200)

        if st.button("送出"):
            if receiver and subject and body:
                send_mail(receiver, subject, body)
                st.success("已送出")
            else:
                st.warning("欄位不能空白")

    elif page == "寄件備份":
        st.header("📤 寄件備份")

        mails = get_sent().data

        if not mails:
            st.info("目前沒有寄件紀錄")
        else:
            for mail in mails:
                with st.expander(f"{mail['subject']} ｜ to: {mail['receiver_email']}"):
                    st.write(mail["body"])
                    st.caption(mail["created_at"])
