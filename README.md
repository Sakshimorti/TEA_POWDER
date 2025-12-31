# 🍵 GOLD Tea Powder - Sales Entry Application

A simple and user-friendly Streamlit application for managing tea powder sales entries.

## Features

- **Auto-filled Date**: Today's date is automatically filled in
- **Auto-calculated Day**: Day of the week is calculated from the selected date
- **Dynamic Rate**: Rate automatically updates based on selected packaging
- **Auto-calculated Total**: Total amount is calculated automatically (Rate × Quantity)
- **Excel Storage**: All sales data is stored in `gold_tea_sales.xlsx`
- **Recent Entries Display**: View the last 5 sales entries
- **Quick Summary**: See total sales, quantity, and entry count

## Business Details

**Brand**: GOLD Tea Powder

**Tea Types**:
- Mix
- Barik

**Packaging & Rates**:
- 100gm → ₹60
- 250gm → ₹140
- 500gm → ₹270
- 1kg → ₹520

## Installation

1. Make sure you have Python installed (3.8 or higher)

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the following command in your terminal:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## How to Use

1. **Date & Day**: Date defaults to today and day is auto-calculated. You can edit both if needed.
2. **Village**: Select from the dropdown (default village is pre-selected)
3. **Customer Name**: Enter the customer's name
4. **Tea Type**: Select either Mix or Barik
5. **Packaging**: Choose the package size (100gm, 250gm, 500gm, or 1kg)
6. **Rate**: Automatically filled based on packaging (read-only)
7. **Quantity**: Enter the quantity
8. **Total Amount**: Automatically calculated (read-only)
9. Click **Save Sales Entry** to save the data

## Data Storage

All sales entries are saved in `gold_tea_sales.xlsx` in the same directory as the app. The file will be created automatically on the first save.

**Excel Columns**:
- Date
- Day
- Village
- Customer Name
- Brand
- Tea Type
- Packaging
- Rate
- Quantity
- Total Amount

## Customization

You can customize the village list in [app.py](app.py#L21):
```python
VILLAGES = ["Village A", "Village B", "Village C", "Village D", "Village E"]
```

Replace the village names with your actual village names.

## Requirements

- Python 3.8+
- streamlit
- pandas
- openpyxl

## License

© 2025 GOLD Tea Powder Sales Management System
