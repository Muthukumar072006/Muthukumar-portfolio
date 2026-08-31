# 🚀 Dynamic Flask Portfolio Website

A personal portfolio web application built with Python Flask and SQLite, featuring a dynamic project showcase, skills section, and an admin management dashboard.

## 🌐 Live Demo
🔗 **Live Site:** [https://muthukumar-portfolio-1.onrender.com](https://muthukumar-portfolio-1.onrender.com)

---

## ✨ Features
- **Dynamic Content:** Projects and skills loaded dynamically from SQLite database.
- **Admin Dashboard:** Secure login for managing portfolio content (Add/Edit/Delete projects & skills).
- **Responsive UI:** Clean and modern interface built with HTML5, CSS3, and JavaScript.
- **Resume Download:** Direct link to download resume.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask, SQLite3, Gunicorn
- **Frontend:** HTML5, CSS3, JavaScript
- **Deployment:** Render Platform

---

## 📁 Project Structure
```text
Personal_portfolio/
│
├── app.py
├── portfolio.db
├── Procfile
├── requirements.txt
├── README.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── resume/
│       └── Muthukumar_Data_Analytics_Resume.pdf
│
└── templates/
    ├── index.html
    ├── admin.html
    └── login.html