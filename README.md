# Streakie - Productivity Tracking App

Streakie is a modern productivity tracking application that helps users build and maintain daily habits through streak-based motivation.

## Features

- Todo List Management
- Streak Tracking
- Dynamic Analytics Dashboard
- Smart Deadline Management
- User Authentication
- Responsive Design

## Tech Stack

### Frontend
- React
- Framer Motion for animations
- React Router for navigation
- Axios for API requests
- Custom CSS theming

### Backend
- Flask (Python)
- MongoDB for database
- JWT for authentication
- RESTful API design

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- MongoDB

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/streakie.git
cd streakie
```

2. Install backend dependencies:
```bash
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Create a .env file in the root directory:
```
MONGODB_URI=your_mongodb_uri
JWT_SECRET_KEY=your_secret_key
```

5. Start the backend server:
```bash
python app.py
```

6. Start the frontend development server:
```bash
cd frontend
npm start
```

The app will be available at http://localhost:3002

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
