import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="نظام بيبسي - الطلبات المتعددة", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔑 بوابة الدخول")
user_role = st.sidebar.selectbox("اختر الصلاحية:", ["مشرف", "مدير التنمية", "مسؤول المخزن"])

user_name = ""
if user_role == "مشرف":
    user_name = st.sidebar.selectbox("اسم المشرف:", ["مشعل رسول", "محمد أركن", "حسين علي"])

st.title(f"🥤 لوحة تحكم: {user_role}")
st.markdown("---")

col1, col2 = st.columns([1.2, 2])

# --- أولاً: واجهة المشرف (إضافة طلبات متعددة) ---
if user_role == "مشرف":
    with col1:
        st.header("➕ تقديم طلبات متعددة")
        route = st.text_input("المسار المشترك (Route)")
        
        # استخدام session_state لخزن قائمة العملاء المؤقتة قبل الحفظ
        if 'temp_orders' not in st.session_state:
            st.session_state.temp_orders = []

        with st.container(border=True):
            st.subheader("إضافة عميل للقائمة")
            cust_name = st.text_input("اسم العميل")
            cust_loc = st.text_input("العنوان")
            c_type = st.selectbox("نوع البراد", [
                "دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", 
                "ثلاثي بيبسي", "سلم بيبسي", "ستاند 50", "ستاند 75", 
                "ستاند 90", "ستاند 110", "ستاند 120"
            ])
            
            if st.button("أضف العميل للقائمة ➕"):
                if cust_name and cust_loc:
                    st.session_state.temp_orders.append({
                        "customer_name": cust_name,
                        "address": cust_loc,
                        "cooler_type": c_type
                    })
                    st.toast(f"تمت إضافة {cust_name}")
                else:
                    st.error("املاً البيانات")

        # عرض القائمة المؤقتة
        if st.session_state.temp_orders:
            st.write("---")
            st.write("📋 العملاء المضافون حالياً:")
            for i, o in enumerate(st.session_state.temp_orders):
                st.text(f"{i+1}. {o['customer_name']} - {o['cooler_type']}")
            
            if st.button("إرسال الكل لمدير التنمية 🚀"):
                try:
                    for o in st.session_state.temp_orders:
                        data = {
                            "customer_name": o['customer_name'],
                            "route_name": route,
                            "address": o['address'],
                            "cooler_type": o['cooler_type'],
                            "supervisor_name": user_name,
                            "status": "بانتظار موافقة المدير"
                        }
                        supabase.table("cooler_orders").insert(data).execute()
                    st.success("تم إرسال كافة الطلبات بنجاح!")
                    st.session_state.temp_orders = [] # تصفير القائمة
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ: {e}")

# --- ثانياً: عرض وإدارة الطلبات (لكل عميل سطر مستقل) ---
with col2:
    st.header("📋 متابعة الطلبات")
    try:
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        orders = res.data

        if orders:
            for order in orders:
                status = order['status']
                # أيقونة الحالة
                icon = "🟡"
                if "الموافقة" in status: icon = "🔵"
                if "التجهيز" in status: icon = "✅"
                if "مرفوض" in status: icon = "❌"
                
                with st.expander(f"{icon} {order['customer_name']} | {order['cooler_type']} | {order.get('route_name')}"):
                    st.write(f"👤 **المشرف:** {order.get('supervisor_name')} | 📍 **العنوان:** {order['address']}")
                    st.write(f"🔢 **رقم البراد:** {order.get('cooler_serial') or '---'}")
                    st.info(f"🚦 **الحالة:** {status}")

                    # --- صلاحيات مدير التنمية (موافقة أو رفض لكل شخص) ---
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
                        serial = st.text_input("رقم البراد:", key=f"ser_{order['id']}")
                        if st.button("تسجيل الرقم", key=f"btn_ser_{order['id']}"):
                            if serial:
                                supabase.table("cooler_orders").update({"cooler_serial": serial, "status": "تم التجهيز بالكامل"}).eq("id", order['id']).execute()
                                st.rerun()
        else:
            st.write("لا توجد بيانات.")
    except Exception as e:
        st.error(f"خطأ: {e}")
