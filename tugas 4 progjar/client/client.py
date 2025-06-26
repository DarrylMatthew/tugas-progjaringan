import requests
import os
import sys

def run_test(server_url):
    TEST_FILENAME = "test_file.txt"
    UPLOADED_FILENAME = "file_from_client.txt"

    print(f"--- Menjalankan tes untuk server di {server_url} ---")

    print(f"--- Membuat file uji: {TEST_FILENAME} ---")
    with open(TEST_FILENAME, "w") as f:
        f.write("Ini adalah file tes otomatis dari client.py.")
    print(f"[*] File '{TEST_FILENAME}' dibuat.")

    upload_url = f"{server_url}/upload"
    print(f"\n--- UPLOAD: Mengirim file ke {upload_url} ---")
    try:
        with open(TEST_FILENAME, 'rb') as f:
            files = {'filetoupload': (UPLOADED_FILENAME, f)}
            response = requests.post(upload_url, files=files, allow_redirects=False)
        print(f"[+] Server merespons upload dengan status: {response.status_code}")
        if response.status_code == 303:
            print("[SUCCESS] Upload berhasil.")
        else:
            print(f"[-] Upload mungkin gagal.")
    except requests.exceptions.RequestException as e:
        print(f"[!] Gagal terhubung ke server: {e}")
        os.remove(TEST_FILENAME)
        sys.exit(1)

    print("\n--- VERIFY UPLOAD: Meminta daftar file (GET) ---")
    try:
        response = requests.get(server_url)
        if UPLOADED_FILENAME in response.text:
            print(f"[SUCCESS] File '{UPLOADED_FILENAME}' ditemukan di server setelah upload.")
        else:
            print(f"[FAIL] File '{UPLOADED_FILENAME}' TIDAK ditemukan setelah upload.")
    except requests.RequestException as e:
        print(f"[!] Gagal mendapatkan daftar file: {e}")

    print("\n\n*** SKRIP DIJEDA ***")
    print("Sekarang Anda bisa memeriksa direktori 'web-files' di server.")
    input("Tekan Enter untuk melanjutkan dan menghapus file...")

    delete_url = f"{server_url}/delete/{UPLOADED_FILENAME}"
    print(f"\n--- DELETE: Menghapus file dari {delete_url} ---")
    try:
        response = requests.delete(delete_url)
        print(f"[+] Server merespons delete dengan status: {response.status_code}")
        if response.status_code == 200:
            print(f"[SUCCESS] Hapus berhasil.")
        else:
            print(f"[-] Penghapusan mungkin gagal.")
    except requests.RequestException as e:
        print(f"[!] Gagal menghapus file: {e}")

    print("\n--- VERIFY DELETE: Meminta daftar file lagi (GET) ---")
    try:
        response = requests.get(server_url)
        if UPLOADED_FILENAME not in response.text:
            print(f"[SUCCESS] File '{UPLOADED_FILENAME}' telah berhasil dihapus dari server.")
        else:
            print(f"[FAIL] File '{UPLOADED_FILENAME}' MASIH ada di server.")
    except requests.RequestException as e:
        print(f"[!] Gagal mendapatkan daftar file: {e}")

    print(f"\n--- Membersihkan file lokal ---")
    os.remove(TEST_FILENAME)
    print(f"[*] File '{TEST_FILENAME}' dihapus.")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ['thread', 'process']:
        print("Penggunaan: python client.py [thread|process]")
        print("  thread   : untuk terhubung ke server thread pool (port 8885)")
        print("  process  : untuk terhubung ke server process pool (port 8889)")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == 'thread':
        SERVER_URL = "http://localhost:8885"
    elif mode == 'process':
        SERVER_URL = "http://localhost:8889"
    
    run_test(SERVER_URL)
