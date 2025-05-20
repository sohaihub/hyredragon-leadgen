import streamlit as st
import google.generativeai as genai
import pandas as pd
from io import StringIO

# ===== Configure Gemini directly in code =====
genai.configure(api_key="AIzaSyBj1BzzNCg6FOUeic8DTtU3uYNVMaDErQw")  # Replace with your actual Gemini API key

# ===== Gemini model initialization =====
model = genai.GenerativeModel("gemini-1.5-flash")

# ===== Streamlit UI =====
st.set_page_config(page_title="AI Lead Generator", layout="wide")
st.title("📇 AI-Powered B2B Lead Generator")
st.markdown("Generate realistic company leads with details like contact info, LinkedIn, and website.")

# ===== Input Form =====
with st.form("lead_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input("City", placeholder="e.g., Bengaluru")
    with col2:
        company_type = st.text_input("Company Type", placeholder="e.g., SaaS startups")
    with col3:
        number_of_leads = st.number_input("Number of Leads", min_value=1, max_value=50, value=5)
    submitted = st.form_submit_button("Generate Leads")

# ===== Prompt Builder =====
def build_prompt(city, company_type, number_of_leads):
    return f"""
You are a professional lead generator.

Generate {number_of_leads} leads for companies based in:
- City: {city}
- Company Type: {company_type}

Provide the following fields as a markdown table:
| Company Name | Email | LinkedIn ID | Hiring Manager LinkedIn ID | Contact Number | Address | Official Website |

Use realistic-sounding names and values, simulate results from Google Search and LinkedIn.
Only output the markdown table.
- LinkedIn IDs must be full URLs, like: https://www.linkedin.com/in/username
- Company LinkedIn must be full URLs, like: https://www.linkedin.com/company/companyname
- Official websites must be full URLs, like: https://example.com
- Address must include city and postal code
- All contact details should be realistic-looking
only output for the markdown table.

"""

# ===== Table Parser =====
def parse_markdown_table(md_text):
    lines = md_text.strip().splitlines()
    table_lines = [line for line in lines if "|" in line and not line.strip().startswith("|---")]
    csv_str = '\n'.join([','.join(cell.strip() for cell in line.strip('|').split('|')) for line in table_lines])
    df = pd.read_csv(StringIO(csv_str))
    return df

# ===== Generate and Display Output =====
if submitted and city and company_type:
    with st.spinner("🔍 Generating leads..."):
        prompt = build_prompt(city, company_type, number_of_leads)
        try:
            response = model.generate_content(prompt)
            markdown = response.text

            try:
                df = parse_markdown_table(markdown)
                st.success("✅ Leads generated successfully!")
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, "leads.csv", "text/csv")
            except:
                st.error("❌ Could not parse the table. Showing raw output:")
                st.markdown(markdown)

        except Exception as e:
            st.error(f"❌ Gemini error: {str(e)}")
