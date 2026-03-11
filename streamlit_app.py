import streamlit as st
from supabase import create_client
from datetime import datetime

# 1. إعدادات الصفحة وإخفاء العناصر العلوية (Header)
st.set_page_config(page_title="منظومة التنسيق - بيبسي", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. الربط بقاعدة البيانات
url = "https://xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

# 3. قاعدة البيانات والصلاحيات
user_credentials = {
    "مشعل رسول": "1001", "محمد أركن": "1002", "حسين علي": "1003",
    "مدير التنمية": "2001", "مسؤول المخزن": "3001",
    "قسم التنسيق (محمد علي)": "4001", "سائق البرادات": "5001"
}

# --- نظام تسجيل الدخول ---
st.sidebar.title("🔐 دخول آمن")
u_name = st.sidebar.selectbox("اختر اسمك:", list(user_credentials.keys()))
u_pass = st.sidebar.text_input("الرمز السري:", type="password")

if u_pass == user_credentials[u_name]:
    user_role = "مشرف" if u_name in ["مشعل رسول", "محمد أركن", "حسين علي"] else u_name
    
    # --- 🔔 الإشعارات الحية في الجانب ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 حركة الطلبات")
    try:
        logs = supabase.table("cooler_orders").select("customer_name, status, created_at").order('created_at', desc=True).limit(5).execute()
        for log in logs.data:
            with st.sidebar.container(border=True):
                st.caption(f"⏱️ {log['created_at'][11:16]}")
                st.write(f"🏢 **{log['customer_name']}**")
                st.info(f"📍 {log['status']}")
    except: st.sidebar.write("بانتظار البيانات...")

    st.title(f"🥤 لوحة تحكم: {u_name}")
    st.markdown("---")

    col1, col2 = st.columns([1.5, 2.5])

    # --- المرحلة 1: واجهة المشرف (إضافة وإرسال دفعة واحدة) ---
    if user_role == "مشرف":
        with col1:
            st.header("➕ إنشاء طلبات")
            if 'basket' not in st.session_state: st.session_state.basket = []
            
            with st.container(border=True):
                route = st.radio("📍 اختر المسار:", ["1", "2", "3", "4", "5", "6"], horizontal=True)
                delegate = st.text_input("👤 اسم المندوب")
                trade_n = st.text_input("🏢 الاسم التجاري للعميل")
                full_n = st.text_input("📝 الاسم الثلاثي للعميل")
                addr = st.text_input("🗺️ العنوان")
                note_inf = st.text_area("ℹ️ التفاصيل")
                item = st.selectbox("📦 نوع المادة:", ["سنكل بيبسي", "سنكل يومي", "سنكل اكوافينا", "سلم", "دبل بيبسي", "ثلاثي بيبسي", "ستاند 90", "ستاند 110", "ستاند 120", "ستاند 75", "ستاند 50", "مضلة صغيرة", "مضلة كبيرة", "طاولات", "كراسي"])
                
                if st.button("إضافة الطلب للسلة 📥"):
                    if trade_n:
                        st.session_state.basket.append({
                            "route_name": route, "delegate_name": delegate, "customer_name": trade_n,
                            "full_name": full_n, "address": addr, "details": note_inf, "cooler_type": item
                        })
                        st.rerun()

            if st.session_state.basket:
                st.subheader(f"🛒 الطلبات الجاهزة ({len(st.session_state.basket)})")
                for i, b in enumerate(st.session_state.basket):
                    st.caption(f"{i+1}- {b['customer_name']} ({b['cooler_type']})")
                
                if st.button("🚀 إرسال كافة الطلبات للمدير", use_container_width=True):
                    for req in st.session_state.basket:
                        supabase.table("cooler_orders").insert({**req, "supervisor_name": u_name, "status": "بانتظار موافقة المدير"}).execute()
                    st.session_state.basket = []
                    st.success("تم إرسال المجموعة بنجاح!")
                    st.rerun()

    # --- واجهة المتابعة والتصدير ---
    with col2:
        # --- 📑 قسم التصدير العمودي للنسخ ---
        with st.expander("📑 تصدير البيانات بنظام القوائم العمودية"):
            all_res = supabase.table("cooler_orders").select("*").execute().data
            if all_res:
                def list_field(key): return "\n".join([str(o.get(key, '-')) for o in all_res])
                
                exp_text = f"🏢 الاسم التجاري للعملاء:\n{list_field('customer_name')}\n\n"
                exp_text += f"📝 الأسماء الثلاثية:\n{list_field('full_name')}\n\n"
                exp_text += f"👤 أسماء المناديب:\n{list_field('delegate_name')}\n\n"
                exp_text += f"📍 المسارات:\n{list_field('route_name')}\n\n"
                exp_text += f"🎖️ أسماء المشرفين:\n{list_field('supervisor_name')}\n\n"
                exp_text += f"📦 أنواع المواد:\n{list_field('cooler_type')}\n\n"
                exp_text += f"🗺️ العناوين:\n{list_field('address')}"
                
                st.text_area("انسخ القوائم من هنا:", value=exp_text, height=300)
            else: st.write("لا توجد بيانات حالياً.")

        st.header("📋 سجل حركة الطلبات")
        orders = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute().data
        
        if orders:
            for o in orders:
                st_val = o['status']
                with st.expander(f"📦 {o['customer_name']} | {o['cooler_type']} | {st_val}"):
                    st.write(f"المسار: {o['route_name']} | المندوب: {o['delegate_name']} | المشرف: {o['supervisor_name']}")
                    if o.get('manager_notes'): st.error(f"❌ السبب/الملاحظة: {o['manager_notes']}")
                    if o.get('cooler_serial'): st.success(f"🔢 رقم البراد: {o['cooler_serial']}")

                    # 1. مدير التنمية
                    if user_role == "مدير التنمية" and st_val == "بانتظار موافقة المدير":
                        note = st.text_input("بيان سبب الرفض:", key=f"m_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ موافقة", key=f"ma_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تمت الموافقة - بانتظار المخزن"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض", key=f"mr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مرفوض من المدير", "manager_notes": note}).eq("id", o['id']).execute()
                            st.rerun()

                    # 2. مسؤول المخزن
                    elif user_role == "مسؤول المخزن" and st_val == "تمت الموافقة - بانتظار المخزن":
                        ser = st.text_input("أدخل رقم البراد:", key=f"s_{o['id']}")
                        note = st.text_input("سبب عدم التوفر:", key=f"sr_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التجهيز", key=f"sa_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "تم التجهيز - بانتظار العقد", "cooler_serial": ser}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ غير متوفر", key=f"srj_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "غير متوفر بالمخزن", "manager_notes": note}).eq("id", o['id']).execute()
                            st.rerun()

                    # 3. قسم التنسيق (محمد علي)
                    elif user_role == "قسم التنسيق (محمد علي)" and st_val == "تم التجهيز - بانتظار العقد":
                        if st.button("📝 تم إكمال العقد", key=f"co_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "جاهز للتوصيل"}).eq("id", o['id']).execute()
                            st.rerun()

                    # 4. سائق البرادات
                    elif user_role == "سائق البرادات" and st_val == "جاهز للتوصيل":
                        note = st.text_input("سبب رفض الاستلام:", key=f"dn_{o['id']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✅ تم التسليم", key=f"da_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "مكتمل"}).eq("id", o['id']).execute()
                            st.rerun()
                        if c2.button("❌ رفض العميل", key=f"dr_{o['id']}"):
                            supabase.table("cooler_orders").update({"status": "رفض استلام", "driver_notes": note}).eq("id", o['id']).execute()
                            st.rerun()
        
        # --- ⚠️ زر تصفير البيانات (خاص بمحمد علي فقط) ---
        if u_name == "قسم التنسيق (محمد علي)":
            st.markdown("---")
            st.error("⚠️ منطقة التحكم الإداري (تصفير البيانات)")
            if st.button("تصفير كافة الطلبات نهائياً"):
                try:
                    supabase.table("cooler_orders").delete().neq("id", 0).execute()
                    st.success("تم تصفير المنظومة بالكامل!")
                    st.rerun()
                except: st.error("حدث خطأ أثناء التصفير.")

    st.markdown("---")
    st.markdown("<center style='color: #888;'>Designed and Programmed by Coordination Officer: <b>Mohammed Ali Muheel</b></center>", unsafe_allow_html=True)
else:
    st.sidebar.warning("يرجى إدخال الرمز السري الصحيح")
