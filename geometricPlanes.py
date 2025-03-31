# Quarto Geometry: Generalized Affine and Projective Planes

# Position mapping for affine plane: (row, col) -> index
def pos_index(row, col, order):
    return row * order + col

# Base Game: 10 standard Quarto winning lines (4x4 grid)
def base_quarto_lines():
    lines = []

    for r in range(4):
        lines.append([pos_index(r, c, 4) for c in range(4)])

    for c in range(4):
        lines.append([pos_index(r, c, 4) for r in range(4)])

    lines.append([pos_index(i, i, 4) for i in range(4)])
    lines.append([pos_index(i, 3 - i, 4) for i in range(4)])

    return lines

# Cartesian product
def cartesian_product(*sequences):
    if not sequences:
        return [()]
    rest = cartesian_product(*sequences[1:])
    return [(item,) + items for item in sequences[0] for items in rest]

# General Affine Plane of order q
def affine_plane_lines(order):
    lines = []
    seen = set()

    for m in list(range(order)) + ['inf']:
        for b in range(order):
            line = []
            for x in range(order):
                if m == 'inf':
                    line = [(x, y) for y in range(order)]
                    break
                else:
                    y = (m * x + b) % order
                    line.append((x, y))
            indices = tuple(sorted(pos_index(y, x, order) for (x, y) in line))
            if indices not in seen:
                seen.add(indices)
                lines.append(list(indices))

    return lines

# General Projective Plane of order q
def projective_plane_lines(order):
    field = list(range(order))
    all_triples = []
    for x in field:
        for y in field:
            for z in field:
                if (x, y, z) != (0, 0, 0):
                    all_triples.append((x, y, z))
    
    def normalize(v):
        for i in range(3):
            if v[i] != 0:
                inv = pow(v[i], -1, order)
                return tuple((inv * x) % order for x in v)
        return v


    points_set = []
    seen = set()
    for v in all_triples:
        norm = normalize(v)
        if norm not in seen:
            seen.add(norm)
            points_set.append(norm)

    point_idx = {pt: i for i, pt in enumerate(points_set)}

    lines = []
    seen_lines = set()
    for a in field:
        for b in field:
            for c in field:
                if (a, b, c) == (0, 0, 0):
                    continue
                line_pts = []
                for pt in points_set:
                    x, y, z = pt
                    if (a * x + b * y + c * z) % order == 0:
                        line_pts.append(point_idx[pt])
                if len(line_pts) == order + 1:
                    indices = tuple(sorted(line_pts))
                    if indices not in seen_lines:
                        seen_lines.add(indices)
                        lines.append(list(indices))

    return lines

def print_lines(name, lines):
    print(f"\n{name} ({len(lines)} lines):")
    for line in lines:
        print(line)

if __name__ == "__main__":
    print_lines("Base Quarto Lines (10)", base_quarto_lines())
    print_lines("Affine Plane of Order 4 (20)", affine_plane_lines(4))
    print_lines("Fano Plane (Projective Plane of Order 2)", projective_plane_lines(2))
    print_lines("Projective Plane of Order 3", projective_plane_lines(3))
    print_lines("Projective Plane of Order 5", projective_plane_lines(5))