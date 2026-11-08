import re
import streamlit as st

# ---------------------------------------------------------
# 1. DATABASE KATA KAKU AI & SARAN REVISI (DATASET)
# ---------------------------------------------------------
AI_CLICHE_WORDS = {
    "di era digital ini": "saat ini",
    "pada era digital saat ini": "sekarang ini",
    "penting untuk diingat bahwa": "ingat bahwa",
    "dapat disimpulkan bahwa": "singkatnya,",
    "merupakan elemen penting": "sangat penting",
    "menjelajahi": "membahas",
    "merangkul": "menerima",
    "dalam rangka untuk": "untuk",
    "tidak dapat dipungkiri bahwa": "jelas bahwa",
    "memberikan dampak yang signifikan": "berdampak besar",
}

# ---------------------------------------------------------
# 2. LOGIKA PENILAIAN HUMANIZER (SKOR 1 - 100)
# ---------------------------------------------------------
def analyze_text(text):
    if not text.strip():
        return 0, [], text

    words = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    
    total_words = len(words)
    total_sentences = len(sentences) if len(sentences) > 0 else 1

    # Indikator 1: Deteksi Kata Klise AI
    detected_cliches = []
    text_lower = text.lower()
    cliche_count = 0
    
    revised_text = text
    for cliche, replacement in AI_CLICHE_WORDS.items():
        if cliche in text_lower:
            detected_cliches.append(cliche)
            cliche_count += 1
            # Ganti kata kaku dengan variasi natural
            pattern = re.compile(re.escape(cliche), re.IGNORECASE)
            revised_text = pattern.sub(f"**{replacement}**", revised_text)

    # Indikator 2: Variasi Panjang Kalimat (Burstiness)
    sentence_lengths = [len(s.split()) for s in sentences]
    if len(sentence_lengths) > 1:
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((l - avg_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        burstiness_score = min(variance * 2, 25) # Skor variasi maks 25
    else:
        burstiness_score = 5

    # Kalkulasi Skor Akhir Humanizer (Mulai dari 100)
    score = 100
    score -= (cliche_count * 15) # Pengurangan berat jika ada kata klise AI
    score += (burstiness_score - 10) # Bonus jika variasi kalimat tinggi
    
    # Kunci skor di rentang 1 - 100
    final_score = int(max(1, min(100, score)))

    return final_score, detected_cliches, revised_text

# ---------------------------------------------------------
# 3. TAMPILAN ANTARMUKA WEB (STREAMLIT)
# ---------------------------------------------------------
st.set_page_config(page_title="AI Humanizer Checker", page_icon="🤖")

st.title("🤖 AI Humanizer Style Checker")
st.write("Cek seberapa kaku atau natural gaya bahasa teksmu, lengkapi dengan skor 1-100 dan saran revisi otomatis!")

# Input Teks Pengguna
user_text = st.text_area(
    "Masukkan teks / draf tulisan di sini:", 
    height=180,
    placeholder="Contoh: Di era digital ini, penting untuk diingat bahwa teknologi..."
)

if st.button("🔍 Cek Gaya Bahasa & Analisis"):
    if user_text.strip():
        score, cliches, revised = analyze_text(user_text)

        st.markdown("---")
        st.subheader("📊 Hasil Analisis")

        # Tampilan Skor Utama
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(label="Skor Keaslian Manusia", value=f"{score} / 100")
        
        with col2:
            if score >= 80:
                st.success("🎉 **Gaya Bahasa Natural & Manusiawi!** Tulisanmu tidak terasa kaku.")
            elif score >= 50:
                st.warning("⚠️ **Agak Kaku / Terindikasi AI.** Ada beberapa struktur kalimat yang perlu dirapikan.")
            else:
                st.error("🚨 **Sangat Kaku (Gaya AI):** Terlalu banyak frasa klise khas mesin.")

        # Menampilkan Detail Frasa Kaku yang Ditemukan
        if cliches:
            st.write("---")
            st.write("❌ **Frasa Kaku Khas AI yang Terdeteksi:**")
            for c in cliches:
                st.write(f"- *\"{c}\"*")

        # Fitur Revisi Otomatis jika Skor < 80
        if score < 80:
            st.write("---")
            st.subheader("✏️ Saran Revisi (Lebih Natural):")
            st.write("Kata-kata tebal di bawah adalah variasi bahasa yang lebih luwes:")
            st.info(revised)
    else:
        st.warning("Silakan masukkan teks terlebih dahulu!")