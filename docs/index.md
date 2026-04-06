# Design2Web

![Logo Placeholder](assets/logo.svg)

# 🚀 Design2Web: From JSON Specs to Live Web Apps

Design2Web is a powerful Python CLI tool that bridges the gap between design specification and functional web code. Stop manually translating design mockups into HTML/CSS. Simply provide a structured JSON file describing your layout, components, and styling, and watch Design2Web generate a complete, runnable, and semantic HTML, CSS, and vanilla JavaScript web application.

---

## ✨ Key Features

Design2Web transforms abstract design concepts into tangible, production-ready code with ease.

::: grid
::: col-span-1
::: card
### 🎨 Component Abstraction
Define complex UI elements like Buttons, Cards, Forms, and Navbars using simple JSON structures.
:::
::: col-span-1
::: card
### 📐 Style & Layout Control
Specify colors, spacing, and typography directly in your JSON. We translate these into clean, modern CSS using Flexbox for robust layout.
:::
::: col-span-1
::: card
### 🐍 Python CLI Driven
Built as a straightforward Python command-line interface (`main.py`), making integration into automated workflows seamless.
:::
::: col-span-1
::: card
### 🌐 Vanilla & Semantic Output
Generates pure HTML5 and CSS3 without heavy frameworks, ensuring fast load times and excellent accessibility.
:::
::: grid
:::

## 🛠️ How It Works

The process is elegantly simple:

1. **Define:** Create a JSON file detailing your desired application structure, components, and styles.
2. **Run:** Execute the tool from your terminal: `python main.py --spec your_design.json`
3. **Deploy:** Design2Web outputs `index.html` and `style.css`, ready to be served instantly.

### Core Functions

Our tool is built around these core capabilities:

*   **`parse_design_spec(json_file)`**: Intelligently reads and interprets the structure, components, colors, and typography defined in your JSON input.
*   **`generate_html(spec)`**: Constructs a clean, semantic `index.html` file, mapping JSON components to appropriate HTML tags.
*   **`generate_css(spec)`**: Generates a comprehensive `style.css` file, utilizing Flexbox for responsive and predictable styling based on your specifications.

## ⚡ Quick Start

Ready to turn your designs into code?

First, ensure you have Python installed. Then, clone the repository and install dependencies (if any).

```bash
git clone https://github.com/yourusername/design2web.git
cd design2web
pip install -r requirements.txt
```

### Run Your First Conversion

Create a sample JSON file (e.g., `my_app.json`) and run:

```bash
python main.py --spec my_app.json
```

This will instantly generate `index.html` and `style.css` in your directory!

## ➡️ Get Started

Dive deeper into the documentation to learn the exact JSON schema required for maximum control.

[View the Full API Reference and Schema Documentation](./api_reference.md)

---
*Design2Web: Specify. Generate. Deploy.*