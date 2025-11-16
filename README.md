# 🏠 Childcare Finder

A machine learning-powered web application that helps families find the childcare based on location, budget, and educational philosophy. This is my first machine learning application. My background is in content design and technical writing.

## 🌟 Features

- **Smart Matching**: Calculates match scores based on your preferences
- **Interactive Map**: See all providers on an interactive map
- **Real Reviews**: Uses actual Google Places reviews and ratings
- **Budget Filtering**: Find childcare within your budget
- **Educational Philosophy**: Filter by Montessori, Play-Based, STEM, etc.
- **Analytics Dashboard**: Visualize market trends and pricing

## 🛠️ Technologies Used

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

## 📊 How It Works

1. **Data Collection**: Uses Google Places API to gather childcare provider information
2. **Feature Engineering**: Extracts educational philosophies and quality indicators from reviews
3. **Matching Algorithm**: Calculates match scores based on:
   - Distance from your location (35%)
   - Price fit within budget (30%)
   - Google rating (20%)
   - Educational values alignment (15%)
4. **Visualization**: Displays results with interactive maps and charts

## 📸 Screenshots

*(Add screenshots here once deployed)*

## 👨‍💻 Author

**Your Name**
- GitHub: [@kdmeg528](https://github.com/kdmeg528)

## 📄 License

MIT License - feel to use for educational purposes

## 🙏 Acknowledgments

- Google Places API for providing childcare data
- Streamlit for the web framework
- Colleagues and friends who encouraged me to keep going

---

Built for families looking for childcare

## Notes
Initial commits may show my work profile as I developed this on my work laptop. This is a personal project completed independently for my coursework. All subsequent commits use my personal credentials.

