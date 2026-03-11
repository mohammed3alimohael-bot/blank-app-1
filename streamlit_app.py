import streamlit as st
from supabase import create_client
import pandas as pd

# 1. إعدادات الصفحة للهاتف وإخفاء العناصر غير الضرورية
st.set_page_config(page_title="منصة التنسيق الرقمية", layout="centered")

# CSS لتحسين المظهر على الهاتف وإضافة الخط الكوفي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@700&display=swap');
    
    .main-title {
        font-family: 'Reem Kufi', sans-serif;
        font-size: 35px;
        color: #0056b3;
        text-align: center;
        margin-top: -50px;
    }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تحسين عرض البطاقات على الهاتف */
    .stExpander {
        border: 1px solid #ddd !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
    </style>
    <div class="main-title">منصة التنسيق الرقمية</div>
    """, unsafe_allow_html=True)

# 2. الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. المستخدمين والصلاحيات
user_creds = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 تسجيل الدخول")
# أضف هذا السطر بعد تعريف القائمة الجانبية مباشرة
if u_pass != user_creds[u_identity]:
    st.info("👈 يرجى فتح القائمة الجانبية وتسجيل الدخول للبدء")

u_identity = st.sidebar.selectbox("اختر اسمك:", list(user_creds.keys()))
u_pass = st.sidebar.text_input("الرمز السري:", type="password")

if u_pass == user_creds[u_identity]:
    user_role = "مشرف" if u_identity in ["مشعل رسول", "محمد أركن", "حسين علي"] else u_identity

    # --- 🔔 الإشعارات (آخر 10 حركات بالتفصيل) ---
    with st.sidebar.expander("🔔 آخر 10 إشعارات", expanded=False):
        try:
            logs = supabase.table("cooler_orders").select("*").order('updated_at', desc=True).limit(10).execute().data
            for log in logs:
                st.caption(f"⏱️ {log['updated_at'][11:16]}")
                msg = f"**{log['customer_name']}**: {log['status']}"
                if log.get('manager_notes'): msg += f" | سبب الرفض: {log['manager_notes']}"
                if log.get('driver_notes'): msg += f" | ملاحظة السائق: {log['driver_notes']}"
                st.markdown(msg)
                st.divider()
        except: st.write("لا توجد حركات.")

    # --- المرحلة 1: المشرف (إضافة وإرسال دفعة) ---
    if user_role == "مشرف":
        st.subheader("➕ إنشاء طلبات جديدة")
        if 'basket' not in st.session_state: st.session_state.basket = []
        
        with st.container(border=True):
            route = st.select_slider("📍 اختر المسار:", options=["1", "2", "3", "4", "5", "6"])
            delegate = st.text_input("👤 اسم المندوب")
            trade_n = st.text_input("🏢 الاسم التجاري")
            full_n = st.text_input("📝 الاسم الثلاثي")
            addr = st.text_input("🗺️ العنوان")
            item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
            note_inf = st.text_area("ℹ️ تفاصيل الطلب")
            
            if st.button("إضافة الطلب للقائمة 📥", use_container_width=True):
                if trade_n:
                    st.session_state.basket.append({
                        "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                        "full_name": full_n, "address": addr, "details": note_inf, "cooler_type": item
                    })
                    st.rerun()

        if st.session_state.basket:
            st.info(f"🛒 لديك {len(st.session_state.basket)} طلبات جاهزة للإرسال")
            if st.button("🚀 إرسال كافة الطلبات للمدير الآن", use_container_width=True, type="primary"):
                for req in st.session_state.basket:
                    supabase.table("cooler_orders").insert({**req, "supervisor_name": u_identity, "status": "بانتظار موافقة المدير"}).execute()
                st.session_state.basket = []
                st.success("تم إرسال المجموعة بنجاح!")
                st.rerun()

    # --- عرض وسجل الطلبات (سلسلة التوريد) ---
    st.subheader("📋 متابعة الطلبات")
    all_orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
    
    if all_orders:
        for o in all_orders:
            st_val = o['status']
            with st.expander(f"📦 {o['customer_name']} - {st_val}"):
                # عرض التفاصيل كاملة لكل المستخدمين
                st.markdown(f"""
                **المندوب:** {o['delegate_name']} | **المسار:** {o['route_name']}
                **الاسم الثلاثي:** {o['full_name']}
                **العنوان:** {o['address']}
                **نوع المادة:** {o['cooler_type']}
                **التفاصيل:** {o['details']}
                **المشرف:** {o['supervisor_name']}
                """)
                
                if o.get('manager_notes'): st.error(f"❌ ملاحظة/سبب الرفض: {o['manager_notes']}")
                if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")
                if o.get('driver_notes'): st.warning(f"⚠️ ملاحظة السائق: {o['driver_notes']}")

                # حركات المستخدمين
                if user_role == "مدير التنمية" and st_val == "بانتظار موافقة المدير":
                    m_note = st.text_input("سبب الرفض:", key=f"mn_{o['id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ موافقة", key=f"ma_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                        st.rerun()
                    if c2.button("❌ رفض", key=f"mr_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": m_note}).eq("id", o['id']).execute()
                        st.rerun()

                elif user_role == "مسؤول المخزن" and st_val == "تمت الموافقة - بانتظار المخزن":
                    ser = st.text_input("رقم البراد:", key=f"s_{o['id']}")
                    w_note = st.text_input("سبب عدم التوفر:", key=f"wn_{o['id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ تجهيز", key=f"wa_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser}).eq("id", o['id']).execute()
                        st.rerun()
                    if c2.button("❌ غير متوفر", key=f"wr_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": w_note}).eq("id", o['id']).execute()
                        st.rerun()

                elif user_role == "قسم التنسيق (محمد علي)" and st_val == "تم التجهيز - بانتظار العقد":
                    if st.button("📝 تم إكمال العقد", key=f"co_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                        st.rerun()

                elif user_role == "سائق البرادات" and st_val == "جاهز للتوصيل":
                    d_note = st.text_input("سبب رفض الاستلام:", key=f"dn_{o['id']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ تم التسليم", key=f"da_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                        st.rerun()
                    if c2.button("❌ رفض استلام", key=f"dr_{o['id']}", use_container_width=True):
                        supabase.table("cooler_orders").update({"status": "رفض استلام العميل", "driver_notes": d_note}).eq("id", o['id']).execute()
                        st.rerun()

        # --- 📑 قسم التصدير (نظام القوائم العمودية) ---
        with st.expander("📑 تصدير البيانات بنظام القوائم"):
            def get_col(field): return "\n".join([str(x.get(field, '-')) for x in all_orders])
            export_data = f"🏢 الاسم التجاري:\n{get_col('customer_name')}\n\n📝 الاسم الثلاثي:\n{get_col('full_name')}\n\n👤 المندوب:\n{get_col('delegate_name')}\n\n📍 المسار:\n{get_col('route_name')}\n\n🎖️ المشرف:\n{get_col('supervisor_name')}\n\n📦 نوع البراد:\n{get_col('cooler_type')}\n\n🗺️ العنوان:\n{get_col('address')}"
            st.text_area("انسخ البيانات من هنا مباشرة:", value=export_data, height=300)

    # --- ⚠️ زر التصفير (خاص بمحمد علي فقط) ---
    if u_identity == "قسم التنسيق (محمد علي)":
        st.divider()
        if st.button("⚠️ تصفير كافة طلبات المشرفين", use_container_width=True):
            supabase.table("cooler_orders").delete().neq("id", 0).execute()
            st.success("تم تصفير المنظومة!")
            st.rerun()

    st.divider()
    st.markdown("<center style='color: #888; font-size: 12px;'>Designed and Programmed by: <br><b>MOHAMMED ALI MUHEEL</b></center>", unsafe_allow_html=True)
else:
    st.sidebar.warning("ادخل الرمز السري")
