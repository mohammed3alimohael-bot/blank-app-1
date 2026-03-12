import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والتصميم (خلفية سوداء ونصوص بيضاء)
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    
    .main-title { 
        font-family: 'Reem Kufi', sans-serif; font-size: 32px; 
        color: #007bff !important; text-align: center; padding: 15px 0;
    }

    /* تحسين الرؤية في الموبايل */
    label, p, .stMarkdown, .stSelectbox, .stTextInput { color: #ffffff !important; font-weight: bold; }
    
    input, textarea, [data-baseweb="select"] {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border: 1px solid #007bff !important; border-radius: 8px !important;
    }

    .stButton button { 
        background-color: #007bff !important; color: #ffffff !important; 
        border-radius: 12px; height: 50px; font-weight: bold; width: 100%;
    }
    
    .announcement-box { 
        background-color: #332b00; color: #ffd700; padding: 10px; 
        border-radius: 10px; border-right: 5px solid #ffd700; margin-bottom: 15px;
    }

    .notification-item { 
        background-color: #1a1a1a; padding: 10px; border-radius: 8px; 
        margin-bottom: 8px; border-right: 4px solid #007bff; font-size: 13px;
    }

    .footer-signature {
        color: #ffffff !important; text-align: center; font-size: 12px;
        padding: 40px 0; font-family: sans-serif;
    }
    
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بـ Supabase
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# دالة تشغيل الصوت (تنبيه)
def play_notif_sound():
    st.components.v1.html('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>', height=0)

# 3. نظام الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 دخول المستخدمين")
        creds = {"مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003", "مدير التنمية": "2001", "مسؤول المخزن": "3001", "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"}
        u_id = st.selectbox("اختر الاسم:", list(creds.keys()))
        u_p = st.text_input("الرمز السري:", type="password")
        if st.button("دخول ✅"):
            if u_p == creds[u_id]:
                st.session_state.logged_in, st.session_state.user_name = True, u_id
                st.rerun()
    st.stop()

u_name = st.session_state.user_name

# --- 📣 نظام الإعلانات والإشعارات (آخر 10 حركات) ---
# إعلان محمد علي العام
try:
    ann = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute().data
    if ann: st.markdown(f'<div class="announcement-box">📢 إعلان الإدارة: {ann[0]["content"]}</div>', unsafe_allow_html=True)
except: pass

# الإشعارات بالتفصيل
with st.expander("🔔 سجل الإشعارات (آخر 10 حركات)", expanded=True):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        if logs:
            for l in logs:
                msg = f"**{l['customer_name']}**: {l['status']}"
                if l.get('manager_notes'): msg += f" | ⚠️ ملاحظة: {l['manager_notes']}"
                if l.get('driver_notes'): msg += f" | ⚠️ ملاحظة السائق: {l['driver_notes']}"
                st.markdown(f'<div class="notification-item">{msg}</div>', unsafe_allow_html=True)
        else: st.write("لا توجد حركات مسجلة حالياً.")
    except: st.write("جاري تحديث سجل الإشعارات...")

# --- واجهة المشرف (إرسال دفعة واحدة) ---
if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"]:
    if 'basket' not in st.session_state: st.session_state.basket = []
    with st.container(border=True):
        st.subheader("➕ تقديم طلبات جديدة")
        route = st.radio("📍 المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
        delegate = st.text_input("👤 اسم المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        details = st.text_area("ℹ️ التفاصيل")
        item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        
        if st.button("إضافة الطلب للقائمة 📥"):
            st.session_state.basket.append({"route_name": route, "delegate_name": delegate, "customer_name": trade_n, "full_name": full_n, "address": addr, "details": details, "cooler_type": item})
            st.success("تمت الإضافة بنجاح")
            st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 القائمة تحتوي على ({len(st.session_state.basket)}) طلبات")
        if st.button("🚀 إرسال كافة الطلبات للمدير"):
            for r in st.session_state.basket:
                supabase.table("cooler_orders").insert({**r, "supervisor_name": u_name, "status": "بانتظار موافقة المدير", "updated_at": "now()"}).execute()
            st.session_state.basket = []
            play_notif_sound()
            st.rerun()

# --- سلسلة الموافقات والقرارات ---
st.subheader("📋 متابعة الطلبات")
try:
    orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
    if orders:
        for o in orders:
            with st.expander(f"📦 {o['customer_name']} | {o['status']}"):
                st.write(f"المندوب: {o['delegate_name']} | المسار: {o['route_name']}")
                st.write(f"المادة: {o['cooler_type']} | العنوان: {o['address']}")
                st.write(f"التفاصيل: {o['details']}")
                
                # مدير التنمية
                if u_name == "مدير التنمية" and o['status'] == "بانتظار موافقة المدير":
                    m_note = st.text_input("سبب الرفض (اختياري):", key=f"mn_{o['id']}")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ موافقة", key=f"ma_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن", "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()
                    if col2.button("❌ رفض", key=f"mr_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": m_note, "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()

                # مسؤول المخزن
                elif u_name == "مسؤول المخزن" and "الموافقة" in o['status']:
                    ser = st.text_input("رقم البراد:", key=f"ser_{o['id']}")
                    w_note = st.text_input("سبب الرفض:", key=f"wn_{o['id']}")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ تجهيز", key=f"wa_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser, "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()
                    if col2.button("❌ غير متوفر", key=f"wr_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": w_note, "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()

                # قسم التنسيق (محمد علي)
                elif u_name == "قسم التنسيق (محمد علي)" and "التجهيز" in o['status']:
                    if st.button("📝 تم إكمال العقد", key=f"ca_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "جاهز للتوصيل", "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()

                # سائق البرادات
                elif u_name == "سائق البرادات" and o['status'] == "جاهز للتوصيل":
                    d_note = st.text_input("ملاحظة السائق:", key=f"dn_{o['id']}")
                    col1, col2 = st.columns(2)
                    if col1.button("✅ تم التسليم", key=f"da_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "مكتمل", "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()
                    if col2.button("❌ رفض استلام", key=f"dr_{o['id']}"):
                        supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": d_note, "updated_at": "now()"}).eq("id", o['id']).execute()
                        play_notif_sound(); st.rerun()

        # --- تصدير البيانات (نسخ عمودي) ---
        with st.expander("📑 تصدير قوائم البيانات للنسخ"):
            def get_col(k): return "\n".join([str(x.get(k, '-')) for x in orders])
            exp = f"🏢 الاسم التجاري:\n{get_col('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_col('full_name')}\n\n👤 المندوب:\n{get_col('delegate_name')}\n\n📍 المسار:\n{get_col('route_name')}\n\n📦 النوع:\n{get_col('cooler_type')}"
            st.text_area("انسخ من هنا مباشرة:", exp, height=250)
except: st.warning("جاري تحميل الطلبات...")

# --- أدوات محمد علي (تصفير + تعميم) ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    with st.expander("🛠️ لوحة تحكم الإدارة (محمد علي)"):
        new_ann = st.text_area("نشر إعلان عام يظهر للكل:")
        if st.button("بث الإعلان الآن 📡"):
            supabase.table("announcements").insert({"content": new_ann, "sender": u_name}).execute()
            st.success("تم البث بنجاح!"); st.rerun()
        
        if st.button("⚠️ تصفير كافة الطلبات"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم مسح كافة البيانات!"); st.rerun()

st.markdown('<div class="footer-signature">Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></div>', unsafe_allow_html=True)
