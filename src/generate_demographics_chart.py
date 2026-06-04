import os
import matplotlib.pyplot as plt

# Create directories if they don't exist
os.makedirs(r'e:\VKU\Research\Research2026-tamli\outputs', exist_ok=True)
os.makedirs(r'C:\Users\quang\.gemini\antigravity\brain\5d3d439f-681a-4a05-8499-5b7bc51710f3\artifacts', exist_ok=True)

# Set style
plt.style.use('ggplot')

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']

# Create figure with 2 columns
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), facecolor='none')
fig.suptitle('SURVEY DEMOGRAPHICS OVERVIEW\nN = 645 Valid Responses', fontsize=22, fontweight='bold', color='#1E293B', y=0.95)

# --- Left Plot: Donut Chart for Age ---
labels = ['Age 18-23\n(86.0%)', 'Other Gen Z\n(14.0%)']
sizes = [86, 14]
colors = ['#3B82F6', '#E2E8F0'] # Modern Blue and Light Gray

wedges, texts = ax1.pie(
    sizes, 
    labels=labels, 
    colors=colors, 
    startangle=90, 
    counterclock=False,
    textprops=dict(color='#1E293B', fontsize=13, fontweight='semibold'),
    wedgeprops=dict(width=0.35, edgecolor='none', linewidth=3)
)

# Add a circle at the center
centre_circle = plt.Circle((0,0), 0.50, fc='none')
ax1.add_artist(centre_circle)
ax1.set_title('Age Distribution (Gen Z: 15-29)', fontsize=16, fontweight='bold', color='#475569', pad=20)
ax1.set_facecolor('none')


# Add percentage in the center
ax1.text(0, 0, '86%', ha='center', va='center', fontsize=36, fontweight='bold', color='#3B82F6')

# --- Right Plot: Info Card ---
ax2.axis('off')
ax2.set_facecolor('#F8F9FA')

# Draw a nice background box for info
bbox_props = dict(boxstyle="round,pad=1.5", fc="#FFFFFF", ec="#E2E8F0", lw=2)
info_text = """
GEOGRAPHICAL DISTRIBUTION

• Primarily distributed in areas with:
  - High school densities
  - Major urban centers throughout Vietnam

• Majority of responses recorded from:
  - Hanoi
  - Da Nang
  - Ho Chi Minh City



TARGET AUDIENCE INSIGHTS

• Age Group: 15 - 29 (Gen Z)
• Focus Group (18-23): ~86%
• Representative of:
  - University Students
  - Young Workforce
  (Aligned with Government policies)
"""

ax2.text(0.05, 0.5, info_text, ha='left', va='center', fontsize=14, color='#334155', linespacing=1.8, bbox=bbox_props)

plt.tight_layout(rect=[0, 0.03, 1, 0.9])

# Save paths
path1 = r'e:\VKU\Research\Research2026-tamli\outputs\survey_demographics.png'
path2 = r'C:\Users\quang\.gemini\antigravity\brain\5d3d439f-681a-4a05-8499-5b7bc51710f3\artifacts\survey_demographics.png'

plt.savefig(path1, dpi=300, bbox_inches='tight', transparent=True)
plt.savefig(path2, dpi=300, bbox_inches='tight', transparent=True)

plt.close()

print(f"Charts saved to:\n1. {path1}\n2. {path2}")
