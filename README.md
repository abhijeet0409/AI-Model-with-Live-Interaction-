🧠 Frontdesk AI — Intelligent Virtual Frontdesk System

Frontdesk AI is an AI-powered virtual frontdesk assistant designed to automate interactions between users and supervisors.
It combines real-time video conferencing, AI-driven chat automation, and role-based dashboards into one unified web platform.

🚀 Features
👥 Role-based System

User Login: Ask questions and get instant AI-generated responses.

Supervisor Login: Manage pending queries, provide manual answers, and monitor live sessions.

💬 AI-Powered Interaction

Automatically answers user queries using a custom-trained AI model.

Forwards unresolved queries to supervisors in real-time.

🎥 Live Meeting Integration

Built-in Jitsi Meet integration for instant “Join Meeting” functionality.

Both users and supervisors can join live video calls seamlessly.

📊 Dynamic Dashboards

Supervisors can view all pending and resolved requests.

Real-time status updates every 5 seconds.

💡 Smooth UI

Modern, responsive interface built with React + Tailwind/CSS3 animations.

Clean gradients, adaptive layout, and fade-in transitions.

🧩 Tech Stack
Layer	Technology
Frontend	React.js (Vite)
Backend	FastAPI / Node.js
Database	PostgreSQL / MongoDB
AI Layer	Custom NLP Model / OpenAI API
Video SDK	Jitsi Meet API
Styling	CSS3 / Flexbox / Animations
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/frontdesk-ai.git
cd frontdesk-ai

2️⃣ Install Dependencies
npm install

3️⃣ Configure Environment

Create a .env file in the root directory:

VITE_BACKEND_URL=http://localhost:8000

4️⃣ Start the Development Server
npm run dev


Access the app at http://localhost:5173

🖼️ Project Structure
frontdesk-ai/
├── src/
│   ├── App.jsx
│   ├── App.css
│   ├── components/
│   └── assets/
├── public/
├── .env
├── package.json
└── README.md

🌐 How It Works

User selects login type (User / Supervisor).

User can ask questions → AI responds automatically.

If AI can’t answer → query sent to Supervisor.

Supervisor can reply or join a live Jitsi meeting.

Both roles can join the same live meeting room instantly.

🧠 Future Enhancements

Integrate advanced voice assistant support.

Add analytics dashboard for supervisors.

Multi-language model integration.

Support for multiple meeting rooms.

🧑‍💻 Developers

Frontdesk AI Team - (Abhijeet)

Built with ❤️ using React, AI APIs, and Jitsi SDK.
