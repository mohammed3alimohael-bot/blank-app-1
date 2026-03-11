import streamlit as st
from supabase import create_client

# إعدادات واجهة النظام
st.set_page_config(page_title="نظام بيبسي بغداد", layout="wide")

# الربط بقاعدة البيانات - المفاتيح الخاصة بك
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_MjA3YzRhMTItMDY2Ny00ZDEzLWI1MDctNmU3MTBiYjQwZThm"
supabase = create_client(url, key)

st.title("🚛 نظام تنسيق البرادات - شركة بيبسي")
st.markdown("---")

# تقسيم الشاشة إلى عمودين
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("➕ إضافة طلب جديد")
    
    # خانات الإدخال
    customer = st.text_input("اسم العميل (المحل/السوبر ماركت)")
    location = st.text_input("العنوان بالتفصيل")
    cooler = st.selectbox("نوع البراد", ["براد بيبسي كبير", "براد بيبسي وسط", "ستاند عرض"])
    
    if st.button("حفظ وإرسال للمدير"):
        if customer and location:
            try:
                # تجهيز البيانات للإرسال (تأكد من مطابقة أسماء الأعمدة للجدول)
                data = {
                    "customer_name": customer, 
                    "address": location, 
                    "cooler_type": cooler, 
                    "status": "قيد الانتظار"
                }
                # تنفيذ الإرسال
                supabase.table("cooler_orders").insert(data).execute()
                st.success(f"✅ تم حفظ طلب {customer} بنجاح!")
                st.balloons() # بالونات احتفال عند النجاح
            except Exception as e:
                st.error(f"حدث خطأ أثناء الحفظ: {e}")
        else:
            st.warning("الرجاء كتابة اسم العميل والعنوان")

with col2:
    st.header("📋 قائمة الطلبات الحالية")
    
    # جلب البيانات من Supabase وعرضها
    try:
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        
        if res.data:
            for order in res.data:
                # عرض كل طلب في صندوق خاص
                with st.expander(f"👤 {order['customer_name']} - {order['status']}"):
                    st.write(f"📍 **العنوان:** {order['address']}")
                    st.write(f"🥤 **نوع البراد:** {order['cooler_type']}")
                    st.write(f"📅 **التاريخ:** {order['created_at'][:10]}")
        else:
            st.write("لا توجد طلبات مسجلة حالياً.")
    except:
        st.write("يتم تحديث قائمة الطلبات...")
