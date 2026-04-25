import streamlit as st
from groq import Groq
import json
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS ثابت وواضح ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; }
    .farm-card {
        background-color: #ffffff;
        border-right: 6px solid #2e7d32;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 10px;
        margin-bottom: 10px;
        direction: rtl;
    }
    .farm-name { color: #2e7d32; font-size: 1.2rem; font-weight: bold; }
    .farm-detail { color: #444; font-size: 0.95rem; margin-top: 3px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات والـ API ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

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
    {"id": 14, "name": "Farm 14", "location": "Madaba", "price_per_day": 98, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 15, "name": "Farm 15", "location": "Irbid", "price_per_day": 88, "available": True, "features": ["Garden"]}
]

# --- 3. البرومبت المطور ---
system_prompt = f"""
أنت "ماكان" مساعد event-jo.com. اتبع القواعد التالية بدقة:

1. **التمييز بين المحادثة والبحث:**
   - إذا كان سؤال المستخدم تحية (هاي، كيفك، مين أنت)، جاوب بلهجة أردنية ودودة وبدون ذكر أي مزارع أو استخدام وسم [DATA].
   - إذا طلب المستخدم "مزرعة" أو سأل عن "مكان" أو "عدد أشخاص"، قدم الرد المناسب ثم ألحقه بالبيانات داخل وسم [DATA]...[/DATA].

2. **قاعدة البيانات:** {json.dumps(farms_data)}

3. **تنسيق الـ JSON داخل [DATA]:**
   {{"recommendations": [{{"name": "", "price": "", "features": "", "reason": ""}}]}}
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد مزارع الأردن")
st.caption("موقع event-jo.com - نخدمك بعيونا")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل المخزنة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("اسأل ماكان..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # إرسال تاريخ المحادثة للموديل ليفهم السياق
            messages_history = [{"role": "system", "content": system_prompt}]
            for msg in st.session_state.messages[-3:]: # آخر 3 رسائل للسياق
                role = "assistant" if msg["role"] == "assistant" else "user"
                # تنظيف المحتوى من الـ HTML المخزن قبل إرساله للموديل
                clean_content = re.sub(r'<div.*?>.*?</div>', '', msg["content"], flags=re.DOTALL)
                messages_history.append({"role": role, "content": clean_content})

            chat_completion = client.chat.completions.create(
                messages=messages_history,
                model="llama-3.3-70b-versatile",
                temperature=0.4,
            )
            
            full_response = chat_completion.choices[0].message.content
            
            # فصل النص عن البيانات
            display_text = full_response.split("[DATA]")[0].strip()
            final_html_output = display_text
            
            json_match = re.search(r"\[DATA\](.*?)\[/DATA\]", full_response, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1).strip())
                    cards_html = "<br>"
                    for rec in data.get("recommendations", []):
                        cards_html += f"""
                        <div class="farm-card">
                            <div class="farm-name">🏠 {rec['name']}</div>
                            <div class="farm-detail">💰 السعر: {rec.get('price', 'اتصال')} دينار</div>
                            <div class="farm-detail">🌟 المميزات: {rec.get('features', '')}</div>
                            <div class="farm-detail">📝 ليش بنصحك فيها: {rec.get('reason', '')}</div>
                        </div>
                        """
                    final_html_output += cards_html
                except:
                    pass

            st.markdown(final_html_output, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": final_html_output})
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
