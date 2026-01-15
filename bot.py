import requests
import asyncio
from telegram.ext import ApplicationBuilder

TOKEN = "7985602713:AAFkmSXChVV2783FiHKbCkhm4Vd2jl-MaiQ"
CHAT_ID = "5927558862"
API_URL = "https://lc79md5-lun8.onrender.com/lc79md5"

history = []
last_phien = None
last_prediction = None

total = win = lose = lose_streak = 0

def analyze_cau(hist):
    score = 0
    pred = None
    details = []

    if len(hist) >= 3 and hist[-1] == hist[-2] == hist[-3]:
        score += 4
        pred = hist[-1]
        details.append("• Cầu bệt 3  ✅")
    else:
        details.append("• Cầu bệt 3  ❌")

    if len(hist) >= 3 and hist[-3] == hist[-1] != hist[-2]:
        score += 3
        pred = hist[-1]
        details.append("• Cầu 2–1    ✅")
    else:
        details.append("• Cầu 2–1    ❌")

    if len(hist) >= 4 and hist[-1] == hist[-3] == hist[-4]:
        score += 2
        pred = hist[-1]
        details.append("• Cầu đảo    ✅")
    else:
        details.append("• Cầu đảo    ❌")

    decision = "⚪ KHÔNG NÊN VÀO"
    if score >= 7:
        decision = "🔴 NÊN VÀO"
    elif score >= 4:
        decision = "🟡 CÂN NHẮC"

    return pred, score, decision, "\n".join(details)

async def bot_loop(app):
    global last_phien, last_prediction
    global total, win, lose, lose_streak

    while True:
        try:
            data = requests.get(API_URL, timeout=10).json()
            phien = data["phien"]
            ketqua = data["ket_qua"].upper()

            if phien != last_phien:
                history.append(ketqua)
                history[:] = history[-50:]

                prev_result = "—"
                if last_prediction:
                    total += 1
                    if ketqua == last_prediction:
                        win += 1
                        lose_streak = 0
                        prev_result = "✅ WIN"
                    else:
                        lose += 1
                        lose_streak += 1
                        prev_result = "❌ LOSE"
                    last_prediction = None

                pred, score, decision, detail = analyze_cau(history)

                if lose_streak >= 2:
                    decision = "⚪ KHÔNG NÊN VÀO"

                if decision.startswith("🔴"):
                    last_prediction = pred

                acc = round((win / total) * 100) if total else 0
                du_doan = pred if decision != "⚪ KHÔNG NÊN VÀO" else "KHÔNG ĐƯA KÈO"

                message = f"""
🎰 LC79 | PHÂN TÍCH PHIÊN
══════════════════════
🆔 Phiên: {phien}

📊 Kết quả vừa ra:
➡️  {ketqua}

━━━━━━━━━━━━━━━━━━━━━━
🔮 DỰ ĐOÁN PHIÊN TIẾP
➡️  {du_doan}

🎯 Điểm cầu: {score} / 10
🧠 Thuật toán:
{detail}

🚦 KHUYẾN NGHỊ:
{decision}

━━━━━━━━━━━━━━━━━━━━━━
📈 KẾT QUẢ TRƯỚC ĐÓ
➡️  {prev_result}

📊 THỐNG KÊ TỔNG
• Tổng kèo: {total}
• Win: {win} | Lose: {lose}
• Tỷ lệ: {acc}%

⚠️ CẢNH BÁO
• Thuật toán cầu
• Không đảm bảo 100%
• Quản lý vốn chặt chẽ
══════════════════════
"""
                await app.bot.send_message(chat_id=CHAT_ID, text=message)
                last_phien = phien

        except:
            pass

        await asyncio.sleep(60)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    asyncio.create_task(bot_loop(app))
    await app.initialize()
    await app.start()
    await asyncio.Event().wait()

asyncio.run(main())
