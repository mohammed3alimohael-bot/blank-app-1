import streamlit as st
from supabase import create_client
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - فرع بغداد", layout="wide")

# الرابط والمفتاح
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"

try:
    supabase = create_client(url, key)
    db_status = True
except:
    db_status = False
    st.error("⚠️ خطأ في الاتصال بقاعدة البيانات.")

# رموز الدخول
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

st.sidebar.title("🔐 بوابة الدخول")
user_identity = st.sidebar.selectbox("اختر اسمك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("الرمز السري:", type="password")

if user_password == user_credentials[user_identity]:
    user_role = "مشرف" if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else user_identity
    
    st.title(f"🥤 لوحة تحكم: {user_identity}")
    st.markdown("---")

    col1, col2 = st.columns([1.5, 2.5])

    # --- واجهة المشرف (إرسال دفعة واحدة) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ تجهيز قائمة الطلبات")
            
            # معلومات المسار والمندوب ثابتة لكل الدفعة
            route = st.selectbox("📍 المسار:", ["1", "2", "3", "4", "5", "6"])
            delegate = st.text_input("👤 اسم المندوب")
            
            # إنشاء قائمة مؤقتة في المتصفح
            if 'basket' not in st.session_state:
                st.session_state.basket = []

            with st.container(border=True):
                st.subheader("إضافة زبون للقائمة")
                t_name = st.text_input("🏢 الاسم التجاري")
                f_name = st.text_input("📝 الاسم الثلاثي")
                addr = st.text_input("🗺️ العنوان")
                c_type = st.selectbox("نوع البراد", ["دبل بيبسي", "سنكل بيبسي", "سلم بيبسي", "ستاند 90", "ثلاثي"])
                
                if st.button("إضافة إلى السلة 📥"):
                    if t_name:
                        st.session_state.basket.append({
                            "customer_name": t_name, "full_name": f_name, 
                            "address": addr, "cooler_type": c_type
                        })
                        st.rerun()

            # عرض السلة المؤقتة قبل الإرسال
            if st.session_state.basket:
                st.markdown("### 🛒 الطلبات الجاهزة للإرسال")
                for i, item in enumerate(st.session_state.basket):
                    st.text(f"{i+1}- {item['customer_name']} ({item['cooler_type']})")
                
                if st.button("🚀 إرسال كافة الطلبات للمدير الآن"):
                    for o in st.session_state.basket:
                        supabase.table("cooler_orders").insert({
                            "customer_name": o['customer_name'], "full_name": o['full_name'],
                            "route_name": route, "delegate_name": delegate,
                            "address": o['address'], "cooler_type": o['cooler_type'],
                            "supervisor_name": user_identity, "status": "بانتظار موافقة المدير"
                        }).execute()
                    st.session_state.basket = [] # تفريغ السلة بعد الإرسال
                    st.success("تم إرسال الدفعة بالكامل!")
                    st.rerun()
                
                if st.button("🗑️ تفريغ السلة"):
                    st.session_state.basket = []
                    st.rerun()

    # --- واجهة العرض والطباعة ---
    with col2:
        st.header("📋 سجل الحركة والطباعة")
        if db_status:
            res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
            all_data = res.data
            
            if all_data:
                if st.button("🖨️ تجهيز جدول الطباعة"):
                    df = pd.DataFrame(all_data)
                    st.table(df[['customer_name', 'cooler_type', 'supervisor_name', 'status']])
                    st.info("💡 اضغط (Ctrl + P) للطباعة")

                tabs = st.tabs(["مشعل رسول", "محمد أركن", "حسين علي"])
                for i, sup in enumerate(["مشعل رسول", "محمد أركن", "حسين علي"]):
                    with tabs[i]:
                        orders = [o for o in all_data if o.get('supervisor_name') == sup]
                        for order in orders:
                            with st.expander(f"📦 {order['customer_name']} | {order['status']}"):
                                st.write(f"🏠 العنوان: {order.get('address')}")
                                if user_role == "مدير التنمية" and "بانتظار موافقة" in order['status']:
                                    if st.button("✅ موافقة", key=order['id']):
                                        supabase.table("cooler_orders").update({"status": "تمت الموافقة"}).eq("id", order['id']).execute()
                                        st.rerun()
            else:
                st.write("لا توجد بيانات.")
else:
    st.info("يرجى إدخال الرمز السري.")
