import streamlit as st
from supabase import create_client
from datetime import datetime

# 1. إعدادات الصفحة وإخفاء الأشرطة العلوية لتصميم رسمي
st.set_page_config(page_title="منظومة التنسيق - بيبسي", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. بيانات الدخول والصلاحيات
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 دخول آمن")
user_identity = st.sidebar.selectbox("اختر اسمك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("الرمز السري:", type="password")

if user_password == user_credentials[user_identity]:
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    
    # --- 🔔 قسم الإشعارات الحية للمتابعة ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 تنبيهات الحركات")
    try:
        logs = supabase.table("cooler_orders").select("customer_name, status, created_at").order('created_at', desc=True).limit(5).execute()
        for log in logs.data:
            with st.sidebar.container(border=True):
                st.caption(f"⏱️ {log['created_at'][:16].replace('T', ' ')}")
                st.write(f"🏢 **{log['customer_name']}**")
                st.info(f"📍 {log['status']}")
    except: st.sidebar.write("بانتظار البيانات...")

    st.title(f"🥤 لوحة تحكم: {user_identity}")
    st.markdown("---")

    col1, col2 = st.columns([1.5, 2.5])

    # --- المرحلة 1: واجهة المشرف (إضافة وإرسال دفعة واحدة) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ إنشاء طلبات")
            if 'temp_basket' not in st.session_state: st.session_state.temp_basket = []
            
            with st.container(border=True):
                route = st.radio("📍 المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
                delegate = st.text_input("👤 اسم المندوب")
                trade_n = st.text_input("🏢 الاسم التجاري")
                full_n = st.text_input("📝 الاسم الثلاثي")
                addr = st.text_input("🗺️ العنوان")
                note_inf = st.text_area("ℹ️ التفاصيل")
                item = st.selectbox("📦 النوع:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
                
                if st.button("أضف الطلب للقائمة 📥"):
                    if trade_n:
                        st.session_state.temp_basket.append({
                            "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                            "full_name": full_n, "address": addr, "details": note_inf, "cooler_type": item
                        })
                        st.rerun()

            if st.session_state.temp_basket:
                st.subheader(f"🛒 القائمة الحالية ({len(st.session_state.temp_basket)})")
                for i, b in enumerate(st.session_state.temp_basket):
                    st.caption(f"{i+1}- {b['customer_name']} ({b['cooler_type']})")
                
                if st.button("🚀 إرسال كافة الطلبات للمدير"):
                    for req in st.session_state.temp_basket:
                        supabase.table("cooler_orders").insert({**req, "supervisor_name": user_identity, "status": "بانتظار موافقة المدير"}).execute()
                    st.session_state.temp_basket = []
                    st.success("تم إرسال المجموعة بنجاح!")
                    st.rerun()

    # --- واجهة إدارة وسجل الطلبات (سلسلة التوريد) ---
    with col2:
        st.header("📋 سجل حركة الطلبات")
        orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
        
        if orders:
            for o in orders:
                st_val = o['status']
                with st.expander(f"📦 {o['customer_name']} | {o['cooler_type']} | {st_val}"):
                    st.write(f"📍 المسار: {o['route_name']} | المندوب: {o['delegate_name']}")
                    st.write(f"📝 الاسم: {o['full_name']} | العنوان: {o['address']}")
                    if o.get('manager_notes'): st.error(f"❌ سبب الرفض/ملاحظة: {o['manager_notes']}")
                    if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")

                    # 1. مدير التنمية
                    if user_role == "مدير التنمية" and st_val == "بانتظار موافقة المدير":
                        rej_reason = st.text_input("سبب الرفض إن وجد:", key=f"m_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"ma_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"mr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": rej_reason}).eq("id", o['id']).execute()
                            st.rerun()

                    # 2. مسؤول المخزن
                    elif user_role == "مسؤول المخزن" and st_val == "تمت الموافقة - بانتظار المخزن":
                        ser_no = st.text_input("رقم البراد المجهز:", key=f"s_{o['id']}")
                        m_rej = st.text_input("سبب عدم التوفر:", key=f"sr_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تجهيز", key=f"sa_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser_no}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ غير متوفر", key=f"srj_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": m_rej}).eq("id", o['id']).execute()
                            st.rerun()

                    # 3. مسؤول التنسيق (محمد علي)
                    elif user_role == "قسم التنسيق (محمد علي)" and st_val == "تم التجهيز - بانتظار العقد":
                        if st.button("📝 تم إكمال العقد", key=f"co_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                            st.rerun()

                    # 4. سائق البرادات
                    elif user_role == "سائق البرادات" and st_val == "جاهز للتوصيل":
                        dr_n = st.text_input("سبب رفض العميل:", key=f"dn_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التسليم", key=f"da_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض العميل", key=f"dr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": dr_n}).eq("id", o['id']).execute()
                            st.rerun()
        else: st.info("لا توجد طلبات.")

    # Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #888;'>Programmed by: <b>Mohammed Ali Muheel</b></div>", unsafe_allow_html=True)
else: st.sidebar.warning("ادخل الرمز السري")
