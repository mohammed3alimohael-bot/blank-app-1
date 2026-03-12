import streamlit as st
from supabase import create_client
import time

# 1. إعدادات الموبايل والتصميم الاحترافي (خلفية سوداء)
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    
    /* الخلفية السوداء بالكامل */
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    
    .main-title { 
        font-family: 'Reem Kufi', sans-serif; font-size: 30px; 
        color: #007bff !important; text-align: center; padding: 20px 0;
    }

    /* جعل العناصر واضحة في الموبايل */
    .stTabs [data-baseweb="tab"] { color: #ffffff !important; font-size: 14px; }
    label, p, span, .stMarkdown { color: #ffffff !important; font-weight: bold !important; }
    
    input, textarea, [data-baseweb="select"] {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border: 1px solid #007bff !important; border-radius: 10px !important;
    }

    .stButton button { 
        background-color: #007bff !important; color: #ffffff !important; 
        border-radius: 12px; height: 55px; font-weight: bold; width: 100%;
    }
    
    .announcement-box { 
        background-color: #2c2c00; color: #ffd700; padding: 12px; 
        border-radius: 10px; border-right: 6px solid #ffd700; margin-bottom: 15px; text-align: right;
    }

    .notification-item { 
        background-color: #111111; padding: 12px; border-radius: 8px; 
        margin-bottom: 8px; border-right: 4px solid #007bff; font-size: 13px; color: #e0e0e0;
    }

    .footer-signature {
        color: #ffffff !important; text-align: center; font-size: 13px;
        padding: 50px 0; font-family: 'Arial', sans-serif;
    }
    
    header, footer { visibility: hidden; }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بـ Supabase
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# دالة تشغيل الصوت (تنبيه قوي)
def play_notif_sound():
    st.components.v1.html('<audio autoplay><source src="https://www.soundjay.com/buttons/sounds/button-09.mp3" type="audio/mpeg"></audio>', height=0)

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

# --- 📣 نظام الإشعارات (آخر 10 حركات) ---
try:
    ann = supabase.table("announcements").select("*").order('created_at', desc=True).limit(1).execute().data
    if ann: st.markdown(f'<div class="announcement-box">📢 إعلان الإدارة: {ann[0]["content"]}</div>', unsafe_allow_html=True)
except: pass

with st.expander("🔔 سجل الحركة والإشعارات (آخر 10)", expanded=True):
    try:
        logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
        if logs:
            for l in logs:
                status_txt = f"📦 **{l['customer_name']}**: {l['status']}"
                if l.get('manager_notes'): status_txt += f" | ❌ السبب: {l['manager_notes']}"
                if l.get('driver_notes'): status_txt += f" | ⚠️ ملاحظة السائق: {l['driver_notes']}"
                st.markdown(f'<div class="notification-item">{status_txt}</div>', unsafe_allow_html=True)
    except: st.write("لا توجد إشعارات حالياً.")

# --- واجهة المشرف (إضافة وإرسال دفعة) ---
if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"]:
    if 'basket' not in st.session_state: st.session_state.basket = []
    with st.container(border=True):
        st.subheader("📝 طلب جديد")
        route = st.radio("📍 المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
        delegate = st.text_input("👤 المندوب")
        trade_n = st.text_input("🏢 الاسم التجاري")
        full_n = st.text_input("📝 الاسم الثلاثي")
        addr = st.text_input("🗺️ العنوان")
        details = st.text_area("ℹ️ التفاصيل")
        item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
        
        if st.button("إضافة للقائمة 📥"):
            st.session_state.basket.append({"route_name": route, "delegate_name": delegate, "customer_name": trade_n, "full_name": full_n, "address": addr, "details": details, "cooler_type": item})
            st.success("تمت الإضافة")
            st.rerun()

    if st.session_state.basket:
        st.info(f"🛒 القائمة الجاهزة: {len(st.session_state.basket)} طلبات")
        if st.button("🚀 إرسال كافة الطلبات للمدير"):
            for r in st.session_state.basket:
                supabase.table("cooler_orders").insert({**r, "supervisor_name": u_name, "status": "بانتظار موافقة المدير", "updated_at": "now()"}).execute()
            st.session_state.basket = []; play_notif_sound(); st.rerun()

# --- المتابعة (تقسيم المشرفين + التفاصيل الكاملة) ---
st.subheader("📋 متابعة الطلبات")
res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
if res:
    t1, t2, t3 = st.tabs(["طلبات مشعل", "طلبات محمد", "طلبات حسين"])
    mapping = {"مشعل رسول": t1, "محمد أركن": t2, "حسين علي": t3}
    
    for sup_id, tab in mapping.items():
        with tab:
            filtered = [o for o in res if o['supervisor_name'] == sup_id]
            for o in filtered:
                with st.expander(f"📦 {o['customer_name']} | {o['status']}"):
                    st.markdown(f"""
                    **المسار:** {o['route_name']} | **المندوب:** {o['delegate_name']}
                    **الاسم الثلاثي:** {o['full_name']}
                    **العنوان:** {o['address']}
                    **نوع المادة:** {o['cooler_type']}
                    **التفاصيل:** {o['details']}
                    """)
                    if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")
                    if o.get('manager_notes'): st.error(f"❌ ملاحظة الإدارة: {o['manager_notes']}")

                    # القرارات حسب الصلاحية
                    if u_name == "مدير التنمية" and o['status'] == "بانتظار موافقة المدير":
                        m_reason = st.text_input("سبب الرفض (إلزامي للرفض):", key=f"m_re_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"ma_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن", "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()
                        if c2.button("❌ رفض", key=f"mr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": m_reason, "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

                    elif u_name == "مسؤول المخزن" and "الموافقة" in o['status']:
                        ser_no = st.text_input("رقم البراد:", key=f"ser_{o['id']}")
                        w_reason = st.text_input("سبب الرفض:", key=f"wr_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تجهيز", key=f"wa_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser_no, "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()
                        if c2.button("❌ غير متوفر", key=f"wr_b_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": w_reason, "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

                    elif u_name == "قسم التنسيق (محمد علي)" and "التجهيز" in o['status']:
                        if st.button("📝 تم إكمال العقد", key=f"f_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل", "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

                    elif u_name == "سائق البرادات" and "جاهز" in o['status']:
                        d_note = st.text_input("ملاحظة السائق:", key=f"dn_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التسليم", key=f"dok_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل", "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()
                        if c2.button("❌ رفض استلام العميل", key=f"dfail_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": d_note, "updated_at": "now()"}).eq("id", o['id']).execute()
                            play_notif_sound(); st.rerun()

    # --- تصدير البيانات بنسخ مباشر ---
    with st.expander("📑 تصدير قوائم البيانات للنسخ"):
        def get_l(k): return "\n".join([str(x.get(k, '-')) for x in res])
        exp_txt = f"🏢 الاسم التجاري:\n{get_l('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_l('full_name')}\n\n👤 المندوب:\n{get_l('delegate_name')}\n\n📍 المسار:\n{get_l('route_name')}\n\n📦 النوع:\n{get_l('cooler_type')}\n\n🗺️ العنوان:\n{get_l('address')}"
        st.text_area("انسخ القائمة من هنا:", exp_txt, height=250)

# --- 🛠️ أدوات محمد علي ---
if u_name == "قسم التنسيق (محمد علي)":
    st.divider()
    with st.expander("🛠️ إدارة المنصة"):
        ann_msg = st.text_area("نشر إعلان عام للكل:")
        if st.button("بث الإعلان 📡"):
            supabase.table("announcements").insert({"content": ann_msg, "sender": u_name}).execute()
            st.success("تم النشر!"); st.rerun()
        if st.button("⚠️ تصفير كافة الطلبات"):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم التصفير!"); st.rerun()

st.markdown('<div class="footer-signature">تم التصميم والبرمجة بواسطة محمد علي محيل<br><b>Designed and Programmed by: MOHAMMED ALI MUHEEL</b></div>', unsafe_allow_html=True)
