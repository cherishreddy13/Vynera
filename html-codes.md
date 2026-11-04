### HTML Codes

### Landing Page — `index.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>VYNERA AI – Your Companion</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300;1,500&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #666;
        --card: #0f0f0e;
        --border: #1e1e1c;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        font-family: "DM Sans", sans-serif;
        overflow-x: hidden;
      }

      /* Grain overlay */
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }

      /* Nav */
      nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 28px 48px;
        position: fixed;
        width: 100%;
        top: 0;
        z-index: 100;
        backdrop-filter: blur(6px);
      }
      .logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 28px;
        letter-spacing: 4px;
        color: var(--accent);
      }
      .nav-links {
        display: flex;
        gap: 12px;
      }
      .btn {
        font-family: "DM Sans", sans-serif;
        font-size: 13px;
        font-weight: 500;
        padding: 9px 22px;
        border-radius: 2px;
        cursor: pointer;
        text-decoration: none;
        letter-spacing: 0.5px;
        transition: all 0.2s;
      }
      .btn-outline {
        border: 1px solid var(--border);
        color: var(--text);
        background: transparent;
      }
      .btn-outline:hover {
        border-color: var(--accent);
        color: var(--accent);
      }
      .btn-solid {
        background: var(--accent);
        color: #060606;
        border: 1px solid var(--accent);
      }
      .btn-solid:hover {
        background: #d4ff20;
        box-shadow: 0 0 20px rgba(201, 255, 0, 0.3);
      }

      /* Hero */
      .hero {
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 140px 48px 80px;
        position: relative;
      }
      .hero-eyebrow {
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        letter-spacing: 3px;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 24px;
        opacity: 0;
        animation: fadeUp 0.8s 0.2s forwards;
      }
      h1 {
        font-family: "Bebas Neue", sans-serif;
        font-size: clamp(72px, 10vw, 160px);
        line-height: 0.9;
        letter-spacing: 2px;
        max-width: 900px;
        margin-bottom: 0;
        opacity: 0;
        animation: fadeUp 0.8s 0.4s forwards;
      }
      h1 span {
        color: var(--accent);
      }
      .hero-italic {
        font-family: "Cormorant Garamond", serif;
        font-style: italic;
        font-size: clamp(20px, 2.5vw, 32px);
        color: var(--muted);
        margin-top: 28px;
        max-width: 560px;
        line-height: 1.5;
        opacity: 0;
        animation: fadeUp 0.8s 0.6s forwards;
      }
      .hero-cta {
        display: flex;
        gap: 14px;
        margin-top: 48px;
        flex-wrap: wrap;
        opacity: 0;
        animation: fadeUp 0.8s 0.8s forwards;
      }
      .btn-lg {
        padding: 14px 36px;
        font-size: 14px;
        letter-spacing: 1px;
      }

      /* Philosophy strip */
      .philosophy {
        border-top: 1px solid var(--border);
        padding: 80px 48px;
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 48px;
      }
      .phil-item {
        opacity: 0;
        animation: fadeUp 0.8s forwards;
      }
      .phil-item:nth-child(1) {
        animation-delay: 0.1s;
      }
      .phil-item:nth-child(2) {
        animation-delay: 0.2s;
      }
      .phil-item:nth-child(3) {
        animation-delay: 0.3s;
      }
      .phil-item:nth-child(4) {
        animation-delay: 0.4s;
      }
      .phil-num {
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        color: var(--accent);
        letter-spacing: 2px;
        margin-bottom: 12px;
      }
      .phil-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 26px;
        letter-spacing: 1px;
        margin-bottom: 10px;
      }
      .phil-desc {
        font-size: 13px;
        color: var(--muted);
        line-height: 1.7;
      }

      /* Features */
      .features {
        padding: 80px 48px;
        border-top: 1px solid var(--border);
      }
      .section-label {
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        letter-spacing: 3px;
        color: var(--accent);
        margin-bottom: 40px;
      }
      .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1px;
        background: var(--border);
      }
      .feature-card {
        background: var(--bg);
        padding: 32px;
        transition: background 0.3s;
      }
      .feature-card:hover {
        background: var(--card);
      }
      .f-num {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        color: var(--muted);
        margin-bottom: 16px;
      }
      .f-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 22px;
        letter-spacing: 1px;
        margin-bottom: 8px;
      }
      .f-desc {
        font-size: 13px;
        color: var(--muted);
        line-height: 1.6;
      }

      /* Bottom CTA */
      .bottom-cta {
        padding: 120px 48px;
        text-align: center;
        border-top: 1px solid var(--border);
      }
      .bottom-cta h2 {
        font-family: "Bebas Neue", sans-serif;
        font-size: clamp(48px, 7vw, 100px);
        letter-spacing: 2px;
        margin-bottom: 12px;
      }
      .bottom-cta .sub {
        font-family: "Cormorant Garamond", serif;
        font-style: italic;
        font-size: 22px;
        color: var(--muted);
        margin-bottom: 40px;
      }

      /* Decorative accent line */
      .accent-line {
        width: 60px;
        height: 2px;
        background: var(--accent);
        margin: 0 auto 40px;
      }

      footer {
        border-top: 1px solid var(--border);
        padding: 24px 48px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 12px;
        color: var(--muted);
      }

      @keyframes fadeUp {
        from {
          opacity: 0;
          transform: translateY(24px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      /* Floating orb */
      .orb {
        position: fixed;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: radial-gradient(
          circle,
          rgba(201, 255, 0, 0.06) 0%,
          transparent 70%
        );
        top: -100px;
        right: -200px;
        pointer-events: none;
        animation: orbPulse 8s ease-in-out infinite;
      }
      @keyframes orbPulse {
        0%,
        100% {
          transform: scale(1);
        }
        50% {
          transform: scale(1.1);
        }
      }

      @media (max-width: 768px) {
        nav {
          padding: 20px 24px;
        }
        .hero {
          padding: 120px 24px 60px;
        }
        .philosophy,
        .features,
        .bottom-cta {
          padding: 60px 24px;
        }
        footer {
          flex-direction: column;
          gap: 8px;
          text-align: center;
        }
      }
    </style>
  </head>
  <body>
    <div class="orb"></div>

    <nav>
      <div class="logo">VYNERA</div>
      <div class="nav-links">
        <a href="/login" class="btn btn-outline">Login</a>
        <a href="/signup" class="btn btn-solid">Get Started</a>
      </div>
    </nav>

    <section class="hero">
      <div class="hero-eyebrow">// AI Companion System v1.0</div>
      <h1>Your mind<br />deserves a <span>companion.</span></h1>
      <p class="hero-italic">
        Psychologically grounded. Genuinely curious.<br />Always on your side.
      </p>
      <div class="hero-cta">
        <a href="/signup" class="btn btn-solid btn-lg">Begin Your Journey</a>
        <a href="#features" class="btn btn-outline btn-lg">Learn More</a>
      </div>
    </section>

    <section class="philosophy">
      <div class="phil-item">
        <div class="phil-num">01 // VALIDATE</div>
        <div class="phil-title">Feel Heard First</div>
        <p class="phil-desc">
          VYNERA always acknowledges your feelings before offering perspective.
          No toxic positivity. No dismissal.
        </p>
      </div>
      <div class="phil-item">
        <div class="phil-num">02 // REMEMBER</div>
        <div class="phil-title">Knows You</div>
        <p class="phil-desc">
          Long-term memory means VYNERA grows with you – recalling your goals,
          relationships, and stories.
        </p>
      </div>
      <div class="phil-item">
        <div class="phil-num">03 // ADAPT</div>
        <div class="phil-title">Learns Nightly</div>
        <p class="phil-desc">
          Your feedback shapes future conversations. VYNERA fine-tunes itself to
          serve you better, every day.
        </p>
      </div>
      <div class="phil-item">
        <div class="phil-num">04 // PRIVATE</div>
        <div class="phil-title">Zero External APIs</div>
        <p class="phil-desc">
          Everything runs on your own infrastructure. No data leaves your
          server. Your thoughts stay yours.
        </p>
      </div>
    </section>

    <section class="features" id="features">
      <div class="section-label">// Core Capabilities</div>
      <div class="feature-grid">
        <div class="feature-card">
          <div class="f-num">001</div>
          <div class="f-title">Emotion Recognition</div>
          <p class="f-desc">
            Detects happiness, sadness, anxiety, anger and adapts tone in
            real-time.
          </p>
        </div>
        <div class="feature-card">
          <div class="f-num">002</div>
          <div class="f-title">Goal & Habit Tracking</div>
          <p class="f-desc">
            Set goals, break them into steps, and celebrate every milestone.
          </p>
        </div>
        <div class="feature-card">
          <div class="f-num">003</div>
          <div class="f-title">Journal Mode</div>
          <p class="f-desc">
            Reflection prompts and pattern insights from your journaling
            history.
          </p>
        </div>
        <div class="feature-card">
          <div class="f-num">004</div>
          <div class="f-title">Logical Reasoning</div>
          <p class="f-desc">
            Pros & cons analysis, step-by-step breakdowns for complex decisions.
          </p>
        </div>
        <div class="feature-card">
          <div class="f-num">005</div>
          <div class="f-title">Crisis Safety Net</div>
          <p class="f-desc">
            Detects distress signals instantly and provides compassionate
            support with real resources.
          </p>
        </div>
        <div class="feature-card">
          <div class="f-num">006</div>
          <div class="f-title">Mood Dashboard</div>
          <p class="f-desc">
            Visual trends of your emotional wellbeing across conversations over
            time.
          </p>
        </div>
      </div>
    </section>

    <section class="bottom-cta">
      <div class="accent-line"></div>
      <h2>Ready to talk?</h2>
      <p class="sub">
        No judgment. No algorithms selling your data. Just a conversation.
      </p>
      <a href="/signup" class="btn btn-solid btn-lg">Create Your Account</a>
    </section>

    <footer>
      <span class="logo" style="font-size: 16px">VYNERA</span>
      <span>Built with care. Running on your infrastructure.</span>
      <span
        style="
          font-family: &quot;JetBrains Mono&quot;, monospace;
          font-size: 10px;
        "
        >v1.0.0</span
      >
    </footer>
  </body>
</html>

---

### Login Page — `login.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Login – VYNERA AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #666;
        --card: #0f0f0e;
        --border: #1e1e1c;
        --input: #0a0a09;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        font-family: "DM Sans", sans-serif;
        display: flex;
        flex-direction: column;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }

      nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 24px 48px;
      }
      .logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 24px;
        letter-spacing: 4px;
        color: var(--accent);
        text-decoration: none;
      }
      .nav-link {
        font-size: 13px;
        color: var(--muted);
        text-decoration: none;
        transition: color 0.2s;
      }
      .nav-link:hover {
        color: var(--accent);
      }

      main {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 24px;
      }
      .card {
        width: 100%;
        max-width: 420px;
      }
      .card-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 3px;
        color: var(--accent);
        margin-bottom: 16px;
      }
      .card-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 52px;
        letter-spacing: 2px;
        margin-bottom: 6px;
      }
      .card-sub {
        font-family: "Cormorant Garamond", serif;
        font-style: italic;
        font-size: 16px;
        color: var(--muted);
        margin-bottom: 40px;
      }

      .form-group {
        margin-bottom: 20px;
      }
      label {
        display: block;
        font-size: 11px;
        font-family: "JetBrains Mono", monospace;
        letter-spacing: 1.5px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 8px;
      }
      input {
        width: 100%;
        background: var(--input);
        border: 1px solid var(--border);
        color: var(--text);
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        outline: none;
        border-radius: 2px;
        transition: border-color 0.2s;
      }
      input:focus {
        border-color: var(--accent);
      }
      input::placeholder {
        color: #333;
      }

      .btn {
        width: 100%;
        background: var(--accent);
        color: #060606;
        font-family: "DM Sans", sans-serif;
        font-weight: 500;
        font-size: 14px;
        letter-spacing: 1px;
        padding: 14px;
        border: none;
        border-radius: 2px;
        cursor: pointer;
        transition: all 0.2s;
        margin-top: 8px;
      }
      .btn:hover {
        background: #d4ff20;
        box-shadow: 0 0 24px rgba(201, 255, 0, 0.25);
      }

      .error-msg {
        background: rgba(255, 80, 80, 0.08);
        border: 1px solid rgba(255, 80, 80, 0.3);
        color: #ff6060;
        font-size: 13px;
        padding: 12px 16px;
        border-radius: 2px;
        margin-bottom: 16px;
        display: none;
      }
      .error-msg.show {
        display: block;
      }

      .divider {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 24px 0;
      }
      .divider span {
        font-size: 12px;
        color: var(--muted);
      }
      .divider::before,
      .divider::after {
        content: "";
        flex: 1;
        height: 1px;
        background: var(--border);
      }

      .link-row {
        text-align: center;
        font-size: 13px;
        color: var(--muted);
      }
      .link-row a {
        color: var(--accent);
        text-decoration: none;
      }
      .link-row a:hover {
        text-decoration: underline;
      }

      .forgot {
        display: block;
        text-align: right;
        font-size: 11px;
        color: var(--muted);
        text-decoration: none;
        margin-top: 4px;
        transition: color 0.2s;
      }
      .forgot:hover {
        color: var(--accent);
      }

      @media (max-width: 480px) {
        nav {
          padding: 20px 20px;
        }
        .card-title {
          font-size: 40px;
        }
      }
    </style>
  </head>
  <body>
    <nav>
      <a href="/" class="logo">VYNERA</a>
      <a href="/signup" class="nav-link">No account? Sign up →</a>
    </nav>
    <main>
      <div class="card">
        <div class="card-tag">// Returning User</div>
        <h1 class="card-title">Welcome<br />Back.</h1>
        <p class="card-sub">Your companion is waiting.</p>

        <div class="error-msg" id="errorMsg">
          Invalid credentials. Please try again.
        </div>

        <form id="loginForm">
          <div class="form-group">
            <label>Email or Username</label>
            <input
              type="text"
              id="identifier"
              name="identifier"
              placeholder="you@example.com"
              required
              autocomplete="username"
            />
          </div>
          <div class="form-group">
            <label>Password</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="••••••••"
              required
              autocomplete="current-password"
            />
            <a href="#" class="forgot">Forgot password?</a>
          </div>
          <button type="submit" class="btn" id="loginBtn">Login</button>
        </form>

        <div class="divider"><span>or</span></div>
        <div class="link-row">
          New here? <a href="/signup">Create your account</a>
        </div>
      </div>
    </main>

    <script>
      const form = document.getElementById("loginForm");
      const btn = document.getElementById("loginBtn");
      const errorMsg = document.getElementById("errorMsg");

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorMsg.classList.remove("show");
        btn.textContent = "Logging in...";
        btn.disabled = true;

        const identifier = document.getElementById("identifier").value.trim();
        const password = document.getElementById("password").value;

        try {
          const resp = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ identifier, password }),
          });
          const data = await resp.json();
          if (resp.ok && data.access_token) {
            localStorage.setItem("vynera_token", data.access_token);
            localStorage.setItem("vynera_user", JSON.stringify(data.user));
            window.location.href = "/dashboard";
          } else {
            errorMsg.textContent = data.detail || "Invalid credentials.";
            errorMsg.classList.add("show");
          }
        } catch {
          errorMsg.textContent = "Network error. Please try again.";
          errorMsg.classList.add("show");
        } finally {
          btn.textContent = "Login";
          btn.disabled = false;
        }
      });
    </script>
  </body>
