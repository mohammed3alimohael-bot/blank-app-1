import streamlit as st

st.set_page_config(page_title="نظام بيبسي بغداد", layout="centered")

st.title("🚛 نظام تنسيق البرادات - شركة بيبسي")
st.subheader("أهلاً بك يا محمد في لوحة التحكم")

st.info("النظام الآن مرتبط بـ GitHub وجاهز للعمل.")

# إضافة تجريبية
name = st.text_input("ادخل اسم العميل لتجربة النظام:")
if st.button("حفظ تجريبي"):
    st.success(f"تم تسجيل {name} بنجاح في النظام!")
