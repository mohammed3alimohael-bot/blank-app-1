import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي المتكاملة", layout="wide")

# الربط بقاعدة البيانات
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

# --- ميزة الإشعارات العامة ---
def show_notifications():
    try:
        # جلب آخر التحديثات من المدير والسائق
        res = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(3).execute()
        updates = res.data
        if updates:
            st.sidebar.markdown("### 🔔 آخر التحديثات")
            for up in updates:
                if "مرفوض" in up['status'] or "الموافقة" in up['status']:
                    msg = f"مدير التنمية: {up.get('manager_notes') or 'بدون ملاحظات'}"
                    st.sidebar.warning(f"📌 {up['customer_name']}\n\n{msg}")
    except:
        pass

show_notifications()

col1, col2 = st.columns([1.3, 2])

# --- واجهة المشرف ---
if user_role == "مشرف":
    with col1:
        st.header("➕ تقديم طلبات جديدة")
        route = st.selectbox("📍 اختر المسار (Route):", ["1", "2", "3", "4", "5", "6"])
        delegate = st.text_input("👤 اسم المندوب")
        
        if 'temp_orders' not in st.session_state: st.session_state.temp_orders = []

        with st.container(border=True):
            trade_name = st.text_input("🏢 الاسم التجاري")
            full_name = st.text_input("📝 الاسم الثلاثي")
            address = st.text_input("🗺️ العنوان")
            details = st.text_area("ℹ️ ملاحظات المشرف")
            c_type = st.selectbox("نوع البراد", ["دبل بيبسي", "سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "ثلاثي بيبسي", "سلم بيبسي", "ستاند 50", "ستاند 75", "ستاند 90", "ستاند 110", "ستاند 120"])
            
            if st.button("أضف للقائمة ➕"):
                st.session_state.temp_orders.append({"trade_name": trade_name, "full_name": full_name, "address": address, "details": details, "cooler_type": c_type})

        if st.session_state.temp_orders:
            if st.button("إرسال الكل للمدير 🚀"):
                for o in st.session_state.temp_orders:
                    supabase.table("cooler_orders").insert({
                        "customer_name": o['trade_name'], "full_name": o['full_name'], "route_name": route,
                        "delegate_name": delegate, "address": o['address'], "details": o['details'],
                        "cooler_type": o['cooler_type'], "supervisor_name": user_name, "status": "بانتظار موافقة المدير"
                    }).execute()
                st.session_state.temp_orders = []
                st.rerun()

# --- واجهة العرض والمتابعة ---
with col2:
    st.header("📋 سجل حركة الطلبات")
    res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
    orders = res.data

    if orders:
        for order in orders:
            status = order['status']
            icon = "🟡"
            if "الموافقة" in status: icon = "🔵"
            if order.get('delivery_status') == "تم التوصيل بنجاح": icon = "✅"
            if order.get('delivery_status') == "رفض الاستلام": icon = "❌"
            
            with st.expander(f"{icon} {order['customer_name']} | {status}"):
                st.write(f"👤 **المشرف:** {order['supervisor_name']} | **المندوب:** {order.get('delegate_name')}")
                st.write(f"🔢 **رقم البراد:** {order.get('cooler_serial') or '---'}")
                
                # عرض ملاحظات المدير للمشرفين
                if order.get('manager_notes'):
                    st.info(f"📋 **ملاحظة المدير:** {order['manager_notes']}")
                
                # عرض ملاحظات السائق
                if order.get('driver_notes'):
                    st.warning(f"⚠️ **ملاحظة السائق:** {order['driver_notes']}")
                
                # --- صلاحيات مدير التنمية ---
                if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                    m_notes = st.text_input("اكتب سبب الرفض أو ملاحظات الموافقة:", key=f"mnot_{order['id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ موافقة", key=f"ap_{order['id']}"):
                        supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن", "manager_notes": m_notes}).eq("id", order['id']).execute()
                        st.rerun()
                    if c2.button("❌ رفض", key=f"rej_{order['id']}"):
                        supabase.table("cooler_orders").update({"status": "مرفوض من قبل المدير", "manager_notes": m_notes}).eq("id", order['id']).execute()
                        st.rerun()

                # --- صلاحيات مسؤول المخزن ---
                if user_role == "مسؤول المخزن" and "الموافقة" in status:
                    serial = st.text_input("رقم البراد:", key=f"ser_{order['id']}")
                    if st.button("حفظ الرقم", key=f"bs_{order['id']}"):
                        supabase.table("cooler_orders").update({"cooler_serial": serial, "status": "تم التجهيز - بانتظار العقد"}).eq("id", order['id']).execute()
                        st.rerun()

                # --- صلاحيات المنسق ---
                if user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                    if st.button("📝 تم إنشاء العقد", key=f"con_{order['id']}"):
                        supabase.table("cooler_orders").update({"contract_status": "تم إنشاء العقد", "status": "جاهز للتوصيل"}).eq("id", order['id']).execute()
                        st.rerun()

                # --- صلاحيات السائق ---
                if user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                    d1, d2 = st.columns(2)
                    if d1.button("✅ تم التوصيل", key=f"ok_{order['id']}"):
                        supabase.table("cooler_orders").update({"delivery_status": "تم التوصيل بنجاح", "status": "مكتمل"}).eq("id", order['id']).execute()
                        st.rerun()
                    
                    reason = st.text_input("سبب رفض العميل:", key=f"re_{order['id']}")
                    if d2.button("❌ رفض الاستلام", key=f"fail_{order['id']}"):
                        supabase.table("cooler_orders").update({"delivery_status": "رفض الاستلام", "driver_notes": reason, "status": "ملغي/مرفوض"}).eq("id", order['id']).execute()
                        st.rerun()
