import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components
from groq import Groq
import os

# ======================
# ⚙️ CẤU HÌNH TRANG
# ======================
st.set_page_config(page_title="Trợ lý Lịch sử Việt Nam", layout="centered")

# ======================
# 🧠 KHỞI TẠO TRẠNG THÁI
# ======================
if "audio_unlocked" not in st.session_state:
    st.session_state["audio_unlocked"] = False

# ======================
# 🔧 KHỞI TẠO AI
# ======================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def hoi_ai_lich_su(cau_hoi):
    """DÙNG AI trả lời mọi câu hỏi lịch sử Việt Nam."""
    chat = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", 
             "content": "Bạn là trợ lý lịch sử Việt Nam. Trả lời chính xác, ngắn gọn, rõ ràng."},
            {"role": "user", "content": cau_hoi}
        ],
        max_tokens=200
    )
    return chat.choices[0].message["content"]

# ======================
# 💬 GIAO DIỆN NGƯỜI DÙNG
# ======================
st.title("📚 TRỢ LÝ LỊCH SỬ (AI)")
st.write("👉 Bấm **BẬT ÂM THANH** (chỉ 1 lần), sau đó nhập câu hỏi rồi bấm **Trả lời**.")
st.write("📱 Trên hệ điều hành IOS, bạn cần bấm nút ▶ để nghe giọng nói (quy định của Safari).")
st.write("📱 Trên hệ điều hành android,máy tính bảng,laptop,máy tính bàn không cần bấm nút ▶ để nghe vì nó tự nói .")
# ======================
# 🔓 NÚT BẬT ÂM THANH
# ======================
if st.button("🔊 BẬT ÂM THANH (1 lần)"):
    js_unlock = """
    <script>
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (ctx.state === 'suspended') ctx.resume();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        gain.gain.value = 0;
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.05);
        console.log("Âm thanh đã mở khoá thành công.");
      } catch(e) {
        console.log("Không thể mở khoá âm thanh:", e);
      }
    </script>
    """
    components.html(js_unlock, height=0)
    st.session_state["audio_unlocked"] = True
    st.success("Âm thanh đã mở khoá thành công!")

# ======================
# ❓ NHẬP CÂU HỎI
# ======================
cau_hoi = st.text_input("Nhập câu hỏi lịch sử:")

# ======================
# 📖 TRẢ LỜI
# ======================
if st.button("📖 Trả lời"):

    # AI trả lời
    tra_loi = hoi_ai_lich_su(cau_hoi)
    st.success(tra_loi)

    # 🎙️ TẠO GIỌNG NÓI
    try:
        mp3_fp = BytesIO()
        gTTS(text=tra_loi, lang="vi").write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode()
    except Exception as e:
        st.error("Lỗi tạo giọng nói!")
        audio_b64 = None

    # 🎧 PHÁT ÂM THANH
    if audio_b64:
        autoplay_flag = "true" if st.session_state["audio_unlocked"] else "false"

        audio_html = f"""
        <div id="tts_player"></div>
        <script>
        (function() {{
            const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
            const unlocked = {autoplay_flag};

            const player = document.createElement('audio');
            player.src = "data:audio/mp3;base64,{audio_b64}";
            player.controls = true;
            player.playsInline = true;

            document.getElementById("tts_player").appendChild(player);

            if (!isIOS && unlocked) {{
                player.autoplay = true;
                player.play().catch(e => console.log("Autoplay bị chặn:", e));
            }}
        }})();
        </script>
        """

        components.html(audio_html, height=100)

        # THÔNG BÁO
        if st.session_state["audio_unlocked"]:
            st.info("🔊 Thiết bị này sẽ tự động phát âm (Android, PC, Mac...).")
        else:
            st.warning("⚠️ Trên iPhone/iPad: cần bấm ▶ để nghe.")
