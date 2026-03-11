import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="نظام توزيع برادات بيبسي", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- نظام تسجيل الدخول البسيط ---
st.sidebar.title("🔑 بوابة الدخول")
user_role = st.sidebar.selectbox("اختر الصلاحية:", ["مشرف", "مدير التنمية", "مسؤول المخزن"])

user_name = ""
if user_role == "مشرف":
    user_name = st.sidebar.selectbox("اسم المشرف:", ["مشعل رسول", "محمد أركن"])

st.title(f"🥤 لوحة تحكم: {user_role}")
st.markdown("---")

col1, col2 = st.columns([1, 2])

# --- أولاً: واجهة المشرف (إضافة الطلبات) ---
if user_role == "مشرف":
    with col1:
        st.header("➕ طلب براد جديد")
        customer = st.text_input("اسم العميل (المحل)")
        route = st.text_input("المسار (Route)")
        location = st.text_input("العنوان بالتفصيل")
        # أنواع البرادات الجديدة حسب طلبك
        cooler = st.selectbox("نوع البراد", [
            "دبل بيبسي", 
            "سنكل بيبسي", 
            "سنكل يومي", 
            "سنكل اكوافينا", 
            "ثلاثي بيبسي", 
            "سلم بيبسي"
        ])
        
        if st.button("إرسال الطلب للاعتماد"):
            if customer and route:
                try:
                    data = {
                        "customer_name": customer,
                        "route_name": route,
                        "address": location,
                        "cooler_type": cooler,
                        "supervisor_name": user_name,
                        "status": "بانتظار موافقة المدير"
                    }
                    supabase.table("cooler_orders").insert(data).execute()
                    st.success(f"✅ تم إرسال طلب {customer} للمدير")
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ في الإرسال: {e}")
            else:
                st.warning("الرجاء إكمال اسم العميل والمسار")

# --- ثانياً: عرض وإدارة الطلبات (تظهر للجميع حسب صلاحياته) ---
with col2:
    st.header("📋 متابعة حركة البرادات")
    try:
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        orders = res.data

        if orders:
            for order in orders:
                # تحديد اللون حسب الحالة
                status = order['status']
                color = "🟡" # انتظار
                if "الموافقة" in status: color = "🔵" # بانتظار المخزن
                if "التجهيز" in status: color = "🟢" # كمل
                if "مرفوض" in status: color = "🔴" # رفض
                
                with st.expander(f"{color} {order['customer_name']} | {order.get('route_name', 'بدون مسار')}"):
                    st.write(f"👤 **المشرف:** {order.get('supervisor_name', 'غير معروف')}")
                    st.write(f"🚛 **نوع البراد:** {order['cooler_type']}")
                    st.write(f"📍 **العنوان:** {order['address']}")
                    st.write(f"🔢 **رقم البراد (الشركة):** {order.get('cooler_serial') or '---'}")
                    st.info(f"🚦 **الحالة الحالية:** {status}")

                    # --- صلاحيات مدير التنمية ---
                    if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"app_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار رقم البراد"}).eq("id", order['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"rej_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من قبل المدير"}).eq("id", order['id']).execute()
                            st.rerun()

                    # --- صلاحيات مسؤول المخزن ---
                    if user_role == "مسؤول المخزن" and "الموافقة" in status:
                        serial = st.text_input("أدخل رقم البراد الصادر:", key=f"ser_{order['id']}")
                        if st.button("تحديث وتسليم", key=f"btn_ser_{order['id']}"):
                            if serial:
                                supabase.table("cooler_orders").update({
                                    "cooler_serial": serial, 
                                    "status": "تم التجهيز بالكامل"
                                }).eq("id", order['id']).execute()
                                st.success("تم تسجيل الرقم وتجهيز الطلب")
                                st.rerun()
                            else:
                                st.error("يرجى كتابة رقم البراد أولاً")
        else:
            st.write("لا توجد طلبات حالياً.")
    except Exception as e:
        st.error(f"حدث خطأ في عرض البيانات: {e}")
