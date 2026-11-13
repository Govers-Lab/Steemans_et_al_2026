"""Display both conservation-tree variants from Dataset S9.
Filled/open squares distinguish species/genus support. Blank calls may be
not detected or unresolved; guide dots do not encode evidence.
Run from any directory: python 10-Y_gene_conservation_analysis.py
"""
from pathlib import Path
from io import StringIO
from collections import Counter
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Wedge
from openpyxl import load_workbook
from Bio import Phylo

# Original display settings; scientific observations and tree remain in Dataset S9.
DOMAIN_COLORS = {'Bacteria': {'branch_color': '#2379A6', 'background_color': '#EDF5FA'},
 'Eukaryota': {'branch_color': '#9D5088', 'background_color': '#F9EFF6'},
 'Archaea': {'branch_color': '#43834B', 'background_color': '#F0F7EF'}}

GLOBAL_SETTINGS = {'page_size_mm': 100,
 'font_family': 'Arial',
 'angle_start_deg': 110,
 'angle_span_deg': 340,
 'protein_label_angle_deg': 100,
 'guide_dot_diameter_mm': 0.12,
 'guide_dot_color': '#C7CDD1',
 'scale_bar_source_units': 1}

VARIANT_SETTINGS = {'main': {'species_labels': False,
          'species_font_pt': 3,
          'tree_radius_mm': 30.8,
          'alignment_radius_mm': 32,
          'ring_start_mm': 33,
          'ring_step_mm': 1.6,
          'species_label_radius_mm': 28.7,
          'square_side_mm': 0.9,
          'tree_line_width_pt': 0.28,
          'alignment_line_width_pt': 0.17,
          'square_line_width_pt': 0.35,
          'protein_font_pt': 5.1,
          'domain_font_pt': 6.5,
          'legend_font_pt': 4.5,
          'blank_legend_font_pt': 4,
          'scale_font_pt': 4.5,
          'Bacteria_label_x_mm': -7,
          'Bacteria_label_y_mm': 3.5,
          'Eukaryota_label_x_mm': 9.5,
          'Eukaryota_label_y_mm': 1.8,
          'Archaea_label_x_mm': 1,
          'Archaea_label_y_mm': 7},
 'supplementary': {'species_labels': True,
                   'species_font_pt': 3,
                   'tree_radius_mm': 17.4,
                   'alignment_radius_mm': 18.15,
                   'ring_start_mm': 18.8,
                   'ring_step_mm': 1.1,
                   'species_label_radius_mm': 28.7,
                   'square_side_mm': 0.58,
                   'tree_line_width_pt': 0.2,
                   'alignment_line_width_pt': 0.13,
                   'square_line_width_pt': 0.23,
                   'protein_font_pt': 3.3,
                   'domain_font_pt': 4.5,
                   'legend_font_pt': 3.8,
                   'blank_legend_font_pt': 3.3,
                   'scale_font_pt': 3.7,
                   'Bacteria_label_x_mm': -4,
                   'Bacteria_label_y_mm': 2,
                   'Eukaryota_label_x_mm': 6.5,
                   'Eukaryota_label_y_mm': 1,
                   'Archaea_label_x_mm': 0.1,
                   'Archaea_label_y_mm': 3.8}}


def table(book, sheet):
    rows = book[sheet].iter_rows(values_only=True)
    fields = next(rows)
    return [dict(zip(fields, row)) for row in rows if row[0] is not None]

def xy(radius, angle):
    return (radius * math.cos(angle), radius * math.sin(angle))

