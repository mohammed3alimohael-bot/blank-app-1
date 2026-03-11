import streamlit as st
from supabase import create_client

# 1. إعدادات الصفحة للهاتف والخط الكوفي
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    .main-title {
        font-family: 'Reem Kufi', sans-serif;
        font-size: 32px;
        color: #0056b3;
        text-align: center;
        margin-top: -30px;
        margin-bottom: 20px;
    }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton button { width: 100%; border-radius: 8px; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. بيانات المستخدمين
user_creds = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- واجهة تسجيل الدخول في المنتصف (للهاتف) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 تسجيل الدخول")
        u_identity = st.selectbox("اختر اسمك / صفتك:", list(user_creds.keys()))
        u_pass = st.text_input("أدخل الرمز السري الخاص بك:", type="password")
        if st.button("دخول المنظومة 🚀"):
            if u_pass == user_creds[u_identity]:
                st.session_state.logged_in = True
                st.session_state.user_name = u_identity
                st.rerun()
            else:
                st.error("الرمز السري غير صحيح!")
    st.stop()

# --- بعد تسجيل الدخول ---
u_name = st.session_state.user_name
user_role = "مشرف" if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"] else u_name

# 🔔 نظام الإشعارات (آخر 10 حركات بالتفصيل)
with st.expander("🔔 إشعارات الحركة الأخيرة", expanded=False):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        for log in logs:
            st.markdown(f"**{log['customer_name']}**: {log['status']}")
            if log.get('manager_notes'): st.caption(f"⚠️ ملاحظة المدير: {log['manager_notes']}")
            if log.get('driver_notes'): st.caption(f"⚠️ ملاحظة السائق: {log['driver_notes']}")
            st.divider()
    except: st.write("لا توجد تنبيهات حالياً.")

# --- واجهة المشرف (إضافة وإرسال دفعة واحدة) ---
if user_role == "مشرف":
    st.subheader("➕ تقديم طلبات جديدة")
    if 'basket' not in st.session_state: st.session_state.basket = []
    
    with st.container(border=True):
        route = st.select_slider("📍 اختر المسار:", options=["1", "2", "3", "4", "5", "6"])
        delegate = st.text_input("👤 اسم المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري للعميل")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        details = st.text_area("ℹ️ ملاحظات إضافية")
        
        if st.button("أضف للقائمة المؤقتة 📥"):
            if trade_n:
                st.session_state.basket.append({
                    "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                    "full_name": full_n, "address": addr, "details": details, "cooler_type": item
                })
                st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 لديك ({len(st.session_state.basket)}) طلبات بانتظار الإرسال")
        if st.button("🚀 إرسال كافة الطلبات للمدير الآن", type="primary"):
            for req in st.session_state.basket:
                supabase.table("cooler_orders").insert({**req, "supervisor_name": u_name, "status": "بانتظار موافقة المدير"}).execute()
            st.session_state.basket = []
            st.success("تم الإرسال بنجاح!")
            st.rerun()

# --- عرض وسجل الطلبات (سلسلة التوريد) ---
st.subheader("📋 متابعة الطلبات")
res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data

if res:
    for o in res:
        status = o['status']
        with st.expander(f"📦 {o['customer_name']} | {status}"):
            # عرض كافة التفاصيل لجميع المستخدمين
            st.write(f"**المندوب:** {o['delegate_name']} | **المسار:** {o['route_name']}")
            st.write(f"**الاسم الثلاثي:** {o['full_name']}")
            st.write(f"**العنوان:** {o['address']} | **النوع:** {o['cooler_type']}")
            st.write(f"**التفاصيل:** {o['details']}")
            st.write(f"**المشرف:** {o['supervisor_name']}")
            
            if o.get('manager_notes'): st.error(f"❌ ملاحظة المدير: {o['manager_notes']}")
            if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")

            # إجراءات المستخدمين
            if user_role == "مدير التنمية" and "بانتظار موافقة المدير" in status:
                n = st.text_input("سبب الرفض (إن وجد):", key=f"n_{o['id']}")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ موافقة", key=f"a_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                    st.rerun()
                if col_b.button("❌ رفض", key=f"r_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": n}).eq("id", o['id']).execute()
                    st.rerun()

            elif user_role == "مسؤول المخزن" and "الموافقة" in status:
                ser = st.text_input("رقم البراد:", key=f"s_{o['id']}")
                wn = st.text_input("سبب عدم التوفر:", key=f"wn_{o['id']}")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ تجهيز", key=f"wa_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser}).eq("id", o['id']).execute()
                    st.rerun()
                if col_b.button("❌ غير متوفر", key=f"wr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": wn}).eq("id", o['id']).execute()
                    st.rerun()

            elif user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                if st.button("📝 تم إكمال العقد", key=f"c_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                    st.rerun()

            elif user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                dn = st.text_input("سبب رفض الاستلام:", key=f"dn_{o['id']}")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ تم التسليم", key=f"ok_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                    st.rerun()
                if col_b.button("❌ رفض استلام", key=f"fail_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": dn}).eq("id", o['id']).execute()
                    st.rerun()

    # --- 📑 قسم التصدير العمودي ---
    with st.expander("📑 تصدير البيانات بنظام القوائم (للنسخ)"):
        def get_list(field): return "\n".join([str(x.get(field, '-')) for x in res])
        export_text = f"🏢 الاسم التجاري:\n{get_list('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_list('full_name')}\n\n👤 المندوب:\n{get_list('delegate_name')}\n\n📍 المسار:\n{get_list('route_name')}\n\n🎖️ المشرف:\n{get_list('supervisor_name')}\n\n📦 نوع البراد:\n{get_list('cooler_type')}\n\n🗺️ العنوان:\n{get_list('address')}"
        st.text_area("انسخ البيانات من هنا:", value=export_text, height=250)
else:
    st.info("لا توجد طلبات حالياً.")

# --- ⚠️ زر التصفير (خاص بمحمد علي فقط) ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    if st.button("⚠️ تصفير كافة الطلبات (بدء من الصفر)"):
        supabase.table("cooler_orders").delete().neq("id", 0).execute()
        st.success("تم تصفير المنظومة!")
        st.rerun()

st.divider()
st.markdown("<center style='color: #888; font-size: 11px;'>Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></center>", unsafe_allow_html=True)
