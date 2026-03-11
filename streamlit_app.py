import streamlit as st
from supabase import create_client
from datetime import datetime

# 1. إعدادات الصفحة وإخفاء العناصر العلوية ليكون التصميم نظيفاً
st.set_page_config(page_title="منظومة التنسيق - شركة بيبسي", layout="wide")

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

# 3. قاعدة بيانات المستخدمين والصلاحيات
user_credentials = {
    "مشعل رسول": "1001",
    "محمد أركن": "1002",
    "حسين علي": "1003",
    "مدير التنمية": "2001",
    "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001",
    "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 تسجيل الدخول")
user_identity = st.sidebar.selectbox("اختر اسمك / صفتك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("أدخل رمز الدخول:", type="password")

if user_password == user_credentials[user_identity]:
    st.sidebar.success(f"أهلاً بك يا {user_identity}")
    
    # تحديد الدور الوظيفي
    if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"]:
        user_role = "مشرف"
    else:
        user_role = user_identity

    # --- 🔔 قسم الإشعارات الحية (متابعة الحركات) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 آخر التحديثات")
    try:
        logs = supabase.table("cooler_orders").select("customer_name, status, created_at").order('created_at', desc=True).limit(5).execute()
        if logs.data:
            for log in logs.data:
                with st.sidebar.container(border=True):
                    st.caption(f"⏱️ {log['created_at'][:16].replace('T', ' ')}")
                    st.write(f"🏢 **{log['customer_name']}**")
                    st.info(f"📍 {log['status']}")
    except:
        st.sidebar.write("بانتظار تحديث البيانات...")

    st.title(f"🥤 لوحة تحكم: {user_identity}")
    st.markdown("---")

    col1, col2 = st.columns([1.5, 2.5])

    # --- المرحلة 1: واجهة المشرف (إنشاء الطلب) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ إنشاء طلب جديد")
            with st.container(border=True):
                route = st.radio("📍 اختر المسار (Route):", ["1", "2", "3", "4", "5", "6"], horizontal=True)
                delegate_name = st.text_input("👤 اسم المندوب")
                trade_name = st.text_input("🏢 الاسم التجاري للعميل")
                full_name = st.text_input("📝 اسم العميل الثلاثي")
                address = st.text_input("🗺️ العنوان التفصيلي")
                details = st.text_area("ℹ️ تفاصيل إضافية")
                
                item_type = st.selectbox("📦 نوع المادة (البراد/الملحقات):", [
                    "سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", 
                    "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", 
                    "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"
                ])
                
                if st.button("إرسال الطلب للمدير 🚀", use_container_width=True):
                    if trade_name and delegate_name:
                        supabase.table("cooler_orders").insert({
                            "route_name": route,
                            "delegate_name": delegate_name,
                            "customer_name": trade_name,
                            "full_name": full_name,
                            "address": address,
                            "details": details,
                            "cooler_type": item_type,
                            "supervisor_name": user_identity,
                            "status": "بانتظار موافقة المدير"
                        }).execute()
                        st.success("تم إرسال الطلب بنجاح إلى مدير التنمية")
                        st.rerun()
                    else:
                        st.error("يرجى ملء البيانات الأساسية")

    # --- واجهة سجل الطلبات والمتابعة (تظهر للجميع) ---
    with col2:
        st.header("📋 سجل حركة الطلبات")
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        all_orders = res.data

        if all_orders:
            for order in all_orders:
                status = order['status']
                with st.expander(f"📦 {order['customer_name']} | {order['cooler_type']} | {status}"):
                    st.write(f"📍 **المسار:** {order.get('route_name')} | **المندوب:** {order.get('delegate_name')}")
                    st.write(f"📝 **الاسم الثلاثي:** {order.get('full_name')}")
                    st.write(f"🗺️ **العنوان:** {order.get('address')}")
                    st.write(f"ℹ️ **التفاصيل:** {order.get('details')}")
                    
                    # عرض الملاحظات السابقة إن وجدت
                    if order.get('manager_notes'): st.error(f"⚠️ ملاحظة (الرفض/السبب): {order['manager_notes']}")
                    if order.get('driver_notes'): st.warning(f"⚠️ ملاحظة السائق: {order['driver_notes']}")
                    if order.get('cooler_serial'): st.success(f"🔢 رقم البراد: {order['cooler_serial']}")

                    # --- المرحلة 2: مدير التنمية (موافقة/رفض) ---
                    if user_role == "مدير التنمية" and status == "بانتظار موافقة المدير":
                        note = st.text_input("بيان السبب (في حال الرفض):", key=f"note_{order['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"app_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", order['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض الطلب", key=f"rej_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من قبل المدير", "manager_notes": note}).eq("id", order['id']).execute()
                            st.rerun()

                    # --- المرحلة 3: مسؤول المخزن (تجهيز/رقم براد) ---
                    elif user_role == "مسؤول المخزن" and status == "تمت الموافقة - بانتظار المخزن":
                        serial = st.text_input("أدخل رقم البراد المجهز:", key=f"ser_{order['id']}")
                        m_reason = st.text_input("سبب عدم التوفر (في حال الرفض):", key=f"m_re_{order['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التجهيز", key=f"s_ok_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": serial}).eq("id", order['id']).execute()
                            st.rerun()
                        if c2.button("❌ غير متوفر", key=f"s_no_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": m_reason}).eq("id", order['id']).execute()
                            st.rerun()

                    # --- المرحلة 4: مسؤول التنسيق (محمد علي) - العقد ---
                    elif user_role == "قسم التنسيق (محمد علي)" and status == "تم التجهيز - بانتظار العقد":
                        if st.button("📝 تم إكمال العقد وتحويله للتوصيل", key=f"con_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", order['id']).execute()
                            st.rerun()

                    # --- المرحلة 5: سائق البرادات (التسليم النهائي) ---
                    elif user_role == "سائق البرادات" and status == "جاهز للتوصيل":
                        dr_note = st.text_input("سبب رفض العميل للاستلام (إن وجد):", key=f"dr_{order['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التسليم بنجاح", key=f"d_ok_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل", "delivery_status": "تم التسليم"}).eq("id", order['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض الاستلام", key=f"d_no_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "ملغي - رفض استلام", "driver_notes": dr_note}).eq("id", order['id']).execute()
                            st.rerun()
        else:
            st.info("لا توجد طلبات مسجلة في السجل حالياً.")

    # --- تذييل الصفحة (Footer) ---
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888; font-size: 0.9em; padding: 10px;'>"
        "Designed and Programmed by Coordination Officer: <b>Mohammed Ali Muheel</b>"
        "</div>", 
        unsafe_allow_html=True
    )
else:
    st.sidebar.warning("يرجى اختيار اسمك وإدخال الرمز السري الصحيح للوصول.")
