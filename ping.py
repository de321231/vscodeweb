import os
import shlex
import subprocess


def ask_host():
    host = input("Enter IP-Address to ping: ").strip()
    if not host:
        print("NO INPUT.")
        return None
    return host

def ping_once(host, timeout_sec=2):
    # Linux: ein Paket senden, kurze Wartezeit
    cmd = f"ping -c 1 -W {timeout_sec} {shlex.quote(host)}"
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = proc.stdout + proc.stderr
    if proc.returncode != 0:
        return False, out  # nicht erreichbar / Fehler
    # versuche die Zeit aus der Ausgabe zu parsen, z.B. "time=23.4 ms"
    m = re.search(r"time[=<]\s*([\d\.]+)\s*ms", out)
    if m:
        return True, float(m.group(1))
    # Fallback: rtt-Zeile parsen "rtt min/avg/max/mdev = 23.123/23.123/23.123/0.000 ms"
    m2 = re.search(r"rtt .* = [\d\.]+/([\d\.]+)/", out)
    if m2:
        return True, float(m2.group(1))
    return True, None  # erreichbar, aber Zeit nicht gefunden

def main():
    host = ask_host()
    if not host:
        return
    ok, info = ping_once(host)
    if ok:
        if isinstance(info, (int, float)):
            print(f"host {host} ist erreichbar, durchschnittliche Zeit: {info} ms")
        else:
            print(f"host {host} ist erreichbar, Zeit konnte nicht ermittelt werden")
    else:
        print(f"host {host} ist nicht erreichbar. Fehler:\n{info}")

if __name__ == "__main__":
    main()