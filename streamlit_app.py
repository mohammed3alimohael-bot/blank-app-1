import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والخط الكوفي
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    .main-title { font-family: 'Reem Kufi', sans-serif; font-size: 30px; color: #0045ad; text-align: center; margin-top: -40px; }
    header {visibility: hidden;} #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stButton button { width: 100%; border-radius: 12px; font-weight: bold; }
    .announcement-card { background-color: #fff3cd; border-right: 6px solid #ffc107; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #856404; font-weight: bold; text-align: right; }
    .notification-box { background: #f0f2f6; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-right: 4px solid #0045ad; font-size: 13px; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# دالة لتشغيل صوت التنبيه (تلقائي عند ظهور توست)
def trigger_alert_sound():
    st.components.v1.html("""
        <audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg"></audio>
    """, height=0)

# 2. الربط بـ Supabase
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. قاعدة بيانات المستخدمين
user_creds = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- واجهة تسجيل دخول مصممة للموبايل ---
if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 دخول المستخدمين")
        u_identity = st.selectbox("اختر اسمك:", list(user_creds.keys()))
        u_pass = st.text_input("الرمز السري:", type="password")
        if st.button("دخول ✅"):
            if u_pass == user_creds[u_identity]:
                st.session_state.logged_in = True
                st.session_state.user_name = u_identity
                st.rerun()
            else: st.error("الرمز السري خطأ!")
    st.stop()

u_name = st.session_state.user_name
user_role = "مشرف" if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"] else u_name

# --- 📣 نظام الإعلانات الإدارية (رسائل محمد علي) ---
try:
    ann = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute().data
    if ann:
        st.markdown(f'<div class="announcement-card">📢 إعلان إداري:<br>{ann[0]["content"]}</div>', unsafe_allow_html=True)
except: pass

# --- 🔔 نظام الإشعارات (آخر 10 حركات بالصوت) ---
with st.expander("🔔 آخر 10 إشعارات وحركات", expanded=True):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        if logs:
            # تشغيل صوت إذا حدث تحديث جديد (تبسيط منطقي)
            if 'last_log_id' not in st.session_state or st.session_state.last_log_id != logs[0]['id']:
                trigger_alert_sound()
                st.session_state.last_log_id = logs[0]['id']

            for log in logs:
                msg = f"**{log['customer_name']}**: {log['status']}"
                if log.get('manager_notes'): msg += f" | ❌ سبب الرفض: {log['manager_notes']}"
                if log.get('driver_notes'): msg += f" | ⚠️ ملاحظة السائق: {log['driver_notes']}"
                st.markdown(f'<div class="notification-box">{msg}</div>', unsafe_allow_html=True)
    except: st.write("لا توجد إشعارات.")

# --- واجهة المشرف (إضافة دفعة) ---
if user_role == "مشرف":
    st.subheader("➕ تقديم طلبات")
    if 'basket' not in st.session_state: st.session_state.basket = []
    
    with st.container(border=True):
        route = st.select_slider("📍 اختر المسار:", options=["1", "2", "3", "4", "5", "6"])
        delegate = st.text_input("👤 اسم المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري للعميل")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        details = st.text_area("ℹ️ ملاحظات المشرف")
        
        if st.button("إضافة للقائمة مؤقتاً 📥"):
            if trade_n:
                st.session_state.basket.append({
                    "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                    "full_name": full_n, "address": addr, "details": details, "cooler_type": item
                })
                st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 لديك ({len(st.session_state.basket)}) طلبات جاهزة")
        if st.button("🚀 إرسال كافة الطلبات للمدير"):
            for r in st.session_state.basket:
                supabase.table("cooler_orders").insert({**r, "supervisor_name": u_name, "status": "بانتظار موافقة المدير"}).execute()
            st.session_state.basket = []
            st.success("تم الإرسال!")
            st.rerun()

# --- واجهة المتابعة واتخاذ القرار ---
st.subheader("📋 سجل الطلبات الحالي")
res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data

if res:
    for o in res:
        status = o['status']
        with st.expander(f"📦 {o['customer_name']} | {status}"):
            st.markdown(f"""
            **المندوب:** {o['delegate_name']} | **المسار:** {o['route_name']}
            **الاسم الثلاثي:** {o['full_name']}
            **العنوان:** {o['address']} | **النوع:** {o['cooler_type']}
            **التفاصيل:** {o['details']}
            **المشرف:** {o['supervisor_name']}
            """)
            if o.get('manager_notes'): st.error(f"⚠️ ملاحظة الإدارة: {o['manager_notes']}")
            if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")

            # ترتيب العمليات
            if user_role == "مدير التنمية" and "بانتظار موافقة المدير" in status:
                n = st.text_input("ملاحظة في حال الرفض:", key=f"n_{o['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ موافقة", key=f"a_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                    st.rerun()
                if c2.button("❌ رفض", key=f"r_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": n}).eq("id", o['id']).execute()
                    st.rerun()

            elif user_role == "مسؤول المخزن" and "الموافقة" in status:
                ser = st.text_input("تثبيت رقم البراد:", key=f"s_{o['id']}")
                wn = st.text_input("سبب عدم التوفر:", key=f"wn_{o['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ تجهيز", key=f"wa_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser}).eq("id", o['id']).execute()
                    st.rerun()
                if c2.button("❌ غير متوفر", key=f"wr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": wn}).eq("id", o['id']).execute()
                    st.rerun()

            elif user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in status:
                if st.button("📝 تم إكمال العقد", key=f"co_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                    st.rerun()

            elif user_role == "سائق البرادات" and "جاهز للتوصيل" in status:
                dn = st.text_input("ملاحظة السائق:", key=f"dn_{o['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ تم التسليم", key=f"ok_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                    st.rerun()
                if c2.button("❌ رفض استلام", key=f"fail_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "رفض استلام العميل", "driver_notes": dn}).eq("id", o['id']).execute()
                    st.rerun()

    # --- 📑 نظام التصدير العمودي للنسخ المباشر ---
    with st.expander("📑 تصدير البيانات (نسخ عمودي)"):
        def get_col(f): return "\n".join([str(x.get(f, '-')) for x in res])
        exp = f"🏢 الاسم التجاري:\n{get_col('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_col('full_name')}\n\n👤 المندوب:\n{get_col('delegate_name')}\n\n📍 المسار:\n{get_col('route_name')}\n\n🎖️ المشرف:\n{get_col('supervisor_name')}\n\n📦 نوع البراد:\n{get_col('cooler_type')}\n\n🗺️ العنوان:\n{get_col('address')}"
        st.text_area("اضغط مطولاً للنسخ:", value=exp, height=200)

# --- 🛠️ لوحة تحكم محمد علي (تصفير + تعميم) ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    with st.container(border=True):
        st.write("🛠️ **إدارة المنصة**")
        ann_msg = st.text_area("اكتب رسالة تعميم لكل المستخدمين:")
        if st.button("إرسال إعلان للجميع 📡"):
            supabase.table("announcements").insert({"content": ann_msg, "sender": u_name}).execute()
            st.success("تم النشر!")
            st.rerun()
        
        if st.button("⚠️ تصفير كافة الطلبات (مسح شامل)"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم التصفير!")
            st.rerun()

st.divider()
st.markdown("<center style='color: #888; font-size: 11px;'>Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></center>", unsafe_allow_html=True)