def draw(book, variant):
    taxa = table(book, 'Taxa')
    cells = table(book, 'Protein_status')
    proteins = sorted(table(book, 'Proteins'), key=lambda row: row['ring_order'])
    domains = DOMAIN_COLORS
    settings = {**GLOBAL_SETTINGS, **VARIANT_SETTINGS[variant]}
    show_labels = bool(settings['species_labels'])
    by_tip = {row['source_tree_tip']: row for row in taxa}
    statuses = {(row['taxon_label'], row['protein_name']): row for row in cells}
    newick = next((row['newick'] for row in table(book, 'Tree') if row['tree_id'] == 'display_161'))
    tree = Phylo.read(StringIO(newick), 'newick')
    tips = tree.get_terminals()
    assert len(tips) == len(taxa) and len(statuses) == len(tips) * len(proteins)
    assert set(by_tip) == {tip.name for tip in tips}
    plt.rcParams.update({'font.family': settings['font_family'], 'font.size': 4, 'axes.linewidth': 0.2})
    page_mm = float(settings['page_size_mm'])
    fig = plt.figure(figsize=(page_mm / 25.4, page_mm / 25.4), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    limit = page_mm / 2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')
    ax.axis('off')
    angles = {tip: math.radians(settings['angle_start_deg'] + settings['angle_span_deg'] * i / (len(tips) - 1)) for i, tip in enumerate(tips)}
    angle_step = math.radians(settings['angle_span_deg'] / (len(tips) - 1))
    depths = tree.depths()
    tree_radius = float(settings['tree_radius_mm'])
    mm_per_source_unit = tree_radius / max(depths.values())
    depths_mm = {node: depth * mm_per_source_unit for node, depth in depths.items()}
    radii = {row['protein_name']: settings['ring_start_mm'] + settings['ring_step_mm'] * i for i, row in enumerate(proteins)}
    node_angles, node_domains = ({}, {})
    for node in tree.find_clades(order='postorder'):
        leaves = node.get_terminals()
        node_angles[node] = sum((angles[t] for t in leaves)) / len(leaves)
        domain_set = {by_tip[t.name]['domain'] for t in leaves}
        node_domains[node] = next(iter(domain_set)) if len(domain_set) == 1 else None
    for name, domain in domains.items():
        aa = [angles[t] for t in tips if by_tip[t.name]['domain'] == name]
        lo, hi = (min(aa) - angle_step / 2, max(aa) + angle_step / 2)
        sector = Wedge((0, 0), tree_radius, math.degrees(lo), math.degrees(hi), facecolor=domain['background_color'], edgecolor='none', zorder=-10)
        ax.add_patch(sector)
    for index, node in enumerate(tree.find_clades(order='preorder')):
        r, a = (depths_mm[node], node_angles[node])
        color = domains[node_domains[node]]['branch_color'] if node_domains[node] else '#647077'
        if node.clades:
            lo = min((node_angles[c] for c in node.clades))
            hi = max((node_angles[c] for c in node.clades))
            points = [xy(r, lo + (hi - lo) * i / 120) for i in range(121)]
            line, = ax.plot([p[0] for p in points], [p[1] for p in points], color=color, lw=settings['tree_line_width_pt'], zorder=1)
            for j, child in enumerate(node.clades):
                p, q = (xy(r, node_angles[child]), xy(depths_mm[child], node_angles[child]))
                color = domains[node_domains[child]]['branch_color'] if node_domains[child] else '#647077'
                line, = ax.plot([p[0], q[0]], [p[1], q[1]], lw=settings['tree_line_width_pt'], color=color, zorder=1)
        else:
            p, q = (xy(r, a), xy(settings['alignment_radius_mm'], a))
            ax.plot([p[0], q[0]], [p[1], q[1]], color='#B0BBC1', lw=settings['alignment_line_width_pt'], ls=(0, (1, 2.5)), zorder=0)
    for protein in proteins:
        name = protein['protein_name']
        points = [xy(radii[name], angles[tip]) for tip in tips]
        guide = ax.scatter([p[0] for p in points], [p[1] for p in points], s=(settings['guide_dot_diameter_mm'] * 72 / 25.4) ** 2, facecolor=settings['guide_dot_color'], edgecolors='none', zorder=2)
    counts = Counter()
    for tip_index, tip in enumerate(tips):
        taxon, a = (by_tip[tip.name], angles[tip])
        c, s = (math.cos(a), math.sin(a))
        for protein in proteins:
            name, color = (protein['protein_name'], protein['color'])
            row = statuses[taxon['taxon_label'], name]
            filled, opened = (int(row['supported_presence']), int(row['genus_only_presence']))
            assert filled + opened <= 1
            assert filled == (row['status'] == 'species_present')
            assert opened == (row['status'] == 'genus_only')
            if not (filled or opened):
                continue
            cx, cy = xy(radii[name], a)
            half = settings['square_side_mm'] / 2
            vertices = [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in [(-half, -half), (half, -half), (half, half), (-half, half)]]
            square = Polygon(vertices, closed=True, edgecolor=color, facecolor=color if filled else 'white', lw=settings['square_line_width_pt'], joinstyle='miter', zorder=4)
            kind = 'supported_presence' if filled else 'genus_only_presence'
            ax.add_patch(square)
            counts[kind] += 1
        if show_labels:
            degree = math.degrees(a) % 360
            left = 90 < degree < 270
            text = ax.text(*xy(settings['species_label_radius_mm'], a), taxon['taxon_label'], fontsize=settings['species_font_pt'], fontstyle='italic', rotation=degree + 180 if left else degree, rotation_mode='anchor', ha='right' if left else 'left', va='center', color='#20272C', zorder=6)
    for protein in proteins:
        name = protein['protein_name']
        text = ax.text(*xy(radii[name], math.radians(settings['protein_label_angle_deg'])), name, rotation=10, ha='center', va='center', fontsize=settings['protein_font_pt'], fontstyle='normal', color=protein['color'], zorder=7)
    for name, domain in domains.items():
        text = ax.text(settings[name + '_label_x_mm'], settings[name + '_label_y_mm'], name, color=domain['branch_color'], fontsize=settings['domain_font_pt'], weight='bold', ha='center', va='center', zorder=8)
    for x, y, filled, label in [(-46, -44.4, True, 'Supported presence'), (-46, -46.5, False, 'Genus-only presence')]:
        ax.add_patch(Polygon([(x - 0.35, y - 0.35), (x + 0.35, y - 0.35), (x + 0.35, y + 0.35), (x - 0.35, y + 0.35)], facecolor='#43515A' if filled else 'white', edgecolor='#43515A', lw=0.35))
        ax.text(x + 1.3, y, label, fontsize=settings['legend_font_pt'], va='center', color='#303B42')
    ax.text(-46.5, -48.5, 'No square: not found or unresolved', ha='left', va='center', fontsize=settings['blank_legend_font_pt'], color='#303B42')
    sx, sy = (-45, -40.2)
    length = settings['scale_bar_source_units'] * mm_per_source_unit
    ax.plot([sx, sx + length], [sy, sy], color='#43515A', lw=0.45)
    for x in [sx, sx + length]:
        ax.plot([x, x], [sy - 0.32, sy + 0.32], color='#43515A', lw=0.35)
    ax.text(sx + length / 2, sy - 1.45, f"{settings['scale_bar_source_units']:g} source unit", ha='center', va='center', fontsize=settings['scale_font_pt'])
    fig.canvas.draw()
    outside = [t.get_text() for t in ax.texts if not fig.bbox.contains(*t.get_window_extent().p0) or not fig.bbox.contains(*t.get_window_extent().p1)]
    assert not outside, f'Text outside page: {outside}'
    expected = Counter(supported_presence=sum((int(r['supported_presence']) for r in cells)), genus_only_presence=sum((int(r['genus_only_presence']) for r in cells)))
    assert counts == expected
    assert tree_radius < min(radii.values()) - settings['square_side_mm']
    plt.show()
    return fig

def main():
    workbook = Path(__file__).resolve().parent.parent / "Datasets" / "Dataset S9.xlsx"
    book = load_workbook(workbook, read_only=True, data_only=True)
    try:
        for variant in ("main", "supplementary"):
            draw(book, variant)
    finally:
        book.close()

if __name__ == "__main__":
    main()
