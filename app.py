import streamlit as st
import google.generativeai as genai
import json

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="مساعد حجز مزارع الأردن", page_icon="🏡", layout="centered")

# --- 2. التنسيق (تم تصحيح unsafe_allow_html) ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stJson { background-color: #f0f2f6; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. إعداد المفتاح والبيانات ---
# تأكد من وضع مفتاحك الصحيح هنا
API_KEY = "AIzaSyDkwqVEQroepg-R1Mxeml1bmGzjX9oQnQw" 
genai.configure(api_key=API_KEY)

# بيانات المزارع (الـ 15 مزرعة)
farms_data = [
    {"id": 1, "name": "Green Valley Farm", "location": "Amman", "price_per_day": 120, "available": True, "features": ["Pool", "BBQ", "WiFi"]},
    {"id": 2, "name": "Sunset Farm", "location": "Salt", "price_per_day": 90, "available": True, "features": ["BBQ", "Garden"]},
    {"id": 3, "name": "Olive Tree Farm", "location": "Jerash", "price_per_day": 110, "available": False, "features": ["Pool", "BBQ"]},
    {"id": 4, "name": "Blue Sky Farm", "location": "Madaba", "price_per_day": 100, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 5, "name": "Golden Field Farm", "location": "Irbid", "price_per_day": 95, "available": True, "features": ["Parking", "Farm Animals"]},
    {"id": 6, "name": "Royal Hills Farm", "location": "Amman", "price_per_day": 150, "available": True, "features": ["Pool", "Luxury Seating"]},
    {"id": 7, "name": "Cherry Blossom Farm", "location": "Ajloun", "price_per_day": 85, "available": True, "features": ["Nature View", "BBQ"]},
    {"id": 8, "name": "Palm Oasis Farm", "location": "Aqaba", "price_per_day": 140, "available": False, "features": ["Pool", "Sea View"]},
    {"id": 9, "name": "Green Haven Farm", "location": "Zarqa", "price_per_day": 80, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 10, "name": "Desert Rose Farm", "location": "Wadi Rum", "price_per_day": 160, "available": True, "features": ["Luxury Tents", "Campfire"]},
    {"id": 11, "name": "Farm 11", "location": "Amman", "price_per_day": 105, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 12, "name": "Farm 12", "location": "Salt", "price_per_day": 92, "available": True, "features": ["Garden", "BBQ"]},
    {"id": 13, "name": "Farm 13", "location": "Jerash", "price_per_day": 115, "available": False, "features": ["Pool", "Playground"]},
    {"id": 14, "name": "Farm 14", "location": "Madaba", "price_per_day": 98, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 15, "name": "Farm 15", "location": "Irbid", "price_per_day": 88, "available": True, "features": ["Garden"]}
]

# --- 4. بناء الموديل ---
system_instruction = f"أنت مساعد ذكي لمنصة حجز مزارع في الأردن. داتا المزارع المتاحة: {json.dumps(farms_data)}. المهام: للأسئلة العامة جاوب بلهجة أردنية. لطلبات البحث أعطِ النتيجة حصراً بصيغة JSON فيها filters و assumptions و recommendations."

# محاولة تحميل الموديل بالاسم الأكثر استقراراً
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction=system_instruction
    )
except Exception as e:
    st.error(f"خطأ في تحميل الموديل: {e}")

# --- 5. واجهة المستخدم ---
st.title("🏡 بوكر مزارع الأردن")
st.caption("نظام بحث ذكي تجريبي (RAG)")

# ذاكرة الشات
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], dict):
            st.json(message["content"])
        else:
            st.markdown(message["content"])

# إدخال المستخدم الجديد
if prompt := st.chat_input("كيف بقدر أساعدك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # طلب الرد من الموديل
            response = model.generate_content(prompt)
            text_resp = response.text
            
            try:
                # محاولة استخراج الـ JSON من الرد (في حال وضع الموديل الرد بين علامات ```)
                clean_json = text_resp.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0]
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0]
                
                data = json.loads(clean_json.strip())
                st.json(data)
                st.session_state.messages.append({"role": "assistant", "content": data})
            except:
                # إذا لم يكن الرد JSON (مثل جواب "أهلاً بك")
                st.markdown(text_resp)
                st.session_state.messages.append({"role": "assistant", "content": text_resp})
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالذكاء الاصطناعي: {e}")