</html>


---

### Signup Page — `signup.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sign Up – VYNERA AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #666;
        --card: #0f0f0e;
        --border: #1e1e1c;
        --input: #0a0a09;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        font-family: "DM Sans", sans-serif;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }

      nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 24px 48px;
      }
      .logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 24px;
        letter-spacing: 4px;
        color: var(--accent);
        text-decoration: none;
      }
      .nav-link {
        font-size: 13px;
        color: var(--muted);
        text-decoration: none;
        transition: color 0.2s;
      }
      .nav-link:hover {
        color: var(--accent);
      }

      .page-wrap {
        max-width: 680px;
        margin: 0 auto;
        padding: 20px 24px 80px;
      }
      .step-indicator {
        display: flex;
        gap: 8px;
        margin-bottom: 40px;
      }
      .step-dot {
        width: 24px;
        height: 3px;
        background: var(--border);
        border-radius: 2px;
        transition: background 0.3s;
      }
      .step-dot.active {
        background: var(--accent);
      }
      .step-dot.done {
        background: #4a6a00;
      }

      .step {
        display: none;
      }
      .step.active {
        display: block;
      }

      .step-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 3px;
        color: var(--accent);
        margin-bottom: 12px;
      }
      .step-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 44px;
        letter-spacing: 2px;
        margin-bottom: 6px;
      }
      .step-sub {
        font-family: "Cormorant Garamond", serif;
        font-style: italic;
        font-size: 16px;
        color: var(--muted);
        margin-bottom: 36px;
      }

      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 0;
      }
      .form-group {
        margin-bottom: 20px;
      }
      label {
        display: block;
        font-size: 11px;
        font-family: "JetBrains Mono", monospace;
        letter-spacing: 1.5px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 8px;
      }
      input,
      select {
        width: 100%;
        background: var(--input);
        border: 1px solid var(--border);
        color: var(--text);
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        outline: none;
        border-radius: 2px;
        transition: border-color 0.2s;
        -webkit-appearance: none;
      }
      input:focus,
      select:focus {
        border-color: var(--accent);
      }
      input::placeholder {
        color: #333;
      }
      select option {
        background: var(--bg);
      }

      .note {
        font-size: 12px;
        color: var(--muted);
        margin-top: 4px;
        line-height: 1.4;
      }

      /* Personality cards */
      .p-question {
        margin-bottom: 28px;
      }
      .p-question p {
        font-size: 14px;
        margin-bottom: 12px;
        color: var(--text);
      }
      .p-options {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .p-option {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border: 1px solid var(--border);
        border-radius: 2px;
        cursor: pointer;
        transition: all 0.2s;
      }
      .p-option:hover {
        border-color: var(--accent);
      }
      .p-option input[type="radio"] {
        display: none;
      }
      .p-option.selected {
        border-color: var(--accent);
        background: rgba(201, 255, 0, 0.05);
      }
      .p-option span {
        font-size: 13px;
      }
      .p-dot {
        width: 14px;
        height: 14px;
        border: 1.5px solid var(--muted);
        border-radius: 50%;
        flex-shrink: 0;
        transition: all 0.2s;
      }
      .p-option.selected .p-dot {
        border-color: var(--accent);
        background: var(--accent);
      }

      .btn-row {
        display: flex;
        gap: 12px;
        margin-top: 32px;
      }
      .btn {
        font-family: "DM Sans", sans-serif;
        font-weight: 500;
        font-size: 14px;
        letter-spacing: 0.5px;
        padding: 13px 28px;
        border-radius: 2px;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
      }
      .btn-solid {
        background: var(--accent);
        color: #060606;
      }
      .btn-solid:hover {
        background: #d4ff20;
        box-shadow: 0 0 20px rgba(201, 255, 0, 0.2);
      }
      .btn-ghost {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
      }
      .btn-ghost:hover {
        border-color: var(--muted);
        color: var(--text);
      }
      .btn-full {
        width: 100%;
      }

      .error-msg {
        background: rgba(255, 80, 80, 0.08);
        border: 1px solid rgba(255, 80, 80, 0.3);
        color: #ff6060;
        font-size: 13px;
        padding: 12px 16px;
        border-radius: 2px;
        margin-bottom: 16px;
        display: none;
      }
      .error-msg.show {
        display: block;
      }

      @media (max-width: 600px) {
        .form-row {
          grid-template-columns: 1fr;
        }
        .step-title {
          font-size: 36px;
        }
        nav {
          padding: 20px 20px;
        }
      }
    </style>
  </head>
  <body>
    <nav>
      <a href="/" class="logo">VYNERA</a>
      <a href="/login" class="nav-link">Already a member? Login →</a>
    </nav>
    <div class="page-wrap">
      <div class="step-indicator">
        <div class="step-dot active" id="dot0"></div>
        <div class="step-dot" id="dot1"></div>
        <div class="step-dot" id="dot2"></div>
      </div>

      <div class="error-msg" id="errorMsg"></div>

      <!-- Step 1: Account Info -->
      <div class="step active" id="step0">
        <div class="step-tag">// Step 1 of 3</div>
        <h2 class="step-title">Who Are You?</h2>
        <p class="step-sub">Let's set up your account.</p>
        <div class="form-row">
          <div class="form-group">
            <label>Full Name</label
            ><input type="text" id="name" placeholder="Alex Chen" required />
          </div>
          <div class="form-group">
            <label>Age</label
            ><input
              type="number"
              id="age"
              placeholder="24"
              min="13"
              max="120"
              required
            />
          </div>
        </div>
        <div id="parentPhoneWrap" class="form-group" style="display: none">
          <label>Parent / Guardian Phone</label>
          <input type="tel" id="parentPhone" placeholder="+91 99999 99999" />
          <div class="note">Required for users under 18.</div>
        </div>
        <div class="form-group">
          <label>Email</label
          ><input
            type="email"
            id="email"
            placeholder="alex@example.com"
            required
          />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Username</label
            ><input type="text" id="username" placeholder="alexc" required />
          </div>
          <div class="form-group">
            <label>Password</label
            ><input
              type="password"
              id="password"
              placeholder="Min 8 characters"
              required
            />
          </div>
        </div>
        <div class="btn-row">
          <button class="btn btn-solid" onclick="nextStep(0)">
            Continue →
          </button>
        </div>
      </div>

      <!-- Step 2: Personality -->
      <div class="step" id="step1">
        <div class="step-tag">// Step 2 of 3</div>
        <h2 class="step-title">Your Inner World</h2>
        <p class="step-sub">Five questions to calibrate your companion.</p>

        <div class="p-question">
          <p>1. When something goes wrong, I usually…</p>
          <div class="p-options" data-q="q1">
            <label class="p-option"
              ><input type="radio" name="q1" value="analytical" />
              <div class="p-dot"></div>
              <span>Analyse the situation step-by-step</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q1" value="emotional" />
              <div class="p-dot"></div>
              <span>Need to process my feelings first</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q1" value="action" />
              <div class="p-dot"></div>
              <span>Jump into fixing it immediately</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q1" value="social" />
              <div class="p-dot"></div>
              <span>Talk to someone about it</span></label
            >
          </div>
        </div>

        <div class="p-question">
          <p>2. My communication style is mostly…</p>
          <div class="p-options" data-q="q2">
            <label class="p-option"
              ><input type="radio" name="q2" value="direct" />
              <div class="p-dot"></div>
              <span>Direct and to the point</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q2" value="thoughtful" />
              <div class="p-dot"></div>
              <span>Thoughtful and considered</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q2" value="warm" />
              <div class="p-dot"></div>
              <span>Warm and emotionally expressive</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q2" value="playful" />
              <div class="p-dot"></div>
              <span>Light and a bit humorous</span></label
            >
          </div>
        </div>

        <div class="p-question">
          <p>3. I usually feel most like myself when I am…</p>
          <div class="p-options" data-q="q3">
            <label class="p-option"
              ><input type="radio" name="q3" value="creating" />
              <div class="p-dot"></div>
              <span>Creating or building something</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q3" value="connecting" />
              <div class="p-dot"></div>
              <span>Connecting deeply with others</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q3" value="learning" />
              <div class="p-dot"></div>
              <span>Learning or exploring ideas</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q3" value="resting" />
              <div class="p-dot"></div>
              <span>Resting and recharging alone</span></label
            >
          </div>
        </div>

        <div class="p-question">
          <p>4. When I get advice, I prefer it to be…</p>
          <div class="p-options" data-q="q4">
            <label class="p-option"
              ><input type="radio" name="q4" value="encouraging" />
              <div class="p-dot"></div>
              <span>Encouraging and motivating</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q4" value="honest" />
              <div class="p-dot"></div>
              <span>Honest even if it's hard to hear</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q4" value="structured" />
              <div class="p-dot"></div>
              <span>Clear and structured with steps</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q4" value="open" />
              <div class="p-dot"></div>
              <span>Open-ended, let me figure it out</span></label
            >
          </div>
        </div>

        <div class="p-question">
          <p>5. My ideal companion bot would be…</p>
          <div class="p-options" data-q="q5">
            <label class="p-option"
              ><input type="radio" name="q5" value="wise" />
              <div class="p-dot"></div>
              <span>Wise and philosophical</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q5" value="playful" />
              <div class="p-dot"></div>
              <span>Playful and light-hearted</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q5" value="analytical" />
              <div class="p-dot"></div>
              <span>Analytical and problem-solving</span></label
            >
            <label class="p-option"
              ><input type="radio" name="q5" value="encouraging" />
              <div class="p-dot"></div>
              <span>Warm and encouraging</span></label
            >
          </div>
        </div>

        <div class="btn-row">
          <button class="btn btn-ghost" onclick="prevStep(1)">← Back</button>
          <button class="btn btn-solid" onclick="nextStep(1)">
            Continue →
          </button>
        </div>
      </div>

      <!-- Step 3: Confirm -->
      <div class="step" id="step2">
        <div class="step-tag">// Step 3 of 3</div>
        <h2 class="step-title">Almost There.</h2>
        <p class="step-sub">Review your choices and create your companion.</p>
        <div
          id="summaryBox"
          style="
            border: 1px solid var(--border);
            padding: 24px;
            border-radius: 2px;
            margin-bottom: 28px;
            font-size: 13px;
            line-height: 2;
            color: var(--muted);
          "
        ></div>
        <div class="form-group">
          <label>Choose Your Bot Personality</label>
          <select id="personality">
            <option value="encouraging">
              Encouraging – warm, celebratory, motivating
            </option>
            <option value="analytical">
              Analytical – logical, structured, precise
            </option>
            <option value="playful">Playful – light, witty, fun</option>
            <option value="wise">
              Wise – thoughtful, philosophical, measured
            </option>
          </select>
        </div>
        <div class="btn-row">
          <button class="btn btn-ghost" onclick="prevStep(2)">← Back</button>
          <button
            class="btn btn-solid btn-full"
            id="submitBtn"
            onclick="submitForm()"
          >
            Create My Companion
          </button>
        </div>
      </div>
    </div>

    <script>
      let currentStep = 0;
      const dots = [
        document.getElementById("dot0"),
        document.getElementById("dot1"),
        document.getElementById("dot2"),
      ];
      const steps = [
        document.getElementById("step0"),
        document.getElementById("step1"),
        document.getElementById("step2"),
      ];
      const errorMsg = document.getElementById("errorMsg");

      // Age-gate parent phone
      document.getElementById("age").addEventListener("input", function () {
        document.getElementById("parentPhoneWrap").style.display =
          parseInt(this.value) < 18 ? "block" : "none";
      });

      // Radio styling
      document.querySelectorAll(".p-option").forEach((opt) => {
        opt.addEventListener("click", () => {
          const name = opt.querySelector("input").name;
          document
            .querySelectorAll(`input[name="${name}"]`)
            .forEach((r) =>
              r.closest(".p-option").classList.remove("selected"),
            );
          opt.classList.add("selected");
          opt.querySelector("input").checked = true;
        });
      });

      function showError(msg) {
        errorMsg.textContent = msg;
        errorMsg.classList.add("show");
        errorMsg.scrollIntoView({ behavior: "smooth" });
      }
      function clearError() {
        errorMsg.classList.remove("show");
      }

      function nextStep(from) {
        clearError();
        if (from === 0) {
          const name = document.getElementById("name").value.trim();
          const age = parseInt(document.getElementById("age").value);
          const email = document.getElementById("email").value.trim();
          const username = document.getElementById("username").value.trim();
          const password = document.getElementById("password").value;
          if (!name || !age || !email || !username || !password)
            return showError("Please fill all required fields.");
          if (password.length < 8)
            return showError("Password must be at least 8 characters.");
          if (age < 13)
            return showError("You must be at least 13 to use VYNERA.");
          if (age < 18 && !document.getElementById("parentPhone").value.trim())
            return showError(
              "Parent/guardian phone required for users under 18.",
            );
        }
        if (from === 1) {
          const qs = ["q1", "q2", "q3", "q4", "q5"];
          for (const q of qs) {
            if (!document.querySelector(`input[name="${q}"]:checked`))
              return showError("Please answer all 5 questions.");
          }
          buildSummary();
        }
        steps[from].classList.remove("active");
        dots[from].classList.remove("active");
        dots[from].classList.add("done");
        currentStep = from + 1;
        steps[currentStep].classList.add("active");
        dots[currentStep].classList.add("active");
        window.scrollTo(0, 0);
      }

      function prevStep(from) {
        steps[from].classList.remove("active");
        dots[from].classList.remove("active");
        currentStep = from - 1;
        steps[currentStep].classList.add("active");
        dots[currentStep].classList.remove("done");
        dots[currentStep].classList.add("active");
        window.scrollTo(0, 0);
      }

      function buildSummary() {
        const name = document.getElementById("name").value.trim();
        const answers = {};
        ["q1", "q2", "q3", "q4", "q5"].forEach((q) => {
          const el = document.querySelector(`input[name="${q}"]:checked`);
          if (el) answers[q] = el.value;
        });
        document.getElementById("summaryBox").innerHTML = `
    <strong style="color:var(--text)">Name:</strong> ${name}<br/>
    <strong style="color:var(--text)">Response style:</strong> ${answers.q1 || "–"}<br/>
    <strong style="color:var(--text)">Communication:</strong> ${answers.q2 || "–"}<br/>
    <strong style="color:var(--text)">Recharge type:</strong> ${answers.q3 || "–"}<br/>
    <strong style="color:var(--text)">Advice preference:</strong> ${answers.q4 || "–"}<br/>
    <strong style="color:var(--text)">Bot personality:</strong> ${answers.q5 || "–"}
  `;
        // Auto-select personality from q5
        const q5 = document.querySelector('input[name="q5"]:checked');
        if (q5) document.getElementById("personality").value = q5.value;
      }

      async function submitForm() {
        clearError();
        const btn = document.getElementById("submitBtn");
        btn.textContent = "Creating...";
        btn.disabled = true;

        const getAnswers = () => {
          const obj = {};
          ["q1", "q2", "q3", "q4", "q5"].forEach((q) => {
            const el = document.querySelector(`input[name="${q}"]:checked`);
            obj[q] = el ? el.value : "";
          });
          return obj;
        };

        const payload = {
          name: document.getElementById("name").value.trim(),
          age: parseInt(document.getElementById("age").value),
          email: document.getElementById("email").value.trim().toLowerCase(),
          username: document
            .getElementById("username")
            .value.trim()
            .toLowerCase(),
          password: document.getElementById("password").value,
          parent_phone:
            document.getElementById("parentPhone").value.trim() || null,
          personality: document.getElementById("personality").value,
          personality_answers: getAnswers(),
        };

        try {
          const resp = await fetch("/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
          });
          const data = await resp.json();
          if (resp.ok) {
            localStorage.setItem("vynera_token", data.access_token);
            localStorage.setItem("vynera_user", JSON.stringify(data.user));
            window.location.href = "/chat";
          } else {
            showError(data.detail || "Registration failed. Please try again.");
          }
        } catch {
          showError("Network error. Please try again.");
        } finally {
          btn.textContent = "Create My Companion";
          btn.disabled = false;
        }
      }
    </script>
  </body>
