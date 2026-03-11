import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي المتكاملة", layout="wide")

# الربط
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔑 بوابة الدخول")
user_role = st.sidebar.selectbox("اختر الصلاحية:", 
    ["مشرف", "مدير التنمية", "مسؤول المخزن", "قسم التنسيق (محمد علي)", "سائق البرادات"])

user_name = ""
if user_role == "مشرف":
    user_name = st.sidebar.selectbox("اسم المشرف:", ["مشعل رسول", "محمد أركن", "حسين علي"])

st.title(f"🥤 لوحة تحكم: {user_role}")
st.markdown("---")

col1, col2 = st.columns([1.3, 2])

# --- واجهة المشرف (إضافة طلبات تفصيلية) ---
if user_role == "مشرف":
    with col1:
        st.header("➕ تقديم طلبات جديدة")
        
        # تعديل خانة المسار لتصبح قائمة خيارات
        route = st.selectbox("📍 اختر المسار (Route):", ["1", "2", "3", "4", "5", "6"])
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
                if trade_name:
                    st.session_state.temp_orders.append({
                        "trade_name": trade_name,
                        "full_name": full_name,
                        "address": address,
                        "details": details,
                        "cooler_type": c_type
                    })
                    st.toast(f"تمت إضافة {trade_name}")
                else:
                    st.error("يرجى ملء الاسم التجاري")

        if st.session_state.temp_orders:
            st.write("---")
            st.write(f"📋 الطلبات الحالية للمسار رقم: **{route}**")
            for i, o in enumerate(st.session_state.temp_orders):
                st.text(f"{i+1}. {o['trade_name']} - {o['cooler_type']}")
            
            if st.button("إرسال كافة الطلبات للمدير 🚀"):
                try:
                    for o in st.session_state.temp_orders:
                        data = {
                            "customer_name": o['trade_name'],
                            "full_name": o['full_name'],
                            "route_name": route,
                            "delegate_name": delegate,
                            "address": o['address'],
                            "details": o['details'],
                            "cooler_type": o['cooler_type'],
                            "supervisor_name": user_name,
                            "status": "بانتظار موافقة المدير"
                        }
                        supabase.table("cooler_orders").insert(data).execute()
                    st.success("تم إرسال البيانات بنجاح!")
                    st.session_state.temp_orders = []
                    st.rerun()
                except Exception as e:
                    st.error(f"خطأ في الحفظ: {e}")

# --- واجهة العرض والإدارة ---
with col2:
    st.header("📋 سجل حركة الطلبات")
    try:
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        orders = res.data

        if orders:
            for order in orders:
                status = order['status']
                icon = "🟡"
                if "الموافقة" in status: icon = "🔵"
                if "التوصيل" in order.get('delivery_status', ''): icon = "🚚"
                if order.get('delivery_status') == "تم التوصيل بنجاح": icon = "✅"
                if order.get('delivery_status') == "رفض الاستلام": icon = "❌"
                
                with st.expander(f"{icon} {order['customer_name']} | مسار {order.get('route_name')} | {order['cooler_type']}"):
                    st.write(f"👤 **المشرف:** {order.get('supervisor_name')} | **المندوب:** {order.get('delegate_name')}")
                    st.write(f"📝 **الاسم الثلاثي:** {order.get('full_name')}")
                    st.write(f"📍 **العنوان:** {order['address']}")
                    st.write(f"🔢 **رقم البراد:** {order.get('cooler_serial') or '---'}")
                    st.write(f"📄 **العقد:** {order.get('contract_status', 'لم ينشأ')}")
                    st.info(f"🚦 **الحالة:** {status}")

                    # أزرار مدير التنمية
                    if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"app_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", order['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"rej_{order['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من قبل المدير"}).eq("id", order['id']).execute()
                            st.rerun()

                    # أزرار مسؤول المخزن
                    if user_role == "مسؤول المخزن" and "الموافقة" in status:
                        serial = st.text_input("رقم البراد:", key=f"ser_{order['id']}")
                        if st.button("حفظ الرقم", key=f"btn_ser_{order['id']}"):
                            supabase.table("cooler_orders").update({"cooler_serial": serial, "status": "تم التجهيز - بانتظار العقد"}).eq("id", order['id']).execute()
                            st.rerun()

                    # أزرار قسم التنسيق (محمد علي)
                    if user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                        if st.button("📝 تم إنشاء العقد", key=f"con_{order['id']}"):
                            supabase.table("cooler_orders").update({"contract_status": "تم إنشاء العقد بنجاح", "status": "جاهز للتوصيل"}).eq("id", order['id']).execute()
                            st.rerun()

                    # أزرار السائق
                    if user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                        d1, d2 = st.columns(2)
                        if d1.button("✅ تم التوصيل", key=f"dev_{order['id']}"):
                            supabase.table("cooler_orders").update({"delivery_status": "تم التوصيل بنجاح", "status": "مكتمل"}).eq("id", order['id']).execute()
                            st.rerun()
                        if d2.button("❌ رفض الاستلام", key=f"ref_{order['id']}"):
                            notes = st.text_input("سبب الرفض:", key=f"not_{order['id']}")
                            if st.button("تأكيد الرفض", key=f"cnf_{order['id']}"):
                                supabase.table("cooler_orders").update({"delivery_status": "رفض الاستلام", "driver_notes": notes, "status": "ملغي/مرفوض"}).eq("id", order['id']).execute()
                                st.rerun()
        else:
            st.write("لا توجد بيانات.")
    except Exception as e:
        st.error(f"خطأ: {e}")
