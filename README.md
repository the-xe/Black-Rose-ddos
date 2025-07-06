

<div align="center">

<img src="https://i.imgur.com/KqY7QyH.png" alt="Black Rose Banner" width="600"/>

Black Rose 🥀
Advanced Multi-Vector Stress Testing Framework - v15.0 "Overload Protocol"

![alt text](https://img.shields.io/badge/version-15.0%20Overload-purple?style=for-the-badge)


![alt text](https://img.shields.io/badge/language-Python-blue?style=for-the-badge)


![alt text](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)


![alt text](https://img.shields.io/badge/author-Amir%20Masoud-9cf?style=for-the-badge)

An elite, multi-vector stress testing and penetration testing tool designed to simulate sophisticated, high-intensity DDoS attack scenarios.

</div>

⚠️ Disclaimer & Legal Notice

This tool is intended strictly for educational, research, and authorized penetration testing purposes only. The use of this script for any illegal or malicious activities is strictly prohibited. The developer (Amir Masoud) and any contributors assume no liability and are not responsible for any misuse or damage caused by this program. The end-user is solely responsible for their actions.

📋 Table of Contents

✨ Key Features

📸 Dashboard Preview

⚙️ Installation & Setup

📝 Configuration

🚀 How to Use

🛡️ Attack Vectors

🤝 Contributing

📜 License

✨ Key Features

💥 Multi-Vector Attack Capability: Seamlessly combines Layer 3/4 (e.g., SYN Flood, UDP Flood) and Layer 7 (e.g., HTTP/2 Rapid Reset, Slowloris, Smuggling) attack vectors.

💻 Elegant Live Dashboard: A beautiful, real-time terminal UI powered by rich to monitor attack statistics and performance metrics.

⚡️ High-Performance Engine: Utilizes a ThreadPoolExecutor to manage thousands of concurrent threads for maximum attack intensity.

🌐 Intelligent Proxy Management: Automatically fetches, validates, and rotates proxies (HTTP, SOCKS4, SOCKS5) to ensure anonymity and bypass IP-based blocks.

🧩 Highly Configurable: Fine-tune attack mixes, thread counts, durations, and other parameters via a config.json file or command-line arguments.

💨 Modern Attack Vectors: Includes devastating, modern vectors like HTTP/2 Rapid Reset and HTTP Smuggling for testing next-generation infrastructure.

🛡️ Advanced Evasion: Employs randomized user-agents, referers, and custom headers to mimic legitimate traffic and evade security systems.

🔥 Overload Protocol: The latest version is engineered for extreme impact, designed to push target servers to their absolute limits.

📸 Dashboard Preview

A screenshot of the beautiful Black Rose dashboard in action:

(Note: Please replace this placeholder with an actual screenshot of the running application.)

<div align="center">
<img src="https://i.imgur.com/your-screenshot.png" alt="Black Rose Dashboard Preview" width="800"/>
</div>

⚙️ Installation & Setup

Follow these steps to get Black Rose up and running:

Clone the Repository:

Generated bash
git clone https://github.com/your-username/black-rose.git
cd black-rose


(Replace your-username/black-rose with your actual repository URL.)

Install Dependencies:
It is highly recommended to use a Python virtual environment.

Generated bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Then, install all required libraries:

Generated bash
pip install requests pysocks rich loguru h2 impacket cloudscraper certifi
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
📝 Configuration

All primary settings are managed in the config.json file. This file will be automatically generated with default values upon the first run.

Generated json
{
    "target": "https://example.com",   // Target URL
    "duration": 600,                   // Attack duration in seconds
    "threads": 8000,                   // Total number of attack threads
    "proxies": {
        "proxy_file": "proxies.txt",   // File containing proxies
        "sources": [ /* Proxy download sources */ ],
        "validate": true,              // Enable/disable proxy validation
        "validation_threads": 500
    },
    "logging": {
        "level": "INFO",
        "file": "black_rose_overload.log"
    },
    "attack_mix": { // Define the attack composition (percentages)
        "HYBRID_ASSAULT": 25,
        "HTTP2_RAPID_RESET": 25,
        "HTTP_GARBAGE_FLOOD": 15,
        "HTTP_SMUGGLING": 10,
        "SPOOF_SYN": 15,
        "UDP_FLOOD": 10
    },
    "plugin_config": { // Fine-tune settings for each attack vector
        "rpc": 200,
        "udp_flood_packet_size": 1472,
        "http_garbage_flood_size": 4096,
        "HTTP2RapidReset": {
            "streams_per_connection": 1000
        }
    }
}
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Json
IGNORE_WHEN_COPYING_END
🚀 How to Use

To launch an attack, simply run the script:

Generated bash
python black_rose.py
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

This command will use the settings defined in config.json. You can also override the main settings via command-line arguments for quick tests:

Generated bash
# Example: Attack a specific site for 5 minutes (300 seconds) with 10,000 threads
python black_rose.py -t https://target-site.com -d 300 -th 10000

# Use a different proxy file
python black_rose.py -p my_custom_proxies.txt
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
Argument	Description
-t, --target	Specifies the target URL.
-d, --duration	Sets the attack duration in seconds.
-th, --threads	Defines the total number of attack threads.
-p, --proxies	Provides the path to a custom proxy file.

To stop the attack at any time, press Ctrl+C.

🛡️ Attack Vectors

Black Rose supports a powerful suite of attack vectors:

Vector Name	Layer	Description
Hybrid Assault	L7	An intelligent mix that randomly cycles through potent L7 attack methods.
HTTP/2 Rapid Reset	L7	Abuses the H2 protocol to cause extreme CPU load on the target server.
HTTP Garbage Flood	L7	Sends POST requests with large, junk data payloads to saturate bandwidth.
HTTP Smuggling	L7	Sends obfuscated requests to confuse reverse proxies and web application firewalls.
SPOOF SYN	L3/L4	A classic SYN flood using spoofed IPs to exhaust the server's connection table.
UDP Flood	L3/L4	A high-volume UDP packet flood designed to saturate the target's network capacity.
Slowloris	L7	Keeps connections open by slowly sending partial headers, exhausting socket pools.
DNS/NTP AMP	L4	DRDoS attacks that use public servers to amplify traffic towards the target.
🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

If you have a suggestion that would make this better, or if you find a bug, please open an Issue or submit a Pull Request.

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request

📜 License

Distributed under the MIT License. See the LICENSE file for more information.

<div align="center">


Forged with ❤️ by Amir Masoud

</div>
