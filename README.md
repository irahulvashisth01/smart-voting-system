# 🗳 Smart Voting System with Face Authentication

A **secure web-based voting platform** that allows users to register, authenticate using facial capture, and cast votes digitally.
The system includes an **admin dashboard, candidate management, real-time results, and Progressive Web App (PWA) support**.

🔗 **Live Project:**
https://smart-voting-system-boqy.onrender.com

# 📌 Project Overview

The **Smart Voting System** is designed to simulate a secure digital election environment where voters can register using their camera, authenticate using face capture, and vote for candidates through a web interface.

The platform also includes an **admin panel to manage elections**, candidates, and voting status.

This project demonstrates practical implementation of:

* Web development
* Database management
* Camera integration
* Authentication logic
* Cloud deployment
* Progressive Web Apps

### 👤 Voter System

* Voter Registration with camera capture
* Face-based login verification
* Prevents duplicate voting
* Secure vote submission

### 🗳 Voting System

* View candidate list
* Vote for preferred candidate
* Automatic vote counting
* Voting status control

### 👨‍💼 Admin Dashboard

* Add candidates
* Upload candidate photos
* Upload party symbols
* Delete candidates
* Start election
* Stop election
* View live results

### 📊 Result System

* Automatic winner detection
* Vote count display
* Download results
* Result visualization charts

### 📱 Progressive Web App

* Installable as mobile application
* Works like a native app
* Mobile responsive design

# 🧰 Technologies Used

| Technology       | Purpose              |
| ---------------- | -------------------- |
| Python           | Backend logic        |
| Flask            | Web framework        |
| SQLite           | Database             |
| HTML             | Page structure       |
| CSS              | UI styling           |
| JavaScript       | Camera capture & PWA |
| OpenCV           | Image handling       |
| Face Recognition | Authentication       |
| Gunicorn         | Production server    |
| Render           | Cloud deployment     |

# 📂 Project Structure

smart-voting-system
│
├── app.py
├── database.db
├── requirements.txt
│
├── templates
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── vote.html
│   ├── result.html
│   └── admin_dashboard.html
│
├── static
│   ├── uploads
│   ├── manifest.json
│   ├── service-worker.js
│   └── icons
│
└── README.md

# ⚙ Installation (Local Setup)

### 1️⃣ Clone repository

git clone https://github.com/irahulvashisth01/smart-voting-system.git

### 2️⃣ Open project

cd smart-voting-system

### 3️⃣ Install dependencies

pip install -r requirements.txt

### 4️⃣ Run application

python app.py

Open in browser:

http://127.0.0.1:5000

# 🌐 Deployment (Render)

The project is deployed on **Render Cloud Platform**.

### Deployment Steps

1. Push project to GitHub
2. Connect repository to Render
3. Create a **Web Service**
4. Use following configuration:

**Build Command**
pip install -r requirements.txt

**Start Command**
gunicorn app:app

Render automatically redeploys when new commits are pushed.

# 🔐 Security Features

* Prevents duplicate voter registration
* Prevents multiple votes from same user
* Camera verification before voting
* Controlled election start and stop
* Admin-controlled candidate management

# 📱 PWA Support

The system can be installed as a **mobile application**.

Features include:

* Installable web app
* Home screen icon
* Mobile responsive UI
* Service worker support

# 👨‍💻 Developer

**Rahul Sharma**
B.Tech Computer Science Engineering

# 📄 License

This project is created for **educational and demonstration purposes**.

# ⭐ Project Highlights

* Cloud deployed voting system
* Face authentication integration
* Admin election management
* Mobile installable application
* Full-stack web development project

# 📷 Screenshots

Home Page
<img width="1763" height="853" alt="image" src="https://github.com/user-attachments/assets/a8e4bbb0-8cee-4e2d-bf49-96d8db9e4333" />

Voting Page
<img width="1763" height="853" alt="image" src="https://github.com/user-attachments/assets/4474c87b-a746-4a5d-8a59-bf13f25f8321" />

Admin Dashboard
<img width="1763" height="947" alt="image" src="https://github.com/user-attachments/assets/676603fd-cc3d-4b74-a827-f30c6ae0ae85" />

Election Results
<img width="1763" height="910" alt="image" src="https://github.com/user-attachments/assets/b9291bec-f22e-4427-bf11-a0858d966f61" />


# 💡 Future Improvements

* Real face recognition matching
* OTP verification
* Blockchain-based vote storage
* End-to-end encryption
* Advanced biometric authentication

# 📬 Contact

For queries or collaboration:

GitHub
https://github.com/irahulvashisth01