</html>


---

### Dashboard Page — `dashboard.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Dashboard – VYNERA AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #666;
        --card: #0c0c0b;
        --border: #1e1e1c;
        --input: #0a0a09;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        font-family: "DM Sans", sans-serif;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }

      /* Sidebar */
      .layout {
        display: flex;
        min-height: 100vh;
      }
      .sidebar {
        width: 220px;
        border-right: 1px solid var(--border);
        padding: 28px 0;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
      }
      .sidebar-logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 22px;
        letter-spacing: 4px;
        color: var(--accent);
        padding: 0 24px;
        margin-bottom: 40px;
      }
      .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 24px;
        font-size: 13px;
        color: var(--muted);
        text-decoration: none;
        transition: all 0.2s;
        border-left: 2px solid transparent;
      }
      .nav-item:hover,
      .nav-item.active {
        color: var(--text);
        border-left-color: var(--accent);
        background: rgba(201, 255, 0, 0.04);
      }
      .nav-item.active {
        color: var(--accent);
      }
      .nav-icon {
        font-size: 15px;
        width: 18px;
        text-align: center;
      }
      .sidebar-bottom {
        margin-top: auto;
        padding: 0 24px;
      }
      .user-chip {
        background: var(--card);
        border: 1px solid var(--border);
        padding: 12px;
        border-radius: 2px;
        font-size: 12px;
      }
      .user-name {
        color: var(--text);
        font-weight: 500;
      }
      .user-role {
        color: var(--muted);
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
      }

      /* Main */
      .main {
        flex: 1;
        padding: 40px 48px;
        overflow-y: auto;
      }
      .page-header {
        margin-bottom: 40px;
      }
      .page-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 3px;
        color: var(--accent);
        margin-bottom: 8px;
      }
      .page-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 48px;
        letter-spacing: 2px;
      }
      .page-sub {
        font-family: "Cormorant Garamond", serif;
        font-style: italic;
        color: var(--muted);
        font-size: 16px;
        margin-top: 4px;
      }

      /* Stats row */
      .stats-row {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1px;
        background: var(--border);
        margin-bottom: 40px;
      }
      .stat-card {
        background: var(--bg);
        padding: 28px 24px;
      }
      .stat-num {
        font-family: "Bebas Neue", sans-serif;
        font-size: 48px;
        color: var(--accent);
        line-height: 1;
      }
      .stat-label {
        font-size: 12px;
        color: var(--muted);
        margin-top: 4px;
        font-family: "JetBrains Mono", monospace;
        letter-spacing: 1px;
      }

      /* Grid */
      .content-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 24px;
      }
      .card {
        background: var(--card);
        border: 1px solid var(--border);
        padding: 28px;
      }
      .card-title {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 2px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 20px;
      }

      /* Chart */
      canvas {
        width: 100% !important;
      }
      .chart-wrap {
        position: relative;
        height: 200px;
      }

      /* Goal list */
      .goal-item {
        border-bottom: 1px solid var(--border);
        padding: 14px 0;
      }
      .goal-item:last-child {
        border-bottom: none;
      }
      .goal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
      }
      .goal-name {
        font-size: 13px;
        font-weight: 500;
      }
      .goal-pct {
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        color: var(--accent);
      }
      .progress-bar {
        height: 3px;
        background: var(--border);
        border-radius: 2px;
        overflow: hidden;
      }
      .progress-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 2px;
        transition: width 0.8s ease;
      }

      /* Memory chips */
      .memory-list {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      .memory-chip {
        background: var(--bg);
        border: 1px solid var(--border);
        padding: 10px 14px;
        border-radius: 2px;
        font-size: 12px;
      }
      .mem-key {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        color: var(--accent);
        margin-bottom: 2px;
      }
      .mem-val {
        color: var(--text);
      }

      /* CTA */
      .chat-cta {
        background: rgba(201, 255, 0, 0.05);
        border: 1px solid rgba(201, 255, 0, 0.2);
        padding: 28px;
        text-align: center;
        margin-top: 24px;
      }
      .chat-cta h3 {
        font-family: "Bebas Neue", sans-serif;
        font-size: 28px;
        letter-spacing: 1px;
        margin-bottom: 8px;
      }
      .chat-cta p {
        font-size: 13px;
        color: var(--muted);
        margin-bottom: 16px;
      }
      .btn {
        display: inline-block;
        background: var(--accent);
        color: #060606;
        font-weight: 500;
        font-size: 13px;
        padding: 11px 24px;
        border-radius: 2px;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s;
      }
      .btn:hover {
        background: #d4ff20;
      }

      @media (max-width: 900px) {
        .content-grid {
          grid-template-columns: 1fr;
        }
        .sidebar {
          display: none;
        }
        .main {
          padding: 24px;
        }
      }
    </style>
  </head>
  <body>
    <div class="layout">
      <aside class="sidebar">
        <div class="sidebar-logo">VYNERA</div>
        <a href="/dashboard" class="nav-item active"
          ><span class="nav-icon">◈</span>Dashboard</a
        >
        <a href="/chat" class="nav-item"><span class="nav-icon">◎</span>Chat</a>
        <a href="/history" class="nav-item"
          ><span class="nav-icon">◷</span>History</a
        >
        <a href="/profile" class="nav-item"
          ><span class="nav-icon">◉</span>Profile</a
        >
        <div class="sidebar-bottom">
          <div class="user-chip">
            <div class="user-name" id="sidebarName">–</div>
            <div class="user-role">// companion active</div>
          </div>
        </div>
      </aside>

      <main class="main">
        <div class="page-header">
          <div class="page-tag">// Overview</div>
          <h1 class="page-title">Your Dashboard</h1>
          <p class="page-sub" id="greetLine">Welcome back.</p>
        </div>

        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-num" id="statSessions">–</div>
            <div class="stat-label">Chat Sessions</div>
          </div>
          <div class="stat-card">
            <div class="stat-num" id="statActiveGoals">–</div>
            <div class="stat-label">Active Goals</div>
          </div>
          <div class="stat-card">
            <div class="stat-num" id="statDoneGoals">–</div>
            <div class="stat-label">Goals Completed</div>
          </div>
          <div class="stat-card">
            <div class="stat-num" id="statMemories">–</div>
            <div class="stat-label">Facts Remembered</div>
          </div>
        </div>

        <div class="content-grid">
          <div>
            <div class="card" style="margin-bottom: 24px">
              <div class="card-title">Mood Trend (Last 14 Sessions)</div>
              <div class="chart-wrap"><canvas id="moodChart"></canvas></div>
            </div>

            <div class="card">
              <div class="card-title">Active Goals</div>
              <div id="goalList">
                <div style="color: var(--muted); font-size: 13px">
                  No active goals yet. Start a chat to set one!
                </div>
              </div>
            </div>
          </div>

          <div>
            <div class="card" style="margin-bottom: 24px">
              <div class="card-title">What I Know About You</div>
              <div class="memory-list" id="memoryList">
                <div style="color: var(--muted); font-size: 13px">
                  Chat a bit and I'll start remembering things about you.
                </div>
              </div>
            </div>

            <div class="chat-cta">
              <h3>Ready to Talk?</h3>
              <p>Your companion is always here.</p>
              <a href="/chat" class="btn">Open Chat</a>
            </div>
          </div>
        </div>
      </main>
    </div>

    <script>
      // Inline minimal chart (no external lib dependency)
      function drawMoodChart(canvas, moodData) {
        const ctx = canvas.getContext("2d");
        const W = (canvas.width = canvas.offsetWidth * window.devicePixelRatio);
        const H = (canvas.height =
          canvas.offsetHeight * window.devicePixelRatio);
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        const w = canvas.offsetWidth,
          h = canvas.offsetHeight;

        if (!moodData || moodData.length < 2) {
          ctx.fillStyle = "#333";
          ctx.font = "13px DM Sans";
          ctx.textAlign = "center";
          ctx.fillText("Not enough data yet", w / 2, h / 2);
          return;
        }

        const PAD = { top: 16, right: 16, bottom: 32, left: 40 };
        const cw = w - PAD.left - PAD.right;
        const ch = h - PAD.top - PAD.bottom;

        // Grid lines
        ctx.strokeStyle = "#1e1e1c";
        ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
          const y = PAD.top + ch - (i / 4) * ch;
          ctx.beginPath();
          ctx.moveTo(PAD.left, y);
          ctx.lineTo(PAD.left + cw, y);
          ctx.stroke();
          ctx.fillStyle = "#444";
          ctx.font = "9px JetBrains Mono";
          ctx.textAlign = "right";
          const val = ((i / 4) * 2 - 1).toFixed(1);
          ctx.fillText(val, PAD.left - 6, y + 3);
        }

        // Zero line
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 1;
        const zeroY = PAD.top + ch / 2;
        ctx.beginPath();
        ctx.moveTo(PAD.left, zeroY);
        ctx.lineTo(PAD.left + cw, zeroY);
        ctx.stroke();

        const n = moodData.length;
        const pts = moodData.map((d, i) => ({
          x: PAD.left + (i / (n - 1)) * cw,
          y: PAD.top + ch / 2 - ((d.mood / 1) * ch) / 2,
        }));

        // Fill area
        const grad = ctx.createLinearGradient(0, PAD.top, 0, h);
        grad.addColorStop(0, "rgba(201,255,0,0.15)");
        grad.addColorStop(1, "rgba(201,255,0,0)");
        ctx.beginPath();
        ctx.moveTo(pts[0].x, zeroY);
        pts.forEach((p) => ctx.lineTo(p.x, p.y));
        ctx.lineTo(pts[n - 1].x, zeroY);
        ctx.closePath();
        ctx.fillStyle = grad;
        ctx.fill();

        // Line
        ctx.beginPath();
        ctx.strokeStyle = "#C9FF00";
        ctx.lineWidth = 2;
        pts.forEach((p, i) =>
          i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y),
        );
        ctx.stroke();

        // Dots
        pts.forEach((p) => {
          ctx.beginPath();
          ctx.arc(p.x, p.y, 3, 0, Math.PI * 2);
          ctx.fillStyle = "#C9FF00";
          ctx.fill();
        });

        // X labels
        ctx.fillStyle = "#444";
        ctx.font = "9px DM Sans";
        ctx.textAlign = "center";
        const step = Math.ceil(n / 5);
        moodData.forEach((d, i) => {
          if (i % step === 0) ctx.fillText(d.date || "", pts[i].x, h - 8);
        });
      }

      async function loadDashboard() {
        const token = localStorage.getItem("vynera_token");
        if (!token) {
          window.location.href = "/login";
          return;
        }

        const user = JSON.parse(localStorage.getItem("vynera_user") || "{}");
        document.getElementById("sidebarName").textContent =
          user.name || user.username || "–";
        const hour = new Date().getHours();
        const greeting =
          hour < 12
            ? "Good morning"
            : "hour<18"
              ? "Good afternoon"
              : "Good evening";
        document.getElementById("greetLine").textContent =
          `${hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening"}, ${user.name || "friend"}.`;

        try {
          const resp = await fetch("/api/stats", {
            headers: { Authorization: "Bearer " + token },
          });
          if (resp.status === 401) {
            window.location.href = "/login";
            return;
          }
          const data = await resp.json();

          document.getElementById("statSessions").textContent =
            data.total_sessions || 0;
          document.getElementById("statActiveGoals").textContent =
            data.active_goals || 0;
          document.getElementById("statDoneGoals").textContent =
            data.completed_goals || 0;
          document.getElementById("statMemories").textContent = (
            data.recent_memories || []
          ).length;

          // Mood chart
          const canvas = document.getElementById("moodChart");
          if (data.mood_trend && data.mood_trend.length) {
            drawMoodChart(canvas, data.mood_trend);
          } else {
            drawMoodChart(canvas, []);
          }

          // Goals
          const goalList = document.getElementById("goalList");
          if (data.goals && data.goals.length) {
            goalList.innerHTML = data.goals
              .map(
                (g) => `
        <div class="goal-item">
          <div class="goal-header">
            <span class="goal-name">${g.title}</span>
            <span class="goal-pct">${g.progress}%</span>
          </div>
          <div class="progress-bar"><div class="progress-fill" style="width:${g.progress}%"></div></div>
        </div>
      `,
              )
              .join("");
          }

          // Memories
          const memList = document.getElementById("memoryList");
          if (data.recent_memories && data.recent_memories.length) {
            memList.innerHTML = data.recent_memories
              .map(
                (m) => `
        <div class="memory-chip">
          <div class="mem-key">${(m.key || "").replace(/_/g, " ")}</div>
          <div class="mem-val">${m.value}</div>
        </div>
      `,
              )
              .join("");
          }
        } catch (e) {
          console.error(e);
        }
      }

      loadDashboard();
      window.addEventListener("resize", () => loadDashboard());
    </script>
  </body>
