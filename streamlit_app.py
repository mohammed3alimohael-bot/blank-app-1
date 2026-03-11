import streamlit as st
from supabase import create_client
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - فرع بغداد", layout="wide")

# الربط (تأكد من صحة هذه الروابط في حسابك)
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"

try:
    supabase = create_client(url, key)
except Exception as e:
    st.error(f"⚠️ خطأ في الربط: تأكد من رابط Supabase. الخطأ: {e}")

# --- نظام الرموز والولوج ---
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

    # --- واجهة العرض والطباعة ---
    st.header("📋 سجل الطلبات والطباعة")
    
    # جلب البيانات من السحاب
    res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
    data = res.data

    if data:
        # تحويل البيانات لجدول (Pandas) للسهولة
        df = pd.DataFrame(data)
        
        # اختيار الأعمدة المهمة للطباعة فقط
        report_df = df[['customer_name', 'route_name', 'cooler_type', 'supervisor_name', 'status']]
        report_df.columns = ['اسم العميل', 'المسار', 'نوع البراد', 'المشرف', 'الحالة']

        # زر الطباعة الفعلي
        if st.button("🖨️ عرض جدول الطباعة"):
            st.subheader("📄 تقرير الطلبات الجاهز للطباعة")
            st.table(report_df) # يعرض جدول بسيط جداً يسهل على المتصفح طباعته
            st.info("💡 الآن اضغط (Ctrl + P) لطباعة هذا الجدول فقط.")
        
        # --- العرض العادي (الأكورديون) ---
        st.markdown("---")
        supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
        tabs = st.tabs(supervisors)
        
        for i, sup in enumerate(supervisors):
            with tabs[i]:
                sup_orders = [o for o in data if o.get('supervisor_name') == sup]
                for order in sup_orders:
                    with st.expander(f"📦 {order['customer_name']} - {order['status']}"):
                        st.write(f"📍 المسار: {order['route_name']}")
                        # أزرار الإدارة توضع هنا...
                        if user_role == "مدير التنمية" and "بانتظار موافقة" in order['status']:
                            if st.button("موافقة ✅", key=order['id']):
                                supabase.table("cooler_orders").update({"status": "تمت الموافقة"}).eq("id", order['id']).execute()
                                st.rerun()
    else:
        st.write("لا توجد بيانات حالياً.")

    # --- واجهة إضافة الطلب (للمشرفين فقط) ---
    if user_role == "مشرف":
        st.sidebar.markdown("---")
        st.sidebar.header("➕ إضافة طلب جديد")
        r = st.sidebar.selectbox("📍 المسار:", ["1", "2", "3", "4", "5", "6"])
        c = st.sidebar.text_input("🏢 اسم المحل:")
        if st.sidebar.button("حفظ وإرسال"):
            supabase.table("cooler_orders").insert({"customer_name": c, "route_name": r, "supervisor_name": user_identity, "status": "بانتظار موافقة المدير"}).execute()
            st.rerun()

else:
    st.info("الرجاء إدخال الرمز السري الصحيح في القائمة الجانبية.")
