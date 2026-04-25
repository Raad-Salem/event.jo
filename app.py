import streamlit as st
from groq import Groq
import json
import re

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="ماكان - مساعد event-jo.com", page_icon="🏡", layout="centered")

# --- تنسيق CSS احترافي لمنع تكسر الواجهة ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 15px; }
    .farm-card {
        background-color: #ffffff;
        border-right: 6px solid #2e7d32;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 20px 0;
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .farm-name { color: #2e7d32; font-size: 1.3rem; font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .farm-info { color: #333; font-size: 1rem; line-height: 1.8; margin-bottom: 5px; }
    .farm-info b { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. البيانات والـ API ---
# يفضل وضع المفتاح في Streamlit Secrets لاحقاً
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
    {"id": 9, "name": "Green Haven Farm", "location": "Zarqa", "price_per_day": 80, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 10, "name": "Desert Rose Farm", "location": "Wadi Rum", "price_per_day": 160, "available": True, "features": ["Luxury Tents", "Campfire"]},
    {"id": 11, "name": "Farm 11", "location": "Amman", "price_per_day": 105, "available": True, "features": ["BBQ", "WiFi"]},
    {"id": 12, "name": "Farm 12", "location": "Salt", "price_per_day": 92, "available": True, "features": ["Garden", "BBQ"]},
    {"id": 14, "name": "Farm 14", "location": "Madaba", "price_per_day": 98, "available": True, "features": ["BBQ", "Parking"]},
    {"id": 15, "name": "Farm 15", "location": "Irbid", "price_per_day": 88, "available": True, "features": ["Garden"]}
]

# --- 3. البرومبت الذكي ---
system_prompt = f"""
أنت المساعد الذكي "ماكان" من موقع event-jo.com. 
مهمتك: مساعدة المستخدمين في اختيار مزارع الأردن من القائمة التالية فقط: {json.dumps(farms_data)}

القواعد:
1. إذا كانت الرسالة مجرد ترحيب أو سؤال عن اسمك، جاوب بلطف وبلهجة أردنية دون ذكر المزارع.
2. إذا طلب المستخدم مزارع أو سأل عن منطقة، يجب أن تقدم له اقتراحات ثم تضع التفاصيل بصيغة JSON داخل وسم [DATA]...[/DATA].
3. التنسيق المطلوب للـ JSON: 
{{"recommendations": [{{"name": "اسم المزرعة", "price": "السعر", "features": "المميزات", "reason": "سبب الترشيح"}}]}}
4. لا تجب عن أي أسئلة خارج نطاق السياحة والمزارع في الأردن.
5. لا تقترح مزارع غير موجودة في القائمة.
"""

# --- 4. واجهة المستخدم ---
st.title("🏡 ماكان - مساعد مزارع الأردن")
st.caption("موقع event-jo.com - بوابتك لأجمل مزارع المملكة")

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض المحادثة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

if prompt := st.chat_input("كيف بقدر أساعدك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # بناء السياق للذكاء الاصطناعي
            history = [{"role": "system", "content": system_prompt}]
            for msg in st.session_state.messages[-5:]:
                # تنظيف المحتوى من أي كود HTML مخزن قبل إرساله للموديل
                clean_text = re.sub(r'<div.*?>.*?</div>', '', msg["content"], flags=re.DOTALL)
                history.append({"role": msg["role"], "content": clean_text})

            chat_completion = client.chat.completions.create(
                messages=history,
                model="llama-3.3-70b-versatile",
                temperature=0.5, # توازن بين الذكاء والالتزام
            )
            
            full_res = chat_completion.choices[0].message.content
            
            # استخراج النص (ما قبل البيانات التقنية)
            display_text = full_res.split("[DATA]")[0].strip()
            
            # البحث عن الـ JSON بأكثر من طريقة لضمان الاستقرار
            json_pattern = r'\{.*"recommendations".*\}'
            json_match = re.search(json_pattern, full_res, re.DOTALL)
            
            cards_html = ""
            if json_match:
                try:
                    data = json.loads(json_match.group(0).strip())
                    for rec in data.get("recommendations", []):
                        cards_html += f"""
                        <div class="farm-card">
                            <div class="farm-name">🏠 {rec['name']}</div>
                            <div class="farm-info">💰 <b>السعر:</b> {rec.get('price', 'حسب التواصل')} دينار</div>
                            <div class="farm-info">🌟 <b>المميزات:</b> {rec.get('features', 'مسبح وجلسات')}</div>
                            <div class="farm-info">📝 <b>ليش بنصحك فيها:</b> {rec.get('reason', '')}</div>
                        </div>
                        """
                    # تنظيف النص النهائي من أي كود JSON قد يظهر للمستخدم
                    display_text = re.sub(json_pattern, '', display_text, flags=re.DOTALL).strip()
                except:
                    pass

            final_output = display_text + cards_html
            st.markdown(final_output, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error(f"حدث خطأ: {e}")
