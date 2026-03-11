import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="نظام بيبسي بغداد", layout="wide")

# الربط بقاعدة البيانات (المفاتيح اللي دزيتها أنت)
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_MjA3YzRhMTItMDY2Ny00ZDEzLWI1MDctNmU3MTBiYjQwZThm"
supabase = create_client(url, key)

st.title("🚛 نظام تنسيق البرادات - شركة بيبسي")
st.markdown("---")

# تصميم الخانات
col1, col2 = st.columns(2)

with col1:
    st.header("➕ إضافة طلب جديد")
    customer = st.text_input("اسم العميل (المحل/السوبر ماركت)")
    location = st.text_input("العنوان بالتفصيل")
    cooler = st.selectbox("نوع البراد", ["براد بيبسي كبير", "براد بيبسي وسط", "ستاند عرض"])
    
    if st.button("حفظ وإرسال للمدير"):
        if customer and location:
            # إدخال البيانات للجدول
            data = {"customer_name": customer, "address": location, "cooler_type": cooler, "status": "قيد الانتظار"}
            supabase.table("cooler_orders").insert(data).execute()
            st.success(f"✅ تم حفظ طلب {customer} بنجاح!")
        else:
            st.warning("الرجاء كتابة اسم العميل والعنوان")

with col2:
    st.header("📋 قائمة الطلبات الحالية")
    # عرض البيانات من Supabase
    try:
        res = supabase.table("cooler_orders").select("*").execute()
        for order in res.data:
            st.info(f"👤 {order['customer_name']} | 📍 {order['address']} | 🚦 {order['status']}")
    except:
        st.write("لا توجد بيانات حالياً. ابدأ بإضافة أول طلب!")
