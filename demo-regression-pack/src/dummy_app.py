from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

PRODUCTS = ["Widget Pro", "Widget Mini", "Gadget X"]


@app.get("/login", response_class=HTMLResponse)
async def login_get(error: str = ""):
    err_div = f'<div id="error-msg" style="color:red">{error}</div>' if error else ''
    return f'''
    <html><body>
        <h1>Login</h1>
        {err_div}
        <form method="post" action="/login">
            <input type="text" id="email" name="email" placeholder="Email" />
            <input type="password" id="password" name="password" placeholder="Password" />
            <button type="submit" id="login-button">Login</button>
        </form>
    </body></html>
    '''


@app.post("/login")
async def login_post(email: str = Form(...), password: str = Form(...)):
    if email == "demo@example.com" and password == "correct-password":
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login?error=Invalid+credentials", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return "<html><body><h1 id='welcome'>Dashboard</h1></body></html>"


@app.get("/search", response_class=HTMLResponse)
async def search(q: str = ""):
    if q:
        matches = [p for p in PRODUCTS if q.lower() in p.lower()]
        results_text = ", ".join(matches) if matches else "No results found"
    else:
        results_text = ""
    return f'''
    <html><body>
        <h1>Product Search</h1>
        <form method="get" action="/search">
            <input type="text" id="query" name="q" value="{q}" />
            <button type="submit" id="search-button">Search</button>
        </form>
        <div id="results">{results_text}</div>
    </body></html>
    '''


@app.get("/contact", response_class=HTMLResponse)
async def contact_get():
    return '''
    <html><body>
        <h1>Contact Us</h1>
        <form method="post" action="/contact">
            <input type="text" id="name" name="name" placeholder="Name" />
            <textarea id="message" name="message" placeholder="Message"></textarea>
            <button type="submit" id="submit-button">Submit</button>
        </form>
    </body></html>
    '''


@app.post("/contact", response_class=HTMLResponse)
async def contact_post(name: str = Form(...), message: str = Form(...)):
    return f'''
    <html><body>
        <h1>Contact Us</h1>
        <div id="success-msg">Thank you, {name}! Your message has been received.</div>
    </body></html>
    '''


@app.get("/api/health")
async def health():
    return {"status": "ok"}
