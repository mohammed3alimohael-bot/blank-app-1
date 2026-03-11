import streamlit as st
from supabase import create_client
import time

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - واجهة السائق المحدثة", layout="wide")

# --- كود الإخفاء القسري الشامل والتوقيع ---
st.markdown("""
    <style>
    [data-testid="stHeader"] {display: none !important;}
    #MainMenu {visibility: hidden !important;}
    .stActionButton {display: none !important;}
    .stDeployButton {display:none !important;}
    footer {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    img[src*="streamlit_logo"] {display: none !important;}
    div[class^="viewerBadge"] {display: none !important;}
    
    .custom-footer {
        position: fixed;
        bottom: 10px;
        right: 10px;
        background-color: #111;
        color: #fff;
        padding: 5px 12px;
        font-size: 12px;
        border-radius: 5px;
        border: 1px solid #333;
        z-index: 999999;
        font-family: sans-serif;
    }
    </style>
    <div class="custom-footer">
        Designed and Programmed by Coordination Manager: Mohammed Ali Muheel
    </div>
""", unsafe_allow_html=True)

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

# نظام تسجيل الدخول
st.sidebar.title("🔐 تسجيل دخول آمن")
user_identity = st.sidebar.selectbox("اختر اسمك / صفتك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("أدخل رمز الدخول الخاص بك:", type="password")

if user_password == user_credentials[user_identity]:
    st.sidebar.success(f"أهلاً بك يا {user_identity}")
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    user_name = user_identity

    st.title(f"🥤 لوحة تحكم: {user_identity}")
    st.markdown("---")

    col1, col2 = st.columns([1.3, 2.5])

    # --- واجهة المشرف ---
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
                c_type = st.selectbox("نوع البراد", ["دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "ستاند 90", "ستاند 120"])
                
                if st.button("أضف للقائمة ➕"):
                    if trade_name:
                        st.session_state.temp_orders.append({"trade_name": trade_name, "full_name": full_name, "address": address, "cooler_type": c_type})
                        st.toast(f"تمت إضافة {trade_name} للقائمة المؤقتة ✅")
                        time.sleep(0.5)
                        st.rerun()

            if st.session_state.temp_orders:
                if st.button("إرسال كافة الطلبات للمدير 🚀"):
                    for o in st.session_state.temp_orders:
                        supabase.table("cooler_orders").insert({
                            "customer_name": o['trade_name'], "full_name": o['full_name'], "route_name": route,
                            "delegate_name": delegate, "address": o['address'], "status": "بانتظار موافقة المدير", "supervisor_name": user_name
                        }).execute()
                    st.session_state.temp_orders = []
                    st.toast("تم إرسال الطلبات بنجاح إلى المدير 🚀", icon="📩")
                    time.sleep(1)
                    st.rerun()

    # --- واجهة العرض وحركات الطلبات ---
    with col2:
        st.header("📋 سجل حركة الطلبات")
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        all_orders = res.data

        if all_orders:
            supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
            tabs = st.tabs(supervisors)
            for i, sup in enumerate(supervisors):
                with tabs[i]:
                    sup_orders = [o for o in all_orders if o.get('supervisor_name') == sup]
                    for order in sup_orders:
                        status = order['status']
                        with st.expander(f"{order['customer_name']} | {status}"):
                            # حركات المدير
                            if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                                if st.button("✅ موافقة", key=f"a_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", order['id']).execute()
                                    st.toast(f"تمت الموافقة على طلب {order['customer_name']} 👍")
                                    time.sleep(1)
                                    st.rerun()
                            
                            # حركات المخزن
                            if user_role == "مسؤول المخزن" and "الموافقة" in status:
                                if st.button("✅ تم تجهيز البراد", key=f"bs_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد"}).eq("id", order['id']).execute()
                                    st.toast(f"تم تجهيز براد {order['customer_name']} في المخزن 🏗️")
                                    time.sleep(1)
                                    st.rerun()

                            # حركات التنسيق
                            if user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                                if st.button("📝 تم إنشاء العقد", key=f"c_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", order['id']).execute()
                                    st.toast(f"تم إكمال عقد {order['customer_name']} 📄")
                                    time.sleep(1)
                                    st.rerun()

                            # حركات السائق
                            if user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                                if st.button("✅ تم التوصيل", key=f"ok_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", order['id']).execute()
                                    st.toast(f"مبروك! تم توصيل طلب {order['customer_name']} بنجاح 🎉")
                                    time.sleep(1)
                                    st.rerun()
        else:
            st.write("لا توجد بيانات.")
else:
    st.sidebar.info("يرجى إدخال الرمز السري.")
