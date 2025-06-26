import sys
import os
import re
from datetime import datetime
import urllib.parse

class HttpServer:
    def __init__(self):
        self.types = {}
        self.types['.pdf'] = 'application/pdf'
        self.types['.jpg'] = 'image/jpeg'
        self.types['.png'] = 'image/png'
        self.types['.txt'] = 'text/plain'
        self.types['.html'] = 'text/html'
        self.file_dir = 'web-files'
        if not os.path.exists(self.file_dir):
            os.makedirs(self.file_dir)

    def response(self, kode=404, message='Not Found', messagebody=b'', headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = [
            f"HTTP/1.1 {kode} {message}\r\n",
            f"Date: {tanggal}\r\n",
            "Connection: close\r\n",
            "Server: myserver/1.0\r\n",
            f"Content-Length: {len(messagebody)}\r\n"
        ]
        for kk, vv in headers.items():
            resp.append(f"{kk}: {vv}\r\n")
        resp.append("\r\n")

        response_headers = "".join(resp)
        
        if isinstance(messagebody, str):
            messagebody = messagebody.encode()

        return response_headers.encode() + messagebody

    def proses(self, data):
        parts = data.split("\r\n\r\n", 1)
        headers_raw = parts[0]
        body = parts[1] if len(parts) > 1 else ''

        requests = headers_raw.split("\r\n")
        baris = requests[0]
        
        all_headers = {}
        for req in requests[1:]:
            if ':' in req:
                key, value = req.split(':', 1)
                all_headers[key.strip()] = value.strip()
        
        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            object_address = j[1].strip()

            if method == 'GET':
                return self.http_get(object_address)
            elif method == 'POST':
                if object_address == '/upload':
                    return self.http_post(all_headers, body)
                else:
                    return self.response(404, 'Not Found', b'POST requests only allowed at /upload')
            elif method == 'DELETE':
                return self.http_delete(object_address)
            else:
                return self.response(405, 'Method Not Allowed', b'Method Not Allowed')
        except IndexError:
            return self.response(400, 'Bad Request', b'Bad Request')

    def http_get(self, object_address):
        if object_address == '/':
            return self.get_file_list()

        file_path = os.path.join(self.file_dir, object_address.strip('/'))
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as fp:
                isi = fp.read()
            fext = os.path.splitext(file_path)[1].lower()
            content_type = self.types.get(fext, 'application/octet-stream')
            return self.response(200, 'OK', isi, {'Content-Type': content_type})
        
        return self.response(404, 'Not Found', b'File or directory not found')

    def get_file_list(self):
        files = os.listdir(self.file_dir)
        file_list_html = "".join(f"<li>{f}</li>" for f in files)

        html_content = f"""
        <html>
            <head><title>File Server</title></head>
            <body>
                <h2>Upload File</h2>
                <form action="/upload" method="POST" enctype="multipart/form-data">
                    <input type="file" name="filetoupload"><br><br>
                    <input type="submit" value="Upload">
                </form>
                <hr>
                <h2>File List</h2>
                <ul>{file_list_html}</ul>
            </body>
        </html>
        """
        return self.response(200, 'OK', html_content, {'Content-Type': 'text/html'})

    def http_post(self, headers, body):
        content_type = headers.get('Content-Type', '')
        if 'multipart/form-data' in content_type:
            try:
                boundary = content_type.split('boundary=')[1]
                parts = body.split('--' + boundary)
                for part in parts:
                    if 'Content-Disposition: form-data; name="filetoupload"' in part:
                        filename_match = re.search(r'filename="(.+?)"', part)
                        if not filename_match: continue
                        filename = filename_match.group(1)
                        
                        file_content_parts = part.split('\r\n\r\n', 1)
                        if len(file_content_parts) > 1:
                            file_data = file_content_parts[1].rstrip('\r\n--')
                            filepath = os.path.join(self.file_dir, os.path.basename(filename))
                            with open(filepath, 'wb') as f:
                                f.write(file_data.encode('latin-1'))
                            return self.response(303, 'See Other', b'', {'Location': '/'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', b'Failed to process upload')
        
        return self.response(400, 'Bad Request', b'Unsupported POST request')

    def http_delete(self, object_address):
        if not object_address.startswith('/delete/'):
            return self.response(400, 'Bad Request', b'Invalid DELETE path')
            
        filename = object_address.split('/delete/', 1)[1]
        if not filename:
            return self.response(400, 'Bad Request', b'Filename not specified')

        file_path = os.path.join(self.file_dir, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return self.response(200, 'OK', b'File deleted successfully')
            except OSError as e:
                return self.response(500, 'Internal Server Error', b'Could not delete file')
        else:
            return self.response(404, 'Not Found', b'File not found for deletion')