import streamlit as st
from supabase import create_client
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - واجهة السائق المحدثة", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- قاعدة بيانات الرموز السرية ---
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
st.sidebar.title("🔐 تسجيل دخول آمن")
user_identity = st.sidebar.selectbox("اختر اسمك / صفتك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("أدخل رمز الدخول الخاص بك:", type="password")

if user_password == user_credentials[user_identity]:
    st.sidebar.success(f"أهلاً بك يا {user_identity}")
    
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    user_name = user_identity

    # --- 🔔 قسم التنبيهات الحية ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 تنبيهات النظام الحية")
    try:
        updates = supabase.table("cooler_orders").select("customer_name, status, created_at").order('created_at', desc=True).limit(5).execute()
        if updates.data:
            for up in updates.data:
                with st.sidebar.container(border=True):
                    st.caption(f"⏱️ {up['created_at'][:16].replace('T', ' ')}")
                    st.write(f"🏢 **{up['customer_name']}**")
                    st.info(f"📍 {up['status']}")
    except:
        st.sidebar.write("بانتظار البيانات...")

    st.title(f"🥤 لوحة تحكم: {user_identity}")
    st.markdown("---")

    col1, col2 = st.columns([1.3, 2.5])

    # --- واجهة المشرف (إضافة طلبات) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ تقديم طلبات جديدة")
            route = st.selectbox("📍 اختر المسار (Route):", ["1", "2", "3", "4", "5", "6"])
            delegate = st.text_input("👤 اسم المندوب")
            if 'temp_orders' not in st.session_state: st.session_state.temp_orders = []
            with st.container(border=True):
                trade_name = st.text_input("🏢 الاسم التجاري")
                full_name = st.text_input("📝 الاسم الثلاثي")
                address = st.text_input("🗺️ العنوان")
                c_type = st.selectbox("نوع البراد", ["دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "ثلاثي بيبسي", "سلم بيبسي", "ستاند 50", "ستاند 75", "ستاند 90", "ستاند 110", "ستاند 120"])
                if st.button("أضف للقائمة ➕"):
                    if trade_name:
                        st.session_state.temp_orders.append({"trade_name": trade_name, "full_name": full_name, "address": address, "cooler_type": c_type})
                        st.rerun()
            if st.session_state.temp_orders:
                if st.button("إرسال كافة الطلبات للمدير 🚀"):
                    for o in st.session_state.temp_orders:
                        supabase.table("cooler_orders").insert({"customer_name": o['trade_name'], "full_name": o['full_name'], "route_name": route, "delegate_name": delegate, "address": o['address'], "cooler_type": o['cooler_type'], "supervisor_name": user_name, "status": "بانتظار موافقة المدير"}).execute()
                    st.session_state.temp_orders = []
                    st.success("تم الإرسال!")
                    st.rerun()

    # --- واجهة العرض وسجل الحركة ---
    with col2:
        st.header("📋 سجل حركة الطلبات")
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        all_orders = res.data

        if all_orders:
            # --- 📝 قسم تصدير النص (الجديد) ---
            with st.expander("📝 تصدير طلبات اليوم كنص للنسخ"):
                today_str = datetime.now().strftime("%Y-%m-%d")
                summary_text = f"📋 تقرير طلبات البرادات ليوم: {today_str}\n"
                summary_text += "----------------------------------\n"
                
                count = 0
                for o in all_orders:
                    if o['created_at'].startswith(today_str):
                        count += 1
                        summary_text += f"{count}- العميل: {o['customer_name']}\n"
                        summary_text += f"   النوع: {o['cooler_type']} | الحالة: {o['status']}\n"
                        summary_text += f"   العنوان: {o['address']}\n"
                        summary_text += "------------------\n"
                
                if count > 0:
                    st.text_area("انسخ النص من هنا:", value=summary_text, height=300)
                    st.info("حدد النص أعلاه وقم بنسخه (Ctrl+C).")
                else:
                    st.write("لا توجد طلبات مسجلة اليوم.")

            # عرض التبويبات (المشرفين)
            supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
            tabs = st.tabs(supervisors)
            for i, sup in enumerate(supervisors):
                with tabs[i]:
                    sup_orders = [o for o in all_orders if o.get('supervisor_name') == sup]
                    for order in sup_orders:
                        with st.expander(f"🏢 {order['customer_name']} | {order['status']}"):
                            st.write(f"📍 العنوان: {order['address']}")
                            st.write(f"👤 المندوب: {order['delegate_name']}")
                            # (بقية عمليات الإدارة تبقى كما هي...)
        else:
            st.write("لا توجد بيانات.")

    # --- Footer ---
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #888;'>Designed and Programmed by: <b>Mohammed Ali Muheel</b></div>", unsafe_allow_html=True)
else:
    st.sidebar.info("يرجى إدخال الرمز السري.")

# كود إخفاء العناصر العلوية (Header)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
