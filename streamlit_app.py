import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - نظام التقارير والطباعة", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- كود تحسين شكل الطباعة ---
st.markdown("""
    <style>
    @media print {
        .stSidebar, .stButton, .stDownloadButton, header, footer, .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
        }
        .print-table {
            width: 100%;
            border-collapse: collapse;
            direction: rtl;
        }
        .print-table th, .print-table td {
            border: 1px solid black;
            padding: 8px;
            text-align: right;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- قاعدة بيانات الرموز السرية ---
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 تسجيل دخول آمن")
user_identity = st.sidebar.selectbox("اختر اسمك / صفتك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("أدخل رمز الدخول الخاص بك:", type="password")

if user_password == user_credentials[user_identity]:
    st.sidebar.success(f"أهلاً بك يا {user_identity}")
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    user_name = user_identity

    st.title(f"🥤 لوحة تحكم: {user_identity}")
    
    col1, col2 = st.columns([1.3, 2.5])

    # --- واجهة المشرف (إضافة طلبات) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ طلب جديد")
            route = st.selectbox("📍 المسار:", ["1", "2", "3", "4", "5", "6"])
            delegate = st.text_input("👤 المندوب")
            with st.container(border=True):
                trade_name = st.text_input("🏢 الاسم التجاري")
                full_name = st.text_input("📝 الاسم الثلاثي")
                addr = st.text_input("🗺️ العنوان")
                c_type = st.selectbox("نوع البراد", ["دبل بيبسي", "سنكل بيبسي", "ستاند 50", "ستاند 75", "ستاند 90", "ستاند 110", "ستاند 120", "سلم بيبسي"])
                if st.button("أضف مؤقتاً ➕"):
                    if 'temp_orders' not in st.session_state: st.session_state.temp_orders = []
                    st.session_state.temp_orders.append({"trade_name": trade_name, "full_name": full_name, "address": addr, "cooler_type": c_type})
                    st.rerun()

            if st.session_state.get('temp_orders'):
                if st.button("إرسال الكل 🚀"):
                    for o in st.session_state.temp_orders:
                        supabase.table("cooler_orders").insert({
                            "customer_name": o['trade_name'], "full_name": o['full_name'], "route_name": route,
                            "delegate_name": delegate, "address": o['address'], "cooler_type": o['cooler_type'],
                            "supervisor_name": user_name, "status": "بانتظار موافقة المدير"
                        }).execute()
                    st.session_state.temp_orders = []
                    st.rerun()

    # --- واجهة العرض والطباعة ---
    with col2:
        st.header("📋 سجل حركة الطلبات")
        
        # زر الطباعة (يستخدم خاصية الجافا سكريبت لفتح نافذة طباعة المتصفح)
        if st.button("🖨️ طباعة التقرير الحالي"):
            st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
            st.info("💡 سيتم فتح نافذة الطباعة.. تأكد من اختيار 'حفظ بتنسيق PDF' أو الطابعة الخاصة بك.")

        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        all_orders = res.data

        if all_orders:
            supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
            tabs = st.tabs(supervisors)
            
            for i, sup in enumerate(supervisors):
                with tabs[i]:
                    sup_orders = [o for o in all_orders if o.get('supervisor_name') == sup]
                    if sup_orders:
                        # عرض جدول مخصص للطباعة
                        st.markdown(f"### تقرير طلبات المشرف: {sup}")
                        for order in sup_orders:
                            status = order['status']
                            icon = "✅" if order.get('delivery_status') == "تم التوصيل بنجاح" else "🟡"
                            
                            with st.expander(f"{icon} {order['customer_name']} | {order['cooler_type']} | {status}"):
                                st.write(f"📍 المسار: {order['route_name']} | المندوب: {order.get('delegate_name')}")
                                st.write(f"🔢 الرقم: {order.get('cooler_serial') or '---'}")
                                
                                # --- أزرار التحكم (مدير، مخزن، منسق، سائق) ---
                                # (بقيت كما هي في الكود السابق لتؤدي وظائفها)
                                if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                                    n = st.text_input("ملاحظات:", key=f"n_{order['id']}")
                                    if st.button("✅ موافقة", key=f"a_{order['id']}"):
                                        supabase.table("cooler_orders").update({"status": "تمت الموافقة", "manager_notes": n}).eq("id", order['id']).execute()
                                        st.rerun()
                                
                                if user_role == "مسؤول المخزن" and "الموافقة" in status:
                                    ser = st.text_input("رقم البراد:", key=f"s_{order['id']}")
                                    if st.button("حفظ وتجهيز", key=f"b_{order['id']}"):
                                        supabase.table("cooler_orders").update({"cooler_serial": ser, "status": "تم التجهيز"}).eq("id", order['id']).execute()
                                        st.rerun()

                                if user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                                    if st.button("📝 عقد مكتمل", key=f"c_{order['id']}"):
                                        supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", order['id']).execute()
                                        st.rerun()

                                if user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                                    if st.button("🚚 تم التوصيل", key=f"d_{order['id']}"):
                                        supabase.table("cooler_orders").update({"delivery_status": "تم التوصيل بنجاح", "status": "مكتمل"}).eq("id", order['id']).execute()
                                        st.rerun()
                    else:
                        st.write("لا توجد طلبات.")
        else:
            st.write("لا توجد بيانات.")
else:
    st.sidebar.info("أدخل الرمز السري للدخول.")
