from sov.sov_agent import SovAgent

def main():
    print("🜏 SOVEREIGN INTELLIGENCE ONLINE")
    print("Type 'exit' to terminate.\n")

    sov = SovAgent()

    while True:
        user_input = input("You 🜍 ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("\n🜏 Shutting down Sov...\n")
            break
        try:
            response = sov.think(user_input)
            print("\nSov 🜲", response, "\n")
        except Exception as e:
            print("⚠️ Error:", str(e))

if __name__ == "__main__":
    main()
