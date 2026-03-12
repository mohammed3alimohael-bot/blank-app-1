import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والخط الكوفي مع إصلاح الألوان
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    
    /* إجبار النصوص على الظهور بوضوح عالي بغض النظر عن ثيم الموبايل */
    .stApp {
        color: #111111 !important; /* نصوص غامقة واضحة */
    }
    
    .main-title { 
        font-family: 'Reem Kufi', sans-serif; 
        font-size: 28px; 
        color: #0045ad !important; 
        text-align: center; 
        margin-top: -30px;
        padding-bottom: 20px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* تحسين شكل المدخلات في الموبايل */
    input, textarea, [data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #0045ad !important;
    }

    /* تحسين وضوح العناوين الجانبية */
    h1, h2, h3, p, label {
        color: #1a1a1a !important;
        font-weight: bold !important;
    }

    /* جعل الأزرار بارزة جداً للمس باليد */
    .stButton button { 
        background-color: #0045ad !important; 
        color: #ffffff !important; 
        border-radius: 12px; 
        height: 50px; 
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .announcement-box { 
        background-color: #fff3cd !important; 
        color: #856404 !important; 
        padding: 12px; 
        border-radius: 10px; 
        border-right: 6px solid #ffc107 !important; 
        margin-bottom: 15px;
    }
    
    /* إخفاء القوائم غير الضرورية */
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)
    }
    .notification-item { 
        background-color: #f1f3f5; padding: 8px; border-radius: 5px; 
        margin-bottom: 5px; border-right: 3px solid #0045ad; font-size: 12px;
    }
    .stButton button { width: 100%; border-radius: 10px; height: 45px; font-weight: bold; }
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. نظام الصوت (تنبيه عند التحديث)
def play_sound():
    st.components.v1.html('<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-3.mp3" type="audio/mpeg"></audio>', height=0)

# 4. تسجيل الدخول
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.container(border=True):
        st.subheader("🔐 دخول المستخدمين")
        user_creds = {
            "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
            "مدير التنمية": "2001", "مسؤول المخزن": "3001",
            "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
        }
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

# --- 📣 نظام الإعلانات ---
try:
    ann = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute().data
    if ann:
        st.markdown(f'<div class="announcement-box">📢 {ann[0]["content"]}</div>', unsafe_allow_html=True)
except: pass

# --- 🔔 آخر 10 إشعارات ---
with st.expander("🔔 الإشعارات الأخيرة (آخر 10)", expanded=True):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        for log in logs:
            txt = f"**{log['customer_name']}**: {log['status']}"
            if log.get('manager_notes'): txt += f" | ❌ الرفض: {log['manager_notes']}"
            st.markdown(f'<div class="notification-item">{txt}</div>', unsafe_allow_html=True)
    except: st.write("لا توجد حركات.")

# --- واجهة المشرف (إضافة دفعة واحدة) ---
if user_role == "مشرف":
    st.subheader("➕ تقديم طلبات")
    if 'basket' not in st.session_state: st.session_state.basket = []
    
    with st.container(border=True):
        route = st.radio("📍 اختر المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
        delegate = st.text_input("👤 اسم المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        details = st.text_area("ℹ️ تفاصيل إضافية")
        
        if st.button("إضافة الطلب للسلة 📥"):
            if trade_n:
                st.session_state.basket.append({
                    "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                    "full_name": full_n, "address": addr, "details": details, "cooler_type": item
                })
                st.success("تمت الإضافة للسلة")
                st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 لديك ({len(st.session_state.basket)}) طلبات جاهزة")
        if st.button("🚀 إرسال الطلبات للمدير الآن", type="primary"):
            for r in st.session_state.basket:
                supabase.table("cooler_orders").insert({**r, "supervisor_name": u_name, "status": "بانتظار موافقة المدير"}).execute()
            st.session_state.basket = []
            play_sound()
            st.success("تم الإرسال بنجاح!")
            st.rerun()

# --- واجهة المتابعة واتخاذ القرار ---
st.subheader("📋 متابعة الطلبات")
orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data

if orders:
    for o in orders:
        with st.expander(f"📦 {o['customer_name']} | {o['status']}"):
            st.write(f"**المندوب:** {o['delegate_name']} | **المسار:** {o['route_name']}")
            st.write(f"**الاسم الثلاثي:** {o['full_name']}")
            st.write(f"**العنوان:** {o['address']} | **المادة:** {o['cooler_type']}")
            st.write(f"**التفاصيل:** {o['details']}")
            
            if o.get('manager_notes'): st.error(f"❌ ملاحظة الرفض: {o['manager_notes']}")
            if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")

            # سلسلة العمليات
            if user_role == "مدير التنمية" and o['status'] == "بانتظار موافقة المدير":
                note = st.text_input("سبب الرفض (إن وجد):", key=f"mn_{o['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ موافقة", key=f"ma_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن", "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()
                if c2.button("❌ رفض", key=f"mr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": note, "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()

            elif user_role == "مسؤول المخزن" and "الموافقة" in o['status']:
                ser = st.text_input("رقم البراد:", key=f"ser_{o['id']}")
                wnote = st.text_input("سبب الرفض:", key=f"wn_{o['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ تجهيز", key=f"wa_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser, "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()
                if c2.button("❌ غير متوفر", key=f"wr_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": wnote, "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()

            elif user_role == "قسم التنسيق (محمد علي)" and "التجهيز" in o['status']:
                if st.button("📝 تم إكمال العقد", key=f"cc_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "جاهز للتوصيل", "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()

            elif user_role == "سائق البرادات" and o['status'] == "جاهز للتوصيل":
                d_note = st.text_input("ملاحظة السائق:", key=f"dn_{o['id']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ تم التسليم", key=f"dok_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "مكتمل", "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()
                if c2.button("❌ رفض استلام", key=f"dfail_{o['id']}"):
                    supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": d_note, "updated_at": "now()"}).eq("id", o['id']).execute()
                    play_sound(); st.rerun()

    # --- 📑 تصدير البيانات بنظام القوائم ---
    with st.expander("📑 تصدير البيانات للنسخ"):
        def get_list(key): return "\n".join([str(x.get(key, '-')) for x in orders])
        out = f"🏢 الاسم التجاري:\n{get_list('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_list('full_name')}\n\n👤 المندوب:\n{get_list('delegate_name')}\n\n📍 المسار:\n{get_list('route_name')}\n\n🎖️ المشرف:\n{get_list('supervisor_name')}\n\n📦 النوع:\n{get_list('cooler_type')}\n\n🗺️ العنوان:\n{get_list('address')}"
        st.text_area("انسخ من هنا:", out, height=200)

# --- 🛠️ أدوات محمد علي ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    with st.container(border=True):
        st.write("🛠️ **لوحة التحكم الإدارية**")
        ann_msg = st.text_area("إرسال إعلان عام للجميع:")
        if st.button("نشر الإعلان 📡"):
            supabase.table("announcements").insert({"content": ann_msg, "sender": u_name}).execute()
            st.success("تم النشر!"); st.rerun()
        
        if st.button("⚠️ تصفير كافة الطلبات"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم تصفير البيانات!"); st.rerun()

st.divider()
st.markdown("<center style='color: #888; font-size: 11px;'>Designed and Programmed by:<br><b>MOHAMMED ALI MUHEEL</b></center>", unsafe_allow_html=True)
