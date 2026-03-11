import streamlit as st
from supabase import create_client

# إعدادات واجهة النظام
st.set_page_config(page_title="نظام بيبسي بغداد", layout="wide")

# الربط بقاعدة البيانات
url = "xvixqbcqunrvbvqvlplz.supabase.co"
key = "sb_publishable_PSotHRdrxbHMZPpAuBcp4Q_Pxq0H02p"
supabase = create_client(url, key)

st.title("🚛 نظام تنسيق البرادات - شركة بيبسي")
st.markdown("---")

# تقسيم الشاشة
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("➕ إضافة طلب جديد")
    customer = st.text_input("اسم العميل (المحل/السوبر ماركت)")
    location = st.text_input("العنوان بالتفصيل")
    cooler = st.selectbox("نوع البراد", ["براد بيبسي كبير", "براد بيبسي وسط", "ستاند عرض"])
    
    if st.button("حفظ وإرسال للمدير"):
        if customer and location:
            try:
                data = {"customer_name": customer, "address": location, "cooler_type": cooler, "status": "قيد الانتظار"}
                supabase.table("cooler_orders").insert(data).execute()
                st.success(f"✅ تم حفظ طلب {customer} بنجاح!")
                st.balloons()
                st.rerun() # تحديث الصفحة لرؤية الطلب الجديد
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
        else:
            st.warning("الرجاء كتابة اسم العميل والعنوان")

with col2:
    st.header("📋 إدارة الطلبات والإحصائيات")
    
    try:
        # جلب البيانات
        res = supabase.table("cooler_orders").select("*").order('created_at', desc=True).execute()
        orders = res.data

        if orders:
            # --- لوحة الإحصائيات ---
            total = len(orders)
            done = len([o for o in orders if o['status'] == "تم الإنجاز"])
            pending = total - done
            
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الطلبات", total)
            c2.metric("تم الإنجاز ✅", done)
            c3.metric("قيد الانتظار ⏳", pending)
            st.markdown("---")

            # --- عرض الطلبات ---
            for order in orders:
                status_color = "🟢" if order['status'] == "تم الإنجاز" else "🟡"
                with st.expander(f"{status_color} {order['customer_name']} - {order['status']}"):
                    st.write(f"📍 **العنوان:** {order['address']}")
                    st.write(f"🥤 **نوع البراد:** {order['cooler_type']}")
                    
                    # أزرار تغيير الحالة
                    b1, b2, b3 = st.columns(3)
                    if b1.button("✅ تم الإنجاز", key=f"done_{order['id']}"):
                        supabase.table("cooler_orders").update({"status": "تم الإنجاز"}).eq("id", order['id']).execute()
                        st.rerun()
                    
                    if b2.button("⏳ قيد الانتظار", key=f"wait_{order['id']}"):
                        supabase.table("cooler_orders").update({"status": "قيد الانتظار"}).eq("id", order['id']).execute()
                        st.rerun()

                    if b3.button("🗑️ حذف", key=f"del_{order['id']}"):
                        supabase.table("cooler_orders").delete().eq("id", order['id']).execute()
                        st.rerun()
        else:
            st.write("لا توجد طلبات مسجلة حالياً.")
    except Exception as e:
        st.error(f"خطأ في عرض البيانات: {e}")
