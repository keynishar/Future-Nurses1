# Future Nurses — Nurse-Led Health Education Studio (NUR-2)
**Career Venture Lab | Precalculus (Advanced Level) | Stage 1 Dashboard**

## What Each File Does
- `app.py`: The main webpage control screen built with Streamlit.
- `engine.py`: The business math and receipt-book engine (keeps money calculations exact and protects against duplicate entries).
- `requirements.txt`: The list of Python tools needed to run the app.
- `sample_data/monthly_fixture.csv`: The 3-month sample test file from the Student Handbook.
- `tests/test_nur2.py`: Automated checks that prove the math and save-file rules work properly.

## How to Run on Your Computer
1. Open a terminal in this folder and install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the automated Stage 1 checks:
   ```bash
   pytest
   ```
3. Start your business dashboard:
   ```bash
   streamlit run app.py
   ```

## How to Put It Online with GitHub & Render.com
1. Push all files in this folder to your team's GitHub repository.
2. On Render.com, create a **New Web Service** connected to that GitHub repository.
3. Set the **Build Command** to:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the **Start Command** to:
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
   ```
