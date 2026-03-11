import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="نظام بيبسي - الإدارة المتكاملة", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔑 بوابة الدخول")
user_role = st.sidebar.selectbox("اختر الصلاحية:", ["مشرف", "مدير التنمية", "مسؤول المخزن"])

user_name = ""
if user_role == "مشرف":
    user_name = st.sidebar.selectbox("اسم المشرف الحالي:", ["مشعل رسول", "محمد أركن", "حسين علي"])

st.title(f"🥤 لوحة تحكم: {user_role}")
st.markdown("---")

col1, col2 = st.columns([1.3, 2])

# --- أولاً: واجهة المشرف (إضافة طلبات تفصيلية) ---
if user_role == "مشرف":
    with col1:
        st.header("➕ تقديم طلبات المشرف")
        
        # المسار واسم المندوب غالباً يكونون مشتركين لمجموعة عملاء
        route = st.text_input("📍 المسار (Route)")
        delegate = st.text_input("👤 اسم المندوب")
        
        if 'temp_orders' not in st.session_state:
            st.session_state.temp_orders = []

        with st.container(border=True):
            st.subheader("إضافة عميل جديد للقائمة")
            trade_name = st.text_input("🏢 الاسم التجاري (المحل)")
            full_name = st.text_input("📝 الاسم الثلاثي لصاحب المحل")
            address = st.text_input("🗺️ العنوان بالتفصيل")
            details = st.text_area("ℹ️ تفاصيل إضافية (ملاحظات)")
            
            c_type = st.selectbox("نوع البراد", [
                "دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", 
                "ثلاثي بيبسي", "سلم بيبسي", "ستاند 50", "ستاند 75", 
                "ستاند 90", "ستاند 110", "ستاند 120"
            ])
            
            if st.button("أضف العميل للقائمة ➕"):
                if trade_name and route:
                    st.session_state.temp_orders.append({
                        "trade_name": trade_name,
                        "full_name": full_name,
                        "address": address,
                        "details": details,
                        "cooler_type": c_type
                    })
                    st.toast(f"تمت إضافة {trade_name} مؤقتاً")
                else:
                    st.error("يرجى ملء الاسم التجاري والمسار على الأقل")

        if st.session_state.temp_orders:
            st.write("---")
            st.write(f"📋 الطلبات الحالية للمسار: **{route}**")
            for i, o in enumerate(st.session_state.temp_orders):
                st.text(f"{i+1}. {o['trade_name']} - {o['cooler_type']}")
            
            if st.button("إرسال كافة الطلبات للمدير 🚀"):
                try:
                    for o in st.session_state.temp_orders:
                        data = {
                            "customer_name": o['trade_name'], # الاسم التجاري
                            "full_name": o['full_name'],     # الاسم الثلاثي
                            "route_name": route,             # المسار
                            "delegate_name": delegate,       # المندوب
                            "address": o['address'],
                            "details": o['details'],         # التفاصيل
                            "cooler_type": o['cooler_type'],
                            "supervisor_name": user_name,
                            "status": "بانتظار موافقة المدير"
                        }
                        supabase.table("cooler_orders").insert(data).execute()
                    st.success("تم إرسال كافة البيانات بنجاح!")
                    st.session_state.temp_orders = []
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ في الحفظ: {e}")

# --- ثانياً: عرض الطلبات (التفصيلية) ---
with col2:
    st.header("📋 سجل الطلبات والتجهيز")
    try:
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        orders = res.data

        if orders:
            for order in orders:
                status = order['status']
                icon = "🟡"
                if "الموافقة" in status: icon = "🔵"
                if "التجهيز" in status: icon = "✅"
                if "مرفوض" in status: icon = "❌"
                
                with st.expander(f"{icon} {order['customer_name']} | {order.get('route_name')} | {order['cooler_type']}"):
                    st.write(f"👤 **المشرف:** {order.get('supervisor_name')} | **المندوب:** {order.get('delegate_name')}")
                    st.write(f"📝 **الاسم الثلاثي:** {order.get('full_name')}")
                    st.write(f"📍 **العنوان:** {order['address']}")
                    st.write(f"ℹ️ **التفاصيل:** {order.get('details')}")
                    st.write(f"🔢 **رقم البراد:** {order.get('cooler_serial') or '---'}")
                    st.info(f"🚦 **الحالة:** {status}")

                    # أزرار مدير التنمية
                    if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"app_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار رقم البراد"}).eq("id", order['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"rej_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من قبل المدير"}).eq("id", order['id']).execute()
                            st.rerun()

                    # أزرار مسؤول المخزن
                    if user_role == "مسؤول المخزن" and "الموافقة" in status:
                        serial = st.text_input("رقم البراد:", key=f"ser_{order['id']}")
                        if st.button("تسجيل الرقم", key=f"btn_ser_{order['id']}"):
                            if serial:
                                supabase.table("cooler_orders").update({"cooler_serial": serial, "status": "تم التجهيز بالكامل"}).eq("id", order['id']).execute()
                                st.rerun()
        else:
            st.write("السجل فارغ حالياً.")
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
