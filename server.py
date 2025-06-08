import os
import io
import qrcode
import subprocess
import aiofiles

from sanic import Sanic
from sanic import response

app = Sanic("fileshare")


def get_lan_address():
    result = subprocess.run(["./get_lan_address.sh"], stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8').strip()

def read_src_content():
    with open(__file__, 'r') as f:
        content = f.read()
        return content

def make_qr(content):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(content)
    with io.StringIO() as out:
        qr.print_ascii(out=out)
        out.seek(0)

        return out.read()



@app.route("/")
async def test(req):
    port = 1337 # TODO: parse from sanic somehow
    url = f"http://{get_lan_address()}:{port}/all"
    print(f"\nUrl: >>>{url}<<<\n")
    return response.text(f"{url}\n{make_qr(url)}")

    # this breaks with html for some reason
    # <span style="white-space: pre-wrap">{make_qr(url)}</span>

def human_size(bytes, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']):
    """ Returns a human readable string representation of bytes """
    return str(bytes) + units[0] if bytes < 1024 else human_size(bytes>>10, units[1:])

upload_dir = "./tmp"

def get_filesize(f):
    return human_size(os.path.getsize(f"{upload_dir}/{f}"))

@app.route("/all")
async def f(req):

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)
    files = "\n".join(
        f'<li><a href="/file?fname={f}">{f}</a> - {get_filesize(f)}</li>'
        for f in os.listdir(upload_dir)
        if not f.startswith(".")
    )
    return response.html(f"""
        <div style="margin: 1em;">
    <ul>
    {files}
    </ul>
    <style>
    input[type=button], input[type=submit], input[type=reset] {{
        background-color: #04AA6D;
        border: none;
        color: white;
        padding: 1em 2em;
        text-decoration: none;
        cursor: pointer;
        font-size: small;
    }}
    input[type="file"] {{
        display: none;
    }}
    .custom-file-upload {{
        background-color: #04AA6D;
        border: none;
        color: white;
        padding: 1em 2em;
        text-decoration: none;
        cursor: pointer;
        display: inline-block;
        font-size: small;
    }}
    input[type=submit]:disabled {{
        background-color: grey;
    }}
    </style>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <label class="custom-file-upload">
            <input type="file" name="file" id="file_inp">
            Select file
        </label>
        <span id="selected_file"></span>
        <input type="submit" value="Upload" id="submit_btn" disabled>
    </form>
    <script>
        document.getElementById("file_inp").onchange = function (event) {{
          document.getElementById("submit_btn").disabled = !event.target.value;
          document.getElementById("selected_file").textContent = document.getElementById("file_inp").files[0].name;
        }};
      </script>
    </div>
    """)


@app.route("/file")
async def get_file(request):
    fname = request.args.get('fname')
    return await response.file(f"{upload_dir}/{fname}")


@app.route("/upload", methods=["POST"])
async def upload(request):
    content = request.files.get("file").body
    fname = request.files["file"][0].name
    if not content:
        return response.redirect("/all")

    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)
    save_path = f"{upload_dir}/{fname}"
    while os.path.exists(save_path):
        save_path = f"{save_path}_1"
    async with aiofiles.open(save_path, 'wb') as f:
        await f.write(content)
    return response.redirect("/all")
