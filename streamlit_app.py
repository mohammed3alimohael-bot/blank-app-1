import streamlit as st
from supabase import create_client
from datetime import datetime

# 1. إعدادات الصفحة وإخفاء العناصر العلوية
st.set_page_config(page_title="منظومة بيبسي - التنسيق الموحد", layout="wide")

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

# 3. الصلاحيات
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 دخول المنظومة")
user_id = st.sidebar.selectbox("اختر اسمك:", list(user_credentials.keys()))
user_pass = st.sidebar.text_input("الرمز السري:", type="password")

if user_pass == user_credentials[user_id]:
    user_role = "مشرف" if user_id in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_id
    
    # --- 🔔 الإشعارات الحية ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 تنبيهات الحركة")
    try:
        logs = supabase.table("cooler_orders").select("customer_name, status").order('created_at', desc=True).limit(5).execute()
        for log in logs.data:
            st.sidebar.caption(f"🏢 {log['customer_name']}: {log['status']}")
    except: pass

    st.title(f"🥤 لوحة تحكم: {user_id}")

    col1, col2 = st.columns([1.5, 2.5])

    # --- المرحلة 1: المشرف (إضافة وإرسال دفعة واحدة) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ إنشاء طلبات")
            if 'basket' not in st.session_state: st.session_state.basket = []
            
            with st.container(border=True):
                route = st.radio("📍 المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
                delegate = st.text_input("👤 اسم المندوب")
                trade_n = st.text_input("🏢 الاسم التجاري")
                full_n = st.text_input("📝 الاسم الثلاثي")
                addr = st.text_input("🗺️ العنوان")
                note_inf = st.text_area("ℹ️ التفاصيل")
                item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
                
                if st.button("إضافة الطلب للقائمة 📥"):
                    if trade_n:
                        st.session_state.basket.append({
                            "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                            "full_name": full_n, "address": addr, "details": note_inf, "cooler_type": item
                        })
                        st.rerun()

            if st.session_state.basket:
                st.subheader(f"🛒 القائمة الجاهزة ({len(st.session_state.basket)})")
                if st.button("🚀 إرسال الكل للمدير"):
                    for req in st.session_state.basket:
                        supabase.table("cooler_orders").insert({**req, "supervisor_name": user_id, "status": "بانتظار موافقة المدير"}).execute()
                    st.session_state.basket = []
                    st.success("تم الإرسال!")
                    st.rerun()

    # --- المرحلة 2-5: إدارة الطلبات والتصدير النصي ---
    with col2:
        # --- 📑 قسم التصدير النصي (الطلب الخاص) ---
        with st.expander("📑 تصدير البيانات بنظام القوائم (للنسخ)"):
            all_res = supabase.table("cooler_orders").select("*").execute().data
            if all_res:
                def get_col(key): return "\n".join([str(o.get(key, '---')) for o in all_res])
                
                output = f"🏢 الاسم التجاري:\n{get_col('customer_name')}\n\n"
                output += f"📝 الاسم الثلاثي:\n{get_col('full_name')}\n\n"
                output += f"👤 اسم المندوب:\n{get_col('delegate_name')}\n\n"
                output += f"📍 المسار:\n{get_col('route_name')}\n\n"
                output += f"🎖️ اسم المشرف:\n{get_col('supervisor_name')}\n\n"
                output += f"📦 نوع البراد:\n{get_col('cooler_type')}\n\n"
                output += f"🗺️ العنوان:\n{get_col('address')}"
                
                st.text_area("انسخ البيانات من هنا مباشرة:", value=output, height=300)
            else: st.write("لا توجد بيانات للتصدير.")

        st.header("📋 متابعة الطلبات")
        orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
        
        if orders:
            for o in orders:
                st_val = o['status']
                with st.expander(f"📦 {o['customer_name']} | {st_val}"):
                    st.write(f"المسار: {o['route_name']} | المندوب: {o['delegate_name']} | النوع: {o['cooler_type']}")
                    if o.get('manager_notes'): st.error(f"سبب الرفض: {o['manager_notes']}")
                    if o.get('cooler_serial'): st.success(f"رقم البراد: {o['cooler_serial']}")

                    # مدير التنمية
                    if user_role == "مدير التنمية" and st_val == "بانتظار موافقة المدير":
                        reason = st.text_input("السبب عند الرفض:", key=f"m_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"ma_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"mr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": reason}).eq("id", o['id']).execute()
                            st.rerun()

                    # مسؤول المخزن
                    elif user_role == "مسؤول المخزن" and st_val == "تمت الموافقة - بانتظار المخزن":
                        ser = st.text_input("رقم البراد:", key=f"s_{o['id']}")
                        reason = st.text_input("السبب:", key=f"sr_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تجهيز", key=f"sa_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ غير متوفر", key=f"srj_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": reason}).eq("id", o['id']).execute()
                            st.rerun()

                    # قسم التنسيق (محمد علي)
                    elif user_role == "قسم التنسيق (محمد علي)" and st_val == "تم التجهيز - بانتظار العقد":
                        if st.button("📝 تم إكمال العقد", key=f"co_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                            st.rerun()

                    # سائق البرادات
                    elif user_role == "سائق البرادات" and st_val == "جاهز للتوصيل":
                        note = st.text_input("سبب الرفض:", key=f"dn_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التسليم", key=f"da_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"dr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": note}).eq("id", o['id']).execute()
                            st.rerun()
        else: st.info("لا توجد طلبات.")

    st.markdown("---")
    st.markdown("<center>Designed by: <b>Mohammed Ali Muheel</b></center>", unsafe_allow_html=True)
else: st.sidebar.warning("ادخل الرمز السري")
