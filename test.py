from app.chatbot import generate_response_debug

print("=== Chatbot Test Mode ===")
print("Nhập câu hỏi (gõ 'exit' để thoát)\n")

while True:
    user_input = input("👤 Bạn: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Kết thúc phiên trò chuyện.")
        break

    print("🤖 Chatbot đang trả lời...\n")
    response = generate_response_debug(user_input)
    print("🤖 Chatbot:", response)
    print("\n" + "-"*60 + "\n")