</html>


---

### Chat Page — `chat.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Chat – VYNERA AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #555;
        --card: #0c0c0b;
        --border: #1c1c1a;
        --user-bubble: #141412;
        --bot-bubble: #0c0c0b;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        height: 100vh;
        font-family: "DM Sans", sans-serif;
        overflow: hidden;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }

      .layout {
        display: flex;
        height: 100vh;
      }

      /* Sidebar */
      .sidebar {
        width: 280px;
        border-right: 1px solid var(--border);
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
      }
      .sidebar-top {
        padding: 20px;
        border-bottom: 1px solid var(--border);
      }
      .logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 20px;
        letter-spacing: 4px;
        color: var(--accent);
      }
      .sidebar-nav {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 12px 0;
      }
      .nav-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 20px;
        font-size: 12px;
        color: var(--muted);
        text-decoration: none;
        transition: all 0.2s;
        border-left: 2px solid transparent;
      }
      .nav-item:hover,
      .nav-item.active {
        color: var(--text);
        border-left-color: var(--accent);
      }

      .sidebar-section {
        padding: 16px 20px;
        border-top: 1px solid var(--border);
        flex: 1;
        overflow-y: auto;
      }
      .section-label {
        font-family: "JetBrains Mono", monospace;
        font-size: 9px;
        letter-spacing: 2px;
        color: var(--muted);
        margin-bottom: 12px;
        text-transform: uppercase;
      }

      /* Memory chips */
      .mem-chip {
        background: var(--card);
        border: 1px solid var(--border);
        padding: 8px 10px;
        margin-bottom: 6px;
        border-radius: 2px;
      }
      .mem-k {
        font-family: "JetBrains Mono", monospace;
        font-size: 9px;
        color: var(--accent);
      }
      .mem-v {
        font-size: 11px;
        color: var(--text);
        margin-top: 2px;
      }

      /* Goals */
      .goal-mini {
        border-bottom: 1px solid var(--border);
        padding: 8px 0;
      }
      .goal-mini:last-child {
        border-bottom: none;
      }
      .goal-mini-name {
        font-size: 11px;
        margin-bottom: 4px;
      }
      .mini-bar {
        height: 2px;
        background: var(--border);
        border-radius: 1px;
      }
      .mini-fill {
        height: 100%;
        background: var(--accent);
        border-radius: 1px;
      }

      .new-chat-btn {
        margin: 12px 20px;
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
        font-size: 12px;
        padding: 10px;
        cursor: pointer;
        transition: all 0.2s;
        border-radius: 2px;
        width: calc(100% - 40px);
      }
      .new-chat-btn:hover {
        border-color: var(--accent);
        color: var(--accent);
      }

      /* Chat area */
      .chat-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-width: 0;
      }
      .chat-header {
        padding: 16px 24px;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-shrink: 0;
      }
      .chat-header-name {
        font-family: "Bebas Neue", sans-serif;
        font-size: 22px;
        letter-spacing: 2px;
      }
      .chat-header-sub {
        font-size: 11px;
        color: var(--muted);
      }
      .emotion-badge {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        padding: 4px 10px;
        border: 1px solid var(--border);
        border-radius: 20px;
        color: var(--muted);
      }

      /* Messages */
      .messages {
        flex: 1;
        overflow-y: auto;
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        scroll-behavior: smooth;
      }
      .messages::-webkit-scrollbar {
        width: 4px;
      }
      .messages::-webkit-scrollbar-track {
        background: transparent;
      }
      .messages::-webkit-scrollbar-thumb {
        background: var(--border);
      }

      .msg-row {
        display: flex;
        align-items: flex-end;
        gap: 10px;
        animation: msgIn 0.3s ease;
      }
      .msg-row.user {
        flex-direction: row-reverse;
      }
      @keyframes msgIn {
        from {
          opacity: 0;
          transform: translateY(8px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-family: "JetBrains Mono", monospace;
      }
      .avatar.bot {
        background: rgba(201, 255, 0, 0.1);
        border: 1px solid rgba(201, 255, 0, 0.2);
        color: var(--accent);
      }
      .avatar.user {
        background: var(--card);
        border: 1px solid var(--border);
        color: var(--muted);
      }

      .bubble {
        max-width: 70%;
        padding: 14px 16px;
        border-radius: 2px;
        font-size: 14px;
        line-height: 1.65;
        position: relative;
      }
      .bubble.bot {
        background: var(--bot-bubble);
        border: 1px solid var(--border);
        border-radius: 2px 12px 12px 2px;
      }
      .bubble.user {
        background: var(--user-bubble);
        border: 1px solid var(--border);
        border-radius: 12px 2px 2px 12px;
        text-align: left;
      }

      .feedback-row {
        display: flex;
        gap: 8px;
        margin-top: 8px;
      }
      .fb-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
        font-size: 12px;
        padding: 4px 10px;
        cursor: pointer;
        border-radius: 20px;
        transition: all 0.2s;
      }
      .fb-btn:hover.up {
        border-color: #00cc66;
        color: #00cc66;
      }
      .fb-btn:hover.down {
        border-color: #cc4400;
        color: #cc4400;
      }
      .fb-btn.voted-up {
        border-color: #00cc66;
        color: #00cc66;
      }
      .fb-btn.voted-down {
        border-color: #cc4400;
        color: #cc4400;
      }

      /* Typing indicator */
      .typing-indicator {
        display: none;
        align-items: center;
        gap: 10px;
        padding: 0 0 8px;
      }
      .typing-indicator.show {
        display: flex;
      }
      .typing-dots {
        display: flex;
        gap: 4px;
      }
      .dot {
        width: 6px;
        height: 6px;
        background: var(--muted);
        border-radius: 50%;
        animation: dotBounce 1.2s infinite;
      }
      .dot:nth-child(2) {
        animation-delay: 0.2s;
      }
      .dot:nth-child(3) {
        animation-delay: 0.4s;
      }
      @keyframes dotBounce {
        0%,
        60%,
        100% {
          transform: translateY(0);
        }
        30% {
          transform: translateY(-6px);
        }
      }

      /* Input area */
      .input-area {
        padding: 16px 24px;
        border-top: 1px solid var(--border);
        flex-shrink: 0;
      }
      .input-wrap {
        display: flex;
        gap: 10px;
        align-items: flex-end;
      }
      .message-input {
        flex: 1;
        background: var(--card);
        border: 1px solid var(--border);
        color: var(--text);
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        outline: none;
        border-radius: 2px;
        resize: none;
        min-height: 44px;
        max-height: 140px;
        transition: border-color 0.2s;
        line-height: 1.5;
      }
      .message-input:focus {
        border-color: rgba(201, 255, 0, 0.4);
      }
      .message-input::placeholder {
        color: #333;
      }
      .send-btn {
        background: var(--accent);
        border: none;
        color: #060606;
        width: 44px;
        height: 44px;
        border-radius: 2px;
        cursor: pointer;
        font-size: 16px;
        transition: all 0.2s;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .send-btn:hover {
        background: #d4ff20;
        box-shadow: 0 0 16px rgba(201, 255, 0, 0.3);
      }
      .send-btn:disabled {
        opacity: 0.4;
        cursor: default;
      }

      .mode-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 10px;
      }
      .mode-tab {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
        font-size: 11px;
        font-family: "JetBrains Mono", monospace;
        padding: 5px 12px;
        cursor: pointer;
        border-radius: 20px;
        transition: all 0.2s;
      }
      .mode-tab.active,
      .mode-tab:hover {
        border-color: var(--accent);
        color: var(--accent);
      }

      @media (max-width: 768px) {
        .sidebar {
          display: none;
        }
        .bubble {
          max-width: 90%;
        }
      }
    </style>
  </head>
  <body>
    <div class="layout">
      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-top">
          <div class="logo">VYNERA</div>
        </div>
        <div class="sidebar-nav">
          <a href="/dashboard" class="nav-item">◈ Dashboard</a>
          <a href="/chat" class="nav-item active">◎ Chat</a>
          <a href="/history" class="nav-item">◷ History</a>
          <a href="/profile" class="nav-item">◉ Profile</a>
        </div>
        <button class="new-chat-btn" id="newChatBtn">+ New Conversation</button>

        <div class="sidebar-section">
          <div class="section-label">Memories</div>
          <div id="sidebarMemories">
            <div style="color: var(--muted); font-size: 11px">
              Chat to build memories.
            </div>
          </div>
        </div>

        <div
          class="sidebar-section"
          style="border-top: 1px solid var(--border)"
        >
          <div class="section-label">Goals</div>
          <div id="sidebarGoals">
            <div style="color: var(--muted); font-size: 11px">
              No active goals.
            </div>
          </div>
        </div>
      </aside>

      <!-- Chat -->
      <div class="chat-area">
        <div class="chat-header">
          <div>
            <div class="chat-header-name">VYNERA</div>
            <div class="chat-header-sub" id="connStatus">Connecting...</div>
          </div>
          <div class="emotion-badge" id="emotionBadge">– neutral</div>
        </div>

        <div class="messages" id="messages">
          <!-- Messages will be inserted here -->
        </div>

        <div style="padding: 0 24px">
          <div class="typing-indicator" id="typingIndicator">
            <div class="avatar bot">V</div>
            <div class="typing-dots">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="mode-tabs">
            <button class="mode-tab active" data-mode="chat">Chat</button>
            <button class="mode-tab" data-mode="journal">Journal</button>
            <button class="mode-tab" data-mode="goals">Goals</button>
            <button class="mode-tab" data-mode="reason">Reason</button>
          </div>
          <div class="input-wrap">
            <textarea
              class="message-input"
              id="messageInput"
              placeholder="Say anything..."
              rows="1"
            ></textarea>
            <button class="send-btn" id="sendBtn">➤</button>
          </div>
        </div>
      </div>
    </div>

    <script src="/static/js/chat.js"></script>
  </body>
</html>


---

### Profile Page — `profile.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Profile – VYNERA AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #666;
        --card: #0c0c0b;
        --border: #1e1e1c;
        --input: #0a0a09;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        font-family: "DM Sans", sans-serif;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }
      .layout {
        display: flex;
        min-height: 100vh;
      }
      .sidebar {
        width: 220px;
        border-right: 1px solid var(--border);
        padding: 28px 0;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
      }
      .sidebar-logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 22px;
        letter-spacing: 4px;
        color: var(--accent);
        padding: 0 24px;
        margin-bottom: 40px;
      }
      .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 24px;
        font-size: 13px;
        color: var(--muted);
        text-decoration: none;
        transition: all 0.2s;
        border-left: 2px solid transparent;
      }
      .nav-item:hover,
      .nav-item.active {
        color: var(--text);
        border-left-color: var(--accent);
      }
      .nav-item.active {
        color: var(--accent);
      }
      .main {
        flex: 1;
        padding: 48px;
        max-width: 720px;
      }
      .page-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 3px;
        color: var(--accent);
        margin-bottom: 8px;
      }
      .page-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 52px;
        letter-spacing: 2px;
        margin-bottom: 40px;
      }
      .section {
        margin-bottom: 40px;
      }
      .section-head {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 2px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--border);
      }
      .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
      }
      .form-group {
        margin-bottom: 18px;
      }
      label {
        display: block;
        font-size: 11px;
        font-family: "JetBrains Mono", monospace;
        letter-spacing: 1.5px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 8px;
      }
      input,
      select {
        width: 100%;
        background: var(--input);
        border: 1px solid var(--border);
        color: var(--text);
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        outline: none;
        border-radius: 2px;
        transition: border-color 0.2s;
        -webkit-appearance: none;
      }
      input:focus,
      select:focus {
        border-color: var(--accent);
      }
      select option {
        background: var(--bg);
      }
      .btn {
        font-family: "DM Sans", sans-serif;
        font-weight: 500;
        font-size: 13px;
        letter-spacing: 0.5px;
        padding: 11px 24px;
        border-radius: 2px;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
      }
      .btn-solid {
        background: var(--accent);
        color: #060606;
      }
      .btn-solid:hover {
        background: #d4ff20;
      }
      .btn-ghost {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
      }
      .btn-ghost:hover {
        border-color: var(--text);
        color: var(--text);
      }
      .btn-danger {
        background: transparent;
        border: 1px solid #662020;
        color: #cc4444;
      }
      .btn-danger:hover {
        background: #cc4444;
        color: #fff;
      }
      .toast {
        position: fixed;
        bottom: 32px;
        right: 32px;
        background: var(--card);
        border: 1px solid var(--border);
        padding: 14px 20px;
        font-size: 13px;
        border-radius: 2px;
        display: none;
        z-index: 1000;
      }
      .toast.show {
        display: block;
      }
      .toast.success {
        border-color: rgba(201, 255, 0, 0.4);
        color: var(--accent);
      }
      .toast.error {
        border-color: rgba(200, 60, 60, 0.4);
        color: #ff6060;
      }
      .danger-zone {
        border: 1px solid #331010;
        padding: 24px;
        background: rgba(180, 30, 30, 0.04);
      }
      .danger-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 20px;
        color: #cc4444;
        margin-bottom: 8px;
      }
      .danger-desc {
        font-size: 13px;
        color: var(--muted);
        margin-bottom: 16px;
        line-height: 1.6;
      }
      .modal-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.8);
        z-index: 500;
        display: none;
        align-items: center;
        justify-content: center;
      }
      .modal-overlay.show {
        display: flex;
      }
      .modal {
        background: var(--card);
        border: 1px solid var(--border);
        padding: 36px;
        max-width: 400px;
        width: 90%;
      }
      .modal h3 {
        font-family: "Bebas Neue", sans-serif;
        font-size: 28px;
        margin-bottom: 12px;
        color: #cc4444;
      }
      .modal p {
        font-size: 13px;
        color: var(--muted);
        margin-bottom: 24px;
        line-height: 1.6;
      }
      .modal-btns {
        display: flex;
        gap: 12px;
      }
      @media (max-width: 768px) {
        .sidebar {
          display: none;
        }
        .main {
          padding: 24px;
        }
        .form-row {
          grid-template-columns: 1fr;
        }
      }
    </style>
  </head>
  <body>
    <div class="layout">
      <aside class="sidebar">
        <div class="sidebar-logo">VYNERA</div>
        <a href="/dashboard" class="nav-item">◈ Dashboard</a>
        <a href="/chat" class="nav-item">◎ Chat</a>
        <a href="/history" class="nav-item">◷ History</a>
        <a href="/profile" class="nav-item active">◉ Profile</a>
      </aside>
      <main class="main">
        <div class="page-tag">// Settings</div>
        <h1 class="page-title">Your Profile</h1>

        <!-- Account Info -->
        <div class="section">
          <div class="section-head">Account Information</div>
          <div class="form-row">
            <div class="form-group">
              <label>Full Name</label><input type="text" id="pName" />
            </div>
            <div class="form-group">
              <label>Age</label
              ><input type="number" id="pAge" min="13" max="120" />
            </div>
          </div>
          <div class="form-group">
            <label>Email</label><input type="email" id="pEmail" />
          </div>
          <div class="form-group">
            <label>Username</label><input type="text" id="pUsername" />
          </div>
          <button class="btn btn-solid" onclick="saveProfile()">
            Save Changes
          </button>
        </div>

        <!-- Personality -->
        <div class="section">
          <div class="section-head">Bot Personality</div>
          <div class="form-group">
            <label>Preferred Style</label>
            <select id="pPersonality">
              <option value="encouraging">
                Encouraging – warm, celebratory, motivating
              </option>
              <option value="analytical">
                Analytical – logical, structured, precise
              </option>
              <option value="playful">Playful – light, witty, fun</option>
              <option value="wise">
                Wise – thoughtful, philosophical, measured
              </option>
            </select>
          </div>
          <button class="btn btn-solid" onclick="savePersonality()">
            Update Personality
          </button>
        </div>

        <!-- Password -->
        <div class="section">
          <div class="section-head">Change Password</div>
          <div class="form-group">
            <label>Current Password</label
            ><input type="password" id="pCurrentPw" placeholder="••••••••" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>New Password</label
              ><input
                type="password"
                id="pNewPw"
                placeholder="Min 8 characters"
              />
            </div>
            <div class="form-group">
              <label>Confirm New</label
              ><input type="password" id="pConfirmPw" placeholder="••••••••" />
            </div>
          </div>
          <button class="btn btn-solid" onclick="changePassword()">
            Update Password
          </button>
        </div>

        <!-- Export -->
        <div class="section">
          <div class="section-head">Data & Privacy</div>
          <p
            style="
              font-size: 13px;
              color: var(--muted);
              margin-bottom: 16px;
              line-height: 1.6;
            "
          >
            Export all your conversations, memories, goals, and journal entries
            as a JSON file.
          </p>
          <button class="btn btn-ghost" onclick="exportData()">
            ⬇ Export All My Data
          </button>
        </div>

        <!-- Danger Zone -->
        <div class="section">
          <div class="section-head" style="color: #cc4444">Danger Zone</div>
          <div class="danger-zone">
            <div class="danger-title">Delete Account</div>
            <p class="danger-desc">
              This will permanently delete your account, all conversations,
              memories, goals, and journal entries. This action cannot be
              undone.
            </p>
            <button class="btn btn-danger" onclick="showDeleteModal()">
              Delete My Account
            </button>
          </div>
        </div>

        <div style="padding-top: 16px; border-top: 1px solid var(--border)">
          <button class="btn btn-ghost" onclick="logout()">↩ Logout</button>
        </div>
      </main>
    </div>

    <!-- Delete Confirm Modal -->
    <div class="modal-overlay" id="deleteModal">
      <div class="modal">
        <h3>Delete Account?</h3>
        <p>
          Type <strong style="color: var(--text)">DELETE</strong> to confirm.
          This removes all your data permanently.
        </p>
        <div class="form-group">
          <input type="text" id="deleteConfirmInput" placeholder="DELETE" />
        </div>
        <div class="modal-btns">
          <button class="btn btn-ghost" onclick="closeDeleteModal()">
            Cancel
          </button>
          <button class="btn btn-danger" onclick="deleteAccount()">
            Delete Forever
          </button>
        </div>
      </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
      const token = () => localStorage.getItem("vynera_token");
      const toast = (msg, type = "success") => {
        const el = document.getElementById("toast");
        el.textContent = msg;
        el.className = `toast show ${type}`;
        setTimeout(() => el.classList.remove("show"), 3200);
      };

      async function loadProfile() {
        if (!token()) {
          window.location.href = "/login";
          return;
        }
        try {
          const r = await fetch("/api/me", {
            headers: { Authorization: "Bearer " + token() },
          });
          if (r.status === 401) {
            window.location.href = "/login";
            return;
          }
          const u = await r.json();
          document.getElementById("pName").value = u.name || "";
          document.getElementById("pAge").value = u.age || "";
          document.getElementById("pEmail").value = u.email || "";
          document.getElementById("pUsername").value = u.username || "";
          document.getElementById("pPersonality").value =
            u.personality || "encouraging";
        } catch (e) {
          toast("Failed to load profile.", "error");
        }
      }

      async function saveProfile() {
        const payload = {
          name: document.getElementById("pName").value.trim(),
          age: parseInt(document.getElementById("pAge").value) || null,
          email: document.getElementById("pEmail").value.trim(),
          username: document.getElementById("pUsername").value.trim(),
        };
        try {
          const r = await fetch("/api/me", {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + token(),
            },
            body: JSON.stringify(payload),
          });
          if (r.ok) {
            const u = await r.json();
            localStorage.setItem("vynera_user", JSON.stringify(u));
            toast("Profile updated!");
          } else {
            const d = await r.json();
            toast(d.detail || "Update failed.", "error");
          }
        } catch {
          toast("Network error.", "error");
        }
      }

      async function savePersonality() {
        const payload = {
          personality: document.getElementById("pPersonality").value,
        };
        try {
          const r = await fetch("/api/me", {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + token(),
            },
            body: JSON.stringify(payload),
          });
          if (r.ok) toast("Personality updated!");
          else toast("Update failed.", "error");
        } catch {
          toast("Network error.", "error");
        }
      }

      async function changePassword() {
        const cur = document.getElementById("pCurrentPw").value;
        const nw = document.getElementById("pNewPw").value;
        const cf = document.getElementById("pConfirmPw").value;
        if (!cur || !nw || !cf)
          return toast("Fill all password fields.", "error");
        if (nw.length < 8)
          return toast("New password must be 8+ characters.", "error");
        if (nw !== cf) return toast("New passwords do not match.", "error");
        try {
          const r = await fetch("/api/change-password", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + token(),
            },
            body: JSON.stringify({ current_password: cur, new_password: nw }),
          });
          const d = await r.json();
          if (r.ok) {
            toast("Password changed!");
            ["pCurrentPw", "pNewPw", "pConfirmPw"].forEach(
              (id) => (document.getElementById(id).value = ""),
            );
          } else toast(d.detail || "Failed.", "error");
        } catch {
          toast("Network error.", "error");
        }
      }

      async function exportData() {
        try {
          const r = await fetch("/api/export", {
            headers: { Authorization: "Bearer " + token() },
          });
          if (!r.ok) return toast("Export failed.", "error");
          const blob = await r.blob();
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "vynera_export.json";
          a.click();
          URL.revokeObjectURL(url);
          toast("Export downloaded!");
        } catch {
          toast("Export error.", "error");
        }
      }

      function showDeleteModal() {
        document.getElementById("deleteModal").classList.add("show");
      }
      function closeDeleteModal() {
        document.getElementById("deleteModal").classList.remove("show");
      }

      async function deleteAccount() {
        if (document.getElementById("deleteConfirmInput").value !== "DELETE")
          return toast("Type DELETE to confirm.", "error");
        try {
          const r = await fetch("/api/me", {
            method: "DELETE",
            headers: { Authorization: "Bearer " + token() },
          });
          if (r.ok) {
            localStorage.clear();
            window.location.href = "/";
          } else toast("Deletion failed.", "error");
        } catch {
          toast("Network error.", "error");
        }
      }

      function logout() {
        localStorage.clear();
        window.location.href = "/login";
      }

      loadProfile();
    </script>
  </body>
