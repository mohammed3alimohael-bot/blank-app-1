import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - طباعة التقارير", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- كود CSS لإخفاء الأشياء غير الضرورية عند الطباعة ---
st.markdown("""
    <style>
    @media print {
        /* إخفاء القائمة الجانبية والأزرار والرأس والتذييل */
        .stSidebar, .stButton, header, footer, [data-testid="stHeader"] {
            display: none !important;
        }
        /* توسيع محتوى الصفحة ليشمل كل الورقة */
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
        }
        /* إظهار الجداول بشكل أوضح */
        .stExpander {
            border: 1px solid #ccc !important;
            margin-bottom: 10px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- نظام الرموز والولوج (نفس الكود السابق) ---
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

st.sidebar.title("🔐 تسجيل دخول")
user_identity = st.sidebar.selectbox("اختر الاسم:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("الرمز السري:", type="password")

if user_password == user_credentials[user_identity]:
    st.sidebar.success(f"أهلاً {user_identity}")
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    
    # --- عنوان النظام ---
    st.title("🥤 نظام متابعة برادات بيبسي")
    st.markdown("---")

    col1, col2 = st.columns([1, 2.8])

    # واجهة المشرف (إضافة الطلبات)
    if user_role == "مشرف":
        with col1:
            st.header("➕ إضافة طلب")
            route = st.selectbox("📍 المسار:", ["1", "2", "3", "4", "5", "6"])
            trade_name = st.text_input("🏢 المحل")
            full_name = st.text_input("📝 الاسم الثلاثي")
            if st.button("أضف الطلب للقائمة"):
                if trade_name:
                    supabase.table("cooler_orders").insert({
                        "customer_name": trade_name, "full_name": full_name, "route_name": route,
                        "supervisor_name": user_identity, "status": "بانتظار موافقة المدير"
                    }).execute()
                    st.success("تم الحفظ!")
                    st.rerun()

    # واجهة العرض والطباعة
    with col2:
        st.header("📋 حركة الطلبات")
        
        # زر الطباعة مع تعليمات واضحة
        if st.button("🖨️ تجهيز الصفحة للطباعة"):
            st.warning("🔄 تم تجهيز الصفحة! الآن اضغط على (Ctrl + P) من لوحة المفاتيح للطباعة أو الحفظ كـ PDF.")
        
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        all_orders = res.data

        if all_orders:
            supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
            tabs = st.tabs(supervisors)
            
            for i, sup in enumerate(supervisors):
                with tabs[i]:
                    st.subheader(f"طلبات المشرف: {sup}")
                    sup_orders = [o for o in all_orders if o.get('supervisor_name') == sup]
                    
                    if sup_orders:
                        for order in sup_orders:
                            with st.expander(f"📦 {order['customer_name']} | الحالة: {order['status']}"):
                                st.write(f"📍 المسار: {order['route_name']} | 📝 صاحب المحل: {order.get('full_name')}")
                                st.write(f"🔢 رقم البراد: {order.get('cooler_serial') or 'قيد التجهيز'}")
                                
                                # أزرار الإدارة (مدير، مخزن، الخ) تظهر هنا حسب صلاحية الشخص الداخل
                                if user_role == "مدير التنمية" and "بانتظار موافقة" in order['status']:
                                    if st.button("موافقة ✅", key=f"a_{order['id']}"):
                                        supabase.table("cooler_orders").update({"status": "تمت الموافقة"}).eq("id", order['id']).execute()
                                        st.rerun()
                    else:
                        st.info("لا توجد طلبات لهذا المشرف.")
else:
    st.info("الرجاء إدخال الرمز السري للدخول.")
