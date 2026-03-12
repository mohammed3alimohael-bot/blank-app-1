import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والتصميم (خلفية سوداء، نصوص بيضاء وزرقاء)
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    .main-title { 
        font-family: 'Reem Kufi', sans-serif; font-size: 32px; 
        color: #007bff !important; text-align: center; padding: 15px 0;
    }
    label, p, .stMarkdown { color: #ffffff !important; font-weight: bold; }
    input, textarea, [data-baseweb="select"] {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border: 1px solid #007bff !important;
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
        padding: 40px 0;
    }
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بـ Supabase
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

def play_notif_sound():
    st.components.v1.html('<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-09.mp3" type="audio/mpeg"></audio>', height=0)

# 3. نظام الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 دخول")
        creds = {"مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003", "مدير التنمية": "2001", "مسؤول المخزن": "3001", "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"}
        u_id = st.selectbox("اختر الاسم:", list(creds.keys()))
        u_p = st.text_input("الرمز السري:", type="password")
        if st.button("دخول ✅"):
            if u_p == creds[u_id]:
                st.session_state.logged_in, st.session_state.user_name = True, u_id
                st.rerun()
    st.stop()

u_name = st.session_state.user_name

# --- 📣 الإعلانات والإشعارات (آخر 10) ---
try:
    ann = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute().data
    if ann: st.markdown(f'<div class="announcement-box">📢 {ann[0]["content"]}</div>', unsafe_allow_html=True)
except: pass

with st.expander("🔔 آخر 10 إشعارات بالتفصيل", expanded=True):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        for l in logs:
            info = f"📦 {l['customer_name']} -> {l['status']}"
            if l.get('manager_notes'): info += f" | ❌ الرفض: {l['manager_notes']}"
            st.markdown(f'<div class="notification-item">{info}</div>', unsafe_allow_html=True)
    except: st.write("لا توجد إشعارات.")

# --- واجهة المشرف (إرسال دفعة واحدة) ---
if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"]:
    if 'basket' not in st.session_state: st.session_state.basket = []
    with st.container(border=True):
        st.subheader("➕ طلب براد")
        route = st.select_slider("📍 المسار:", options=["1", "2", "3", "4", "5", "6"])
        delegate = st.text_input("👤 المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        details = st.text_area("ℹ️ التفاصيل")
        item = st.selectbox("📦 المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        if st.button("إضافة للقائمة 📥"):
            st.session_state.basket.append({"route_name": route, "delegate_name": delegate, "customer_name": trade_n, "full_name": full_n, "address": addr, "details": details, "cooler_type": item})
            st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 لديك ({len(st.session_state.basket)}) طلبات")
        if st.button("🚀 إرسال الكل للمدير"):
            for r in st.session_state.basket:
                supabase.table("cooler_orders").insert({**r, "supervisor_name": u_name, "status": "بانتظار موافقة المدير", "updated_at": "now()"}).execute()
            st.session_state.basket = []; play_notif_sound(); st.rerun()

# --- المتابعة (تقسيم حسب المشرف) ---
st.subheader("📋 متابعة الطلبات")
orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
if orders:
    t1, t2, t3 = st.tabs(["طلبات مشعل", "طلبات محمد", "طلبات حسين"])
    tab_map = {"مشعل رسول": t1, "محمد أركن": t2, "حسين علي": t3}
    
    for sup_name, tab in tab_map.items():
        with tab:
            sup_orders = [o for o in orders if o['supervisor_name'] == sup_name]
            for o in sup_orders:
                with st.expander(f"📦 {o['customer_name']} | {o['status']}"):
                    st.write(f"المندوب: {o['delegate_name']} | المسار: {o['route_name']}")
                    st.write(f"الاسم: {o['full_name']} | المادة: {o['cooler_type']}")
                    st.write(f"العنوان: {o['address']} | التفاصيل: {o['details']}")
                    
                    if u_name == "مدير التنمية" and o['status'] == "بانتظار موافقة المدير":
                        note = st.text_input("سبب الرفض:", key=f"n_{o['id']}")
                        if st.button("✅ موافقة", key=f"a_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - المخزن", "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()
                        if st.button("❌ رفض", key=f"r_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض", "manager_notes": note, "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

                    elif u_name == "مسؤول المخزن" and "الموافقة" in o['status']:
                        ser = st.text_input("رقم البراد:", key=f"s_{o['id']}")
                        if st.button("✅ تجهيز", key=f"sa_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "بانتظار العقد", "cooler_serial": ser, "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

                    elif u_name == "قسم التنسيق (محمد علي)" and "العقد" in o['status']:
                        if st.button("📝 تم إكمال العقد", key=f"cc_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل", "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

                    elif u_name == "سائق البرادات" and "جاهز" in o['status']:
                        d_n = st.text_input("ملاحظة:", key=f"dn_{o['id']}")
                        if st.button("✅ تم التسليم", key=f"ok_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل", "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

    # تصدير البيانات
    with st.expander("📑 نسخ القوائم"):
        def get_col(k): return "\n".join([str(x.get(k, '-')) for x in orders])
        st.text_area("البيانات:", f"الاسم التجاري:\n{get_col('customer_name')}\n\nالمندوب:\n{get_col('delegate_name')}", height=200)

# --- أدوات محمد علي ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    with st.expander("🛠️ إدارة"):
        msg = st.text_area("نشر إعلان:")
        if st.button("بث 📡"):
            supabase.table("announcements").insert({"content": msg, "sender": u_name}).execute()
            st.rerun()
        if st.button("⚠️ تصفير البيانات"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم التصفير"); st.rerun()

st.markdown('<div class="footer-signature">Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></div>', unsafe_allow_html=True)
