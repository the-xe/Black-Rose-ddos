# 🥀 BLACK ROSE

**Version 2.0 — Reborn & Relentless.**

Black Rose is an elite stress testing framework designed for simulating sophisticated, high-intensity network attacks. It combines raw power with a clean, stealthy interface. Perfect for those who believe in strength through silence. 😈

---

## ✨ Features

- ⚡ **High-Intensity Performance:** A multi-threaded engine capable of launching thousands of concurrent connections.
- 🛡️ **Multi-Vector Attack Engine:** Combines Layer 3, 4, and 7 vectors like `HTTP/2 Rapid Reset`, `SYN Flood`, and `Hybrid Assault`.
- 🌐 **Stealth & Anonymity:** Integrated proxy manager with auto-validation (SOCKS5/SOCKS4/HTTP) to mask your origin.
- 🖥️ **Powerful Live Dashboard:** A clean and powerful CLI interface for real-time monitoring of attack telemetry.
- ⚙️ **Simple Configuration:** Easily configure complex attack scenarios via a single `config.json` file.

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/the-xe/sick-mind.git

# Navigate to the project directory
cd sick-mind

# Install the required dependencies
pip install -r requirements.txt

# Launch the tool (it will use config.json)
python main.py
```

---

## 🧪 Usage

From the command line:

```bash
# Launch an attack with custom parameters
python main.py --target https://example.com --duration 600
```

Or programmatically (by importing its modules, if designed for it):
```python
# This is a conceptual example if you structure it as a library
from black_rose import AttackOrchestrator

config = {"target": "https://example.com", "duration": 30, "threads": 100}
orchestrator = AttackOrchestrator(config)
orchestrator.unleash_vengeance()
```

---

## 📁 Project Structure

```
sick-mind/
├── files/
│   ├── dns.txt
│   └── headers.txt
├── black_rose.py
├── config.json
├── proxies.txt
├── README.md
└── requirements.txt
```

---

## ⚠️ Disclaimer

**Powered by a twisted mind.**
This tool is for educational and authorized testing ONLY.
We take no responsibility for how you use this tool.
*Use it however you want — it’s not our concern.*

---

## 🙋‍♂️ FAQ

**Q:** Is this project free?
**A:** Yes, it’s released under the MIT License.

**Q:** How can I contribute?
**A:** Fork the repo, make your changes, and submit a Pull Request!

---

## 👤 Developer

* **Amir Masoud**
* GitHub: [@the-xe](https://github.com/the-xe)
* Telegram: `@the_ouo`

---

## 📜 License

This project is licensed under **CC BY-NC 4.0**  
© 2025 Amir Masoud | All non-commercial uses allowed.
