import streamlit as st
from groq import Groq
import json
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS محسّن لمنع تكسر الكروت ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; }
    .farm-card {
        background-color: #fdfdfd;
        border-right: 6px solid #2e7d32;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 15px 0;
        direction: rtl;
        text-align: right;
    }
    .farm-name { color: #2e7d32; font-size: 1.2rem; font-weight: bold; margin-bottom: 8px; }
    .farm-info { color: #444; font-size: 0.95rem; line-height: 1.6; }
    .emoji { margin-left: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات والـ API ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# بيانات المزارع (تم التأكد من صحتها)
farms_data = [
    {"id": 1, "name": "Green Valley Farm", "location": "Amman", "price_per_day": 120, "available": True, "features": ["Pool", "BBQ", "WiFi"]},
    {"id": 2, "name": "Sunset Farm", "location": "Salt", "price_per_day": 90, "available": True, "features": ["BBQ", "Garden"]},
    {"id": 3, "name": "Olive Tree Farm", "location": "Jerash", "price_per_day": 110, "available": False, "features": ["Pool", "BBQ"]},
    {"id": 4, "name": "Blue Sky Farm", "location": "Madaba", "price_per_day": 100, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 5, "name": "Golden Field Farm", "location": "Irbid", "price_per_day": 95, "available": True, "features": ["Parking", "Farm Animals"]},
    {"id": 6, "name": "Royal Hills Farm", "location": "Amman", "price_per_day": 150, "available": True, "features": ["Pool", "Luxury Seating"]},
    {"id": 7, "name": "Cherry Blossom Farm", "location": "Ajloun", "price_per_day": 85, "available": True, "features": ["Nature View", "BBQ"]},
    {"id": 9, "name": "Green Haven Farm", "location": "Zarqa", "price_per_day": 80, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 10, "name": "Desert Rose Farm", "location": "Wadi Rum", "price_per_day": 160, "available": True, "features": ["Luxury Tents", "Campfire"]},
    {"id": 11, "name": "Farm 11", "location": "Amman", "price_per_day": 105, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 12, "name": "Farm 12", "location": "Salt", "price_per_day": 92, "available": True, "features": ["Garden", "BBQ"]},
    {"id": 14, "name": "Farm 14", "location": "Madaba", "price_per_day": 98, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 15, "name": "Farm 15", "location": "Irbid", "price_per_day": 88, "available": True, "features": ["Garden"]}
]

# --- 3. البرومبت الصارم ---
system_prompt = f"""
أنت "ماكان"، المساعد الذكي الرسمي لموقع event-jo.com.

قواعد صارمة:
1. وظيفتك **فقط** هي المساعدة في حجز المزارع في الأردن من هذه البيانات: {json.dumps(farms_data)}
2. إذا سألك المستخدم عن أي موضوع خارج المزارع (سياسة، كورونا، طبخ، أخبار)، اعتذر بلباقة بلهجة أردنية وقل: "أنا متخصص بس بمزارع الأردن من event-jo.com، بقدر أساعدك تلاقي مزرعة بتجنن!".
3. في حال البحث: ابدأ الرد بجملة ترحيبية، ثم ضع البيانات حصراً داخل وسم [DATA]...[/DATA] بصيغة JSON.
4. لا تقترح مزارع في مناطق غير موجودة (مثل صويلح إذا لم تكن في القائمة).
5. ممنوع عرض أي كود HTML في ردك النصي.
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد مزارع الأردن")
st.caption("النسخة المطورة - event-jo.com")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("كيف بقدر أساعدك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # تنظيف السياق للموديل
            messages_history = [{"role": "system", "content": system_prompt}]
            for msg in st.session_state.messages[-5:]: 
                clean_content = re.sub(r'<div.*?>.*?</div>', '', msg["content"], flags=re.DOTALL)
                messages_history.append({"role": msg["role"], "content": clean_content})

            chat_completion = client.chat.completions.create(
                messages=messages_history,
                model="llama-3.3-70b-versatile",
                temperature=0.3, # تقليل الحرارة لزيادة الدقة ومنع الهذيان
            )
            
            full_response = chat_completion.choices[0].message.content
            
            # معالجة الفصل بين النص والكروت
            display_text = full_response.split("[DATA]")[0].strip()
            json_match = re.search(r"\[DATA\](.*?)\[/DATA\]", full_response, re.DOTALL)
            
            cards_html = ""
            if json_match:
                try:
                    data = json.loads(json_match.group(1).strip())
                    for rec in data.get("recommendations", []):
                        # بناء الكرت برمجياً لضمان عدم تكسر الـ HTML
                        cards_html += f"""
                        <div class="farm-card">
                            <div class="farm-name">🏠 {rec['name']}</div>
                            <div class="farm-info">💰 <b>السعر:</b> {rec.get('price', 'حسب الموسم')} دينار</div>
                            <div class="farm-info">🌟 <b>المميزات:</b> {rec.get('features', 'متعددة')}</div>
                            <div class="farm-info">📝 <b>ليش بنصحك فيها:</b> {rec.get('reason', '')}</div>
                        </div>
                        """
                except:
                    pass

            final_output = display_text + cards_html
            st.markdown(final_output, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
