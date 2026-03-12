import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والتصميم (خلفية سوداء، نصوص بيضاء وزرقاء)
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    
    /* خلفية التطبيق سوداء بالكامل */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* العنوان العلوي بخط كوفي كبير */
    .main-title { 
        font-family: 'Reem Kufi', sans-serif; 
        font-size: 35px; 
        color: #007bff !important; 
        text-align: center; 
        padding: 20px 0;
    }

    /* تحسين وضوح العناصر في الوضع الداكن */
    label, p, span, .stMarkdown {
        color: #ffffff !important;
    }

    /* حقول الإدخال */
    input, textarea, [data-baseweb="select"] {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #007bff !important;
    }

    /* الأزرار المصممة للهاتف */
    .stButton button { 
        background-color: #007bff !important; 
        color: #ffffff !important; 
        border-radius: 12px; 
        height: 55px; 
        font-weight: bold;
        width: 100%;
    }
    
    /* صناديق الإشعارات والإعلانات */
    .announcement-box { 
        background-color: #332b00 !important; 
        color: #ffd700 !important; 
        padding: 12px; 
        border-radius: 10px; 
        border-right: 6px solid #ffd700 !important; 
        margin-bottom: 15px;
        text-align: right;
    }

    .notification-item { 
        background-color: #1a1a1a; 
        padding: 10px; 
        border-radius: 8px; 
        margin-bottom: 8px; 
        border-right: 4px solid #007bff;
        color: #ffffff;
    }

    /* توقيع محمد علي باللون الأبيض في الأسفل */
    .footer-signature {
        color: #ffffff !important;
        text-align: center;
        font-size: 12px;
        padding: 30px 0;
        letter-spacing: 1px;
    }
    
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بـ Supabase
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# دالة لتشغيل صوت التنبيه
def play_notif_sound():
    st.components.v1.html('<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg"></audio>', height=0)

# 3. نظام الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 تسجيل الدخول")
        creds = {"مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003", "مدير التنمية": "2001", "مسؤول المخزن": "3001", "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"}
        u_id = st.selectbox("اختر الاسم:", list(creds.keys()))
        u_p = st.text_input("الرمز السري:", type="password")
        if st.button("دخول ✅"):
            if u_p == creds[u_id]:
                st.session_state.logged_in, st.session_state.user_name = True, u_id
                st.rerun()
    st.stop()

u_name = st.session_state.user_name

# --- 📣 نظام الإعلانات والإشعارات (آخر 10) ---
try:
    ann = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute().data
    if ann: st.markdown(f'<div class="announcement-box">📢 {ann[0]["content"]}</div>', unsafe_allow_html=True)
except: pass

with st.expander("🔔 آخر 10 إشعارات بالتفصيل", expanded=True):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        for l in logs:
            info = f"📦 {l['customer_name']} -> {l['status']}"
            if l.get('manager_notes'): info += f" | سبب الرفض: {l['manager_notes']}"
            st.markdown(f'<div class="notification-item">{info}</div>', unsafe_allow_html=True)
    except: st.write("لا توجد حركات.")

# --- واجهة المشرف (إرسال دفعة واحدة) ---
if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"]:
    if 'basket' not in st.session_state: st.session_state.basket = []
    with st.container(border=True):
        st.subheader("➕ تقديم طلبات")
        route = st.radio("📍 المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
        delegate = st.text_input("👤 اسم المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        details = st.text_area("ℹ️ التفاصيل")
        item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        
        if st.button("إضافة للسلة 📥"):
            st.session_state.basket.append({"route_name": route, "delegate_name": delegate, "customer_name": trade_n, "full_name": full_n, "address": addr, "details": details, "cooler_type": item})
            st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 لديك ({len(st.session_state.basket)}) طلبات")
        if st.button("🚀 إرسال الكل للمدير"):
            for r in st.session_state.basket:
                supabase.table("cooler_orders").insert({**r, "supervisor_name": u_name, "status": "بانتظار موافقة المدير"}).execute()
            st.session_state.basket = []
            play_notif_sound(); st.rerun()

# --- سلسلة الموافقات (عرض التفاصيل الكاملة) ---
st.subheader("📋 متابعة الطلبات")
orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
if orders:
    for o in orders:
        with st.expander(f"📦 {o['customer_name']} | {o['status']}"):
            st.write(f"المندوب: {o['delegate_name']} | المسار: {o['route_name']}")
            st.write(f"الاسم: {o['full_name']} | النوع: {o['cooler_type']}")
            st.write(f"العنوان: {o['address']} | التفاصيل: {o['details']}")
            
            # منطق التنقل بين المستخدمين
            if u_name == "مدير التنمية" and o['status'] == "بانتظار موافقة المدير":
                reason = st.text_input("سبب الرفض:", key=f"m_{o['id']}")
                if st.button("✅ موافقة", key=f"ma_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()
                if st.button("❌ رفض", key=f"mr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": reason}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()

            elif u_name == "مسؤول المخزن" and "الموافقة" in o['status']:
                ser = st.text_input("رقم البراد:", key=f"s_{o['id']}")
                r_note = st.text_input("سبب عدم التوفر:", key=f"rn_{o['id']}")
                if st.button("✅ تجهيز", key=f"sa_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()
                if st.button("❌ غير متوفر", key=f"sr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": r_note}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()

            elif u_name == "قسم التنسيق (محمد علي)" and "التجهيز" in o['status']:
                if st.button("📝 تم إكمال العقد", key=f"ca_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()

            elif u_name == "سائق البرادات" and o['status'] == "جاهز للتوصيل":
                d_note = st.text_input("ملاحظة السائق:", key=f"dn_{o['id']}")
                if st.button("✅ تم التسليم", key=f"da_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()
                if st.button("❌ رفض الاستلام", key=f"dr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": d_note}).eq("id", o['id']).execute()
                    play_notif_sound(); st.rerun()

    # --- تصدير البيانات بنسخ مباشر ---
    with st.expander("📑 تصدير البيانات للنسخ العمودي"):
        def get_col(k): return "\n".join([str(x.get(k, '-')) for x in orders])
        export_text = f"🏢 الاسم التجاري:\n{get_col('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_col('full_name')}\n\n👤 المندوب:\n{get_col('delegate_name')}\n\n📍 المسار:\n{get_col('route_name')}\n\n📦 النوع:\n{get_col('cooler_type')}"
        st.text_area("انسخ القوائم من هنا:", export_text, height=250)

# --- أدوات محمد علي (تصفير + تعميم) ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    with st.expander("🛠️ إدارة المنصة"):
        new_ann = st.text_area("نشر إعلان عام:")
        if st.button("بث الإعلان 📡"):
            supabase.table("announcements").insert({"content": new_ann, "sender": u_name}).execute()
            st.success("تم النشر!"); st.rerun()
        if st.button("⚠️ تصفير كافة الطلبات"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم التصفير!"); st.rerun()

st.markdown('<div class="footer-signature">Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></div>', unsafe_allow_html=True)
