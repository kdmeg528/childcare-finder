# 🏠 Childcare Finder

A machine learning-powered web application that helps families find childcare based on location, budget, and educational philosophy.

## 📘 About this project

This repository contains my midterm project for [ML Zoomcamp](https://datatalks.club/blog/machine-learning-zoomcamp.html). It gathers childcare data from the Google Places API and uses it to make basic, customizable recommendations. My background is in content design and technical writing. This project is for building skills in Python, data engineering, and applied machine learning. 

## 🌟 Features

- **Smart matching**: Calculates match scores based on your preferences
- **Interactive map**: See all providers on an interactive map
- **Real reviews**: Uses actual Google Places reviews and ratings
- **Budget filtering**: Find childcare within your budget
- **Educational philosophy**: Filter by Montessori, Play-Based, STEM, etc.
- **Analytics dashboard**: Visualize market trends and pricing

## 🛠️ Technologies used

- **Python 3.11**
- **Streamlit** - Web framework
- **Google Places API** - Data source
- **Pandas & NumPy** - Data processing
- **Plotly** - Interactive visualizations
- **Docker** - Containerization

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR-USERNAME/childcare-finder.git
cd childcare-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Collect data:
```bash
python3 collect_data.py
```

4. Run the app:
```bash
streamlit run app.py
```

5. Open your browser to `http://localhost:8501`

## 🐳 Docker

Run with Docker:
```bash
docker build -t childcare-finder .
docker run -p 8501:8501 childcare-finder
```

## 📊 How it works

1. **Data Collection**: Uses Google Places API to gather childcare provider information
2. **Feature Engineering**: Extracts educational philosophies and quality indicators from reviews
3. **Matching Algorithm**: Calculates match scores based on:
   - Distance from your location (35%)
   - Price fit within budget (30%)
   - Google rating (20%)
   - Educational values alignment (15%)
4. **Visualization**: Displays results with interactive maps and charts

## 📸 Screenshots

![childcare-finder](https://1787891.fs1.hubspotusercontent-na1.net/hubfs/1787891/ML%20Zoomcamp%202025/Screen%20Shot%202025-11-16%20at%208.25.22%20PM.png)

## 👨‍💻 Author

**Megan Driscoll**
- GitHub: [@kdmeg528](https://github.com/kdmeg528)

## 📄 License
MIT License - feel free to use this project for learning!

## 🙏 Acknowledgments

- Google Places API for providing childcare data
- Streamlit for the web framework
- Coworkers and friends who encouraged me to continue with this course
- Built with guidance from colleagues, online FAQs and resources, and Claude

---

Built for families looking for childcare

## Notes
Initial commits may show my work profile as I developed this on my work laptop. This is a personal project completed independently for my coursework. All subsequent commits use my personal credentials.

