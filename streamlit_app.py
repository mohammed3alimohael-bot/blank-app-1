import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والخط الكوفي
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    .stApp { background-color: #ffffff; }
    .main-title { 
        font-family: 'Reem Kufi', sans-serif; 
        font-size: 30px; color: #0045ad; 
        text-align: center; margin-top: -30px; 
    }
    .announcement-card { 
        background-color: #fff3cd; color: #856404; 
        padding: 15px; border-radius: 8px; 
        border-right: 6px solid #ffc107; 
        margin-bottom: 15px; font-weight: bold; text-align: right; 
    }
    .stButton button { width: 100%; border-radius: 10px; font-weight: bold; height: 45px; }
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بـ Supabase
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. إدارة الجلسة والدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 دخول المستخدمين")
        user_creds = {
            "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
            "مدير التنمية": "2001", "مسؤول المخزن": "3001",
            "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
        }
        u_identity = st.selectbox("اختر اسمك:", list(user_creds.keys()))
        u_pass = st.text_input("الرمز السري:", type="password")
        if st.button("دخول ✅"):
            if u_pass == user_creds[u_identity]:
                st.session_state.logged_in = True
                st.session_state.user_name = u_identity
                st.rerun()
            else: st.error("الرمز السري غير صحيح!")
    st.stop()

u_name = st.session_state.user_name

# --- 📣 عرض الإعلانات (مع حماية من أخطاء الجدول) ---
try:
    ann_res = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute()
    if ann_res.data:
        st.markdown(f'<div class="announcement-card">📢 إشعار إداري جديد:<br>{ann_res.data[0]["content"]}</div>', unsafe_allow_html=True)
except:
    pass # في حال عدم وجود الجدول لن ينهار التطبيق

# --- 🛠️ لوحة تحكم محمد علي (تصفير + تعميم) ---
if u_name == "قسم التنسيق (محمد علي)":
    with st.expander("🛠️ لوحة تحكم الإدارة"):
        msg = st.text_area("رسالة تعميم لكل المستخدمين:")
        if st.button("إرسال التعميم 📡"):
            if msg:
                try:
                    supabase.table("announcements").insert({"content": msg, "sender": u_name}).execute()
                    st.success("تم النشر بنجاح!")
                    time.sleep(1)
                    st.rerun()
                except:
                    st.error("خطأ: يرجى تنفيذ كود SQL في Supabase أولاً.")
            
        if st.button("⚠️ تصفير كافة الطلبات"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم تصفير المنظومة!")
            st.rerun()

st.divider()
st.markdown("<center style='color: #888; font-size: 11px;'>Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></center>", unsafe_allow_html=True)

# ملاحظة: يمكنك دمج باقي كود المشرف والمخزن والمدير هنا كما هو في النسخ السابقة.
