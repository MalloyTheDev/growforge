# FILE: growforge/utils/exporters.py
"""
GrowForge — PDF and CSV export functionality for grow reports.
"""

import csv
import os
from datetime import datetime
from fpdf import FPDF
from config import EXPORT_DIR


class GrowReportPDF(FPDF):
    """Custom PDF class for grow reports."""

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(76, 175, 80)
        self.cell(0, 10, "GrowForge Grow Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)
        self.set_draw_color(76, 175, 80)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(46, 125, 50)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def key_value(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(50, 6, f"{key}:")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")


def export_plant_report(plant, events, environment=None):
    """Export a full plant grow report as PDF."""
    pdf = GrowReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Plant info
    pdf.section_title(f"Plant: {plant.get('name', 'Unknown')}")
    pdf.key_value("Strain", plant.get("strain_name", "N/A"))
    pdf.key_value("Type", plant.get("plant_type", "N/A"))
    pdf.key_value("Genetics", plant.get("genetics_type", "N/A"))
    pdf.key_value("Stage", plant.get("stage", "N/A"))
    pdf.key_value("Start Date", plant.get("start_date", "N/A"))
    pdf.key_value("Medium", plant.get("medium", "N/A"))
    pdf.key_value("Pot Size", plant.get("pot_size", "N/A"))

    if plant.get("yield_grams"):
        pdf.key_value("Yield", f"{plant['yield_grams']}g")

    if plant.get("notes"):
        pdf.ln(3)
        pdf.sub_title("Notes")
        pdf.body_text(plant["notes"])

    # Environment
    if environment:
        pdf.ln(5)
        pdf.section_title("Environment")
        pdf.key_value("Name", environment.get("name", "N/A"))
        pdf.key_value("Type", environment.get("env_type", "N/A"))
        pdf.key_value("Light", f"{environment.get('light_type', 'N/A')} ({environment.get('light_wattage', 0)}W)")
        pdf.key_value("Schedule", environment.get("light_schedule", "N/A"))
        pdf.key_value("Tent Size", environment.get("tent_size", "N/A"))

    # Events / Journal
    if events:
        pdf.add_page()
        pdf.section_title("Grow Journal")

        for event in events:
            date = event.get("event_date", "")[:10]
            etype = event.get("event_type", "")
            pdf.sub_title(f"{date} — {etype}")

            if event.get("notes"):
                pdf.body_text(event["notes"])

            metrics = []
            if event.get("ph"):
                metrics.append(f"pH: {event['ph']}")
            if event.get("ec"):
                metrics.append(f"EC: {event['ec']}")
            if event.get("temp"):
                metrics.append(f"Temp: {event['temp']}°C")
            if event.get("humidity"):
                metrics.append(f"RH: {event['humidity']}%")
            if event.get("vpd"):
                metrics.append(f"VPD: {event['vpd']} kPa")
            if event.get("water_ml"):
                metrics.append(f"Water: {event['water_ml']}ml")

            if metrics:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 5, " | ".join(metrics), new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)

    # Save
    filename = f"grow_report_{plant.get('name', 'plant')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(str(EXPORT_DIR), filename)
    pdf.output(filepath)
    return filepath


def export_events_csv(events, filename=None):
    """Export events to CSV."""
    if not filename:
        filename = f"events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(str(EXPORT_DIR), filename)

    if not events:
        return None

    fieldnames = list(events[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)

    return filepath


def export_all_data(plants, events, environments, strains):
    """Export all data as a comprehensive CSV bundle."""
    files = []

    if plants:
        fp = os.path.join(str(EXPORT_DIR), f"all_plants_{datetime.now().strftime('%Y%m%d')}.csv")
        with open(fp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(plants[0].keys()))
            writer.writeheader()
            writer.writerows(plants)
        files.append(fp)

    if events:
        fp = export_events_csv(events, f"all_events_{datetime.now().strftime('%Y%m%d')}.csv")
        if fp:
            files.append(fp)

    if environments:
        fp = os.path.join(str(EXPORT_DIR), f"all_environments_{datetime.now().strftime('%Y%m%d')}.csv")
        with open(fp, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(environments[0].keys()))
            writer.writeheader()
            writer.writerows(environments)
        files.append(fp)

    return files
