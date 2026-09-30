"""Exports for simulation results."""

from __future__ import annotations

from io import BytesIO
from typing import Any


def make_pdf_report(result: dict[str, Any]) -> bytes:
    """Build a compact, reproducible PDF report. Requires ReportLab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    except ImportError as exc:
        raise RuntimeError("Para gerar PDF, instale as dependências com: pip install -r requirements.txt") from exc

    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=17 * mm, leftMargin=17 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm, title="Relatório de simulação geotécnica")
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#17324d")))
    story = [Paragraph("Simulação de tensões geotécnicas", styles["TitleCenter"]),
             Paragraph("Perfil inicial e isóbaras no plano do grupo", styles["Heading2"]), Spacer(1, 5 * mm)]
    p = result["inputs"]
    g = result["geometry"]
    initial = result["initial_at_group_plane"]
    summary = result["summary"]
    rows = [
        ["Parâmetro", "Valor", "Unidade"],
        ["Cota do plano", f"{p['group_elevation_m']:.2f}", "m"],
        ["Nível d’água", f"{p['water_table_elevation_m']:.2f}", "m"],
        ["γw", f"{p['gamma_water_kN_m3']:.3f}", "kN/m³"],
        ["Tensão total inicial σv", f"{initial['sigma_v_kPa']:.3f}", "kPa"],
        ["Poropressão u", f"{initial['u_kPa']:.3f}", "kPa"],
        ["Tensão efetiva inicial σ′v", f"{initial['sigma_eff_kPa']:.3f}", "kPa"],
        ["Pressão do aterro extenso", f"{g['fill_pressure_kPa']:.3f}", "kPa"],
        ["Altura calculada do aterro anelar", f"{g['ring_height_m']:.5f}", "m"],
        ["Pressão do alívio da escavação", f"{g['excavation_pressure_kPa']:.3f}", "kPa"],
        ["Pressão do aterro anelar", f"{g['ring_pressure_kPa']:.3f}", "kPa"],
        ["Maior Δσv na malha", f"{summary['max_total']['total_kPa']:.3f}", "kPa"],
        ["Menor Δσv na malha", f"{summary['min_total']['total_kPa']:.3f}", "kPa"],
        ["Maior Δσv/σ′v", f"{100 * summary['max_ratio']['ratio']:.3f}", "%"],
        ["Menor Δσv/σ′v", f"{100 * summary['min_ratio']['ratio']:.3f}", "%"],
    ]
    table = Table(rows, colWidths=[83 * mm, 42 * mm, 35 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3f8")]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
        ("FONTSIZE", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [Paragraph("Parâmetros e resultados", styles["Heading1"]), table, Spacer(1, 5 * mm)]
    story.append(Paragraph("Geometria e cargas", styles["Heading1"]))
    story.append(Paragraph(
        f"Torre Q={p['tower_load_kN']:.2f} kN em ({p['tower_x_m']:.2f}, {p['tower_y_m']:.2f}) m. "
        f"Aterro q={g['fill_pressure_kPa']:.3f} kPa, x={p['fill_x_min_m']:.2f}–{p['fill_x_max_m']:.2f} m. "
        f"Escavação com centro ({p['excavation_x_m']:.2f}, {p['excavation_y_m']:.2f}) m e raio {g['excavation_radius_m']:.2f} m; "
        f"anel com raios {g['ring_inner_radius_m']:.2f}–{g['ring_outer_radius_m']:.2f} m."
        , styles["BodyText"]))
    story += [Spacer(1, 3 * mm), Paragraph("Equações implementadas", styles["Heading1"]),
              Paragraph("σv = soma(γi·Δzi); u = γw·max(0, d−dNA); σ′v = σv−u.", styles["BodyText"]),
              Paragraph("Torre: Δσv = 3Qz³/[2π(r²+z²)^(5/2)] (Boussinesq).", styles["BodyText"]),
              Paragraph("Aterro: integração da solução de Boussinesq sobre faixa uniforme infinita em y e finita em x.", styles["BodyText"]),
              Paragraph("Disco e anel: integração numérica polar do mesmo núcleo de Boussinesq, com sinal negativo para o alívio.", styles["BodyText"]),
              Paragraph("Razão exibida: Δσv,total/σ′v,inicial na cota do grupo.", styles["BodyText"]),
              Spacer(1, 3 * mm), Paragraph("Hipóteses e limitações", styles["Heading1"])]
    for assumption in result["assumptions"]:
        story.append(Paragraph("• " + assumption, styles["BodyText"]))
        story.append(Spacer(1, 1.2 * mm))
    story += [Spacer(1, 3 * mm), Paragraph("Coordenadas dos extremos na malha", styles["Heading1"])]
    for label, key in (("Máximo Δσv", "max_total"), ("Mínimo Δσv", "min_total"), ("Máximo da razão", "max_ratio"), ("Mínimo da razão", "min_ratio")):
        pt = summary[key]
        val = pt["total_kPa"] if "total" in key else 100 * pt["ratio"]
        unit = "kPa" if "total" in key else "%"
        story.append(Paragraph(f"{label}: {val:.3f} {unit} em (x,y)=({pt['x_m']:.2f},{pt['y_m']:.2f}) m.", styles["BodyText"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Este relatório apresenta tensões calculadas conforme as hipóteses listadas. Não representa uma verificação de segurança, estabilidade ou dimensionamento, pois tais critérios não foram fornecidos no enunciado.", styles["Italic"]))
    doc.build(story)
    return out.getvalue()

