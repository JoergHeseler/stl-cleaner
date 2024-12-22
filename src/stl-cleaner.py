# Title: stl-cleaner
# Version: 1.0.0
# Publisher: NFDI4Culture
# Publication date: December 16, 2024
# License: CC BY-SA 4.0
# Author: Joerg Heseler
# References: https://www.fabbers.com/tech/STL_Format

from __future__ import print_function
import os
import struct
import sys
import math
import re

SUCCESS_CODE = 0
ERROR_CODE = 1
DEBUG = 1
# strict_mode = True
force_repositioning = False
new_min_pos = [0.01, 0.01, 0.01]
ignore_endsolid_name = False
indent_spaces = 1
ERROR = True
WARNING = False

warning_count = 0
error_count = 0
first_error_message = ""
output_detailed_warnings = False 
# stop_on_first_error = False

######################## GEOMETRY FUNCTIONS ########################

def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def cross_product(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def vector_magnitude(v):
    return math.sqrt(sum(x ** 2 for x in v))

def normalize_vector(v):
    magnitude = vector_magnitude(v)
    if magnitude == 0:
        return [0, 0, 0]
    return [x / magnitude for x in v]

# New feature: Recalculate facet normal if invalid
def recalculate_normal(vertex1, vertex2, vertex3):
    """
    Recalculates the normal vector for a given facet using the cross product.
    """
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    return normalize_vector(cross_product(edge1, edge2))

def are_vectors_close(v1, v2, tol=1e-3):
    return all(abs(a - b) <= tol for a, b in zip(v1, v2))

# def is_facet_oriented_correctly(vertex1, vertex2, vertex3, normal):
#     edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
#     edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
#     calculated_normal = normalize_vector(cross_product(edge1, edge2))
#     normal = normalize_vector(normal)
#     return are_vectors_close(calculated_normal, normal)

def ensure_counterclockwise(vertex1, vertex2, vertex3, normal):
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    calculated_normal = cross_product(edge1, edge2)
    if dot_product(calculated_normal, normal) < 0:
        return [vertex1, vertex3, vertex2]
    return [vertex1, vertex2, vertex3]

def is_counterclockwise(vertex1, vertex2, vertex3, normal):
    edge1 = [v2 - v1 for v1, v2 in zip(vertex1, vertex2)]
    edge2 = [v3 - v1 for v1, v3 in zip(vertex1, vertex3)]
    calculated_normal = cross_product(edge1, edge2)
    return dot_product(calculated_normal, normal) > 0

def make_model_manifold(facets):
    """
    Ensures the manifoldness of the model by applying the vector-to-vector rule.
    This involves fixing open edges and removing duplicate facets.
    """
    edge_to_facets = {}
    fixed_facets = []
    open_edges = []

    # Step 1: Track edges and their associated facets
    for facet in facets:
        edges = [
            tuple(sorted((tuple(facet[1]), tuple(facet[2])))),
            tuple(sorted((tuple(facet[2]), tuple(facet[3])))),
            tuple(sorted((tuple(facet[3]), tuple(facet[1]))))
        ]
        for edge in edges:
            if edge not in edge_to_facets:
                edge_to_facets[edge] = []
            edge_to_facets[edge].append(facet)

    # Step 2: Identify and handle open edges
    for edge, associated_facets in edge_to_facets.items():
        if len(associated_facets) == 1:
            open_edges.append(edge) # Open edge found

    # Step 3: Close open edges
    for edge in open_edges:
        v1, v2 = edge
        # Find a vertex close to the open edge to form a new triangle
        for other_edge in open_edges:
            if v2 in other_edge and edge != other_edge:
                v3 = other_edge[0] if other_edge[1] == v2 else other_edge[1]
                new_normal = recalculate_normal(v1, v2, v3)
                new_facet = [new_normal, v1, v2, v3]
                fixed_facets.append(new_facet)
                break

    # Step 4: Remove duplicate facets
    unique_facets = {tuple(tuple(vertex) for vertex in facet) for facet in (facets + fixed_facets)}
    manifold_facets = [list(map(list, facet)) for facet in unique_facets]

    return manifold_facets


def is_model_manifold(facets):
    """
    Checks if a 3D model is manifold.
    A model is manifold if each edge is shared by exactly two triangles.
    
    Parameters:
        facets (list): List of facets, where each facet is a list of 4 elements:
                       [normal, vertex1, vertex2, vertex3].
    
    Returns:
        bool: True if the model is manifold, False otherwise.
        dict: A report containing details about non-manifold edges, if any.
    """
    edge_usage = {}

    # Step 1: Count usage of each edge
    for facet in facets:
        edges = [
            tuple(sorted((tuple(facet[1]), tuple(facet[2])))),
            tuple(sorted((tuple(facet[2]), tuple(facet[3])))),
            tuple(sorted((tuple(facet[3]), tuple(facet[1]))))
        ]
        for edge in edges:
            if edge in edge_usage:
                edge_usage[edge] += 1
            else:
                edge_usage[edge] = 1

    # Step 2: Analyze edge usage
    non_manifold_edges = {edge: count for edge, count in edge_usage.items() if count != 2}
    is_manifold = len(non_manifold_edges) == 0

    # # Step 3: Return result
    # report = {
    #     "is_manifold": is_manifold,
    #     "non_manifold_edges": non_manifold_edges,
    #     "total_edges": len(edge_usage),
    #     "non_manifold_edge_count": len(non_manifold_edges),
    # }

    return is_manifold #, report


######################## LINE FUNCTIONS ########################

line_index = 0
lines = []

def handle_error_with_line_index(type, expected, got = None):
    global line_index, error_count, warning_count, output_detailed_warnings
    if type == ERROR:
        # Error
        error_count += 1
        if got:
            error_message = f"Error on line {line_index + 1}: Expected '{expected}' but got '{got.strip()}'."
        else:
            error_message = f"Error on line {line_index + 1}: {expected}."
        raise STLCleanerException(error_message)
    elif type == WARNING:
        # Warning
        warning_count += 1
        if output_detailed_warnings:
            if got:
                print(f"Warning on line {line_index + 1}: Expected '{expected}' but got '{got.strip()}'.")
            else:
                print(f"Warning on line {line_index + 1}: {expected}.")

def handle_error_with_file_pos(type, pos, expected, got = None):
    global error_count, warning_count, output_detailed_warnings
    if type == ERROR:
        # Error
        error_count += 1
        if got:
            error_message = f"Error on position {pos}: Expected '{expected}' but got '{got.strip()}'."
        else:
            error_message = f"Error on position {pos}: {expected}."
        raise STLCleanerException(error_message)
    elif type == WARNING:
        # Warning
        warning_count += 1
        if output_detailed_warnings:
            if got:
                print(f"Warning on position {pos}: Expected '{expected}' but got '{got.strip()}'.")
            else:
                print(f"Warning on position {pos}: {expected}.")


def get_current_line():
    global line_index, lines
    return lines[line_index]

def skip_empty_lines():
    global line_index
    global lines
    while len(lines) > line_index + 1 and lines[line_index].strip() == "":
        handle_error_with_line_index(WARNING, "Line is empty")
        line_index += 1

def init_line():
    global line_index, lines
    line_index = 0
    skip_empty_lines()

def go_to_next_line():
    global line_index, lines
    line_index += 1
    skip_empty_lines()

######################## STL FUNCTIONS ########################

def is_binary_stl(file_path):
    # Check if the STL file is binary or ASCII.
    with open(file_path, 'rb') as file:
        file_size = os.path.getsize(file_path)
        file.read(80).decode('ascii', errors='ignore')
        try:
            triangle_count = struct.unpack('<I', file.read(4))[0]
        except struct.error:
            return False
        return 80 + 4 + 50 * triangle_count == file_size

######################## VALIDATION FUNCTIONS ########################

class STLCleanerException(Exception):
    
    def __init__(self, result):
        super().__init__(result)
        if DEBUG:
            print(result)
        
    # def __init__(self, y, expected, got):
        # super().__init__(result)
        # if DEBUG:
            # print(result)

def clean_binary_stl_file(input_file_path, output_file_path):
    global error_count, warning_count, first_error_message
    with open(input_file_path, 'rb') as file:
        header = file.read(80) # Header
        triangle_count = struct.unpack('<I', file.read(4))[0]
        
        min_vertex = [float("inf"), float("inf"), float("inf")]
        facets = []

        for i in range(triangle_count):
            normal = struct.unpack('<3f', file.read(12))
            vertex1 = struct.unpack('<3f', file.read(12))
            vertex2 = struct.unpack('<3f', file.read(12))
            vertex3 = struct.unpack('<3f', file.read(12))
            attr_byte_count = struct.unpack('<H', file.read(2))[0]

            for j in range(3):
                vertices = [vertex1, vertex2, vertex3]
                vertex = vertices[j]
                for i in range(3):
                    if vertex[j] < min_vertex[j]:
                        min_vertex[j] = vertex[j]

            normal = recalculate_normal(vertex1, vertex2, vertex3)

            facets.append([normal, vertex1, vertex2, vertex3])

            pos = 84 + i * 50

            if any(coord < 0 for coord in vertex1 + vertex2 + vertex3):
                handle_error_with_file_pos(WARNING, pos, "Not all vertices of this facet have positive values")

            if not is_counterclockwise(vertex1, vertex2, vertex3, normal):
                handle_error_with_line_index(WARNING, "Vertices of this facet are not ordered counterclockwise")

            # if any(math.isnan(v) for v in normal + vertex1 + vertex2 + vertex3):
            #     handle_error_with_file_pos(ERROR, pos, "File contains NaN values in normal or vertex coordinates")
            
            if attr_byte_count != 0:
                handle_error_with_file_pos(ERROR, pos, f"Attribute byte count should be '0', but got '{attr_byte_count}'")

    
        # Close holes in the model
        facets = make_model_manifold(facets)
        # print(is_model_manifold(facets))


        with open(output_file_path, 'wb') as fixed_file:
            fixed_file.write(header)
            fixed_file.write(struct.pack("<I", triangle_count))

            adapt_vertex = [0.0, 0.0, 0.0]
            for i in range(3):
                if force_repositioning or min_vertex[i] < new_min_pos[i]:
                    adapt_vertex[i] = -min_vertex[i] + new_min_pos[i]
                else:
                    adapt_vertex[i] = 0

            for k in range(len(facets)):
                facet = facets[k]
                vertices = []
                for j in range(3):
                    vertex = []
                    for i in range(3):
                        vertex.append(facet[1 + j][i] + adapt_vertex[i])
                    vertices.append(vertex)
                fixed_vertices = ensure_counterclockwise(vertices[0], vertices[1], vertices[2], facet[0])
                fixed_file.write(struct.pack("<3f", *(facet[0])))
                fixed_file.write(struct.pack("<3f", *(fixed_vertices[0])))
                fixed_file.write(struct.pack("<3f", *(fixed_vertices[1])))
                fixed_file.write(struct.pack("<3f", *(fixed_vertices[2])))
                fixed_file.write(struct.pack("<H", 0)) # Attribute byte count



def format_event_outcome_detail_note(format, version, result):
    note = 'format="{}";'.format(format)
    if version is not None:
        note = note + ' version="{}";'.format(version)
    if result is not None:
        note = note + ' result="{}"'.format(result)

    return note


def clean_ascii_stl_file(input_file_path, output_file_path):
    global line_index, lines, force_repositioning, indent_spaces, new_min_pos
    with open(input_file_path, 'r') as file:
        lines = [re.sub(r'\s+', ' ' , line.strip()) for line in file.readlines()]
    
    init_line()

    if not get_current_line().startswith("solid"):
        handle_error_with_line_index(ERROR, "solid", get_current_line())
    if not re.search(f"^solid [^\n]+$", get_current_line()):
        handle_error_with_line_index(WARNING, "solid <string>", get_current_line())
        solid_name = ""
    else:
        solid_name = str(get_current_line()[6:]).lstrip()
    go_to_next_line()
    
    # The notation, “{…}+,” means that the contents of the brace brackets
    # can be repeated one or more times.
    # --> Changed by the author to “{…}*”, meaning that the contents of the
    # brace brackets can be repeated none, one or more times, to support
    # empty scenes as many programs are able to export.
    total_facet_count = (len([line for line in lines if line.strip()]) - 2) // 7
    # all_vertex_coordinates_are_positive = True
    # all_facets_normals_are_correct = True
    # all_vertices_of_facets_are_ordered_clockwise = True
    
    min_vertex = [float("inf"), float("inf"), float("inf")]
    facets = []

    for _ in range(total_facet_count):
        if not re.search(f"^facet normal -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
            handle_error_with_line_index(ERROR, "facet normal <float> <float> <float>", get_current_line())
        normal = list(map(float, get_current_line().split()[2:]))
        go_to_next_line()
        if not "outer loop" == get_current_line():
            handle_error_with_line_index(ERROR, "outer loop", get_current_line())
        go_to_next_line()

        vertices = []
        for _ in range(3):
        
            # A facet normal coordinate may have a leading minus sign; 
            # a vertex coordinate may not.
            # --> Changed by the author to vertex coordinates may have a
            # leading minus, to support negative vertices to support many
            # programs are able to export
            if not re.search(f"^vertex -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)? -?\d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                handle_error_with_line_index(ERROR, "vertex <unsigned float> <unsigned float> <unsigned float>", get_current_line())
            # if not re.search(f"^vertex \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)? \d*(\.\d+)?([Ee][+-]?\d+)?$", get_current_line()):
                # print_warning("vertex <unsigned float> <unsigned float> <unsigned float>", get_current_line())
            vertex = list(map(float, get_current_line().split()[1:]))
            go_to_next_line()
            for j in range(3):
                if vertex[j] < min_vertex[j]:
                    min_vertex[j] = vertex[j]
            if any(coord < 0 for coord in vertex):
                # all_vertex_coordinates_are_positive = False
                handle_error_with_line_index(WARNING, "Not all vertice coordinates have positive values")
            vertices.append(vertex)
        # if not is_facet_oriented_correctly(vertices[0], vertices[1], vertices[2], normal):
        #     print_warning("Facet is not oriented correctly")
        #     # all_facets_normals_are_correct = False

        normal = recalculate_normal(vertices[0], vertices[1], vertices[2])
        facets.append([normal, vertices[0], vertices[1], vertices[2]])

        if not is_counterclockwise(vertices[0], vertices[1], vertices[2], normal):
            handle_error_with_line_index(WARNING, "Vertices of this facet are not ordered counterclockwise")
            # all_vertices_of_facets_are_ordered_clockwise = False
        if not "endloop" == get_current_line():
            handle_error_with_line_index(ERROR, "endloop", get_current_line())
        go_to_next_line()
        if not "endfacet" == get_current_line():
            handle_error_with_line_index(ERROR, "endfacet", get_current_line())
        go_to_next_line()

    if not re.search("^endsolid", get_current_line()):
        handle_error_with_line_index(ERROR, "endsolid", get_current_line())
    if solid_name != "":
        if not f"endsolid {solid_name}" == get_current_line():
            handle_error_with_line_index(WARNING, f"endsolid {solid_name}", get_current_line())
    if not re.search(f"^endsolid [^\n]+$", get_current_line()):
        endsolid_name = ""
    else:
        endsolid_name = str(get_current_line()[6:]).lstrip()

    # Close holes in the model
    facets = make_model_manifold(facets)


    go_to_next_line()
    print("Minimum coordinates found:", min_vertex)

    name = solid_name
    if not ignore_endsolid_name:
        if name == '':
            name = endsolid_name
        if solid_name != '' and endsolid_name != '' and solid_name != endsolid_name:
            name = solid_name + ' | ' + endsolid_name
    if name == '':
        name = 'model'
    fixed_lines = []
    fixed_lines.append('solid ' + name)
    INDENT = ' ' * indent_spaces

    adapt_vertex = [0.0, 0.0, 0.0]
    for i in range(3):
        if force_repositioning or min_vertex[i] < new_min_pos[i]:
            adapt_vertex[i] = -min_vertex[i] + new_min_pos[i]
        else:
            adapt_vertex[i] = 0
    
    for facet in facets:
        # print(str(facet))
        fixed_lines.append(f'{INDENT}facet normal {facet[0][0]} {facet[0][1]} {facet[0][2]}')
        fixed_lines.append(f'{INDENT}{INDENT}outer loop')
        vertices = []
        for j in range(3):
            vertex = []
            for i in range(3):
                vertex.append(facet[1 + j][i] + adapt_vertex[i])
            vertices.append(vertex)
        fixed_vertices = ensure_counterclockwise(vertices[0], vertices[1], vertices[2], facet[0])
        for j in range(3):
            fixed_lines.append(f'{INDENT}{INDENT}{INDENT}vertex {fixed_vertices[j][0]} {fixed_vertices[j][1]} {fixed_vertices[j][2]}')
        fixed_lines.append(f'{INDENT}{INDENT}endloop')
        fixed_lines.append(f'{INDENT}endfacet')
    fixed_lines.append('endsolid ' + name)
    with open(output_file_path, 'w') as fixed_file:
        fixed_file.writelines(line + '\n' for line in fixed_lines)
    

def clean_stl_file(input_file_path, output_file_path):
    global error_count, warning_count, first_error_message
    try:
        if is_binary_stl(input_file_path):
            clean_binary_stl_file(input_file_path, output_file_path)
            version = 'binary'
        else:
            clean_ascii_stl_file(input_file_path, output_file_path)
            version = 'ASCII'

        if error_count > 0:
            raise STLCleanerException(f"Validation failed: errors={error_count}, warnings={warning_count}, first error: {first_error_message}")
        
        print('Cleaned STL successfully stored to', output_file_path)
        
        return SUCCESS_CODE

    except STLCleanerException as e:
        print(e, file=sys.stderr)
        return ERROR_CODE


######################## MAIN FUNCTION ########################

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f'STL Cleaner, version 1.0.0')
        print()
        print(f'This script converts ASCII and binary STL files specified at https://www.fabbers.com/tech/STL_Format.')
        print()
        print(f'Usage: python stl-cleaner.py <STL file> [options]')
        print()
        print(f'--o=<output file path>               path to the corrected output STL file')
        print(f'--indent=<number of spaces>          indentation spaces, default={indent_spaces}')
        print(f'--min-pos=<minimum position>         mininum allowed model position, default={new_min_pos[0]},{new_min_pos[1]},{new_min_pos[2]}')
        print(f'--force-repos                        always repositions the model to the minimum position')
        print(f'--ignore-endsolid-name               only considers the solid name')
        sys.exit(0)
    # output_detailed_warnings = any(arg.strip().lower() == "--warnings" for arg in sys.argv)
    input_file_path = sys.argv[1]
    output_file_path = re.sub(r'\.stl$', '-cleaned.stl' , input_file_path)
    for arg in sys.argv: 
        if arg.strip().lower() == '--force-repos':
            force_repositioning = True
        elif arg.strip().lower().startswith('--o='):
            output_file_path = arg.split('=')[1]
            # print('Output file: ', output_file_path)
        elif arg.strip().lower().startswith('--indent='):
            indent_spaces = int(arg.split('=')[1])
        elif arg.strip().lower().startswith('--min-pos='):
            v = arg.split('=')[1].split(',')
            new_min_pos = [float(v[0]), float(v[1]), float(v[2])]
        elif arg.strip().lower() == '--ignore-endsolid-name':
            ignore_endsolid_name = True
    if input_file_path == output_file_path:
        print("Input and output files must not be the same.", file=sys.stderr)
        sys.exit(1)
    sys.exit(clean_stl_file(input_file_path, output_file_path))
