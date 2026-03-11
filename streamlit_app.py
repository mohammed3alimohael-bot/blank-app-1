import streamlit as st
from supabase import create_client
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - فرع بغداد", layout="wide")

# الرابط والمفتاح (تأكد من نسخهم بدقة بدون مسافات)
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"

# محاولة الربط مع حماية الواجهة من الانهيار
try:
    supabase = create_client(url, key)
    db_status = True
except:
    db_status = False
    st.error("⚠️ هناك مشكلة في الاتصال بقاعدة البيانات، تأكد من الرابط والمفتاح.")

# --- قاعدة بيانات الرموز السرية ---
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

    col1, col2 = st.columns([1.3, 2.5])

    # --- واجهة المشرف (إضافة طلبات بكل الحقول) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ تقديم طلب جديد")
            # الحقول اللي كانت مختفية رجعت هنا بالكامل
            route = st.selectbox("📍 اختر المسار (Route):", ["1", "2", "3", "4", "5", "6"])
            delegate = st.text_input("👤 اسم المندوب")
            
            with st.container(border=True):
                trade_name = st.text_input("🏢 الاسم التجاري (المحل)")
                full_name = st.text_input("📝 الاسم الثلاثي للزبون")
                address = st.text_input("🗺️ العنوان بالتفصيل")
                details = st.text_area("ℹ️ ملاحظات إضافية")
                c_type = st.selectbox("نوع البراد المطلوب", [
                    "دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", 
                    "ثلاثي بيبسي", "سلم بيبسي", "ستاند 50", "ستاند 75", 
                    "ستاند 90", "ستاند 110", "ستاند 120"
                ])
                
                if st.button("إرسال الطلب للمدير 🚀"):
                    if trade_name and db_status:
                        supabase.table("cooler_orders").insert({
                            "customer_name": trade_name, 
                            "full_name": full_name, 
                            "route_name": route,
                            "delegate_name": delegate, 
                            "address": address, 
                            "details": details,
                            "cooler_type": c_type, 
                            "supervisor_name": user_identity, 
                            "status": "بانتظار موافقة المدير"
                        }).execute()
                        st.success("تم إرسال الطلب بنجاح!")
                        st.rerun()
                    elif not trade_name:
                        st.warning("يرجى كتابة اسم المحل أولاً.")

    # --- واجهة العرض والطباعة ---
    with col2:
        st.header("📋 سجل الحركة والطباعة")
        
        if db_status:
            res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
            all_data = res.data
            
            if all_data:
                # زر "عرض جدول الطباعة" اللي اتفقنا عليه
                if st.button("🖨️ تجهيز الجدول للطباعة"):
                    df = pd.DataFrame(all_data)
                    print_df = df[['customer_name', 'route_name', 'cooler_type', 'supervisor_name', 'status']]
                    print_df.columns = ['المحل', 'المسار', 'النوع', 'المشرف', 'الحالة']
                    st.table(print_df)
                    st.info("💡 اضغط الآن (Ctrl + P) لطباعة هذا الجدول.")

                # نظام التبويبات (Tabs) للمشرفين
                supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
                tabs = st.tabs(supervisors)
                for i, sup in enumerate(supervisors):
                    with tabs[i]:
                        sup_orders = [o for o in all_data if o.get('supervisor_name') == sup]
                        for order in sup_orders:
                            with st.expander(f"📦 {order['customer_name']} | {order['status']}"):
                                st.write(f"🏠 **العنوان:** {order.get('address')}")
                                st.write(f"📝 **صاحب الطلب:** {order.get('full_name')}")
                                # أزرار الإدارة (مدير، مخزن، الخ)
                                if user_role == "مدير التنمية" and "بانتظار موافقة" in order['status']:
                                    if st.button("✅ موافقة", key=f"app_{order['id']}"):
                                        supabase.table("cooler_orders").update({"status": "تمت الموافقة"}).eq("id", order['id']).execute()
                                        st.rerun()
            else:
                st.write("لا توجد طلبات حالياً.")
else:
    st.info("يرجى إدخال الرمز السري للدخول.")
