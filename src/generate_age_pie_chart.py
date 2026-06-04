import os
import matplotlib.pyplot as plt

# Create directories if they don't exist
os.makedirs(r'e:\VKU\Research\Research2026-tamli\outputs', exist_ok=True)
os.makedirs(r'C:\Users\quang\.gemini\antigravity\brain\5d3d439f-681a-4a05-8499-5b7bc51710f3\artifacts', exist_ok=True)

# Set style
plt.style.use('ggplot')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']

# Data
labels = ['Aged 18-23\n(Students & Young Workforce)', 'Other Gen Z\n(Aged 15-17 & 24-29)']
sizes = [86, 14]
colors = ['#3B82F6', '#94A3B8'] # Blue and Slate Gray
explode = (0.1, 0)  # Highlight 18-23

# Create figure
fig, ax = plt.subplots(figsize=(8, 8), facecolor='none')

# Pie chart
wedges, texts, autotexts = ax.pie(
    sizes, 
    explode=explode, 
    labels=labels, 
    colors=colors, 
    autopct='%1.1f%%',
    startangle=140, 
    textprops=dict(color='#1E293B', fontsize=14, fontweight='semibold'),
    wedgeprops=dict(edgecolor='none', linewidth=2)
)

# Customize percentage labels
for autotext in autotexts:
    autotext.set_fontsize(16)
    autotext.set_color('#FFFFFF')
    autotext.set_weight('bold')

# Title
ax.set_title('SURVEY AGE DISTRIBUTION\n(N = 645)', fontsize=18, fontweight='bold', color='#1E293B', pad=20)


plt.tight_layout()

# Save paths
path1 = r'e:\VKU\Research\Research2026-tamli\outputs\age_pie_chart.png'
path2 = r'C:\Users\quang\.gemini\antigravity\brain\5d3d439f-681a-4a05-8499-5b7bc51710f3\artifacts\age_pie_chart.png'

plt.savefig(path1, dpi=300, bbox_inches='tight', transparent=True)
plt.savefig(path2, dpi=300, bbox_inches='tight', transparent=True)

plt.close()

print(f"Pie chart saved to:\n1. {path1}\n2. {path2}")
