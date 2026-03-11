import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="نظام بيبسي الموحد", layout="wide")

# الربط
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- نظام تسجيل الدخول البسيط ---
st.sidebar.title("🔑 تسجيل الدخول")
user_role = st.sidebar.selectbox("اختر هويتك:", ["مشرف", "مدير التنمية", "مسؤول المخزن"])
user_name = ""

if user_role == "مشرف":
    user_name = st.sidebar.selectbox("اسم المشرف:", ["مشعل رسول", "محمد أركن"])

st.title(f"🏢 لوحة تحكم: {user_role}")
st.markdown("---")

col1, col2 = st.columns([1, 2])

# --- أولاً: واجهة المشرف (إضافة الطلبات) ---
if user_role == "مشرف":
    with col1:
        st.header("➕ طلب براد جديد")
        customer = st.text_input("اسم العميل")
        route = st.text_input("المسار (مثلاً: الكرادة/المنصور)")
        location = st.text_input("العنوان بالتفصيل")
        cooler = st.selectbox("نوع البراد", ["براد دبل", "براد بيبسي وسط", "ستاند عرض"])
        
        if st.button("إرسال الطلب للاعتماد"):
            if customer and route:
                data = {
                    "customer_name": customer,
                    "route_name": route,
                    "address": location,
                    "cooler_type": cooler,
                    "supervisor_name": user_name,
                    "status": "بانتظار موافقة المدير"
                }
                supabase.table("cooler_orders").insert(data).execute()
                st.success("تم إرسال الطلب بنجاح")
                st.rerun()

# --- ثانياً: واجهة الإدارة والمخزن (عرض الطلبات) ---
with col2:
    st.header("📋 متابعة الطلبات")
    res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
    orders = res.data

    for order in orders:
        color = "🟡" if "بانتظار" in order['status'] else "🟢"
        if "مرفوض" in order['status']: color = "🔴"
        
        with st.expander(f"{color} {order['customer_name']} | المسار: {order.get('route_name', 'غير محدد')}"):
            st.write(f"👤 **المشرف:** {order.get('supervisor_name')}")
            st.write(f"🥤 **النوع:** {order['cooler_type']} | 📍 **العنوان:** {order['address']}")
            st.write(f"🔢 **رقم البراد:** {order.get('cooler_serial') or 'لم يحدد بعد'}")
            st.info(f"🚦 **الحالة:** {order['status']}")

            # صلاحيات مدير التنمية
            if user_role == "مدير التنمية" and "بانتظار" in order['status']:
                c1, c2 = st.columns(2)
                if c1.button("✅ موافقة", key=f"app_{order['id']}"):
                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار التجهيز"}).eq("id", order['id']).execute()
                    st.rerun()
                if c2.button("❌ رفض", key=f"rej_{order['id']}"):
                    supabase.table("cooler_orders").update({"status": "مرفوض"}).eq("id", order['id']).execute()
                    st.rerun()

            # صلاحيات مسؤول المخزن
            if user_role == "مسؤول المخزن" and "الموافقة" in order['status']:
                new_serial = st.text_input("أدخل رقم البراد:", key=f"ser_{order['id']}")
                if st.button("تحديث رقم البراد", key=f"btn_ser_{order['id']}"):
                    supabase.table("cooler_orders").update({"cooler_serial": new_serial, "status": "تم التجهيز بالكامل"}).eq("id", order['id']).execute()
                    st.rerun()
