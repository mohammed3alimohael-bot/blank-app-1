import streamlit as st
from supabase import create_client
from datetime import datetime

# 1. إعدادات الصفحة وإخفاء الشريط العلوي
st.set_page_config(page_title="منظومة بيبسي - التنسيق", layout="wide")

hide_style = """
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 2. الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. قاعدة البيانات والصلاحيات
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 دخول المنظومة")
user_identity = st.sidebar.selectbox("اختر اسمك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("الرمز السري:", type="password")

if user_password == user_credentials[user_identity]:
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    st.title(f"🥤 لوحة تحكم: {user_identity}")
    
    # جلب البيانات
    res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
    all_orders = res.data

    col1, col2 = st.columns([1.3, 2.5])

    # --- المرحلة 1: المشرف (إضافة طلب) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ طلب جديد")
            with st.container(border=True):
                trade_name = st.text_input("🏢 الاسم التجاري")
                address = st.text_input("🗺️ العنوان")
                c_type = st.selectbox("نوع البراد", ["دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "ثلاثي بيبسي"])
                if st.button("إرسال الطلب للمدير 🚀"):
                    supabase.table("cooler_orders").insert({
                        "customer_name": trade_name, "address": address, "cooler_type": c_type,
                        "supervisor_name": user_identity, "status": "بانتظار موافقة المدير"
                    }).execute()
                    st.success("تم الإرسال!")
                    st.rerun()

    with col2:
        st.header("📋 حركة الطلبات")
        if all_orders:
            for o in all_orders:
                status = o['status']
                with st.expander(f"📦 {o['customer_name']} | {status}"):
                    st.write(f"📍 العنوان: {o['address']} | 👤 المشرف: {o['supervisor_name']}")
                    
                    # --- المرحلة 2: مدير التنمية ---
                    if user_role == "مدير التنمية" and status == "بانتظار موافقة المدير":
                        reason = st.text_input("السبب (في حال الرفض):", key=f"re_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"a_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"r_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": reason}).eq("id", o['id']).execute()
                            st.rerun()

                    # --- المرحلة 3: مسؤول المخزن ---
                    elif user_role == "مسؤول المخزن" and status == "تمت الموافقة - بانتظار المخزن":
                        serial = st.text_input("رقم البراد:", key=f"s_{o['id']}")
                        reason = st.text_input("سبب عدم التوفر:", key=f"sr_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تجهيز", key=f"s_ok_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": serial}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ غير متوفر", key=f"s_no_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": reason}).eq("id", o['id']).execute()
                            st.rerun()

                    # --- المرحلة 4: مسؤول التنسيق ---
                    elif user_role == "قسم التنسيق (محمد علي)" and status == "تم التجهيز - بانتظار العقد":
                        if st.button("📝 تم إكمال العقد", key=f"con_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                            st.rerun()

                    # --- المرحلة 5: سائق البرادات ---
                    elif user_role == "سائق البرادات" and status == "جاهز للتوصيل":
                        note = st.text_input("ملاحظة السائق (سبب الرفض):", key=f"dr_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التسليم", key=f"d_ok_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل بنجاح"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض الاستلام", key=f"d_no_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "رفض استلام العميل", "driver_notes": note}).eq("id", o['id']).execute()
                            st.rerun()
                    
                    # عرض الملاحظات السابقة إن وجدت
                    if o.get('manager_notes'): st.error(f"⚠️ ملاحظة: {o['manager_notes']}")
                    if o.get('driver_notes'): st.warning(f"⚠️ ملاحظة السائق: {o['driver_notes']}")
        else:
            st.write("لا توجد طلبات حالياً.")

    # --- Footer ---
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #888;'>Designed and Programmed by: <b>Mohammed Ali Muheel</b></div>", unsafe_allow_html=True)
else:
    st.sidebar.info("يرجى إدخال الرمز السري.")
