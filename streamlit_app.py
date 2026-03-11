import streamlit as st
from supabase import create_client

# إعدادات الصفحة
st.set_page_config(page_title="منظومة بيبسي - واجهة السائق المحدثة", layout="wide")

# الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# --- قاعدة بيانات الرموز السرية ---
user_credentials = {
    "مشعل رسول": "1001",
    "محمد أركن": "1002",
    "حسين علي": "1003",
    "مدير التنمية": "2001",
    "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001",
    "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 تسجيل دخول آمن")
user_identity = st.sidebar.selectbox("اختر اسمك / صفتك:", list(user_credentials.keys()))
user_password = st.sidebar.text_input("أدخل رمز الدخول الخاص بك:", type="password")

if user_password == user_credentials[user_identity]:
    st.sidebar.success(f"أهلاً بك يا {user_identity}")
    
    if user_identity in ["مشعل رسول", "محمد أركن", "حسين علي"]:
        user_role = "مشرف"
        user_name = user_identity
    else:
        user_role = user_identity
        user_name = user_identity

    # --- 🔔 قسم التنبيهات الحية (الجديد) ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 تنبيهات النظام الحية")
    
    try:
        # جلب آخر 5 تحديثات طرأت على الطلبات
        recent_updates = supabase.table("cooler_orders").select("customer_name, status, created_at").order('created_at', desc=True).limit(5).execute()
        
        if recent_updates.data:
            for update in recent_updates.data:
                with st.sidebar.container(border=True):
                    st.caption(f"⏱️ {update['created_at'][:16].replace('T', ' ')}")
                    st.write(f"🏢 **{update['customer_name']}**")
                    st.info(f"📍 {update['status']}")
        else:
            st.sidebar.write("لا توجد تنبيهات حالياً.")
    except:
        st.sidebar.write("بانتظار تحديث البيانات...")

    st.title(f"🥤 لوحة تحكم: {user_identity}")
    st.markdown("---")

    col1, col2 = st.columns([1.3, 2.5])

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
                    if trade_name:
                        st.session_state.temp_orders.append({"trade_name": trade_name, "full_name": full_name, "address": address, "details": details, "cooler_type": c_type})
                        st.rerun()

            if st.session_state.temp_orders:
                if st.button("إرسال كافة الطلبات للمدير 🚀"):
                    for o in st.session_state.temp_orders:
                        supabase.table("cooler_orders").insert({
                            "customer_name": o['trade_name'], "full_name": o['full_name'], "route_name": route,
                            "delegate_name": delegate, "address": o['address'], "details": o['details'],
                            "cooler_type": o['cooler_type'], "supervisor_name": user_name, "status": "بانتظار موافقة المدير"
                        }).execute()
                    st.session_state.temp_orders = []
                    st.success("تم الإرسال بنجاح")
                    st.rerun()

    # --- واجهة العرض (Tabs) ---
    with col2:
        st.header("📋 سجل حركة الطلبات")
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        all_orders = res.data

        if all_orders:
            supervisors = ["مشعل رسول", "محمد أركن", "حسين علي"]
            tabs = st.tabs(supervisors)
            
            for i, sup in enumerate(supervisors):
                with tabs[i]:
                    sup_orders = [o for o in all_orders if o.get('supervisor_name') == sup]
                    for order in sup_orders:
                        status = order['status']
                        icon = "🟡"
                        if "الموافقة" in status: icon = "🔵"
                        if "المخزن" in status and "غير متوفر" in status: icon = "🟠"
                        if order.get('delivery_status') == "تم التوصيل بنجاح": icon = "✅"
                        if order.get('delivery_status') == "رفض الاستلام": icon = "❌"
                        
                        with st.expander(f"{icon} {order['customer_name']} | {order['cooler_type']} | {status}"):
                            st.write(f"📝 **المندوب:** {order.get('delegate_name')} | **الاسم:** {order.get('full_name')}")
                            st.write(f"🔢 **رقم البراد:** {order.get('cooler_serial') or '---'}")
                            if order.get('manager_notes'): st.info(f"📋 **ملاحظة المدير:** {order['manager_notes']}")
                            if order.get('driver_notes'): st.warning(f"⚠️ **ملاحظة السائق:** {order['driver_notes']}")

                            # --- مدير التنمية ---
                            if user_role == "مدير التنمية" and "بانتظار موافقة" in status:
                                n = st.text_input("ملاحظات:", key=f"n_{order['id']}")
                                c1, c2 = st.columns(2)
                                if c1.button("✅ موافقة", key=f"a_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن", "manager_notes": n}).eq("id", order['id']).execute()
                                    st.rerun()
                                if c2.button("❌ رفض", key=f"r_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "مرفوض من قبل المدير", "manager_notes": n}).eq("id", order['id']).execute()
                                    st.rerun()

                            # --- مسؤول المخزن ---
                            if user_role == "مسؤول المخزن" and "الموافقة" in status:
                                ser = st.text_input("رقم البراد:", key=f"s_{order['id']}")
                                c1, c2 = st.columns(2)
                                if c1.button("✅ حفظ الرقم", key=f"bs_{order['id']}"):
                                    if ser:
                                        supabase.table("cooler_orders").update({"cooler_serial": ser, "status": "تم التجهيز - بانتظار العقد"}).eq("id", order['id']).execute()
                                        st.rerun()
                                if c2.button("❌ غير متوفر", key=f"out_{order['id']}"):
                                    supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "cooler_serial": "غير متوفر"}).eq("id", order['id']).execute()
                                    st.rerun()

                            # --- قسم التنسيق (محمد علي) ---
                            if user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                                if st.button("📝 تم إنشاء العقد", key=f"c_{order['id']}"):
                                    supabase.table("cooler_orders").update({"contract_status": "تم إنشاء العقد", "status": "جاهز للتوصيل"}).eq("id", order['id']).execute()
                                    st.rerun()

                            # --- سائق البرادات ---
                            if user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                                st.markdown("---")
                                dr_note = st.text_input("ملاحظة السائق (سبب الرفض إن وجد):", key=f"drn_{order['id']}")
                                col_a, col_b = st.columns(2)
                                if col_a.button("✅ تم التوصيل بنجاح", key=f"ok_{order['id']}"):
                                    supabase.table("cooler_orders").update({"delivery_status": "تم التوصيل بنجاح", "status": "مكتمل"}).eq("id", order['id']).execute()
                                    st.rerun()
                                if col_b.button("❌ رفض الاستلام", key=f"fail_{order['id']}"):
                                    supabase.table("cooler_orders").update({"delivery_status": "رفض الاستلام", "driver_notes": dr_note, "status": "ملغي/مرفوض"}).eq("id", order['id']).execute()
                                    st.rerun()
        else:
            st.write("لا توجد بيانات.")

    # --- تذييل الصفحة (Footer) ---
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888; font-size: 0.9em; padding: 10px;'>"
        "Designed and Programmed by Coordination Officer: <b>Mohammed Ali Muheel</b>"
        "</div>", 
        unsafe_allow_html=True
    )

else:
    st.sidebar.info("يرجى إدخال الرمز السري.")