</html>


---

### History Page — `history.html`

<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>History – VYNERA AI</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Cormorant+Garamond:ital,wght@1,300&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400&display=swap"
      rel="stylesheet"
    />
    <style>
      :root {
        --bg: #060606;
        --accent: #c9ff00;
        --text: #e8e8e0;
        --muted: #666;
        --card: #0c0c0b;
        --border: #1e1e1c;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html,
      body {
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        font-family: "DM Sans", sans-serif;
      }
      body::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
        opacity: 0.035;
        pointer-events: none;
        z-index: 9999;
      }
      .layout {
        display: flex;
        min-height: 100vh;
      }
      .sidebar {
        width: 220px;
        border-right: 1px solid var(--border);
        padding: 28px 0;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
      }
      .sidebar-logo {
        font-family: "Bebas Neue", sans-serif;
        font-size: 22px;
        letter-spacing: 4px;
        color: var(--accent);
        padding: 0 24px;
        margin-bottom: 40px;
      }
      .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 24px;
        font-size: 13px;
        color: var(--muted);
        text-decoration: none;
        transition: all 0.2s;
        border-left: 2px solid transparent;
      }
      .nav-item:hover,
      .nav-item.active {
        color: var(--text);
        border-left-color: var(--accent);
      }
      .nav-item.active {
        color: var(--accent);
      }
      .main {
        flex: 1;
        padding: 48px;
        max-width: 900px;
      }
      .page-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        letter-spacing: 3px;
        color: var(--accent);
        margin-bottom: 8px;
      }
      .page-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 52px;
        letter-spacing: 2px;
        margin-bottom: 32px;
      }
      .search-bar {
        display: flex;
        gap: 12px;
        margin-bottom: 32px;
      }
      .search-input {
        flex: 1;
        background: #0a0a09;
        border: 1px solid var(--border);
        color: var(--text);
        font-family: "DM Sans", sans-serif;
        font-size: 14px;
        padding: 12px 16px;
        outline: none;
        border-radius: 2px;
        transition: border-color 0.2s;
      }
      .search-input:focus {
        border-color: var(--accent);
      }
      .search-input::placeholder {
        color: #333;
      }
      .search-btn {
        background: var(--accent);
        color: #060606;
        border: none;
        font-size: 13px;
        font-weight: 500;
        padding: 12px 20px;
        cursor: pointer;
        border-radius: 2px;
        transition: all 0.2s;
      }
      .search-btn:hover {
        background: #d4ff20;
      }
      .conv-list {
        display: flex;
        flex-direction: column;
        gap: 1px;
        background: var(--border);
      }
      .conv-item {
        background: var(--bg);
        padding: 20px 24px;
        cursor: pointer;
        transition: background 0.2s;
        border-left: 3px solid transparent;
      }
      .conv-item:hover {
        background: var(--card);
        border-left-color: var(--accent);
      }
      .conv-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
      }
      .conv-title {
        font-size: 14px;
        font-weight: 500;
      }
      .conv-date {
        font-family: "JetBrains Mono", monospace;
        font-size: 10px;
        color: var(--muted);
      }
      .conv-preview {
        font-size: 12px;
        color: var(--muted);
        line-height: 1.5;
        max-width: 600px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .conv-meta {
        display: flex;
        gap: 12px;
        margin-top: 6px;
      }
      .meta-pill {
        font-family: "JetBrains Mono", monospace;
        font-size: 9px;
        padding: 3px 8px;
        border: 1px solid var(--border);
        border-radius: 20px;
        color: var(--muted);
      }
      .empty {
        text-align: center;
        padding: 80px;
        color: var(--muted);
      }
      .empty-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 32px;
        margin-bottom: 8px;
      }

      /* Conv detail panel */
      .detail-overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.85);
        z-index: 400;
        display: none;
        align-items: flex-start;
        justify-content: flex-end;
      }
      .detail-overlay.show {
        display: flex;
      }
      .detail-panel {
        background: var(--bg);
        border-left: 1px solid var(--border);
        width: min(640px, 100vw);
        height: 100vh;
        display: flex;
        flex-direction: column;
        animation: slideIn 0.25s ease;
      }
      @keyframes slideIn {
        from {
          transform: translateX(40px);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      .detail-header {
        padding: 24px;
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-shrink: 0;
      }
      .detail-title {
        font-family: "Bebas Neue", sans-serif;
        font-size: 24px;
        letter-spacing: 1px;
      }
      .close-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
        width: 32px;
        height: 32px;
        cursor: pointer;
        border-radius: 2px;
        font-size: 16px;
        transition: all 0.2s;
      }
      .close-btn:hover {
        border-color: var(--accent);
        color: var(--accent);
      }
      .detail-messages {
        flex: 1;
        overflow-y: auto;
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      .detail-msg {
        padding: 12px 16px;
        border-radius: 2px;
        font-size: 13px;
        line-height: 1.65;
        max-width: 85%;
      }
      .detail-msg.user {
        background: #141412;
        border: 1px solid var(--border);
        align-self: flex-end;
        border-radius: 12px 2px 2px 12px;
      }
      .detail-msg.bot {
        background: var(--card);
        border: 1px solid var(--border);
        align-self: flex-start;
        border-radius: 2px 12px 12px 2px;
      }
      .detail-role {
        font-family: "JetBrains Mono", monospace;
        font-size: 9px;
        color: var(--muted);
        margin-bottom: 4px;
      }
      .detail-emotion {
        font-family: "JetBrains Mono", monospace;
        font-size: 9px;
        color: var(--accent);
        margin-top: 4px;
      }

      .pagination {
        display: flex;
        gap: 8px;
        margin-top: 24px;
      }
      .page-btn {
        background: transparent;
        border: 1px solid var(--border);
        color: var(--muted);
        font-size: 12px;
        padding: 8px 16px;
        cursor: pointer;
        border-radius: 2px;
        transition: all 0.2s;
      }
      .page-btn:hover,
      .page-btn.active {
        border-color: var(--accent);
        color: var(--accent);
      }
      .page-btn:disabled {
        opacity: 0.3;
        cursor: default;
      }

      @media (max-width: 768px) {
        .sidebar {
          display: none;
        }
        .main {
          padding: 24px;
        }
      }
    </style>
  </head>
  <body>
    <div class="layout">
      <aside class="sidebar">
        <div class="sidebar-logo">VYNERA</div>
        <a href="/dashboard" class="nav-item">◈ Dashboard</a>
        <a href="/chat" class="nav-item">◎ Chat</a>
        <a href="/history" class="nav-item active">◷ History</a>
        <a href="/profile" class="nav-item">◉ Profile</a>
      </aside>
      <main class="main">
        <div class="page-tag">// Conversation Archive</div>
        <h1 class="page-title">Chat History</h1>

        <div class="search-bar">
          <input
            class="search-input"
            id="searchInput"
            placeholder="Search by topic, date, or keyword..."
            type="text"
          />
          <button class="search-btn" onclick="searchConvs()">Search</button>
        </div>

        <div id="convList"></div>
        <div class="pagination" id="pagination"></div>
      </main>
    </div>

    <!-- Detail Panel -->
    <div class="detail-overlay" id="detailOverlay" onclick="closeDetail(event)">
      <div class="detail-panel" id="detailPanel">
        <div class="detail-header">
          <div class="detail-title" id="detailTitle">Conversation</div>
          <button class="close-btn" onclick="closeDetailPanel()">✕</button>
        </div>
        <div class="detail-messages" id="detailMessages"></div>
      </div>
    </div>

    <script>
      const token = localStorage.getItem("vynera_token");
      if (!token) window.location.href = "/login";

      let currentPage = 0;
      const PAGE_SIZE = 20;
      let allConvs = [];

      async function loadConvs(search = "") {
        try {
          const url = `/api/conversations?search=${encodeURIComponent(search)}&limit=200`;
          const r = await fetch(url, {
            headers: { Authorization: "Bearer " + token },
          });
          if (r.status === 401) {
            window.location.href = "/login";
            return;
          }
          allConvs = await r.json();
          currentPage = 0;
          renderPage();
        } catch (e) {
          console.error(e);
        }
      }

      function formatDate(str) {
        if (!str) return "–";
        try {
          return new Date(str).toLocaleDateString("en-IN", {
            day: "numeric",
            month: "short",
            year: "numeric",
          });
        } catch {
          return str;
        }
      }

      function renderPage() {
        const start = currentPage * PAGE_SIZE;
        const page = allConvs.slice(start, start + PAGE_SIZE);
        const listEl = document.getElementById("convList");

        if (!allConvs.length) {
          listEl.innerHTML = `<div class="empty"><div class="empty-title">No Conversations Yet</div><p style="font-size:13px;">Start chatting to see your history here.</p></div>`;
          document.getElementById("pagination").innerHTML = "";
          return;
        }

        listEl.innerHTML = `<div class="conv-list">${page
          .map((c) => {
            const msgs = c.messages || [];
            const lastMsg = msgs.length ? msgs[msgs.length - 1] : null;
            const preview = lastMsg
              ? lastMsg.content.substring(0, 120)
              : "No messages";
            const count = msgs.length;
            return `<div class="conv-item" onclick="openDetail('${c._id}','${(c.title || "Conversation").replace(/'/g, "\\'")}')">
      <div class="conv-top">
        <div class="conv-title">${c.title || "Conversation"}</div>
        <div class="conv-date">${formatDate(c.created_at)}</div>
      </div>
      <div class="conv-preview">${preview}</div>
      <div class="conv-meta">
        <span class="meta-pill">${count} messages</span>
        ${c.topic ? `<span class="meta-pill">${c.topic}</span>` : ""}
      </div>
    </div>`;
          })
          .join("")}</div>`;

        renderPagination();
      }

      function renderPagination() {
        const total = Math.ceil(allConvs.length / PAGE_SIZE);
        if (total <= 1) {
          document.getElementById("pagination").innerHTML = "";
          return;
        }
        let html = `<button class="page-btn" onclick="goPage(${currentPage - 1})" ${currentPage === 0 ? "disabled" : ""}>← Prev</button>`;
        for (let i = 0; i < total; i++) {
          html += `<button class="page-btn ${i === currentPage ? "active" : ""}" onclick="goPage(${i})">${i + 1}</button>`;
        }
        html += `<button class="page-btn" onclick="goPage(${currentPage + 1})" ${currentPage === total - 1 ? "disabled" : ""}>Next →</button>`;
        document.getElementById("pagination").innerHTML = html;
      }

      function goPage(p) {
        const total = Math.ceil(allConvs.length / PAGE_SIZE);
        if (p < 0 || p >= total) return;
        currentPage = p;
        renderPage();
        window.scrollTo(0, 0);
      }

      function searchConvs() {
        const q = document.getElementById("searchInput").value.trim();
        loadConvs(q);
      }

      document
        .getElementById("searchInput")
        .addEventListener("keydown", (e) => {
          if (e.key === "Enter") searchConvs();
        });

      async function openDetail(convId, title) {
        document.getElementById("detailTitle").textContent = title;
        document.getElementById("detailMessages").innerHTML =
          '<div style="color:var(--muted);text-align:center;padding:40px;font-size:13px;">Loading...</div>';
        document.getElementById("detailOverlay").classList.add("show");

        try {
          const r = await fetch(`/api/conversations/${convId}`, {
            headers: { Authorization: "Bearer " + token },
          });
          const data = await r.json();
          const msgs = data.messages || [];
          document.getElementById("detailMessages").innerHTML =
            msgs
              .map(
                (m) => `
      <div class="detail-msg ${m.role}">
        <div class="detail-role">${m.role === "user" ? "// YOU" : "// VYNERA"}</div>
        ${m.content}
        ${m.emotion ? `<div class="detail-emotion">◎ ${m.emotion} (${Math.round((m.intensity || 0) * 100)}%)</div>` : ""}
      </div>
    `,
              )
              .join("") ||
            '<div style="color:var(--muted);font-size:13px;">No messages in this conversation.</div>';
        } catch {
          document.getElementById("detailMessages").innerHTML =
            '<div style="color:#cc4444;text-align:center;padding:40px;">Failed to load.</div>';
        }
      }

      function closeDetail(e) {
        if (e.target === document.getElementById("detailOverlay"))
          closeDetailPanel();
      }
      function closeDetailPanel() {
        document.getElementById("detailOverlay").classList.remove("show");
      }

      loadConvs();
    </script>
  </body>
</html>

---