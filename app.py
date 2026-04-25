import streamlit as st
from groq import Groq
import json
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS ثابت ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; }
    .farm-card {
        background-color: #ffffff;
        border-right: 6px solid #2e7d32;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 10px 0;
        direction: rtl;
        text-align: right;
    }
    .farm-name { color: #2e7d32; font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }
    .farm-info { color: #333; font-size: 0.95rem; line-height: 1.6; }
    .farm-info b { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد الـ API والبيانات ---
# بدل السطر القديم، حط هاد السطر:
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

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

# --- 3. تعليمات النظام ---
system_prompt = f"""
أنت "ماكان"، المساعد الذكي لموقع event-jo.com. 
مهمتك إيجاد مزارع للإيجار في الأردن من هذه الداتا فقط: {json.dumps(farms_data)}

القواعد الصارمة:
1. إذا كانت رسالة المستخدم مجرد تحية (هاي، مرحبا، كيفك)، جاوب بترحيب لطيف واسأله كيف ممكن تساعده. **ممنوع نهائياً** ترشيح أي مزرعة أو استخدام وسم [DATA].
2. إذا طلب المستخدم مزرعة أو سأل عن منطقة، اكتب مقدمة بسيطة، ثم ضع الاقتراحات حصراً داخل وسم [DATA]...[/DATA] بصيغة JSON.
3. التنسيق الإلزامي للاقتراحات:
[DATA]
{{
  "recommendations": [
    {{"name": "اسم المزرعة", "price": 120, "features": "الميزات", "reason": "سبب الترشيح"}}
  ]
}}
[/DATA]
4. ممنوع كتابة أي كود HTML أو CSS.
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد مزارع الأردن")
st.caption("event-jo.com - بوابتك لأجمل مزارع المملكة")

# تهيئة الذاكرة بشكل جديد (النص مفصول عن الداتا)
if "messages" not in st.session_state:
    st.session_state.messages = []

# دالة رسم الكروت (هيك الموديل ما بشوف الـ HTML)
def render_cards(farms_list):
    for rec in farms_list:
        st.markdown(f"""
        <div class="farm-card">
            <div class="farm-name">🏠 {rec.get('name', '')}</div>
            <div class="farm-info">💰 <b>السعر:</b> {rec.get('price', '')} دينار</div>
            <div class="farm-info">🌟 <b>المميزات:</b> {rec.get('features', '')}</div>
            <div class="farm-info">📝 <b>ليش بنصحك فيها:</b> {rec.get('reason', '')}</div>
        </div>
        """, unsafe_allow_html=True)

# عرض الرسائل السابقة
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])
        if msg.get("farms"):
            render_cards(msg["farms"])

if prompt := st.chat_input("كيف بقدر أساعدك اليوم؟"):
    st.session_state.messages.append({"role": "user", "text": prompt, "farms": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 1. إرسال المحادثة للموديل (نص صافي فقط بدون HTML)
            history_for_llm = [{"role": "system", "content": system_prompt}]
            for msg in st.session_state.messages[-5:]:
                history_for_llm.append({"role": msg["role"], "content": msg["text"]})

            chat_completion = client.chat.completions.create(
                messages=history_for_llm,
                model="llama-3.3-70b-versatile",
                temperature=0.3, # دقة عالية عشان يلتزم بالقواعد
            )
            
            full_res = chat_completion.choices[0].message.content
            
            # 2. استخراج النص والـ JSON بأمان تام
            display_text = full_res.split("[DATA]")[0].strip()
            
            # تنظيف إضافي لمنع ظهور أقواس الـ JSON ككلام عادي
            display_text = re.sub(r'\{.*?\}', '', display_text, flags=re.DOTALL).strip()
            
            extracted_farms = []
            json_match = re.search(r"\[DATA\](.*?)\[/DATA\]", full_res, re.DOTALL)
            
            if json_match:
                try:
                    data = json.loads(json_match.group(1).strip())
                    extracted_farms = data.get("recommendations", [])
                except Exception:
                    pass

            # 3. عرض النتيجة
            st.markdown(display_text)
            if extracted_farms:
                render_cards(extracted_farms)
            
            # 4. حفظ الرسالة في الذاكرة بشكل منظم
            st.session_state.messages.append({
                "role": "assistant",
                "text": display_text,
                "farms": extracted_farms
            })
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
